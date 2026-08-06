"""Founding 100 — quiet incentive for one real civic problem or debate.

Pay ₹150 UPI only for real civic behavior (not bare signup). Cap: first 100 users.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.topics_data import CIVIC_ARENA_KEYS

FOUNDING_CAP = 100
FOUNDING_AMOUNT_INR = 150
MIN_PROBLEM_CHARS = 50


def slots_remaining(db: Session) -> int:
    used = db.query(models.FoundingReward).count()
    return max(0, FOUNDING_CAP - used)


def my_reward(db: Session, user_id: str) -> Optional[models.FoundingReward]:
    return (
        db.query(models.FoundingReward)
        .filter(models.FoundingReward.user_id == user_id)
        .first()
    )


def status_payload(db: Session, user: Optional[models.User] = None) -> dict:
    mine = my_reward(db, user.id) if user else None
    remaining = slots_remaining(db)
    return {
        "cap": FOUNDING_CAP,
        "amount_inr": FOUNDING_AMOUNT_INR,
        "min_problem_chars": MIN_PROBLEM_CHARS,
        "slots_remaining": remaining,
        "open": remaining > 0,
        "my_status": mine.status if mine else None,
        "my_kind": mine.kind if mine else None,
        "civic_arenas": sorted(CIVIC_ARENA_KEYS),
    }


def try_award(
    db: Session,
    *,
    user: models.User,
    kind: str,
    post_id: Optional[str] = None,
    space_id: Optional[str] = None,
) -> Optional[models.FoundingReward]:
    """Award at most one Founding reward per user while slots remain. Idempotent."""
    if not user or user.is_official:
        return None
    if kind not in ("problem", "debate"):
        return None
    if my_reward(db, user.id):
        return None
    if slots_remaining(db) <= 0:
        return None

    row = models.FoundingReward(
        user_id=user.id,
        kind=kind,
        amount_inr=FOUNDING_AMOUNT_INR,
        status="eligible",
        qualifying_post_id=post_id,
        qualifying_space_id=space_id,
    )
    # Savepoint so a unique-user race does not wipe the parent post/debate txn.
    nested = db.begin_nested()
    try:
        db.add(row)
        db.flush()
        nested.commit()
    except IntegrityError:
        nested.rollback()
        return None
    return row


def qualifies_as_problem(text: str) -> bool:
    return len((text or "").strip()) >= MIN_PROBLEM_CHARS


def mark_paid(db: Session, reward_id: str, note: str = "") -> models.FoundingReward:
    row = db.query(models.FoundingReward).filter(models.FoundingReward.id == reward_id).first()
    if not row:
        raise LookupError("reward_not_found")
    row.status = "paid"
    row.paid_at = datetime.now(timezone.utc)
    if note is not None:
        row.note = (note or "").strip()[:280]
    db.flush()
    return row
