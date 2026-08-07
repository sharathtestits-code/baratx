"""Community-guideline auto-moderation for Live Talk and reports.

Removes misbehaving participants from calls without waiting for an admin,
and escalates repeated / severe violations to account removal (non-protected).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models, seed

# Soft cap — product can raise later
LIVE_TALK_MAX = 15

# Unique reporters in this window → auto-delete (misleading / guideline breach)
REPORT_DELETE_WINDOW_HOURS = 24
REPORT_DELETE_THRESHOLD = 3

# Talk-only strikes before account escalate
TALK_STRIKE_DELETE = 3

SEVERE_RE = re.compile(
    r"("
    r"\bkys\b|"
    r"kill\s+yourself|"
    r"rape\b|"
    r"\bnazi\b|"
    r"child\s*porn|"
    r"\bcsam\b|"
    r"terror(ist)?\s+attack|"
    r"bomb\s+threat"
    r")",
    re.I,
)

SPAM_RE = re.compile(
    r"("
    r"https?://\S+\s+https?://|"
    r"(free\s+)?crypto\s+giveaway|"
    r"whatsapp\s*\+?\d{8,}|"
    r"click\s+here\s+now"
    r")",
    re.I,
)

GUIDELINE_REASONS = frozenset(
    {
        "harassment",
        "hate",
        "threats",
        "spam",
        "misinformation",
        "misleading",
        "sexual",
        "violence",
        "impersonation",
        "community guidelines",
        "guidelines",
    }
)


def is_protected_user(user: models.User) -> bool:
    return (user.username or "") in seed.PROTECTED_BLUE_USERNAMES


def text_violation_level(text: str) -> Optional[str]:
    """Return 'severe' | 'mild' | None."""
    t = (text or "").strip()
    if not t:
        return None
    if SEVERE_RE.search(t):
        return "severe"
    if SPAM_RE.search(t):
        return "mild"
    return None


def reason_is_guideline(reason: str) -> bool:
    r = (reason or "").strip().lower()
    if not r:
        return False
    if any(k in r for k in GUIDELINE_REASONS):
        return True
    return text_violation_level(r) is not None


def kick_from_all_talks(db: Session, user_id: str, reason: str) -> int:
    """Mark active talk seats as removed. Returns rows touched."""
    now = datetime.now(timezone.utc)
    rows = (
        db.query(models.LiveTalkParticipant)
        .filter(
            models.LiveTalkParticipant.user_id == user_id,
            models.LiveTalkParticipant.left_at.is_(None),
            models.LiveTalkParticipant.removed_at.is_(None),
        )
        .all()
    )
    for row in rows:
        row.removed_at = now
        row.removed_reason = (reason or "community guidelines")[:200]
        row.left_at = now
    return len(rows)


def add_strike(
    db: Session,
    *,
    user_id: str,
    kind: str,
    detail: str = "",
    space_id: Optional[str] = None,
) -> models.ModerationStrike:
    strike = models.ModerationStrike(
        user_id=user_id,
        kind=kind,
        detail=(detail or "")[:500],
        space_id=space_id,
    )
    db.add(strike)
    return strike


def recent_strike_count(db: Session, user_id: str, hours: int = 72) -> int:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(models.ModerationStrike)
        .filter(
            models.ModerationStrike.user_id == user_id,
            models.ModerationStrike.created_at >= since,
        )
        .count()
    )


def unique_reporters_24h(db: Session, target_user_id: str) -> int:
    since = datetime.now(timezone.utc) - timedelta(hours=REPORT_DELETE_WINDOW_HOURS)
    rows = (
        db.query(models.Report.reporter_id)
        .filter(
            models.Report.target_user_id == target_user_id,
            models.Report.created_at >= since,
        )
        .distinct()
        .all()
    )
    return len(rows)


def maybe_auto_delete_user(db: Session, user: models.User, *, purge_fn) -> Optional[str]:
    """Delete account when thresholds met. Returns message or None."""
    if is_protected_user(user):
        return None
    reporters = unique_reporters_24h(db, user.id)
    strikes = recent_strike_count(db, user.id)
    if reporters >= REPORT_DELETE_THRESHOLD or strikes >= TALK_STRIKE_DELETE:
        username = user.username
        kick_from_all_talks(db, user.id, "auto-removed: community guidelines")
        purge_fn(db, user)
        return f"Auto-removed @{username} for community guideline violations"
    return None


def apply_talk_message_moderation(
    db: Session,
    *,
    space_id: str,
    sender: models.User,
    text: str,
    purge_fn,
) -> Optional[str]:
    """If message violates guidelines, kick (+ maybe delete). Returns error detail or None."""
    level = text_violation_level(text)
    if not level:
        return None
    add_strike(
        db,
        user_id=sender.id,
        kind=f"talk_{level}",
        detail=text[:200],
        space_id=space_id,
    )
    kick_from_all_talks(db, sender.id, f"auto-removed: {level} guideline violation")
    if level == "severe" and not is_protected_user(sender):
        # Severe → strike stack + immediate escalate check
        add_strike(db, user_id=sender.id, kind="severe_escalate", detail="severe talk content", space_id=space_id)
        msg = maybe_auto_delete_user(db, sender, purge_fn=purge_fn)
        if msg:
            return "Message blocked. Account removed for severe community guideline violations."
    elif recent_strike_count(db, sender.id) >= TALK_STRIKE_DELETE:
        msg = maybe_auto_delete_user(db, sender, purge_fn=purge_fn)
        if msg:
            return "Message blocked. Account removed for repeated guideline violations."
    return "Message blocked and you were removed from Talk for breaking community guidelines."


def apply_report_auto_mod(
    db: Session,
    *,
    target: models.User,
    reason: str,
    details: str,
    purge_fn=None,
) -> str:
    """After a report is stored — kick from talks and maybe delete."""
    combined = f"{reason} {details}"
    level = text_violation_level(combined)
    guideline = reason_is_guideline(reason) or level is not None
    kick_from_all_talks(
        db,
        target.id,
        "removed from Live Talk after community report",
    )
    if guideline:
        add_strike(
            db,
            user_id=target.id,
            kind="report",
            detail=(reason or "")[:200],
        )
    if level == "severe":
        add_strike(db, user_id=target.id, kind="severe_report", detail=combined[:200])
    deleted = maybe_auto_delete_user(db, target, purge_fn=purge_fn or purge_user)
    if deleted:
        return deleted
    if guideline:
        return (
            "Report submitted. They were removed from Live Talk. "
            "Repeated guideline breaches remove the account automatically."
        )
    return "Report submitted. Thanks for helping keep BaratX safe."


def purge_user(db: Session, user: models.User) -> None:
    """Remove a user and dependent rows that lack cascade-from-user."""
    uid = user.id
    db.query(models.Follow).filter(
        (models.Follow.follower_id == uid) | (models.Follow.followed_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.Notification).filter(
        (models.Notification.recipient_id == uid) | (models.Notification.actor_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.Bookmark).filter(models.Bookmark.user_id == uid).delete(synchronize_session=False)
    db.query(models.Block).filter(
        (models.Block.blocker_id == uid) | (models.Block.blocked_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.Mute).filter(
        (models.Mute.muter_id == uid) | (models.Mute.muted_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.Report).filter(
        (models.Report.reporter_id == uid) | (models.Report.target_user_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.DirectMessage).filter(
        (models.DirectMessage.sender_id == uid) | (models.DirectMessage.recipient_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.ListMember).filter(models.ListMember.user_id == uid).delete(synchronize_session=False)
    db.query(models.UserList).filter(models.UserList.owner_id == uid).delete(synchronize_session=False)
    db.query(models.CommunityMember).filter(models.CommunityMember.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.SpaceStance).filter(models.SpaceStance.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.LiveTalkParticipant).filter(models.LiveTalkParticipant.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.LiveTalkPin).filter(
        (models.LiveTalkPin.viewer_id == uid) | (models.LiveTalkPin.pinned_user_id == uid)
    ).delete(synchronize_session=False)
    db.query(models.LiveTalkMessage).filter(models.LiveTalkMessage.sender_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.LiveTalkReaction).filter(models.LiveTalkReaction.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.ModerationStrike).filter(models.ModerationStrike.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.UserTopicInterest).filter(models.UserTopicInterest.user_id == uid).delete(
        synchronize_session=False
    )
    host = db.query(models.User).filter(models.User.username == "baratx").first()
    if host and host.id != uid:
        db.query(models.Space).filter(models.Space.host_id == uid).update(
            {models.Space.host_id: host.id}, synchronize_session=False
        )
    else:
        db.query(models.Space).filter(models.Space.host_id == uid).delete(synchronize_session=False)
    if host and host.id != uid:
        db.query(models.Community).filter(models.Community.created_by == uid).update(
            {models.Community.created_by: host.id}, synchronize_session=False
        )
    db.delete(user)