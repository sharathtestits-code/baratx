"""BarathX rewards — Founding 100 + biweekly Square Race.

Evaluation (no AI judge, no self-rating alone):
1. Floor — real action: civic problem post (≥50 chars, flagged) OR open any arena debate.
2. Community rating — likes (and replies / debate stances) prove others cared.
3. Admin payout — human marks paid after UPI; spam/self-like can be rejected.

Founding 100: membership earned by clearing the floor (real debate / civic post);
pay only when the quality bar is met (likes/replies) or admin overrides after review.
Public copy never leads with ₹ — amount is a private surprise after payable.
Not a signup coupon — entry proves the behavior, then India rates.

Square Race (biweekly): highest-liked home post in the period wins ₹150–₹500
scaled by likes. Drives return logins without paying for bare signup.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import models
from app.topics_data import ACTIVE_ARENA_KEYS

FOUNDING_CAP = 100
FOUNDING_AMOUNT_INR = 150
MIN_PROBLEM_CHARS = 50

# Quality bar before Founding payout (community rating).
FOUNDING_MIN_LIKES = 25
FOUNDING_MIN_REPLIES = 5  # human replies (official welcome excluded)
FOUNDING_DEBATE_MIN_STANCES = 2
FOUNDING_DEBATE_MIN_POSTS = 3

# Biweekly Square Race
RACE_CADENCE_DAYS = 14
RACE_PRIZE_MIN = 150
RACE_PRIZE_MAX = 500
RACE_MIN_LIKES_TO_WIN = 25

# Official / seeded accounts never count toward reward rating.
_OFFICIAL_USERNAMES = frozenset({"baratx", "sharath", "bharatvoices", "indiatech"})


def _is_non_community_rater(user: models.User) -> bool:
    """True for brand/founder accounts — their likes/replies don't count for rewards."""
    if not user:
        return True
    if getattr(user, "is_official", False):
        return True
    badge = (getattr(user, "badge", None) or "none").strip().lower()
    if badge == "blue":
        return True
    return (user.username or "").lower() in _OFFICIAL_USERNAMES


def slots_remaining(db: Session) -> int:
    used = db.query(models.FoundingReward).count()
    return max(0, FOUNDING_CAP - used)


def my_reward(db: Session, user_id: str) -> Optional[models.FoundingReward]:
    return (
        db.query(models.FoundingReward)
        .filter(models.FoundingReward.user_id == user_id)
        .first()
    )


def _post_like_count(db: Session, post_id: str, author_id: Optional[str] = None) -> int:
    """Community likes only — exclude author self-likes and official/brand accounts."""
    q = (
        db.query(func.count(models.Like.id))
        .join(models.User, models.User.id == models.Like.user_id)
        .filter(
            models.Like.post_id == post_id,
            models.User.is_official == False,  # noqa: E712
            models.User.badge != "blue",
            ~models.User.username.in_(_OFFICIAL_USERNAMES),
        )
    )
    if author_id:
        q = q.filter(models.Like.user_id != author_id)
    return q.scalar() or 0


def _post_other_reply_count(db: Session, post_id: str, author_id: str) -> int:
    """Human replies only — @baratx/@sharath welcome replies never count for rewards."""
    return (
        db.query(func.count(models.Reply.id))
        .join(models.User, models.User.id == models.Reply.author_id)
        .filter(
            models.Reply.post_id == post_id,
            models.Reply.author_id != author_id,
            models.User.is_official == False,  # noqa: E712
            models.User.badge != "blue",
            ~models.User.username.in_(_OFFICIAL_USERNAMES),
        )
        .scalar()
        or 0
    )


def problem_meets_quality_bar(db: Session, post_id: str, author_id: str) -> dict:
    likes = _post_like_count(db, post_id, author_id=author_id)
    replies = _post_other_reply_count(db, post_id, author_id)
    ok = likes >= FOUNDING_MIN_LIKES or replies >= FOUNDING_MIN_REPLIES
    return {
        "meets_bar": ok,
        "like_count": likes,
        "reply_count": replies,
        "need_likes": FOUNDING_MIN_LIKES,
        "need_replies": FOUNDING_MIN_REPLIES,
    }


