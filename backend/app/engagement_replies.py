"""
Official first replies — @baratx + @sharath.

- New user's first Home post → welcome from both (kept), plus content-aware takes.
- Every community post → both accounts reply in a human voice (not twin scripts).
- Official / digest posts are skipped.
- Replies never count toward Founding / Race (official usernames excluded in rewards).

Disable: DISABLE_OFFICIAL_ENGAGE=1
"""

from __future__ import annotations

import logging
import os
import random
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal

logger = logging.getLogger("baratx.engage")

ADMIN_USERNAME = "baratx"
SHARATH_USERNAME = "sharath"
MAX_REPLY_LENGTH = 220
POLL_SECONDS = 45
LOOKBACK_HOURS = 48
BATCH_LIMIT = 25

_TOPIC_CUES: list[tuple[tuple[str, ...], str]] = [
    (("reel", "reels", "instagram", "tiktok", "short form", "shorts"), "reels_speed"),
    (("gen z", "genz", "gen-z", "zoomer"), "genz"),
    (("startup", "founder", "funding", "saas", "pitch"), "startup"),
    (("cricket", "ipl", "world cup", "bcci"), "cricket"),
    (("traffic", "metro", "auto", "ola", "uber", "commute"), "city"),
    (("exam", "jee", "neet", "upsc", "college", "campus"), "campus"),
    (("job", "layoff", "salary", "wfh", "office"), "work"),
    (("election", "vote", "modi", "bjp", "congress", "politics"), "politics"),
    (("ai", "chatgpt", "llm", "robot"), "ai"),
    (("food", "biryani", "chai", "street food"), "food"),
    (("climate", "pollution", "flood", "heatwave"), "climate"),
    (("movie", "bollywood", "tollywood", "cinema", "ott"), "culture"),
]


def _clip(text: str, limit: int = MAX_REPLY_LENGTH) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return (cut or text[: limit - 1]).rstrip(".,;:") + "…"


def _handle(username: str) -> str:
    return f"@{(username or 'friend').lstrip('@')}"


def _snippet(post_text: str, words: int = 8) -> str:
    cleaned = re.sub(r"\s+", " ", (post_text or "").strip())
    cleaned = re.sub(r"[@#]\w+", "", cleaned).strip(" .,!?:;\"'")
    if not cleaned:
        return ""
    parts = cleaned.split()
    if len(parts) <= words:
        return cleaned
    return " ".join(parts[:words]).rstrip(".,") + "…"


def detect_topic(post_text: str) -> str:
    low = (post_text or "").lower()
    for keys, topic in _TOPIC_CUES:
        if any(k in low for k in keys):
            return topic
    if "?" in (post_text or ""):
        return "question"
    return "general"


def _welcome_baratx(username: str, post_text: str) -> str:
    who = _handle(username)
    bit = _snippet(post_text, 6)
    variants = [
        f"Welcome to BarathX, {who}. Glad you’re here — what’s your city, and what should this square never become?",
        f"Hey {who} — welcome. First post landed. Tell us your city; this square runs on real takes, not performance.",
    ]
    if bit:
        variants.append(
            f"Welcome, {who}. That open about “{bit}” is a solid start — stick around and pick a side."
        )
    return _clip(random.choice(variants))


def _welcome_sharath(username: str, post_text: str) -> str:
    who = _handle(username)
    bit = _snippet(post_text, 7)
    variants = [
        f"Hey {who} — Sharath here. Welcome. One real take from your city beats ten perfect posts.",
        f"{who} welcome. I’ll actually read what you write here — keep it honest.",
    ]
    if bit:
        variants.append(
            f"Hey {who} — Sharath. Welcome. You opened with “{bit}” — don’t polish the next one to death."
        )
    return _clip(random.choice(variants))


