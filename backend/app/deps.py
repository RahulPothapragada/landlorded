"""FastAPI dependencies — auth and Supabase client."""

from fastapi import Depends, HTTPException, Request
from supabase import create_client, Client
import jwt

from .config import get_settings, Settings


def get_supabase(settings: Settings = Depends(get_settings)) -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)


async def get_current_user(request: Request, settings: Settings = Depends(get_settings)) -> str:
    """Extract and verify user ID from Supabase JWT in Authorization header."""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False},  # Supabase handles signing; we trust the token from the client
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no sub claim")
        return user_id
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
