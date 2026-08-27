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


def build_unsubscribe_page_url(token: str) -> str:
    """Human-facing unsubscribe page (footer link)."""
    return f"{FRONTEND_URL}/unsubscribe?token={token}"


def build_unsubscribe_api_url(token: str) -> str:
    """HTTPS endpoint for List-Unsubscribe one-click POST (CAN-SPAM / Gmail)."""
    base = (
        os.environ.get("PUBLIC_API_URL")
        or os.environ.get("API_PUBLIC_URL")
        or ""
    ).strip().rstrip("/")
    if not base:
        fu = (FRONTEND_URL or "").lower()
        if "qa.barathx.com" in fu or "baratx-qa" in fu:
            base = "https://baratx-qa.up.railway.app"
        elif "barathx.com" in fu or "baratx-production" in fu:
            base = "https://baratx-production.up.railway.app"
        else:
            base = "http://localhost:8000"
    return f"{base}/auth/unsubscribe?token={token}"


def _send_smtp(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
    *,
    headers: Optional[dict] = None,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    for key, value in (headers or {}).items():
        if value:
            msg[key] = value
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def _send_resend(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
    *,
    headers: Optional[dict] = None,
) -> None:
    payload = {
        "from": EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }
    if headers:
        payload["headers"] = {k: v for k, v in headers.items() if v}
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


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
    *,
    headers: Optional[dict] = None,
) -> bool:
    """Send email. Returns True if handed to a provider, False if logged only."""
    if RESEND_API_KEY:
        _send_resend(to_email, subject, text_body, html_body, headers=headers)
        return True
    if SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        _send_smtp(to_email, subject, text_body, html_body, headers=headers)
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
    list_unsubscribe_url: Optional[str] = None,
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
    # One-click header URL should hit the API (POST). Footer stays on the web page.
    one_click = list_unsubscribe_url or unsubscribe_url
    headers = None
    if one_click and str(one_click).startswith("http"):
        headers = {
            "List-Unsubscribe": f"<{one_click}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
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
        return send_email(to_email, subject, text_body, html_body, headers=headers)
    except Exception:
        logger.exception("Activity email failed for %s", to_email)
        return False


OPS_ALERT_EMAIL = (os.environ.get("BUG_ALERT_EMAIL") or os.environ.get("OPS_ALERT_EMAIL") or "hello@barathx.com").strip()


def send_ops_alert_email(
    *,
    subject: str,
    summary: str,
    details: str = "",
    reporter: str = "",
    kind: str = "alert",
) -> bool:
    """Notify ops when someone logs a bug, concern, or moderation report."""
    to_email = OPS_ALERT_EMAIL
    if not to_email:
        return False

    def _esc(s: str) -> str:
        return (
            (s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    safe_summary = _esc(summary)
    safe_details = _esc(details)
    safe_reporter = _esc(reporter or "unknown")
    safe_kind = _esc(kind)
    lines = [
        f"Kind: {kind}",
        f"Reporter: {reporter or 'unknown'}",
        "",
        summary.strip(),
        "",
    ]
    if details:
        lines.extend(["Details:", details.strip(), ""])
    lines.append(f"Open app: {FRONTEND_URL}/early-issues")
    text_body = "\n".join(lines)
    details_html = (
        f"<pre style='white-space:pre-wrap;background:#f5f5f5;padding:12px;border-radius:8px;'>{safe_details}</pre>"
        if details
        else ""
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p><strong>BarathX ops alert</strong> · {safe_kind}</p>
  <p>Reporter: {safe_reporter}</p>
  <p>{safe_summary}</p>
  {details_html}
  <p><a href="{FRONTEND_URL}/early-issues">Open Early issues</a></p>
  <p>- BarathX</p>
</body>
</html>
"""
    try:
        return send_email(to_email, subject, text_body, html_body)
    except Exception:
        logger.exception("Ops alert email failed for %s", to_email)
        return False


SOCIAL_PACK_EMAIL = (
    os.environ.get("SOCIAL_PACK_EMAIL")
    or os.environ.get("BUG_ALERT_EMAIL")
    or os.environ.get("OPS_ALERT_EMAIL")
    or "sharathtestits@gmail.com"
).strip()


def send_daily_pack_ready_email(
    *,
    date: str,
    slot: str,
    channels: str,
    pack_path: str,
    wa_body: str = "",
    x_body: str = "",
    li_body: str = "",
    image_hint: str = "",
    feature: str = "",
    trend: str = "",
    video_hint: str = "",
) -> bool:
    """Email Sharath when a daily social pack is ready to paste manually.

    Never auto-posts to WhatsApp / X / LinkedIn — draft + notify only.
    Morning slot also nudges soft-launch mobile: push APK + phone OTP path.
    """
    to_email = SOCIAL_PACK_EMAIL
    if not to_email:
        return False

    slot_label = (slot or "daily").strip().title()
    is_morning = (slot or "").strip().lower() == "morning"
    soft_launch_nudge = (
        "DAILY PASTE (do all three): WhatsApp + X + LinkedIn from today’s pack — "
        "copy includes Android soft launch https://barathx.com/get-app/ (phone OTP). "
        "If you shipped app changes, also push barathx-latest-release.apk to main. "
        "Do not block on Google/Play SHA-1. Never auto-post."
    )

    subject = f"Your BarathX post is ready — {date} {slot_label}"
    if feature:
        subject += f" · {feature}"
    text_body = (
        f"Your BarathX post is ready.\n\n"
        f"Date: {date} (IST)\n"
        f"Slot: {slot_label}\n"
        f"Channels: {channels}\n"
        f"Pack: {pack_path}\n"
    )
    if feature:
        text_body += f"Feature: {feature}\n"
    if trend:
        text_body += f"Trend: {trend}\n"
    if image_hint:
        text_body += f"Images: {image_hint}\n"
    if video_hint:
        text_body += f"Video (~20s): {video_hint}\n"
    if is_morning:
        text_body += f"\n{soft_launch_nudge}\n"
    text_body += "\n— Paste yourself (WhatsApp / X / LinkedIn). Do not auto-blast.\n"
    if wa_body:
        text_body += f"\n--- WhatsApp ---\n{wa_body.strip()}\n"
    if x_body:
        text_body += f"\n--- X ---\n{x_body.strip()}\n"
    if li_body:
        text_body += f"\n--- LinkedIn ---\n{li_body.strip()}\n"
    text_body += "\n- BarathX daily pack\n"

    def _esc(s: str) -> str:
        return (
            (s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    blocks = []
    for label, body in (("WhatsApp", wa_body), ("X", x_body), ("LinkedIn", li_body)):
        if not body:
            continue
        blocks.append(
            f"<h3 style='margin:24px 0 8px;color:#FF671F;'>{_esc(label)}</h3>"
            f"<pre style='white-space:pre-wrap;background:#111;color:#f5f5f5;"
            f"padding:14px;border-radius:10px;font-size:14px;'>{_esc(body.strip())}</pre>"
        )
    blocks_html = "\n".join(blocks)
    soft_html = ""
    if is_morning:
        soft_html = f"""
  <p style="margin:20px 0;padding:12px 16px;background:#0f1419;color:#f5f5f5;border-left:4px solid #FF671F;border-radius:8px;">
    <strong style="color:#FF671F;">Soft launch (daily)</strong><br/>
    {_esc(soft_launch_nudge)}
  </p>
"""
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #0f1419; line-height: 1.5;">
  <p style="font-size:20px;font-weight:700;">Your BarathX post is ready</p>
  <p>Date: <strong>{_esc(date)}</strong> (IST) · Slot: <strong>{_esc(slot_label)}</strong></p>
  <p>Channels: {_esc(channels)}</p>
  {"<p>Feature: <strong>" + _esc(feature) + "</strong></p>" if feature else ""}
  {"<p style='color:#536471;font-size:14px;'>Trend: " + _esc(trend) + "</p>" if trend else ""}
  <p style="color:#536471;font-size:14px;">Pack: {_esc(pack_path)}</p>
  {"<p style='color:#536471;font-size:14px;'>Images: " + _esc(image_hint) + "</p>" if image_hint else ""}
  {"<p style='color:#536471;font-size:14px;'>Video (~20s): " + _esc(video_hint) + "</p>" if video_hint else ""}
  {soft_html}
  <p style="margin:20px 0;padding:12px 16px;background:#fff4ec;border-left:4px solid #FF671F;">
    Paste yourself on WhatsApp / X / LinkedIn. Do not auto-blast.
  </p>
  {blocks_html}
  <p style="color:#8b98a5;font-size:13px;margin-top:28px;">- BarathX daily pack</p>
</body>
</html>
"""
    try:
        return send_email(to_email, subject, text_body, html_body)
    except Exception:
        logger.exception("Daily pack ready email failed for %s", to_email)
        return False
