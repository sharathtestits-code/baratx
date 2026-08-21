"""Normalize Explore/search queries into safe LIKE patterns + match variants."""

from __future__ import annotations

import re


_LIKE_ESCAPE = re.compile(r"([\\%_])")
_CAMEL_SPLIT = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_NON_TOKEN = re.compile(r"[^\w]+", re.UNICODE)


def normalize_search_query(raw: str) -> str:
    """Strip @/# and collapse whitespace."""
    q = (raw or "").strip()
    if q.startswith(("@", "#")):
        q = q[1:].strip()
    return " ".join(q.split())


def escape_like(fragment: str) -> str:
    """Escape SQL LIKE wildcards so user input is literal."""
    return _LIKE_ESCAPE.sub(r"\\\1", fragment or "")


def like_pattern(fragment: str) -> str:
    return f"%{escape_like(fragment)}%"


def search_variants(raw: str) -> list[str]:
    """Build alternate phrases so StartupIndia / #politics / geopolitics all hit."""
    base = normalize_search_query(raw)
    if not base:
        return []

    variants: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        v = " ".join((value or "").split())
        if not v:
            return
        key = v.casefold()
        if key in seen:
            return
        seen.add(key)
        variants.append(v)

    add(base)
    add(base.replace(" ", ""))
    add(_CAMEL_SPLIT.sub(" ", base))

    # Token pieces for multi-word / camel queries (skip tiny noise).
    spaced = _CAMEL_SPLIT.sub(" ", base)
    for token in _NON_TOKEN.split(spaced):
        if len(token) >= 3:
            add(token)

    return variants
