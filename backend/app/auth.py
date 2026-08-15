import os
import random
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

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


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def create_email_unsub_token(user_id: str) -> str:
    """Long-lived token for one-click activity-email unsubscribe links."""
    expire = datetime.now(timezone.utc) + timedelta(days=400)
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
    return f"{random.randint(0, 999999):06d}"
