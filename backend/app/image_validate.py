from __future__ import annotations

from typing import Optional

IMAGE_MAGIC = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),  # WEBP: RIFF....WEBP
)


def sniff_image_type(data: bytes) -> Optional[str]:
    if not data or len(data) < 12:
        return None
    for magic, ctype in IMAGE_MAGIC:
        if data.startswith(magic):
            if ctype == "image/webp":
                if data[8:12] != b"WEBP":
                    return None
            return ctype
    return None


def assert_image_bytes(data: bytes, declared_type: str | None = None) -> str:
    """Return sniffed content-type or raise ValueError."""
    sniffed = sniff_image_type(data)
    if not sniffed:
        raise ValueError("File is not a valid JPEG, PNG, GIF, or WEBP image")
    if declared_type and declared_type in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        # Allow jpeg alias mismatches (image/jpg rare); otherwise require match family
        if declared_type == "image/jpeg" and sniffed == "image/jpeg":
            return sniffed
        if declared_type != sniffed:
            raise ValueError("Image content does not match the uploaded file type")
    return sniffed
