"""Outbound email helpers for account verification.

Cloudflare Email Routing only receives mail at hello@barathx.com, it cannot
send. Prefer Resend; keep Gmail SMTP as backup/debug:

  1) Resend (primary):
     RESEND_API_KEY=re_...
     EMAIL_FROM=BarathX <hello@barathx.com>   # domain must be verified in Resend

  2) Gmail SMTP (backup / debug. App Password):
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=you@gmail.com
     SMTP_PASSWORD=app-password
     EMAIL_FROM=BarathX <hello@barathx.com>

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

ENVIRONMENT = (os.environ.get("ENVIRONMENT", "development") or "development").strip().lower()
_RAW_FRONTEND_URL = (os.environ.get("FRONTEND_URL") or "").strip().rstrip("/")
FRONTEND_URL = _RAW_FRONTEND_URL or "http://localhost:5173"

_PROD_WEB = "https://barathx.com"
_QA_WEB = "https://qa.barathx.com"


def _is_localhost(url: str) -> bool:
    u = (url or "").lower()
    return (not u) or ("localhost" in u) or ("127.0.0.1" in u)


def _is_railway_host(url: str) -> bool:
    return ".up.railway.app" in (url or "").lower()


def _is_prod_web(url: str) -> bool:
    u = (url or "").lower().rstrip("/")
    return u in ("https://barathx.com", "http://barathx.com") or "baratx-production" in u


def _looks_like_qa_runtime() -> bool:
    """QA Railway services are often cloned from prod with ENVIRONMENT=production."""
    if ENVIRONMENT in ("qa", "staging", "stage"):
        return True
    for key in (
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_SERVICE_NAME",
        "RAILWAY_PROJECT_NAME",
        "RAILWAY_ENVIRONMENT_NAME",
    ):
        val = (os.environ.get(key) or "").strip().lower()
        if "qa" in val or "staging" in val or "stage" in val:
            return True
    cors = (os.environ.get("CORS_ORIGINS") or "").lower()
    if "qa.barathx.com" in cors:
        return True
    raw = (_RAW_FRONTEND_URL or "").lower()
    if "qa.barathx.com" in raw or "baratx-qa" in raw:
        return True
    return False


def _resolve_frontend_url(env: str, url: str) -> str:
    """Canonical public web host for email links.

    Ops should set FRONTEND_URL correctly. Harden common misconfigs:
    - never mail localhost from deployed envs
    - never mail Railway *.up.railway.app app hosts (use public web)
    - QA must not mail production barathx.com / production Railway hosts
    """
    qa = _looks_like_qa_runtime()
    if qa:
        if _is_localhost(url) or _is_prod_web(url) or _is_railway_host(url):
            return _QA_WEB
        return url
    if env in ("production", "prod"):
        if _is_localhost(url) or _is_railway_host(url):
            return _PROD_WEB
        return url
    # development / other: keep as-is (incl. localhost)
    return url or "http://localhost:5173"


FRONTEND_URL = _resolve_frontend_url(ENVIRONMENT, FRONTEND_URL)
EMAIL_FROM = os.environ.get("EMAIL_FROM", "BarathX <hello@barathx.com>")

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


def build_reset_url(token: str) -> str:
    return f"{FRONTEND_URL}/reset-password?token={token}"


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
            "User-Agent": "BarathX/1.0 (+https://barathx.com)",
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
        "Email not configured, verification link for %s: see logs / dev_verify_url",
        to_email,
    )
    logger.info("DEV email to=%s subject=%s\n%s", to_email, subject, text_body)
    return False


def send_verification_email(to_email: str, display_name: str, token: str) -> tuple[bool, str]:
    verify_url = build_verify_url(token)
    subject = "Confirm your BarathX account"
    text_body = (
        f"Hi {display_name},\n\n"
        f"Welcome to BarathX. Confirm your email by opening this link:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours. If you did not sign up, ignore this email.\n\n"
        f"- BarathX\n"
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p>Hi {display_name},</p>
  <p>Welcome to <strong>BarathX</strong>. Confirm your email to activate your account.</p>
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
  <p>- BarathX</p>
</body>
</html>
"""
    sent = send_email(to_email, subject, text_body, html_body)
    return sent, verify_url


