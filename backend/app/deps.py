"""FastAPI dependencies (auth gate, CSRF-style origin check)."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request, status

from .config import Settings, get_settings
from .security import (
    PROFILE_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    verify_profile_token,
    verify_session_token,
)

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def require_session(
    request: Request,
    settings: Settings = Depends(get_settings),
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> str:
    if not session:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "not authenticated")
    subject = verify_session_token(session)
    if not subject:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "session expired")

    # Lightweight CSRF defence for state-changing requests.
    if request.method not in SAFE_METHODS:
        origin = request.headers.get("origin") or request.headers.get("referer")
        if origin and not origin.startswith(settings.frontend_origin):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "bad origin")

    return subject


def current_profile_key(
    profile: str | None = Cookie(default=None, alias=PROFILE_COOKIE_NAME),
) -> str | None:
    """Best-effort: returns the active profile key, or None if not set."""
    if not profile:
        return None
    return verify_profile_token(profile)
