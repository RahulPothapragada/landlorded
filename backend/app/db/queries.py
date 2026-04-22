"""Supabase database queries."""

from supabase import Client


def create_audit(db: Client, user_id: str, audit_id: str, file_name: str, mode: str):
    db.table("audits").insert({
        "id": audit_id,
        "user_id": user_id,
        "file_name": file_name,
        "mode": mode,
        "status": "processing",
    }).execute()


def update_audit_results(db: Client, audit_id: str, results: dict):
    db.table("audits").update(results).eq("id", audit_id).execute()


def get_audit(db: Client, user_id: str, audit_id: str) -> dict | None:
    resp = db.table("audits").select("*").eq("id", audit_id).eq("user_id", user_id).execute()
    return resp.data[0] if resp.data else None


def list_audits(db: Client, user_id: str) -> list[dict]:
    resp = (db.table("audits")
            .select("id, status, mode, created_at, file_name, risk_level, red_flags, yellow_flags")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute())
    return resp.data


def delete_audit(db: Client, user_id: str, audit_id: str) -> bool:
    resp = db.table("audits").delete().eq("id", audit_id).eq("user_id", user_id).execute()
    return len(resp.data) > 0


def get_or_create_profile(db: Client, user_id: str) -> dict:
    resp = db.table("profiles").select("*").eq("id", user_id).execute()
    if resp.data:
        return resp.data[0]
    db.table("profiles").insert({"id": user_id}).execute()
    return {"id": user_id, "tenant_name": "", "landlord_name": "", "premises": ""}


def update_profile(db: Client, user_id: str, updates: dict) -> dict:
    resp = db.table("profiles").update(updates).eq("id", user_id).execute()
    return resp.data[0] if resp.data else {}
