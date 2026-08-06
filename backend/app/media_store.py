"""Local, inline (DB data-URL), or S3/R2 media storage.

Railway/Render containers wipe local disk on every deploy/restart. Without
S3/R2 credentials we therefore store uploads as data URLs in Postgres on
those hosts so images survive redeploys. Prefer Cloudflare R2 in production
for scale (set MEDIA_BACKEND=s3 + S3_* env vars).
"""

from __future__ import annotations

import base64
import logging
import os
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

MEDIA_BACKEND = (os.environ.get("MEDIA_BACKEND") or "local").strip().lower()
S3_BUCKET = (os.environ.get("S3_BUCKET") or "").strip()
S3_ENDPOINT_URL = (os.environ.get("S3_ENDPOINT_URL") or "").strip() or None
S3_ACCESS_KEY_ID = (os.environ.get("S3_ACCESS_KEY_ID") or "").strip()
S3_SECRET_ACCESS_KEY = (os.environ.get("S3_SECRET_ACCESS_KEY") or "").strip()
S3_PUBLIC_BASE_URL = (os.environ.get("S3_PUBLIC_BASE_URL") or "").strip().rstrip("/")
S3_REGION = (os.environ.get("S3_REGION") or "auto").strip() or "auto"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = (os.environ.get("MEDIA_DIR") or "").strip() or os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

_EPHEMERAL_HOST = bool(
    os.environ.get("RAILWAY_ENVIRONMENT")
    or os.environ.get("RAILWAY_PROJECT_ID")
    or os.environ.get("RENDER")
    or os.environ.get("FLY_APP_NAME")
)


def s3_enabled() -> bool:
    return (
        MEDIA_BACKEND in {"s3", "r2"}
        and bool(S3_BUCKET)
        and bool(S3_ACCESS_KEY_ID)
        and bool(S3_SECRET_ACCESS_KEY)
        and bool(S3_PUBLIC_BASE_URL)
    )


def use_inline() -> bool:
    if MEDIA_BACKEND in {"inline", "db"}:
        return True
    if s3_enabled():
        return False
    if MEDIA_BACKEND == "local" and _EPHEMERAL_HOST:
        return True
    return False


def _s3_client():
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        region_name=S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def save_bytes(contents: bytes, *, content_type: str, filename: Optional[str] = None) -> str:
    """Persist bytes; return /media/…, https://…, or data:… URL."""
    ext = os.path.splitext(filename or "")[1] or ".jpg"
    key = f"{uuid.uuid4().hex}{ext}"
    ctype = content_type or "application/octet-stream"

    if s3_enabled():
        client = _s3_client()
        client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=contents,
            ContentType=ctype,
            CacheControl="public, max-age=31536000, immutable",
        )
        return f"{S3_PUBLIC_BASE_URL}/{key}"

    if use_inline():
        logger.info(
            "Storing media inline (data URL) — set MEDIA_BACKEND=s3 + S3_* for R2/S3 at scale"
        )
        b64 = base64.b64encode(contents).decode("ascii")
        return f"data:{ctype};base64,{b64}"

    filepath = os.path.join(MEDIA_DIR, key)
    with open(filepath, "wb") as f:
        f.write(contents)
    return f"/media/{key}"


def delete_url(url: Optional[str]) -> None:
    if not url:
        return
    try:
        if url.startswith("data:"):
            return
        if url.startswith("http://") or url.startswith("https://"):
            if not s3_enabled() or not S3_PUBLIC_BASE_URL:
                return
            prefix = f"{S3_PUBLIC_BASE_URL}/"
            if not url.startswith(prefix):
                return
            key = url[len(prefix) :].lstrip("/")
            if not key:
                return
            _s3_client().delete_object(Bucket=S3_BUCKET, Key=key)
            return

        name = os.path.basename(url.lstrip("/"))
        if not name:
            return
        filepath = os.path.join(MEDIA_DIR, name)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:  # noqa: BLE001
        pass
