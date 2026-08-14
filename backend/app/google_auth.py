"""Google ID token verification (Google Identity Services / native Sign-In)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

# Primary web client ID (GIS + Android Credential Manager server client / iOS serverClientId).
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
# Optional extra audiences (comma-separated), e.g. iOS client ID if tokens are not
# minted with iOSServerClientId=web.
_EXTRA = os.environ.get("GOOGLE_CLIENT_IDS", "").strip()


def _allowed_audiences() -> set[str]:
    ids = set()
    if GOOGLE_CLIENT_ID:
        ids.add(GOOGLE_CLIENT_ID)
    if _EXTRA:
        for part in _EXTRA.split(","):
            part = part.strip()
            if part:
                ids.add(part)
    return ids


def google_configured() -> bool:
    return bool(_allowed_audiences())


def verify_google_id_token(id_token: str) -> dict[str, Any]:
    """
    Verify a Google ID token via Google's tokeninfo endpoint.
    Returns claims (email, sub, name, picture, email_verified, ...).
    """
    allowed = _allowed_audiences()
    if not allowed:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")

    url = "https://oauth2.googleapis.com/tokeninfo?" + urllib.parse.urlencode(
        {"id_token": id_token}
    )
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            claims = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Invalid Google token ({exc.code}): {detail}") from exc

    aud = claims.get("aud")
    if aud not in allowed:
        raise ValueError("Google token audience mismatch")

    if claims.get("email_verified") not in (True, "true", "1"):
        raise ValueError("Google email is not verified")

    if not claims.get("email"):
        raise ValueError("Google token missing email")

    return claims
