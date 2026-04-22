"""Streamlit UI for Landlorded."""

import streamlit as st
import tempfile
from pathlib import Path

from extractor import extract_agreement
from detector import detect_all, Severity
from corpus_loader import load_corpus
from reasoner import reason, LegalAnalysis
from generator import generate_all
from whatsapp import generate_whatsapp


st.set_page_config(page_title="Landlorded", page_icon="🏠", layout="wide")

SEVERITY_COLORS = {
    Severity.INFO: "🟢",
    Severity.YELLOW: "🟡",
    Severity.RED: "🔴",
}


def main():
    st.title("Landlorded")
    st.caption("Getting landlorded? Get un-landlorded.")
    st.markdown("Upload a Chennai rental agreement PDF. Get back a clause-by-clause audit, legal notice, and bilingual WhatsApp message.")

    # Sidebar for inputs
    with st.sidebar:
        st.header("Your Details")
        tenant_name = st.text_input("Your name", placeholder="Rahul Pothapragada")
        landlord_name = st.text_input("Landlord name", placeholder="Mrs. J.E. Vasanth")
        premises = st.text_input("Premises address", placeholder="Apt 1136, Estancia, Chengalpattu")

        st.divider()
        st.header("Mode")
        mode = st.radio("Select mode", ["Audit", "Dispute", "Renewal"],
                        captions=["Analyze only", "Analyze + generate documents", "Check renewal terms"])

    # File upload
    uploaded = st.file_uploader("Drop your lease agreement PDF", type=["pdf"])

    if not uploaded:
        st.info("Upload a PDF to get started.")
        _show_sample_output()
        return

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    # Run analysis
    with st.spinner("Reading PDF..."):
        agreement = extract_agreement(tmp_path)

    ocr_note = " *(OCR — scanned PDF)*" if agreement.ocr_used else ""
    st.success(f"Extracted {agreement.page_count} pages ({len(agreement.lease_text):,} chars lease text){ocr_note}")

    with st.spinner("Loading legal corpus..."):
        corpus = load_corpus()

    with st.spinner("Running clause detection..."):
        results = detect_all(agreement.lease_text, agreement.schedule_text)

    with st.spinner("Applying legal reasoning..."):
        analyses = reason(results, corpus)

    # Display results
    _show_summary(analyses)
    _show_detailed(analyses)

    if mode == "Renewal":
        _show_renewal(agreement)

    if mode == "Dispute":
        _show_documents(analyses, tmp_path, tenant_name, landlord_name, premises)


def _show_summary(analyses: list[LegalAnalysis]):
    st.header("Audit Summary")

    fired = [a for a in analyses if a.fired]
    reds = sum(1 for a in fired if a.severity == Severity.RED)
    yellows = sum(1 for a in fired if a.severity == Severity.YELLOW)

    # Risk banner
    if reds > 0:
        st.error(f"**HIGH RISK** — {reds} red flag(s), {yellows} yellow flag(s). {len(fired)} of {len(analyses)} patterns detected.")
    elif yellows > 0:
        st.warning(f"**MODERATE RISK** — {yellows} yellow flag(s). {len(fired)} of {len(analyses)} patterns detected.")
    else:
        st.success(f"**LOW RISK** — {len(fired)} of {len(analyses)} patterns detected. No flags raised.")

    # Summary table
    cols = st.columns([1, 5, 2, 2])
    cols[0].markdown("**#**")
    cols[1].markdown("**Pattern**")
    cols[2].markdown("**Status**")
    cols[3].markdown("**Severity**")

    for a in analyses:
        cols = st.columns([1, 5, 2, 2])
        cols[0].write(str(a.pattern_id))
        cols[1].write(a.pattern_name)
        if a.fired:
            cols[2].write("Detected")
            emoji = SEVERITY_COLORS.get(a.severity, "⚪")
            label = a.severity.value if a.severity else "—"
            cols[3].write(f"{emoji} {label}")
        else:
            cols[2].write("—")
            cols[3].write("—")


