"""India DPDP Act 2023 / Rules 2025 aligned data-protection helpers.

BarathX is a Data Fiduciary for personal data of Data Principals in India.
We follow purpose limitation, data minimisation, retention, and principal rights
(access, correction, erasure, withdraw consent, grievance).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app import models

# Bump when the privacy notice text materially changes (consent re-notice).
PRIVACY_NOTICE_VERSION = "2026-08-16-dpdp"

# Ephemeral auth artefacts — delete when purpose is served (DPDP retention).
OTP_RETENTION_HOURS = 24
EMAIL_TOKEN_RETENTION_DAYS = 7
PASSWORD_RESET_RETENTION_DAYS = 2

# Inactive-account soft policy (ahead of social-media intermediary thresholds).
# Erasure of personal data after long inactivity is handled on request for now;
# this constant documents the product target for automated purge later.
INACTIVE_ACCOUNT_YEARS = 3

GRIEVANCE_EMAIL = "privacy@barathx.com"
SUPPORT_EMAIL = "hello@barathx.com"
# Response target under DPDP Rules grievance timelines (aim well under 90 days).
GRIEVANCE_RESPONSE_DAYS = 7


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def purge_ephemeral_personal_data(db: Session) -> dict[str, int]:
    """Erase expired / consumed OTPs and auth tokens (purpose completed)."""
    now = utcnow()
    otp_cutoff = now - timedelta(hours=OTP_RETENTION_HOURS)
    email_cutoff = now - timedelta(days=EMAIL_TOKEN_RETENTION_DAYS)
    reset_cutoff = now - timedelta(days=PASSWORD_RESET_RETENTION_DAYS)

    otps = (
        db.query(models.OTP)
        .filter(
            (models.OTP.expires_at < now)
            | (models.OTP.consumed.is_(True) & (models.OTP.created_at < otp_cutoff))
        )
        .delete(synchronize_session=False)
    )
    email_tokens = (
        db.query(models.EmailVerificationToken)
        .filter(
            (models.EmailVerificationToken.expires_at < now)
            | (
                models.EmailVerificationToken.consumed.is_(True)
                & (models.EmailVerificationToken.created_at < email_cutoff)
            )
        )
        .delete(synchronize_session=False)
    )
    reset_tokens = (
        db.query(models.PasswordResetToken)
        .filter(
            (models.PasswordResetToken.expires_at < now)
            | (
                models.PasswordResetToken.consumed.is_(True)
                & (models.PasswordResetToken.created_at < reset_cutoff)
            )
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {
        "otps_purged": int(otps or 0),
        "email_tokens_purged": int(email_tokens or 0),
        "password_reset_tokens_purged": int(reset_tokens or 0),
    }


def erase_user_auth_artefacts(db: Session, user_id: str) -> None:
    """On account erasure, wipe verification / reset tokens tied to the user."""
    db.query(models.EmailVerificationToken).filter(
        models.EmailVerificationToken.user_id == user_id
    ).delete(synchronize_session=False)
    db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.user_id == user_id
    ).delete(synchronize_session=False)


def build_personal_data_export(db: Session, user: models.User) -> dict[str, Any]:
    """Right to access — machine-readable copy of personal data we hold."""
    posts = (
        db.query(models.Post)
        .filter(models.Post.author_id == user.id)
        .order_by(models.Post.created_at.desc())
        .limit(2000)
        .all()
    )
    replies = (
        db.query(models.Reply)
        .filter(models.Reply.author_id == user.id)
        .order_by(models.Reply.created_at.desc())
        .limit(2000)
        .all()
    )
    return {
        "export_generated_at": utcnow().isoformat(),
        "privacy_notice_version": PRIVACY_NOTICE_VERSION,
        "lawful_basis": "consent",
        "data_fiduciary": {
            "name": "BarathX",
            "website": "https://barathx.com",
            "grievance_email": GRIEVANCE_EMAIL,
            "support_email": SUPPORT_EMAIL,
        },
        "account": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "phone": user.phone,
            "language": user.language,
            "theme": getattr(user, "theme", None),
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "cover_url": user.cover_url,
            "is_email_verified": user.is_email_verified,
            "is_phone_verified": user.is_phone_verified,
            "email_activity_enabled": bool(getattr(user, "email_activity_enabled", True)),
            "privacy_accepted_at": (
                user.privacy_accepted_at.isoformat()
                if getattr(user, "privacy_accepted_at", None)
                else None
            ),
            "privacy_notice_version": getattr(user, "privacy_notice_version", None),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "posts": [
            {
                "id": p.id,
                "text": p.text,
                "image_url": p.image_url,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in posts
        ],
        "replies": [
            {
                "id": r.id,
                "post_id": r.post_id,
                "text": r.text,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in replies
        ],
        "retention_note": (
            "Account personal data is kept while your account is active for the "
            "specified purpose (public square participation). Ephemeral OTPs and "
            "reset tokens are deleted when expired or shortly after use. "
            f"You may request erasure anytime; grievance response target "
            f"{GRIEVANCE_RESPONSE_DAYS} days."
        ),
    }