def send_password_reset_email(to_email: str, display_name: str, token: str) -> tuple[bool, str]:
    reset_url = build_reset_url(token)
    subject = "Reset your BarathX password"
    text_body = (
        f"Hi {display_name},\n\n"
        f"We received a request to reset your BarathX password. Open this link:\n\n"
        f"{reset_url}\n\n"
        f"This link expires in 1 hour. If you did not request a reset, ignore this email.\n\n"
        f"- BarathX\n"
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p>Hi {display_name},</p>
  <p>We received a request to reset your <strong>BarathX</strong> password.</p>
  <p style="margin: 28px 0;">
    <a href="{reset_url}"
       style="background:#FF671F;color:#fff;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700;">
      Reset password
    </a>
  </p>
  <p style="color:#536471;font-size:14px;">Or paste this link into your browser:<br/>
    <a href="{reset_url}" style="color:#000080;">{reset_url}</a>
  </p>
  <p style="color:#8b98a5;font-size:13px;">This link expires in 1 hour.</p>
  <p>- BarathX</p>
</body>
</html>
"""
    sent = send_email(to_email, subject, text_body, html_body)
    return sent, reset_url


_KIND_COPY = {
    "follow": "followed you",
    "like": "liked your post",
    "repost": "reposted your post",
    "reply": "replied to your post",
    "mention": "mentioned you",
    "message": "sent you a message",
    "post": "posted in the Square",
    "badge": "updated your badge",
}


def send_activity_email(
    to_email: str,
    recipient_name: str,
    actor_name: str,
    actor_username: str,
    kind: str,
    preview: Optional[str] = None,
    post_id: Optional[str] = None,
    unsubscribe_url: Optional[str] = None,
) -> bool:
    """Best-effort retention email when someone interacts with you."""
    if not to_email:
        return False
    action = _KIND_COPY.get(kind, "interacted with you")
    if kind == "reply":
        subject = f"{actor_name} replied to your post on BarathX"
        cta_label = "See the reply"
    elif kind == "post":
        subject = f"{actor_name} posted in the Square"
        cta_label = "Open the Square"
    else:
        subject = f"{actor_name} {action} on BarathX"
        cta_label = "Open Alerts"

    if kind == "message":
        cta = f"{FRONTEND_URL}/messages/{actor_username}"
        cta_label = "Open messages"
    elif post_id and kind in ("reply", "like", "repost", "mention", "post"):
        cta = f"{FRONTEND_URL}/posts/{post_id}"
    else:
        cta = f"{FRONTEND_URL}/notifications"

    unsub = unsubscribe_url or f"{FRONTEND_URL}/settings"
    preview_line = f'\n"{preview[:140]}"\n' if preview else "\n"
    text_body = (
        f"Hi {recipient_name},\n\n"
        f"@{actor_username} {action} on BarathX."
        f"{preview_line}\n"
        f"{cta_label}: {cta}\n\n"
        f"Sign in at {FRONTEND_URL}/login if you need to.\n\n"
        f"Don’t want activity emails? Unsubscribe: {unsub}\n\n"
        f"- BarathX\n"
    )
    preview_html = (
        f'<p style="color:#536471;border-left:3px solid #efe8e0;padding-left:12px;">{preview[:140]}</p>'
        if preview
        else ""
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p>Hi {recipient_name},</p>
  <p><strong>@{actor_username}</strong> {action} on <strong>BarathX</strong>.</p>
  {preview_html}
  <p style="margin: 28px 0;">
    <a href="{cta}"
       style="background:#FF671F;color:#fff;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700;">
      {cta_label}
    </a>
  </p>
  <p style="color:#8b98a5;font-size:13px;">
    Sign in at <a href="{FRONTEND_URL}/login" style="color:#000080;">{FRONTEND_URL}/login</a> to catch up.
  </p>
  <p style="color:#8b98a5;font-size:12px;margin-top:32px;">
    Don’t want activity emails?
    <a href="{unsub}" style="color:#536471;">Unsubscribe</a>
  </p>
  <p>- BarathX</p>
</body>
</html>
"""
    try:
        return send_email(to_email, subject, text_body, html_body)
    except Exception:
        logger.exception("Activity email failed for %s", to_email)
        return False
