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

# Explicit adult / sexual content — blocked everywhere (posts, replies, DMs, Live).
# Aimed at porn/solicitation, not civic debate about policy or harassment as a topic.
ADULT_CONTENT_RE = re.compile(
    r"("
    r"\bporn(o|ography|hub)?\b|"
    r"\bonlyfans\b|\bfansly\b|"
    r"\bnudes?\b|\bnsfw\b|\bxxx+\b|"
    r"send\s+nudes?|"
    r"\bsext(ing|s)?\b|"
    r"\bsex\s*(tape|video|chat|cam|worker|work|pics?|photos?)\b|"
    r"\b(escort|hookers?)\b|"
    r"\b(dick|cock)\s*pics?\b|"
    r"\b(blow\s*jobs?|hand\s*jobs?)\b|"
    r"\b(cum\s*shot|deepthroat)\b|"
    r"\berotic\s+(pics?|photos?|videos?|content)\b|"
    r"\badult\s+(videos?|content|sites?|links?)\b|"
    r"\bnaked\s+(pics?|photos?|selfies?|videos?)\b"
    r")",
    re.I,
)

ADULT_BLOCK_MESSAGE = (
    "Adult or sexual content is not allowed on BarathX. "
    "Keep posts, replies, and messages suitable for India's public square."
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


def is_adult_or_sexual_content(text: str) -> bool:
    return bool(ADULT_CONTENT_RE.search(text or ""))


def assert_safe_public_text(text: str) -> None:
    """Raise ValueError when text must not be posted or messaged on BarathX."""
    if is_adult_or_sexual_content(text):
        raise ValueError(ADULT_BLOCK_MESSAGE)
    if SEVERE_RE.search(text or ""):
        raise ValueError("This text violates BarathX community guidelines.")


def text_violation_level(text: str) -> Optional[str]:
    """Return 'severe' | 'mild' | None."""
    t = (text or "").strip()
    if not t:
        return None
    if SEVERE_RE.search(t) or ADULT_CONTENT_RE.search(t):
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
    return "Report submitted. Thanks for helping keep BarathX safe."


def purge_user(db: Session, user: models.User) -> None:
    """Remove a user and dependent rows that lack cascade-from-user.

    Postgres enforces FKs that SQLite often skips — clear every users.id
    reference before deleting the row (posts, rewards, tokens, etc.).
    """
    uid = user.id

    # Auth artefacts
    db.query(models.EmailVerificationToken).filter(
        models.EmailVerificationToken.user_id == uid
    ).delete(synchronize_session=False)
    db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.user_id == uid
    ).delete(synchronize_session=False)

    # Rewards / product board (may reference posts/spaces too)
    if hasattr(models, "FoundingReward"):
        db.query(models.FoundingReward).filter(models.FoundingReward.user_id == uid).delete(
            synchronize_session=False
        )
    if hasattr(models, "RaceReward"):
        db.query(models.RaceReward).filter(models.RaceReward.user_id == uid).delete(
            synchronize_session=False
        )
    if hasattr(models, "ProductIssue"):
        db.query(models.ProductIssue).filter(models.ProductIssue.author_id == uid).delete(
            synchronize_session=False
        )

    # Posts authored by this user (and everything hanging off those posts)
    post_ids = [
        p[0] for p in db.query(models.Post.id).filter(models.Post.author_id == uid).all()
    ]
    if post_ids:
        reply_ids = [
            r[0]
            for r in db.query(models.Reply.id).filter(models.Reply.post_id.in_(post_ids)).all()
        ]
        if reply_ids:
            db.query(models.Notification).filter(
                models.Notification.reply_id.in_(reply_ids)
            ).delete(synchronize_session=False)
            db.query(models.ReplyLike).filter(models.ReplyLike.reply_id.in_(reply_ids)).delete(
                synchronize_session=False
            )
            db.query(models.Reply).filter(models.Reply.post_id.in_(post_ids)).update(
                {models.Reply.parent_reply_id: None}, synchronize_session=False
            )
            db.query(models.Reply).filter(models.Reply.post_id.in_(post_ids)).delete(
                synchronize_session=False
            )
        db.query(models.Notification).filter(models.Notification.post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Like).filter(models.Like.post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Repost).filter(models.Repost.post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Bookmark).filter(models.Bookmark.post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.PostHashtag).filter(models.PostHashtag.post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Report).filter(models.Report.target_post_id.in_(post_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Post).filter(models.Post.quoted_post_id.in_(post_ids)).update(
            {models.Post.quoted_post_id: None}, synchronize_session=False
        )
        if hasattr(models, "FoundingReward"):
            db.query(models.FoundingReward).filter(
                models.FoundingReward.qualifying_post_id.in_(post_ids)
            ).update(
                {models.FoundingReward.qualifying_post_id: None},
                synchronize_session=False,
            )
        if hasattr(models, "RaceReward"):
            db.query(models.RaceReward).filter(models.RaceReward.post_id.in_(post_ids)).delete(
                synchronize_session=False
            )
        db.query(models.Post).filter(models.Post.id.in_(post_ids)).delete(
            synchronize_session=False
        )

    # Replies authored on other people's posts
    own_reply_ids = [
        r[0] for r in db.query(models.Reply.id).filter(models.Reply.author_id == uid).all()
    ]
    if own_reply_ids:
        db.query(models.Notification).filter(
            models.Notification.reply_id.in_(own_reply_ids)
        ).delete(synchronize_session=False)
        db.query(models.ReplyLike).filter(models.ReplyLike.reply_id.in_(own_reply_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Reply).filter(models.Reply.parent_reply_id.in_(own_reply_ids)).update(
            {models.Reply.parent_reply_id: None}, synchronize_session=False
        )
        db.query(models.Reply).filter(models.Reply.id.in_(own_reply_ids)).delete(
            synchronize_session=False
        )

    # Engagement rows owned by this user
    db.query(models.Like).filter(models.Like.user_id == uid).delete(synchronize_session=False)
    db.query(models.ReplyLike).filter(models.ReplyLike.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.Repost).filter(models.Repost.user_id == uid).delete(synchronize_session=False)

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
    if hasattr(models, "LiveTalkSignal"):
        db.query(models.LiveTalkSignal).filter(
            (models.LiveTalkSignal.from_user_id == uid)
            | (models.LiveTalkSignal.to_user_id == uid)
        ).delete(synchronize_session=False)
    db.query(models.ModerationStrike).filter(models.ModerationStrike.user_id == uid).delete(
        synchronize_session=False
    )
    db.query(models.UserTopicInterest).filter(models.UserTopicInterest.user_id == uid).delete(
        synchronize_session=False
    )
    host = db.query(models.User).filter(models.User.username == "baratx").first()
    owned_space_ids = [
        s[0] for s in db.query(models.Space.id).filter(models.Space.host_id == uid).all()
    ]
    if owned_space_ids and hasattr(models, "FoundingReward"):
        db.query(models.FoundingReward).filter(
            models.FoundingReward.qualifying_space_id.in_(owned_space_ids)
        ).update(
            {models.FoundingReward.qualifying_space_id: None},
            synchronize_session=False,
        )
    if host and host.id != uid:
        db.query(models.Space).filter(models.Space.host_id == uid).update(
            {models.Space.host_id: host.id}, synchronize_session=False
        )
        db.query(models.Community).filter(models.Community.created_by == uid).update(
            {models.Community.created_by: host.id}, synchronize_session=False
        )
    else:
        db.query(models.Space).filter(models.Space.host_id == uid).delete(synchronize_session=False)

    # Avoid ORM relationship cascades fighting bulk query deletes (Postgres IntegrityError / 500).
    db.expunge(user)
    db.query(models.User).filter(models.User.id == uid).delete(synchronize_session=False)