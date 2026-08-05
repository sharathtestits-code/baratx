"""Outbound email helpers for account verification.

Cloudflare Email Routing only receives mail at hello@barathx.com — it cannot
send. Prefer Resend; keep Gmail SMTP as backup/debug:

  1) Resend (primary):
     RESEND_API_KEY=re_...
     EMAIL_FROM=BaratX <hello@barathx.com>   # domain must be verified in Resend

  2) Gmail SMTP (backup / debug — App Password):
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=you@gmail.com
     SMTP_PASSWORD=app-password
     EMAIL_FROM=BaratX <hello@barathx.com>

When RESEND_API_KEY is set it wins over SMTP. When neither is configured,
verification links are logged (and returned as dev_verify_url in development).
"""

from __future__ import annotations

import json
import logging
import os
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger("baratx.email")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "BaratX <hello@barathx.com>")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")


def mail_configured() -> bool:
    if RESEND_API_KEY:
        return True
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def build_verify_url(token: str) -> str:
    return f"{FRONTEND_URL}/verify-email?token={token}"


def _send_smtp(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def _send_resend(to_email: str, subject: str, text_body: str, html_body: str) -> None:
    payload = {
        "from": EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }
    # Cloudflare in front of Resend blocks the default Python-urllib User-Agent
    # (HTTP 403 / error code 1010). Send an explicit client identity.
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "BaratX/1.0 (+https://barathx.com)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Resend HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend failed: {exc.code} {detail}") from exc


def send_email(to_email: str, subject: str, text_body: str, html_body: str) -> bool:
    """Send email. Returns True if handed to a provider, False if logged only."""
    if RESEND_API_KEY:
        _send_resend(to_email, subject, text_body, html_body)
        return True
    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        _send_smtp(to_email, subject, text_body, html_body)
        return True

    logger.warning(
        "Email not configured — verification link for %s: see logs / dev_verify_url",
        to_email,
    )
    logger.info("DEV email to=%s subject=%s\n%s", to_email, subject, text_body)
    return False


def send_verification_email(to_email: str, display_name: str, token: str) -> tuple[bool, str]:
    verify_url = build_verify_url(token)
    subject = "Confirm your BaratX account"
    text_body = (
        f"Hi {display_name},\n\n"
        f"Welcome to BaratX. Confirm your email by opening this link:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours. If you did not sign up, ignore this email.\n\n"
        f"— BaratX\n"
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p>Hi {display_name},</p>
  <p>Welcome to <strong>BaratX</strong>. Confirm your email to activate your account.</p>
  <p style="margin: 28px 0;">
    <a href="{verify_url}"
       style="background:#FF671F;color:#fff;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700;">
      Confirm email
    </a>
  </p>
  <p style="color:#536471;font-size:14px;">Or paste this link into your browser:<br/>
    <a href="{verify_url}" style="color:#000080;">{verify_url}</a>
  </p>
  <p style="color:#8b98a5;font-size:13px;">This link expires in 24 hours.</p>
  <p>— BaratX</p>
</body>
</html>
"""
    sent = send_email(to_email, subject, text_body, html_body)
    return sent, verify_url
