"""Audit endpoints — create, list, get, delete audits."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from supabase import Client

from ..deps import get_supabase, get_current_user
from ..models.schemas import AuditCreate, AuditResponse, AuditListItem, AuditStatus, AuditMode, PatternSummary
from ..db import queries
from ..services import audit_service, storage_service

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("", status_code=202)
async def create_audit(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: AuditMode = Form(AuditMode.audit),
    tenant_name: str = Form(""),
    landlord_name: str = Form(""),
    premises: str = Form(""),
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:  # 20MB limit
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    audit_id = str(uuid.uuid4())

    # Upload to storage
    storage_service.upload_agreement(db, user_id, audit_id, file_bytes, file.filename)

    # Create DB record
    queries.create_audit(db, user_id, audit_id, file.filename, mode.value)

    # Run pipeline in background
    background_tasks.add_task(
        audit_service.run_pipeline,
        db, user_id, audit_id, file.filename, mode.value,
        tenant_name, landlord_name, premises,
    )

    return {"id": audit_id, "status": "processing"}


@router.get("", response_model=list[AuditListItem])
async def list_audits(
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    return queries.list_audits(db, user_id)


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: str,
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    audit = queries.get_audit(db, user_id, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Parse patterns from JSONB
    patterns = []
    for p in (audit.get("patterns") or []):
        patterns.append(PatternSummary(**p))

    return AuditResponse(
        id=audit["id"],
        status=AuditStatus(audit["status"]),
        mode=audit.get("mode", "audit"),
        created_at=audit.get("created_at"),
        file_name=audit.get("file_name", ""),
        page_count=audit.get("page_count"),
        ocr_used=audit.get("ocr_used", False),
        risk_level=audit.get("risk_level"),
        red_flags=audit.get("red_flags", 0),
        yellow_flags=audit.get("yellow_flags", 0),
        patterns=patterns,
        documents_available=audit.get("documents_available", []),
        error=audit.get("error"),
    )


@router.delete("/{audit_id}", status_code=204)
async def delete_audit(
    audit_id: str,
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    # Delete files from storage
    storage_service.delete_audit_files(db, user_id, audit_id)

    # Delete DB record
    deleted = queries.delete_audit(db, user_id, audit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Audit not found")
