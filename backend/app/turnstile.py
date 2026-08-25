"""Cloudflare Turnstile server-side verification (bot gate for email/Google signup).

Phone OTP stays the preferred path and does not require Turnstile.
When TURNSTILE_SECRET_KEY is unset, verification is skipped (local/dev).
When set, email signup + new Google accounts must pass siteverify.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

logger = logging.getLogger("baratx.turnstile")

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def secret_key() -> str:
    return (os.environ.get("TURNSTILE_SECRET_KEY") or "").strip()


def required() -> bool:
    return bool(secret_key())


def verify_token(token: Optional[str], *, remote_ip: Optional[str] = None) -> bool:
    """
    Return True if the token is valid.
    If Turnstile is not configured, return True (do not block local/dev).
    """
    secret = secret_key()
    if not secret:
        return True
    tok = (token or "").strip()
    if not tok:
        return False
    payload = {
        "secret": secret,
        "response": tok,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip
    body = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        SITEVERIFY_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode() or "{}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.warning("Turnstile siteverify failed: %s", exc)
        # Fail closed when configured — bots should not slip through on outage.
        return False
    ok = bool(data.get("success"))
    if not ok:
        logger.info("Turnstile rejected token codes=%s", data.get("error-codes"))
    return ok
