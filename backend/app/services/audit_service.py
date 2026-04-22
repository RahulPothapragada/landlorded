"""Audit pipeline — orchestrates extract → detect → reason → generate."""

import tempfile
import traceback
from pathlib import Path

from supabase import Client

from core.extractor import extract_agreement
from core.detector import detect_all, Severity
from core.corpus_loader import load_corpus, Corpus
from core.reasoner import reason
from core.generator import generate_report_bytes, generate_notice_bytes, generate_checklist_text
from core.whatsapp import generate_whatsapp_text

from ..db import queries
from . import storage_service


# Corpus loaded once, reused across requests
_corpus: Corpus | None = None


def get_corpus() -> Corpus:
    global _corpus
    if _corpus is None:
        _corpus = load_corpus()
    return _corpus


def run_pipeline(db: Client, user_id: str, audit_id: str, file_name: str, mode: str,
                 tenant_name: str, landlord_name: str, premises: str):
    """Run the full analysis pipeline. Called as a background task."""
    try:
        # Download the uploaded PDF to a temp file
        pdf_bytes = storage_service.download_agreement(db, user_id, audit_id, file_name)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        # Extract
        agreement = extract_agreement(tmp_path)

        # Detect
        results = detect_all(agreement.lease_text, agreement.schedule_text)

        # Reason
        corpus = get_corpus()
        analyses = reason(results, corpus)

        # Compute summary
        fired = [a for a in analyses if a.fired]
        red_count = sum(1 for a in fired if a.severity == Severity.RED)
        yellow_count = sum(1 for a in fired if a.severity == Severity.YELLOW)

        if red_count > 0:
            risk_level = "HIGH"
        elif yellow_count > 0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        # Serialize patterns to JSON
        patterns = []
        for a in analyses:
            patterns.append({
                "pattern_id": a.pattern_id,
                "pattern_name": a.pattern_name,
                "fired": a.fired,
                "severity": a.severity.value if a.severity else None,
                "explanation": a.explanation,
                "verdict": a.verdict,
                "statute_citation": a.statute_citation,
                "suggested_rewrite": a.suggested_rewrite,
                "notice_paragraph": a.notice_paragraph,
                "extracted": a.extracted,
                "matched_text": a.matched_text[:3],
            })

        # Generate documents
        documents_available = []

        t_name = tenant_name or "[TENANT NAME]"
        l_name = landlord_name or "[LANDLORD NAME]"
        prem = premises or "[PREMISES ADDRESS]"

        # Report PDF
        report_bytes = generate_report_bytes(analyses, file_name)
        storage_service.upload_document(db, user_id, audit_id, "report", report_bytes)
        documents_available.append("report")

        if mode in ("dispute", "renewal"):
            # Legal notice PDF
            notice_bytes = generate_notice_bytes(analyses, t_name, l_name, prem)
            storage_service.upload_document(db, user_id, audit_id, "legal_notice", notice_bytes)
            documents_available.append("legal_notice")

            # Evidence checklist
            checklist_text = generate_checklist_text(analyses)
            storage_service.upload_document(
                db, user_id, audit_id, "evidence_checklist",
                checklist_text.encode("utf-8"), "text/markdown"
            )
            documents_available.append("evidence_checklist")

            # WhatsApp message
            whatsapp_text = generate_whatsapp_text(analyses, t_name, l_name)
            storage_service.upload_document(
                db, user_id, audit_id, "whatsapp_message",
                whatsapp_text.encode("utf-8"), "text/plain"
            )
            documents_available.append("whatsapp_message")

        # Update DB with results
        queries.update_audit_results(db, audit_id, {
            "status": "complete",
            "page_count": agreement.page_count,
            "ocr_used": agreement.ocr_used,
            "risk_level": risk_level,
            "red_flags": red_count,
            "yellow_flags": yellow_count,
            "patterns": patterns,
            "documents_available": documents_available,
        })

        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        queries.update_audit_results(db, audit_id, {
            "status": "failed",
            "error": str(e),
        })
        traceback.print_exc()
