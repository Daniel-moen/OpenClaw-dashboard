"""User profiles. Two seeded by default (Daniel + Partner).

Profiles are *identity*, not authorization. The app is single-password;
profiles let the assistant know who's currently using the dashboard so
prompts/replies can be tailored.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status

from ..config import Settings, get_settings
from ..db import get_connection, log_activity
from ..deps import current_profile_key, require_session
from ..models import Me, Profile, ProfileIn
from ..security import (
    PROFILE_COOKIE_NAME,
    PROFILE_TTL_SECONDS,
    create_profile_token,
)

router = APIRouter(prefix="/profiles", tags=["profiles"], dependencies=[Depends(require_session)])


def _row(row) -> Profile:
    return Profile(
        id=row["id"],
        key=row["key"],
        name=row["name"],
        role=row["role"],
        emoji=row["emoji"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _get_by_key(key: str) -> Profile | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM profiles WHERE key = ?", (key,)).fetchone()
    return _row(row) if row else None


@router.get("", response_model=list[Profile])
def list_profiles() -> list[Profile]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM profiles ORDER BY id").fetchall()
    return [_row(r) for r in rows]


@router.put("/{profile_id}", response_model=Profile)
def update_profile(profile_id: int, body: ProfileIn) -> Profile:
    conn = get_connection()
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
    conn.execute(
        "UPDATE profiles SET name = ?, role = ?, emoji = ? WHERE id = ?",
        (body.name, body.role, body.emoji[:4], profile_id),
    )
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    return _row(row)


@router.get("/active", response_model=Profile | None)
def get_active(key: str | None = Depends(current_profile_key)) -> Profile | None:
    if not key:
        return None
    return _get_by_key(key)


@router.post("/active", response_model=Profile)
def set_active(
    response: Response,
    body: dict = Body(...),
    settings: Settings = Depends(get_settings),
) -> Profile:
    key = (body or {}).get("key")
    if not key or not isinstance(key, str):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "missing key")
    profile = _get_by_key(key)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown profile")
    token = create_profile_token(profile.key)
    response.set_cookie(
        PROFILE_COOKIE_NAME,
        token,
        max_age=PROFILE_TTL_SECONDS,
        httponly=False,  # frontend reads this for greeting; safe to expose key only
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    log_activity("profile.switch", f"{profile.name} took the wheel", profile_key=profile.key)
    return profile


# /api/me bundles auth state + active profile. Convenient single fetch.
me_router = APIRouter(tags=["profiles"])


@me_router.get("/me", response_model=Me)
def me(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Me:
    from ..security import SESSION_COOKIE_NAME, verify_session_token

    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token or not verify_session_token(token):
        return Me(authenticated=False, profile=None)
    pkey = current_profile_key(request.cookies.get(PROFILE_COOKIE_NAME))
    profile = _get_by_key(pkey) if pkey else None
    return Me(authenticated=True, profile=profile)