def _engage_baratx(username: str, post_text: str) -> str:
    who = _handle(username)
    topic = detect_topic(post_text)
    bit = _snippet(post_text, 7)
    by_topic = {
        "reels_speed": [
            f"{who} reels feel fast because the algo rewards the cut, not the thought. Do you miss slower takes, or is speed the point?",
            f"Wild, {who}. Short video trained a generation to decide in 1.5s. Skill… or just twitch?",
        ],
        "genz": [
            f"{who} Gen Z isn’t “fast” — the feed is. What still feels worth slowing down for?",
            f"Fair, {who}. Half of “Gen Z energy” is platforms built like slot machines. Where do you still go deep?",
        ],
        "startup": [
            f"{who} builders talk — what’s the unglamorous part nobody puts on LinkedIn?",
            f"Noted, {who}. Startup India loves the pitch. What’s the boring constraint that actually decides winners?",
        ],
        "cricket": [
            f"{who} cricket takes hit different here. Heat, nostalgia, or Sunday brain?",
            f"Okay {who} — for or against that take? The Square loves a clean split.",
        ],
        "city": [
            f"{who} city problems are the real Square. Which city’s version of this is worse?",
            f"Felt that, {who}. Commute trauma is a national sport. Where are you writing from?",
        ],
        "campus": [
            f"{who} campus pressure is underrated. What would you change first?",
            f"Respect, {who}. Exams vs life — which side are you on today?",
        ],
        "work": [
            f"{who} work takes land hard here. Money, dignity, or both?",
            f"Hmm {who}. Less LinkedIn gloss — what won’t people say out loud?",
        ],
        "politics": [
            f"{who} civic takes welcome — keep it specific. One policy lever you wish more people named?",
            f"Square heard you, {who}. What’s the local version where you live?",
        ],
        "ai": [
            f"{who} AI talk is everywhere. Tool for you, or watching it flatten the voice?",
            f"Fair, {who}. Human takes only here — where do you still want the messy version?",
        ],
        "food": [
            f"{who} food takes are undefeated. Name the city and the dish — we’ll take sides.",
            f"Okay {who}, you’ve started something. Best plate this month?",
        ],
        "climate": [
            f"{who} climate hits different when it’s your street. What are you seeing locally?",
            f"Heavy, {who}. One fix your city could do this year that isn’t a slogan?",
        ],
        "culture": [
            f"{who} culture keeps the Square awake. Hot take or soft take?",
            f"Saw that, {who}. Would you defend it out loud to your friends?",
        ],
        "question": [
            f"Good question, {who}. Curious what answers you get from people living it.",
            f"{who} asking the right thing. What’s your own answer before the room piles on?",
        ],
        "general": [
            f"Heard, {who}. Real take — what’s the version from your city?",
            f"{who} solid open. Who disagrees with you hardest?",
            f"Okay {who}, listening. What made you post this today?",
        ],
    }
    pool = list(by_topic.get(topic, by_topic["general"]))
    if bit and topic in ("general", "question"):
        pool.append(f"{who} “{bit}” — say more. What’s the part you almost deleted?")
    return _clip(random.choice(pool))


def _engage_sharath(username: str, post_text: str) -> str:
    who = _handle(username)
    topic = detect_topic(post_text)
    bit = _snippet(post_text, 7)
    by_topic = {
        "reels_speed": [
            f"{who} I don’t think reels made Gen Z fast — boredom did. Attention got farmed. You feel that too?",
            f"Sharath here — {who}, the scary part isn’t speed, it’s how rarely we finish a thought. Defend the reel era for me.",
        ],
        "genz": [
            f"{who} Gen Z gets roasted for pace, but millennials invented the scroll. What does your lot do better?",
            f"Real talk {who}: “fast” is marketing. Who around you still goes deep?",
        ],
        "startup": [
            f"{who} honest founders sound like this. What’s broken in your world right now?",
            f"{who} builders energy. ₹150 and one week — what would you ship?",
        ],
        "cricket": [
            f"{who} cricket arguments are peak India. Who’s actually wrong in your view?",
            f"Haha {who}. Quiet part: cricket or ego?",
        ],
        "city": [
            f"{who} city takes > national slogans. Paint the street you’re on.",
            f"{who} if your city’s CM read this, what one line should scare them?",
        ],
        "campus": [
            f"{who} campus India is a pressure cooker with wifi. What should adults stop pretending?",
            f"Listening, {who}. Would you tell a younger sibling the same thing?",
        ],
        "work": [
            f"{who} work chat without HR language — rare. What would you quit if money wasn’t the issue?",
            f"Felt that, {who}. Dignity > title. Agree, or am I soft?",
        ],
        "politics": [
            f"{who} party labels are easy, mechanisms are hard. What’s the mechanism?",
            f"I’m in, {who}. Local proof > TV panel. Example from your state?",
        ],
        "ai": [
            f"{who} if AI writes the take, the Square dies. What’s the human part only you can add?",
            f"Sharath — {who}, allergic to AI slop. Your line felt human. More of that.",
        ],
        "food": [
            f"{who} don’t start a food war unless you’re ready. Pick a city side.",
            f"Okay {who}, aftertaste review — overrated or underrated?",
        ],
        "climate": [
            f"{who} climate without guilt-trip — what are you seeing with your own eyes?",
            f"Heavy, {who}. One fix that isn’t “awareness”?",
        ],
        "culture": [
            f"{who} culture takes reveal the person. Nostalgia or calling a bluff?",
            f"Hooked, {who}. What’s the unpopular half of that opinion?",
        ],
        "question": [
            f"{who} I’ll answer after you do — gut answer in one line?",
            f"Good prompt, {who}. My bias: people move fast when the platform pays for speed. You?",
        ],
        "general": [
            f"Sharath here — {who}, that landed. What’s the next sentence you didn’t type?",
            f"{who} don’t leave it at the headline. Give me the uncomfortable detail.",
            f"Reading you, {who}. Who should disagree with this — the vibe, not a person.",
        ],
    }
    pool = list(by_topic.get(topic, by_topic["general"]))
    if bit:
        pool.append(f"{who} sitting with “{bit}”. Push back if I’m reading it wrong.")
    return _clip(random.choice(pool))