def debate_meets_quality_bar(db: Session, space_id: str) -> dict:
    stances = (
        db.query(func.count(models.SpaceStance.id))
        .filter(models.SpaceStance.space_id == space_id)
        .scalar()
        or 0
    )
    posts = (
        db.query(func.count(models.Post.id)).filter(models.Post.space_id == space_id).scalar() or 0
    )
    ok = stances >= FOUNDING_DEBATE_MIN_STANCES or posts >= FOUNDING_DEBATE_MIN_POSTS
    return {
        "meets_bar": ok,
        "stance_count": stances,
        "post_count": posts,
        "need_stances": FOUNDING_DEBATE_MIN_STANCES,
        "need_posts": FOUNDING_DEBATE_MIN_POSTS,
    }


def refresh_founding_payable(db: Session, reward: models.FoundingReward) -> models.FoundingReward:
    """Move eligible → payable when community rating clears the bar."""
    if reward.status != "eligible":
        return reward
    ok = False
    if reward.kind == "problem" and reward.qualifying_post_id:
        post = db.query(models.Post).filter(models.Post.id == reward.qualifying_post_id).first()
        if post:
            ok = problem_meets_quality_bar(db, post.id, post.author_id)["meets_bar"]
    elif reward.kind == "debate" and reward.qualifying_space_id:
        ok = debate_meets_quality_bar(db, reward.qualifying_space_id)["meets_bar"]
    if ok:
        reward.status = "payable"
        db.flush()
    return reward


def quality_snapshot(db: Session, reward: models.FoundingReward) -> dict:
    if reward.kind == "problem" and reward.qualifying_post_id:
        post = db.query(models.Post).filter(models.Post.id == reward.qualifying_post_id).first()
        if post:
            snap = problem_meets_quality_bar(db, post.id, post.author_id)
            return {"kind": "problem", **snap}
    if reward.kind == "debate" and reward.qualifying_space_id:
        snap = debate_meets_quality_bar(db, reward.qualifying_space_id)
        return {"kind": "debate", **snap}
    return {"kind": reward.kind, "meets_bar": False}


