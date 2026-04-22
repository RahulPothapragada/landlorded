"""Document download endpoints — signed URLs for generated documents."""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from ..deps import get_supabase, get_current_user
from ..db import queries
from ..services import storage_service

router = APIRouter(prefix="/audits/{audit_id}/documents", tags=["documents"])

VALID_TYPES = {"report", "legal_notice", "evidence_checklist", "whatsapp_message"}


@router.get("/{doc_type}")
async def get_document_url(
    audit_id: str,
    doc_type: str,
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    if doc_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {', '.join(VALID_TYPES)}")

    # Verify audit belongs to user
    audit = queries.get_audit(db, user_id, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if audit["status"] != "complete":
        raise HTTPException(status_code=409, detail="Audit not yet complete")

    if doc_type not in (audit.get("documents_available") or []):
        raise HTTPException(status_code=404, detail=f"Document '{doc_type}' not available for this audit")

    url = storage_service.get_signed_url(db, user_id, audit_id, doc_type)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

    return {"url": url, "doc_type": doc_type}
