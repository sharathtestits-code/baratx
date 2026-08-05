"""Google ID token verification (Google Identity Services / Gmail sign-in)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")


def google_configured() -> bool:
    return bool(GOOGLE_CLIENT_ID)


def verify_google_id_token(id_token: str) -> dict[str, Any]:
    """
    Verify a Google ID token via Google's tokeninfo endpoint.
    Returns claims (email, sub, name, picture, email_verified, ...).
    """
    if not GOOGLE_CLIENT_ID:
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
    if aud != GOOGLE_CLIENT_ID:
        raise ValueError("Google token audience mismatch")

    if claims.get("email_verified") not in (True, "true", "1"):
        raise ValueError("Google email is not verified")

    if not claims.get("email"):
        raise ValueError("Google token missing email")

    return claims
