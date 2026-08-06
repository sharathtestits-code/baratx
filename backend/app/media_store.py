"""Durable media storage: S3/R2, Postgres blobs, or local disk.

Why images vanished: Railway wipes the container filesystem on every deploy.
Uploads were saved under local `/media`, so files 404'd while post rows stayed.

Default on production/ephemeral hosts: store bytes in Postgres (`media_assets`)
and serve via `/media/{id}.ext`. Prefer Cloudflare R2 (MEDIA_BACKEND=s3) at scale.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

MEDIA_BACKEND = (os.environ.get("MEDIA_BACKEND") or "auto").strip().lower()
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
    or os.environ.get("RAILWAY_SERVICE_ID")
    or os.environ.get("RENDER")
    or os.environ.get("FLY_APP_NAME")
    or (os.environ.get("ENVIRONMENT", "").strip().lower() == "production")
)


def s3_enabled() -> bool:
    return (
        MEDIA_BACKEND in {"s3", "r2"}
        and bool(S3_BUCKET)
        and bool(S3_ACCESS_KEY_ID)
        and bool(S3_SECRET_ACCESS_KEY)
        and bool(S3_PUBLIC_BASE_URL)
    )


def use_db_store() -> bool:
    """Postgres blob storage — survives redeploys without R2."""
    if MEDIA_BACKEND in {"db", "postgres", "inline"}:
        return True
    if s3_enabled():
        return False
    if MEDIA_BACKEND == "local":
        return False
    # auto (default): DB on Railway/production, local disk on laptop
    return _EPHEMERAL_HOST


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
    """Persist bytes; return /media/… or https://… URL."""
    ext = os.path.splitext(filename or "")[1].lower() or ".jpg"
    if len(ext) > 8:
        ext = ".jpg"
    ctype = content_type or "application/octet-stream"

    if s3_enabled():
        key = f"{uuid.uuid4().hex}{ext}"
        client = _s3_client()
        client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=contents,
            ContentType=ctype,
            CacheControl="public, max-age=31536000, immutable",
        )
        return f"{S3_PUBLIC_BASE_URL}/{key}"

    if use_db_store():
        from app import models
        from app.database import SessionLocal

        asset_id = uuid.uuid4().hex
        with SessionLocal() as db:
            db.add(
                models.MediaAsset(
                    id=asset_id,
                    content_type=ctype,
                    filename=filename,
                    size=len(contents),
                    data=contents,
                )
            )
            db.commit()
        logger.info("Stored media in DB id=%s size=%s", asset_id, len(contents))
        return f"/media/{asset_id}{ext}"

    key = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(MEDIA_DIR, key)
    with open(filepath, "wb") as f:
        f.write(contents)
    return f"/media/{key}"


def load_bytes(name: str) -> tuple[bytes, str] | None:
    """Load media by `/media/{name}` basename. Returns (bytes, content_type) or None."""
    if not name:
        return None
    base = os.path.basename(name)
    asset_id = base.split(".", 1)[0]

    from app import models
    from app.database import SessionLocal

    with SessionLocal() as db:
        asset = db.query(models.MediaAsset).filter(models.MediaAsset.id == asset_id).first()
        if asset and asset.data is not None:
            return bytes(asset.data), asset.content_type or "application/octet-stream"

    filepath = os.path.join(MEDIA_DIR, base)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
        ctype = "application/octet-stream"
        lower = base.lower()
        if lower.endswith((".jpg", ".jpeg")):
            ctype = "image/jpeg"
        elif lower.endswith(".png"):
            ctype = "image/png"
        elif lower.endswith(".gif"):
            ctype = "image/gif"
        elif lower.endswith(".webp"):
            ctype = "image/webp"
        elif lower.endswith((".mp4", ".m4v")):
            ctype = "video/mp4"
        elif lower.endswith(".webm"):
            ctype = "video/webm"
        elif lower.endswith(".mp3"):
            ctype = "audio/mpeg"
        elif lower.endswith(".m4a"):
            ctype = "audio/mp4"
        return data, ctype
    return None


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
        asset_id = name.split(".", 1)[0]
        from app import models
        from app.database import SessionLocal

        with SessionLocal() as db:
            asset = db.query(models.MediaAsset).filter(models.MediaAsset.id == asset_id).first()
            if asset:
                db.delete(asset)
                db.commit()
                return

        filepath = os.path.join(MEDIA_DIR, name)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:  # noqa: BLE001
        pass
