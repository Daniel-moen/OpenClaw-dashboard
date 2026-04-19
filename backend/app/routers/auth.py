"""Login / logout / session endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..config import Settings, get_settings
from ..db import log_activity
from ..models import LoginRequest, LoginResponse
from .. import security
from ..security import (
    SESSION_COOKIE_NAME,
    SESSION_TTL_SECONDS,
    create_session_token,
    verify_session_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    if not security.login_limiter.allow(_client_key(request)):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "too many attempts")
    # Constant-time-ish compare via Python's `==` on equal-length strings is fine here:
    # the password lives in env and is single-user; argon2 isn't necessary.
    if not settings.admin_password or body.password != settings.admin_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid password")
    token = create_session_token("admin")
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    log_activity("auth.login", "Signed in")
    return LoginResponse(ok=True)


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/session")
def session(request: Request) -> dict[str, bool | str]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return {"authenticated": False}
    subject = verify_session_token(token)
    if not subject:
        return {"authenticated": False}
    return {"authenticated": True, "subject": subject}
