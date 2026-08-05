"""MSG91 SMS OTP + simple in-memory rate limiting."""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from threading import Lock

MSG91_AUTH_KEY = os.environ.get("MSG91_AUTH_KEY", "").strip()
MSG91_TEMPLATE_ID = os.environ.get("MSG91_TEMPLATE_ID", "").strip()
MSG91_SENDER_ID = os.environ.get("MSG91_SENDER_ID", "BARATX").strip() or "BARATX"

_otp_hits: dict[str, list[float]] = defaultdict(list)
_lock = Lock()

OTP_RATE_LIMIT = 5  # requests
OTP_RATE_WINDOW_SEC = 15 * 60  # 15 minutes


def sms_configured() -> bool:
    return bool(MSG91_AUTH_KEY and MSG91_TEMPLATE_ID)


def check_otp_rate_limit(phone: str) -> None:
    """Raise ValueError if phone has requested too many OTPs recently."""
    now = time.time()
    key = phone.strip()
    with _lock:
        hits = [t for t in _otp_hits[key] if now - t < OTP_RATE_WINDOW_SEC]
        if len(hits) >= OTP_RATE_LIMIT:
            raise ValueError("Too many OTP requests. Try again in a few minutes.")
        hits.append(now)
        _otp_hits[key] = hits


def send_otp_sms(phone: str, code: str) -> bool:
    """
    Send OTP via MSG91 Flow API when configured.
    Returns True if an SMS provider accepted the send.
    """
    if not sms_configured():
        return False

    # MSG91 expects digits; strip leading +
    mobile = phone.lstrip("+")
    payload = {
        "template_id": MSG91_TEMPLATE_ID,
        "short_url": "0",
        "recipients": [
            {
                "mobiles": mobile,
                "otp": code,
                "var": code,
            }
        ],
    }
    # Prefer Flow API; fall back to older sendotp-style endpoint if needed.
    body = urllib.parse.urlencode(
        {
            "authkey": MSG91_AUTH_KEY,
            "mobile": mobile,
            "otp": code,
            "sender": MSG91_SENDER_ID,
            "template_id": MSG91_TEMPLATE_ID,
            "otp_length": str(len(code)),
        }
    ).encode()
    req = urllib.request.Request(
        "https://control.msg91.com/api/v5/otp",
        data=body,
        headers={
            "authkey": MSG91_AUTH_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            return 200 <= res.status < 300
    except urllib.error.HTTPError as exc:
        # Log body for ops; don't leak to clients.
        try:
            detail = exc.read().decode()[:300]
        except Exception:
            detail = str(exc)
        print(f"[sms] MSG91 HTTP {exc.code}: {detail}")
        return False
    except Exception as exc:
        print(f"[sms] MSG91 error: {exc}")
        return False
