"""Supabase Storage operations — upload PDFs, generated docs, and create signed URLs."""

from supabase import Client

BUCKET = "landlorded"


def upload_agreement(db: Client, user_id: str, audit_id: str, file_bytes: bytes, file_name: str) -> str:
    path = f"{user_id}/{audit_id}/agreement/{file_name}"
    db.storage.from_(BUCKET).upload(path, file_bytes, {"content-type": "application/pdf"})
    return path


def upload_document(db: Client, user_id: str, audit_id: str, doc_type: str, content: bytes, content_type: str = "application/pdf") -> str:
    ext = "pdf" if "pdf" in content_type else "md" if "markdown" in content_type else "txt"
    path = f"{user_id}/{audit_id}/output/{doc_type}.{ext}"
    db.storage.from_(BUCKET).upload(path, content, {"content-type": content_type})
    return path


def get_signed_url(db: Client, user_id: str, audit_id: str, doc_type: str) -> str | None:
    ext_map = {
        "report": "pdf",
        "legal_notice": "pdf",
        "evidence_checklist": "md",
        "whatsapp_message": "txt",
    }
    ext = ext_map.get(doc_type, "pdf")
    path = f"{user_id}/{audit_id}/output/{doc_type}.{ext}"
    try:
        resp = db.storage.from_(BUCKET).create_signed_url(path, 60)
        return resp.get("signedURL")
    except Exception:
        return None


def download_agreement(db: Client, user_id: str, audit_id: str, file_name: str) -> bytes:
    path = f"{user_id}/{audit_id}/agreement/{file_name}"
    return db.storage.from_(BUCKET).download(path)


def delete_audit_files(db: Client, user_id: str, audit_id: str):
    prefix = f"{user_id}/{audit_id}/"
    try:
        files = db.storage.from_(BUCKET).list(prefix)
        if files:
            paths = [f"{prefix}{f['name']}" for f in files]
            db.storage.from_(BUCKET).remove(paths)
    except Exception:
        pass