def _official_pair(db: Session) -> tuple[Optional[models.User], Optional[models.User]]:
    rows = (
        db.query(models.User)
        .filter(models.User.username.in_((ADMIN_USERNAME, SHARATH_USERNAME)))
        .all()
    )
    by = {u.username: u for u in rows}
    admin = by.get(ADMIN_USERNAME)
    sharath = by.get(SHARATH_USERNAME)
    for u in (admin, sharath):
        if u is not None and not getattr(u, "is_official", False):
            u.is_official = True
    return admin, sharath


def _author_is_official(user: Optional[models.User]) -> bool:
    """Seeded platform accounts only — blue/gold members still get engagement."""
    if not user:
        return True
    return (user.username or "").lower() in {
        ADMIN_USERNAME,
        SHARATH_USERNAME,
        "bharatvoices",
        "indiatech",
    }


def _reply_count(db: Session, post_id: str, author_id: str) -> int:
    return (
        db.query(models.Reply.id)
        .filter(models.Reply.post_id == post_id, models.Reply.author_id == author_id)
        .count()
    )


def _add_reply(
    db: Session,
    *,
    post: models.Post,
    official: models.User,
    text: str,
    recipient_id: str,
    create_notification,
    allow_second: bool = False,
) -> Optional[models.Reply]:
    if not text or official.id == recipient_id:
        return None
    count = _reply_count(db, post.id, official.id)
    if count >= 1 and not allow_second:
        return None
    if count >= 2:
        return None
    reply = models.Reply(
        post_id=post.id,
        author_id=official.id,
        text=_clip(text),
        parent_reply_id=None,
    )
    db.add(reply)
    db.flush()
    if create_notification:
        create_notification(
            db,
            recipient_id=recipient_id,
            actor_id=official.id,
            kind="reply",
            post_id=post.id,
            reply_id=reply.id,
        )
    return reply


