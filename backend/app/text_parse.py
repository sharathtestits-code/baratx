"""Extract @mentions and #hashtags from post/reply text."""

from __future__ import annotations

import re
import unicodedata

MENTION_RE = re.compile(r"(?<![A-Za-z0-9_])@([A-Za-z0-9][A-Za-z0-9._-]{2,19})\b")
HASHTAG_RE = re.compile(r"(?<![A-Za-z0-9_])#([A-Za-z0-9_]{2,40})\b")

# Bidirectional / isolate overrides used for filename & URL spoofing (e.g. gnp.exe ↔ exe.png).
_BIDI_CONTROLS = re.compile(
    "["
    "\u200e\u200f"  # LTR/RTL marks
    "\u202a-\u202e"  # embedding / override
    "\u2066-\u2069"  # isolates
    "]"
)


def sanitize_user_text(text: str) -> str:
    """Normalize and strip bidi control chars that enable visual spoofing."""
    cleaned = unicodedata.normalize("NFC", text or "")
    cleaned = _BIDI_CONTROLS.sub("", cleaned)
    return cleaned


def extract_mentions(text: str) -> list[str]:
    seen = set()
    out = []
    for m in MENTION_RE.finditer(text or ""):
        name = m.group(1).lower()
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def extract_hashtags(text: str) -> list[str]:
    seen = set()
    out = []
    for m in HASHTAG_RE.finditer(text or ""):
        tag = m.group(1).lower()
        if tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out
