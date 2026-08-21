"""Daily debate participation streak (IST calendar days)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models

IST = timezone(timedelta(hours=5, minutes=30))
STREAK_MILESTONES = frozenset({3, 7, 14, 30})


def ist_today() -> str:
    return datetime.now(IST).date().isoformat()


def bump_debate_streak(user: models.User) -> int:
    """Increment debate streak for an IST calendar day. Idempotent within the day."""
    today = ist_today()
    last = getattr(user, "debate_streak_day", None)
    if last == today:
        return int(getattr(user, "debate_streak", 0) or 0)
    yesterday = (datetime.now(IST).date() - timedelta(days=1)).isoformat()
    prev = int(getattr(user, "debate_streak", 0) or 0)
    streak = prev + 1 if last == yesterday else 1
    user.debate_streak = streak
    user.debate_streak_day = today
    return streak


def maybe_notify_streak(
    db: Session,
    *,
    user: models.User,
    streak: int,
    create_notification,
) -> None:
    """High-value streak alerts via @baratx (create_notification skips self-actor)."""
    if streak not in STREAK_MILESTONES or not create_notification:
        return
    actor = db.query(models.User).filter(models.User.username == "baratx").first()
    if not actor:
        return
    create_notification(
        db,
        recipient_id=user.id,
        actor_id=actor.id,
        kind="streak",
        message=f"Debate streak: {streak} days. Keep showing up.",
    )