def _show_detailed(analyses: list[LegalAnalysis]):
    st.header("Detailed Findings")

    fired = [a for a in analyses if a.fired]
    for a in fired:
        emoji = SEVERITY_COLORS.get(a.severity, "⚪")
        label = a.severity.value if a.severity else ""

        with st.expander(f"{emoji} Pattern {a.pattern_id}: {a.pattern_name} [{label}]", expanded=(a.severity == Severity.RED)):
            # Verdict
            if a.verdict:
                st.info(a.verdict)

            # Key values
            if a.extracted:
                important = {k: v for k, v in a.extracted.items()
                             if v is not None and v != [] and v != ""}
                if important:
                    st.markdown("**Key findings:**")
                    for k, v in important.items():
                        if isinstance(v, bool):
                            v = "Yes" if v else "No"
                        elif isinstance(v, int) and v > 1000:
                            v = f"Rs. {v:,}"
                        st.markdown(f"- `{k}`: {v}")

            # Matched text
            if a.matched_text:
                st.markdown("**From your agreement:**")
                for text in a.matched_text[:2]:
                    truncated = text[:300] + "..." if len(text) > 300 else text
                    st.markdown(f"> *{truncated}*")

            # Statute citation
            if a.statute_citation:
                st.markdown("**Applicable law:**")
                st.markdown(a.statute_citation)

            # Rewrite
            if a.suggested_rewrite:
                st.markdown("**Suggested clause rewrite:**")
                st.success(f'"{a.suggested_rewrite}"')

            # Notice paragraph
            if a.notice_paragraph:
                st.markdown("**For your legal notice:**")
                st.markdown(f'> "{a.notice_paragraph}"')


def _show_renewal(agreement):
    import re
    from detector import _normalize

    st.header("Renewal Analysis")

    text = _normalize(agreement.lease_text)
    lower = text.lower()

    escalation_terms = ["not less than", "escalation", "rental rate escalation", "5%"]
    found = []
    for term in escalation_terms:
        if term in lower:
            idx = lower.index(term)
            snippet = text[max(0, idx - 100):idx + len(term) + 150].strip()
            if snippet not in found:
                found.append(snippet)

    if found:
        has_cap = any(t in lower for t in ["not exceeding", "maximum", "cap of"])
        has_floor = any(t in lower for t in ["not less than", "at least"])

        if has_floor and not has_cap:
            st.error("**No upper cap on escalation.** The clause sets a floor (e.g., 'not less than 5%') but no ceiling.")
        elif has_cap:
            st.success("Escalation has a cap. Review whether it's reasonable.")

        for snippet in found[:2]:
            st.markdown(f"> *{snippet[:300]}*")
    else:
        st.info("No explicit escalation clause found.")

    st.markdown("""
**Before signing a renewal:**
1. Check for 'supersession' / 'entire agreement' clauses — strike them
2. Add handwritten note preserving original deposit claim with refund timeline
3. Negotiate escalation cap ('not exceeding 5%' instead of 'not less than 5%')
4. Insist on Rent Authority registration
5. Export all WhatsApp chats before signing
6. Do NOT pay brokerage without GST invoice
""")


def _show_documents(analyses, pdf_path, tenant_name, landlord_name, premises):
    st.header("Generated Documents")

    tenant = tenant_name or "[TENANT NAME]"
    landlord = landlord_name or "[LANDLORD NAME]"
    prem = premises or "[PREMISES ADDRESS]"

    with st.spinner("Generating documents..."):
        outputs = generate_all(analyses, pdf_path, tenant, landlord, prem)
        whatsapp_msg = generate_whatsapp(analyses, tenant, landlord)

    # Download buttons
    col1, col2, col3, col4 = st.columns(4)

    report_path = outputs["report"]
    if report_path.exists():
        with open(report_path, "rb") as f:
            col1.download_button("Download Report PDF", f.read(), "landlorded_report.pdf", "application/pdf")

    notice_path = outputs["legal_notice"]
    if notice_path.exists():
        with open(notice_path, "rb") as f:
            col2.download_button("Download Legal Notice", f.read(), "legal_notice.pdf", "application/pdf")

    checklist_path = outputs["evidence_checklist"]
    if checklist_path.exists():
        with open(checklist_path, "r") as f:
            col3.download_button("Download Checklist", f.read(), "evidence_checklist.md", "text/markdown")

    col4.download_button("Download WhatsApp Msg", whatsapp_msg, "whatsapp_message.txt", "text/plain")

    # WhatsApp preview
    st.subheader("WhatsApp Message Preview")
    st.text_area("Copy and send:", whatsapp_msg, height=300)


def _show_sample_output():
    """Show what the tool does before a file is uploaded."""
    st.markdown("---")
    st.markdown("### What you'll get")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Clause Audit**")
        st.markdown("11 patterns checked against TN tenancy law. Each clause flagged with severity and statute citations.")
    with col2:
        st.markdown("**Legal Documents**")
        st.markdown("Report PDF, legal notice, evidence checklist — all populated with your actual clause text and amounts.")
    with col3:
        st.markdown("**WhatsApp Message**")
        st.markdown("Bilingual Tamil + English warning message with section references. Send before the legal notice.")


if __name__ == "__main__":
    main()