def status_payload(db: Session, user: Optional[models.User] = None) -> dict:
    mine = my_reward(db, user.id) if user else None
    if mine and mine.status == "eligible":
        before = mine.status
        refresh_founding_payable(db, mine)
        if mine.status != before:
            db.commit()
            db.refresh(mine)
    remaining = slots_remaining(db)
    quality = quality_snapshot(db, mine) if mine else None
    # Hide rupee amount until the user has earned payable/paid — surprise, don't advertise.
    reveal_amount = bool(mine and mine.status in ("payable", "paid"))
    return {
        "cap": FOUNDING_CAP,
        "amount_inr": FOUNDING_AMOUNT_INR if reveal_amount else None,
        "min_problem_chars": MIN_PROBLEM_CHARS,
        "slots_remaining": remaining,
        "open": remaining > 0,
        "my_status": mine.status if mine else None,
        "my_kind": mine.kind if mine else None,
        "my_quality": quality,
        "qualify_arenas": sorted(ACTIVE_ARENA_KEYS),
        "civic_arenas": sorted(ACTIVE_ARENA_KEYS),  # back-compat
        "eval": {
            "floor": "Civic problem (≥50 chars + flag) OR open any arena debate",
            "rating": "Community likes / replies (or debate stances) — official @baratx/@sharath replies never count",
            "min_likes": FOUNDING_MIN_LIKES,
            "min_replies": FOUNDING_MIN_REPLIES,
            "payout": "Private thank-you after bar met — never advertised up front",
        },
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
    nested = db.begin_nested()
    try:
        db.add(row)
        db.flush()
        nested.commit()
    except IntegrityError:
        nested.rollback()
        return None
    refresh_founding_payable(db, row)
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


def bump_founding_for_post(db: Session, post_id: str) -> None:
    """Re-check quality bar when a qualifying problem post gets likes/replies."""
    row = (
        db.query(models.FoundingReward)
        .filter(
            models.FoundingReward.qualifying_post_id == post_id,
            models.FoundingReward.status == "eligible",
        )
        .first()
    )
    if row:
        refresh_founding_payable(db, row)


def bump_founding_for_space(db: Session, space_id: str) -> None:
    row = (
        db.query(models.FoundingReward)
        .filter(
            models.FoundingReward.qualifying_space_id == space_id,
            models.FoundingReward.status == "eligible",
        )
        .first()
    )
    if row:
        refresh_founding_payable(db, row)


# ---------- Biweekly Square Race (likes = rating) ----------


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def period_bounds(at: Optional[datetime] = None) -> tuple[datetime, datetime, str]:
    """14-day periods anchored to Unix epoch Mondays (UTC)."""
    at = at or _utc_now()
    if at.tzinfo is None:
        at = at.replace(tzinfo=timezone.utc)
    # Days since epoch Monday 1970-01-05 is messy; use floor division of days.
    epoch = datetime(2026, 1, 5, tzinfo=timezone.utc)  # Monday anchor near product life
    days = (at.date() - epoch.date()).days
    bucket = days // RACE_CADENCE_DAYS
    start = epoch + timedelta(days=bucket * RACE_CADENCE_DAYS)
    end = start + timedelta(days=RACE_CADENCE_DAYS)
    key = start.strftime("%Y-%m-%d")
    return start, end, key


def prize_for_likes(likes: int) -> int:
    """Map likes → ₹150–₹500. Community rating scales the purse."""
    if likes < RACE_MIN_LIKES_TO_WIN:
        return 0
    # 3→150, then +20/like, soft cap 500
    return min(RACE_PRIZE_MAX, RACE_PRIZE_MIN + (likes - RACE_MIN_LIKES_TO_WIN) * 20)


def _home_posts_in_period(db: Session, start: datetime, end: datetime):
    return (
        db.query(models.Post)
        .options(joinedload(models.Post.author), joinedload(models.Post.likes))
        .filter(
            models.Post.created_at >= start,
            models.Post.created_at < end,
            models.Post.community_id.is_(None),
            models.Post.space_id.is_(None),
        )
        .all()
    )


def race_leaderboard(db: Session, *, limit: int = 10, at: Optional[datetime] = None) -> dict:
    start, end, key = period_bounds(at)
    posts = _home_posts_in_period(db, start, end)
    ranked = []
    for p in posts:
        if p.author and p.author.is_official:
            continue
        # Prefer relationship likes but filter self/official in prize calc via query for accuracy
        likes = _post_like_count(db, p.id, author_id=p.author_id)
        ranked.append((likes, p))
    ranked.sort(key=lambda t: (-t[0], t[1].created_at))
    # One row per author — best Home post only (TC-QA2-REWARDS-DUPE-01).
    best_by_author: dict[str, tuple[int, models.Post]] = {}
    for likes, p in ranked:
        prev = best_by_author.get(p.author_id)
        if prev is None or likes > prev[0] or (likes == prev[0] and p.created_at < prev[1].created_at):
            best_by_author[p.author_id] = (likes, p)
    deduped = sorted(best_by_author.values(), key=lambda t: (-t[0], t[1].created_at))
    top = []
    for likes, p in deduped[:limit]:
        top.append(
            {
                "post_id": p.id,
                "text": (p.text or "")[:180],
                "like_count": likes,
                "prize_inr": prize_for_likes(likes),
                "author_id": p.author_id,
                "username": p.author.username if p.author else "?",
                "display_name": p.author.display_name if p.author else "?",
                "created_at": p.created_at,
            }
        )
    leader = top[0] if top and top[0]["like_count"] >= RACE_MIN_LIKES_TO_WIN else None
    return {
        "period_key": key,
        "starts_at": start,
        "ends_at": end,
        "cadence_days": RACE_CADENCE_DAYS,
        "prize_min": RACE_PRIZE_MIN,
        "prize_max": RACE_PRIZE_MAX,
        "min_likes_to_win": RACE_MIN_LIKES_TO_WIN,
        "eval": "Highest likes on a Home post in this fortnight = community rating. Prize scales ₹150–₹500.",
        "leader": leader,
        "leaderboard": top,
    }


def race_status_for_user(db: Session, user: Optional[models.User] = None) -> dict:
    board = race_leaderboard(db, limit=20)
    my_best = None
    my_rank = None
    if user:
        for i, row in enumerate(board["leaderboard"], start=1):
            if row["author_id"] == user.id:
                my_best = row
                my_rank = i
                break
        if my_best is None:
            # User may be outside top N — find their best in period.
            start, end, _ = period_bounds()
            posts = (
                db.query(models.Post)
                .options(joinedload(models.Post.likes))
                .filter(
                    models.Post.author_id == user.id,
                    models.Post.created_at >= start,
                    models.Post.created_at < end,
                    models.Post.community_id.is_(None),
                    models.Post.space_id.is_(None),
                )
                .all()
            )
            if posts:
                best = max(
                    posts,
                    key=lambda p: _post_like_count(db, p.id, author_id=user.id),
                )
                likes = _post_like_count(db, best.id, author_id=user.id)
                my_best = {
                    "post_id": best.id,
                    "text": (best.text or "")[:180],
                    "like_count": likes,
                    "prize_inr": prize_for_likes(likes),
                    "author_id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "created_at": best.created_at,
                }
                # Rank among authors' best posts (matches leaderboard dedupe).
                best_likes: dict[str, tuple[int, str]] = {}
                for p in _home_posts_in_period(db, start, end):
                    if p.author and p.author.is_official:
                        continue
                    likes = _post_like_count(db, p.id, author_id=p.author_id)
                    prev = best_likes.get(p.author_id)
                    if prev is None or likes > prev[0]:
                        best_likes[p.author_id] = (likes, p.id)
                all_ranked = sorted(best_likes.values(), key=lambda t: (-t[0], t[1]))
                for i, (_likes, pid) in enumerate(all_ranked, start=1):
                    if pid == best.id:
                        my_rank = i
                        break
    paid = (
        db.query(models.RaceReward)
        .filter(models.RaceReward.period_key == board["period_key"])
        .first()
    )
    return {
        **board,
        "my_best": my_best,
        "my_rank": my_rank,
        "period_paid": bool(paid and paid.status == "paid"),
        "period_winner_username": paid.username_snapshot if paid else None,
    }


def close_race_winner(
    db: Session,
    *,
    period_key: Optional[str] = None,
    post_id: Optional[str] = None,
    note: str = "",
) -> models.RaceReward:
    """Admin locks biweekly winner (default: current period leader)."""
    at = None
    if period_key:
        try:
            at = datetime.strptime(period_key, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise LookupError("bad_period") from exc
    board = race_leaderboard(db, limit=20, at=at)
    key = board["period_key"]
    existing = db.query(models.RaceReward).filter(models.RaceReward.period_key == key).first()
    if existing and existing.status == "paid":
        return existing

    pick = None
    if post_id:
        for row in board["leaderboard"]:
            if row["post_id"] == post_id:
                pick = row
                break
        if not pick:
            raise LookupError("post_not_in_period")
    else:
        pick = board["leader"]
    if not pick or pick["like_count"] < RACE_MIN_LIKES_TO_WIN:
        raise LookupError("no_qualifying_leader")

    amount = prize_for_likes(pick["like_count"])
    if existing:
        existing.user_id = pick["author_id"]
        existing.post_id = pick["post_id"]
        existing.like_count = pick["like_count"]
        existing.amount_inr = amount
        existing.username_snapshot = pick["username"]
        existing.status = "payable"
        existing.note = (note or existing.note or "")[:280]
        db.flush()
        return existing

    row = models.RaceReward(
        period_key=key,
        period_starts_at=board["starts_at"],
        period_ends_at=board["ends_at"],
        user_id=pick["author_id"],
        post_id=pick["post_id"],
        like_count=pick["like_count"],
        amount_inr=amount,
        username_snapshot=pick["username"],
        status="payable",
        note=(note or "")[:280],
    )
    db.add(row)
    db.flush()
    return row


def mark_race_paid(db: Session, reward_id: str, note: str = "") -> models.RaceReward:
    row = db.query(models.RaceReward).filter(models.RaceReward.id == reward_id).first()
    if not row:
        raise LookupError("reward_not_found")
    row.status = "paid"
    row.paid_at = _utc_now()
    if note is not None:
        row.note = (note or "").strip()[:280]
    db.flush()
    return row
