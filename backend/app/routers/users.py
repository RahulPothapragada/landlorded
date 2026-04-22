"""User profile endpoints."""

from fastapi import APIRouter, Depends
from supabase import Client

from ..deps import get_supabase, get_current_user
from ..models.schemas import UserProfile, UserProfileUpdate
from ..db import queries

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    return queries.get_or_create_profile(db, user_id)


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    body: UserProfileUpdate,
    user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        return queries.get_or_create_profile(db, user_id)
    return queries.update_profile(db, user_id, updates)