def engage_on_new_post(
    db: Session,
    *,
    post: models.Post,
    author: models.User,
    is_first_post: bool,
    create_notification,
) -> dict:
    """
    First post: welcome from @baratx + @sharath, then content replies from both.
    Later posts: content replies from both.
    Idempotent for the poller (won't duplicate beyond welcome+engage caps).
    """
    if os.environ.get("DISABLE_OFFICIAL_ENGAGE", "").strip().lower() in ("1", "true", "yes"):
        return {"ok": True, "skipped": True, "reason": "disabled"}

    if _author_is_official(author):
        return {"ok": True, "skipped": True, "reason": "official_author"}

    text = (post.text or "").strip()
    if len(text) < 2:
        return {"ok": True, "skipped": True, "reason": "empty"}

    admin, sharath = _official_pair(db)
    created: list[str] = []

    if is_first_post:
        if admin:
            r = _add_reply(
                db,
                post=post,
                official=admin,
                text=_welcome_baratx(author.username, text),
                recipient_id=author.id,
                create_notification=create_notification,
            )
            if r:
                created.append("baratx_welcome")
        if sharath:
            r = _add_reply(
                db,
                post=post,
                official=sharath,
                text=_welcome_sharath(author.username, text),
                recipient_id=author.id,
                create_notification=create_notification,
            )
            if r:
                created.append("sharath_welcome")

    # Content replies on ALL posts (including first) — second beat after welcome.
    if admin:
        r = _add_reply(
            db,
            post=post,
            official=admin,
            text=_engage_baratx(author.username, text),
            recipient_id=author.id,
            create_notification=create_notification,
            allow_second=is_first_post,
        )
        if r:
            created.append("baratx_engage")
    if sharath:
        r = _add_reply(
            db,
            post=post,
            official=sharath,
            text=_engage_sharath(author.username, text),
            recipient_id=author.id,
            create_notification=create_notification,
            allow_second=is_first_post,
        )
        if r:
            created.append("sharath_engage")

    return {
        "ok": True,
        "created": created,
        "topic": detect_topic(text),
        "first": is_first_post,
    }


def backfill_missing_replies(db: Session, *, create_notification, limit: int = BATCH_LIMIT) -> dict:
    """Monitor recent community posts missing official replies and fill them."""
    if os.environ.get("DISABLE_OFFICIAL_ENGAGE", "").strip().lower() in ("1", "true", "yes"):
        return {"ok": True, "skipped": True, "reason": "disabled"}

    admin, sharath = _official_pair(db)
    if not admin or not sharath:
        return {"ok": False, "error": "officials_missing"}

    since = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    posts = (
        db.query(models.Post)
        .join(models.User, models.User.id == models.Post.author_id)
        .filter(models.Post.created_at >= since)
        .filter(
            ~models.User.username.in_(
                (ADMIN_USERNAME, SHARATH_USERNAME, "bharatvoices", "indiatech")
            )
        )
        .order_by(models.Post.created_at.desc())
        .limit(limit * 3)
        .all()
    )

    touched = 0
    for post in posts:
        author = post.author
        if _author_is_official(author):
            continue
        admin_n = _reply_count(db, post.id, admin.id)
        sharath_n = _reply_count(db, post.id, sharath.id)
        # Prefer lifetime flag; fall back to "no other posts" for legacy rows.
        has_once = bool(getattr(author, "has_posted_once", False))
        prior = (
            db.query(models.Post.id)
            .filter(models.Post.author_id == author.id, models.Post.id != post.id)
            .limit(1)
            .first()
        )
        if prior is not None and not has_once:
            author.has_posted_once = True
            has_once = True
        # True first post only when the account has never completed a post before.
        is_first = not has_once
        # First posts need up to 2 each (welcome + engage); others need 1 each.
        need = (is_first and (admin_n < 2 or sharath_n < 2)) or (
            not is_first and (admin_n < 1 or sharath_n < 1)
        )
        if not need:
            continue

        engage_on_new_post(
            db,
            post=post,
            author=author,
            is_first_post=is_first,
            create_notification=create_notification,
        )
        touched += 1
        if touched >= limit:
            break

    if touched:
        db.commit()
    return {"ok": True, "engaged_posts": touched}


_scheduler_started = False


def start_engagement_scheduler(*, create_notification) -> None:
    global _scheduler_started
    if _scheduler_started:
        return
    if os.environ.get("DISABLE_OFFICIAL_ENGAGE", "").strip().lower() in ("1", "true", "yes"):
        logger.info("Official engage scheduler disabled via DISABLE_OFFICIAL_ENGAGE")
        return

    def loop() -> None:
        time.sleep(12)
        while True:
            try:
                db = SessionLocal()
                try:
                    res = backfill_missing_replies(db, create_notification=create_notification)
                    if res.get("engaged_posts"):
                        logger.info("Official engage backfill: %s", res)
                finally:
                    db.close()
            except Exception:  # noqa: BLE001
                logger.exception("Official engage poll failed")
            time.sleep(POLL_SECONDS)

    threading.Thread(target=loop, name="baratx-official-engage", daemon=True).start()
    _scheduler_started = True
    logger.info("Official engage scheduler started (every %ss)", POLL_SECONDS)
