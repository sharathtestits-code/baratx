import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
ALGORITHM = "HS256"
# Soft-launch default: 2 days (was 7). Override with JWT_ACCESS_DAYS.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_DAYS", "2")) * 60 * 24
EMAIL_UNSUB_DAYS = int(os.environ.get("EMAIL_UNSUB_DAYS", "90"))

if (
    os.environ.get("ENVIRONMENT", "development") == "production"
    and SECRET_KEY == "dev-secret-change-in-production"
):
    raise RuntimeError("JWT_SECRET must be set to a strong value in production")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def hash_otp(code: str) -> str:
    """Store OTPs hashed — never keep plaintext codes in the DB."""
    return bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_otp(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: str, token_version: int = 0) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "tv": int(token_version or 0), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """Return (user_id, token_version) or (None, None)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub"), int(payload.get("tv") or 0)
    except JWTError:
        return None, None


def create_email_unsub_token(user_id: str) -> str:
    """One-click activity-email unsubscribe (shorter TTL than soft-launch default)."""
    expire = datetime.now(timezone.utc) + timedelta(days=EMAIL_UNSUB_DAYS)
    payload = {"sub": user_id, "purpose": "email_unsub", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_email_unsub_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "email_unsub":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def generate_otp() -> str:
    """Cryptographically strong 6-digit OTP."""
    return f"{secrets.randbelow(1_000_000):06d}"


def bump_token_version(user) -> int:
    """Invalidate existing JWTs after password reset / account security events."""
    current = int(getattr(user, "token_version", 0) or 0)
    user.token_version = current + 1
    return user.token_version
