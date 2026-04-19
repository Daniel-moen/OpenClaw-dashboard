"""Password hashing + signed-cookie session tokens."""

from __future__ import annotations

import time
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

from .config import get_settings

SESSION_COOKIE_NAME = "ocw_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 14  # 14 days
PROFILE_COOKIE_NAME = "ocw_profile"
PROFILE_TTL_SECONDS = 60 * 60 * 24 * 365  # 1 year

_hasher = PasswordHasher()


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def _signer() -> TimestampSigner:
    return TimestampSigner(get_settings().session_secret, salt="ocw-session-v1")


def create_session_token(subject: str = "admin") -> str:
    return _signer().sign(subject.encode("utf-8")).decode("utf-8")


def verify_session_token(token: str) -> str | None:
    try:
        raw = _signer().unsign(token, max_age=SESSION_TTL_SECONDS)
        return raw.decode("utf-8")
    except (BadSignature, SignatureExpired):
        return None


def _profile_signer() -> TimestampSigner:
    return TimestampSigner(get_settings().session_secret, salt="ocw-profile-v1")


def create_profile_token(key: str) -> str:
    return _profile_signer().sign(key.encode("utf-8")).decode("utf-8")


def verify_profile_token(token: str) -> str | None:
    try:
        raw = _profile_signer().unsign(token, max_age=PROFILE_TTL_SECONDS)
        return raw.decode("utf-8")
    except (BadSignature, SignatureExpired):
        return None


# --- Login rate limit (in-memory token bucket per remote address) ---

@dataclass
class _Bucket:
    tokens: float
    updated_at: float


class LoginLimiter:
    def __init__(self, capacity: int = 5, refill_per_minute: float = 5.0) -> None:
        self.capacity = capacity
        self.refill = refill_per_minute / 60.0  # per second
        self._buckets: dict[str, _Bucket] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._buckets.get(key)
        if bucket is None:
            self._buckets[key] = _Bucket(tokens=self.capacity - 1, updated_at=now)
            return True
        elapsed = now - bucket.updated_at
        bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.refill)
        bucket.updated_at = now
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False


login_limiter = LoginLimiter()
