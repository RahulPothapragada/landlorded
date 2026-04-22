"""Pydantic request/response models."""

from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class AuditMode(str, Enum):
    audit = "audit"
    dispute = "dispute"
    renewal = "renewal"


class AuditCreate(BaseModel):
    mode: AuditMode = AuditMode.audit
    tenant_name: str = ""
    landlord_name: str = ""
    premises: str = ""


class PatternSummary(BaseModel):
    pattern_id: int
    pattern_name: str
    fired: bool
    severity: str | None = None
    explanation: str = ""
    verdict: str = ""
    statute_citation: str = ""
    suggested_rewrite: str = ""
    notice_paragraph: str = ""
    extracted: dict = {}
    matched_text: list[str] = []


class AuditStatus(str, Enum):
    processing = "processing"
    complete = "complete"
    failed = "failed"


class AuditResponse(BaseModel):
    id: str
    status: AuditStatus
    mode: str = "audit"
    created_at: datetime | None = None
    file_name: str = ""
    page_count: int | None = None
    ocr_used: bool = False
    risk_level: str | None = None  # HIGH / MODERATE / LOW
    red_flags: int = 0
    yellow_flags: int = 0
    patterns: list[PatternSummary] = []
    documents_available: list[str] = []
    error: str | None = None


class AuditListItem(BaseModel):
    id: str
    status: AuditStatus
    mode: str
    created_at: datetime | None = None
    file_name: str = ""
    risk_level: str | None = None
    red_flags: int = 0
    yellow_flags: int = 0


class UserProfile(BaseModel):
    id: str
    tenant_name: str = ""
    landlord_name: str = ""
    premises: str = ""


class UserProfileUpdate(BaseModel):
    tenant_name: str | None = None
    landlord_name: str | None = None
    premises: str | None = None
