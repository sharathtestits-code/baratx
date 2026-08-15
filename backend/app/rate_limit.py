"""Simple in-memory rate limits for auth / sensitive endpoints."""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

_hits: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def check_rate_limit(bucket: str, *, limit: int, window_sec: int) -> None:
    """Raise ValueError when `bucket` exceeds limit within the window."""
    now = time.time()
    key = (bucket or "").strip().lower()
    if not key:
        key = "unknown"
    with _lock:
        hits = [t for t in _hits[key] if now - t < window_sec]
        if len(hits) >= limit:
            raise ValueError("Too many attempts. Wait a few minutes and try again.")
        hits.append(now)
        _hits[key] = hits


def client_ip(request) -> str:
    """Best-effort client IP (Cloudflare / proxy aware)."""
    forwarded = (request.headers.get("cf-connecting-ip") or "").strip()
    if forwarded:
        return forwarded
    xff = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    if xff:
        return xff
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
