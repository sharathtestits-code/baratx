"""Same-origin SPA shell helpers (Railway serves API + frontend_dist)."""

from __future__ import annotations

# Paths that must never be hijacked by the SPA shell (API docs, health, media).
SPA_SHELL_SKIP_PREFIXES = (
    "/assets/",
    "/media/",
    "/media-files/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/ops",
)


def wants_spa_document(*, method: str, headers: dict[str, str]) -> bool:
    """True for browser document navigations (refresh, new tab, shared link).

    Same-origin Railway serves API + SPA. GET /notifications is both an API
    route and a React route — without this check, refresh returns JSON.
    fetch() from the SPA uses Sec-Fetch-Mode: cors / Dest: empty and keeps API.
    """
    if (method or "").upper() != "GET":
        return False
    lower = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    dest = (lower.get("sec-fetch-dest") or "").lower()
    mode = (lower.get("sec-fetch-mode") or "").lower()
    if dest == "document" or mode == "navigate":
        return True
    accept = (lower.get("accept") or "").lower()
    # First Accept token is text/html on real browser navigations.
    if accept.startswith("text/html"):
        return True
    return False


def spa_shell_allowed(path: str) -> bool:
    if path == "/":
        return True
    for prefix in SPA_SHELL_SKIP_PREFIXES:
        if path == prefix.rstrip("/") or path.startswith(prefix):
            return False
    return True
