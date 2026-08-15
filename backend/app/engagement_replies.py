"""
Official first replies — @baratx + @sharath.

Rules (anti-slop):
- Read the post. Answer *that* post — not a recycled “say more / uncomfortable detail” line.
- Every community post gets BOTH @baratx and @sharath (two distinct human voices).
- Feedback → “we’ve taken it / next release” + follow IG/X/WhatsApp for what’s shipping.
- Bug / product reports → support tone (“where are you seeing that?”), never philosophy.
- Replies never count toward Founding / Race (official usernames excluded in rewards).

Disable: default OFF. Opt in with ENABLE_OFFICIAL_ENGAGE=1 (or set DISABLE_OFFICIAL_ENGAGE=1 to force off).
Purge old slop: POST /admin/engage/purge-slop (ops) or PURGE_ENGAGE_SLOP_ON_BOOT=1
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


def engage_disabled() -> bool:
    """
    Official template auto-replies are OFF by default (felt like bot spam).
    Opt in with ENABLE_OFFICIAL_ENGAGE=1. DISABLE_OFFICIAL_ENGAGE=1 also forces off.
    """
    if os.environ.get("DISABLE_OFFICIAL_ENGAGE", "").strip().lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("ENABLE_OFFICIAL_ENGAGE", "").strip().lower() in ("1", "true", "yes"):
        return False
    return True

# Phrases from the old template bot — used to purge + never regenerate.
SLOP_PHRASES = (
    "almost deleted",
    "uncomfortable detail",
    "don’t leave it at the headline",
    "don't leave it at the headline",
    "say more. what’s the part",
    "say more. what's the part",
    "sitting with “",
    "sitting with \"",
    "who disagrees with you hardest",
    "next sentence you didn’t type",
    "next sentence you didn't type",
    "real take — what’s the version from your city",
    "real take - what's the version from your city",
    "who should disagree with this — the vibe",
    "drop one real take from your city",
    "i’ll read the replies",
    "stick around and pick a side",
    "don’t polish the next one to death",
    "builders energy. ₹150",
)

_TOPIC_CUES: list[tuple[tuple[str, ...], str]] = [
    (
        (
            "feedback",
            "suggestion",
            "feature request",
            "please add",
            "pls add",
            "wishlist",
            "should add",
            "you should add",
            "next release",
            "next update",
            "i suggest",
            "improve the app",
            "improve this",
            "can you add",
            "would be nice if",
        ),
        "feedback",
    ),
    (
        (
            "audio",
            "mic",
            "unmute",
            "mute",
            "speaker",
            "can't hear",
            "cant hear",
            "cannot hear",
            "not hearing",
            "no sound",
            "sound not",
            "video not",
            "camera",
            "not working",
            "not coming",
            "isn't working",
            "isnt working",
            "broken",
            "bug",
            "glitch",
            "crash",
            "error",
            "lag",
            "freeze",
            "live talk",
            "live conversation",
            "can't join",
            "cant join",
            "won't load",
            "wont load",
        ),
        "support",
    ),
    (
        (
            "geopolitics",
            "indo-pacific",
            "foreign affairs",
            "border dispute",
            "ukraine",
            "gaza",
            "middle east",
            "nato",
            "quad alliance",
            "brics",
        ),
        "geopolitics",
    ),
    (("reel", "reels", "instagram", "tiktok", "short form", "shorts"), "reels_speed"),
    (("gen z", "genz", "gen-z", "zoomer"), "genz"),
    (("startup", "founder", "funding", "saas", "pitch"), "startup"),
    (("cricket", "ipl", "world cup", "bcci"), "cricket"),
    (("traffic", "metro", "auto", "ola", "uber", "commute"), "city"),
    (("exam", "jee", "neet", "upsc", "college", "campus"), "campus"),
    (("job", "layoff", "salary", "wfh", "office"), "work"),
    (("election", "vote", "modi", "bjp", "congress", "politics"), "politics"),
    (("ai", "chatgpt", "llm", "robot", "ai slop"), "ai"),
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


def _word_count(post_text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", post_text or ""))


def detect_topic(post_text: str) -> str:
    low = (post_text or "").lower()
    for keys, topic in _TOPIC_CUES:
        if any(k in low for k in keys):
            return topic
    if _word_count(post_text) <= 6:
        return "short"
    if "?" in (post_text or ""):
        return "question"
    return "general"


def _looks_like_slop(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in SLOP_PHRASES)


def _welcome_baratx(username: str, post_text: str) -> str:
    who = _handle(username)
    bit = _snippet(post_text, 6)
    topic = detect_topic(post_text)
    if topic == "feedback":
        return _engage_feedback(username, post_text, voice="baratx")
    if topic == "support":
        return _clip(
            f"Hey {who} — thanks for flagging this. Where are you seeing it (Live room, phone/desktop), "
            f"and did unmute ask for mic permission?"
        )
    variants = [
        f"Hey {who} — welcome. What’s your city?",
        f"Welcome {who}. Glad you’re here — what’s one thing you want this square to stay honest about?",
    ]
    if bit and topic != "short":
        variants.append(f"Welcome {who}. Caught “{bit}” — curious what you meant by that.")
    return _clip(random.choice(variants))


def _welcome_sharath(username: str, post_text: str) -> str:
    who = _handle(username)
    topic = detect_topic(post_text)
    if topic == "feedback":
        return _engage_feedback(username, post_text, voice="sharath")
    if topic == "support":
        return _clip(
            f"Hey {who}, Sharath here — sorry that’s broken for you. Browser + phone or laptop? "
            f"I’ll dig if you drop one more detail."
        )
    variants = [
        f"Hey {who} — Sharath. Welcome. Tell me your city.",
        f"{who} welcome. Write like you talk — that’s the whole point here.",
    ]
    return _clip(random.choice(variants))


def _engage_feedback(username: str, post_text: str, *, voice: str) -> str:
    """Product feedback — acknowledge + next release + where to follow shipping notes."""
    who = _handle(username)
    if voice == "sharath":
        pool = [
            f"{who} Sharath here — logged. Follow what we’re shipping: IG & X @getbaratx · "
            f"WhatsApp community via barathx.com",
            f"Got it {who}. Stay close for the next release — @getbaratx on IG/X + WhatsApp on barathx.com",
        ]
    else:
        pool = [
            f"Hey {who} — we’ve taken your feedback. We’ll fix this in the next release. Thank you.",
            f"Thanks {who}. Feedback noted — targeting a fix in the next release. Appreciate you posting it.",
        ]
    return _clip(random.choice(pool))


def _engage_support(username: str, post_text: str, *, voice: str) -> str:
    """Product / bug reports — sound like a person on support, not a growth bot."""
    who = _handle(username)
    low = (post_text or "").lower()
    bit = _snippet(post_text, 8) or "that"
    if any(k in low for k in ("audio", "mic", "unmute", "sound", "hear", "speaker")):
        pool = [
            f"Hey {who} — audio’s dead for you too? Live room or somewhere else, and mic permission on?",
            f"{who} ugh, that’s annoying. After you hit Unmute, does the browser ask for mic? "
            f"What device are you on?",
            f"Got it {who} — “{bit}”. Can you hear others, or is it both ways? Phone or desktop?",
        ]
    elif any(k in low for k in ("video", "camera")):
        pool = [
            f"Hey {who} — camera acting up? Did the browser block camera permission, or is the button grey?",
            f"{who} on video: phone or laptop, and Chrome/Safari? I’ll try to reproduce.",
        ]
    elif any(k in low for k in ("crash", "freeze", "lag", "error", "bug", "glitch", "broken", "not working", "not coming")):
        pool = [
            f"Hey {who} — sorry that’s busted. What were you doing right before it happened?",
            f"{who} thanks for the report. Phone/desktop + roughly when — so we can chase it.",
        ]
    else:
        pool = [
            f"Hey {who} — sounds like something’s off. What exactly are you stuck on?",
            f"{who} got it. One more detail so we can fix it — screen + what you tapped?",
        ]
    if voice == "sharath":
        pool.append(
            f"{who} Sharath here — yeah that’s not okay. Drop device + step and I’ll look."
        )
    return _clip(random.choice(pool))


def _engage_short(username: str, post_text: str, *, voice: str) -> str:
    who = _handle(username)
    bit = _snippet(post_text, 10) or "that"
    pool = [
        f"Hey {who} — what do you mean by “{bit}”? Where are you seeing it?",
        f"{who} got your note. Can you add one line — what broke / what you expected?",
        f"Hmm {who}, thin on detail. Phone or desktop, and which screen?",
    ]
    if voice == "sharath":
        pool.append(f"{who} say more in plain words — what happened?")
    return _clip(random.choice(pool))


def _engage_baratx(username: str, post_text: str) -> str:
    who = _handle(username)
    topic = detect_topic(post_text)
    bit = _snippet(post_text, 7)
    if topic == "feedback":
        return _engage_feedback(username, post_text, voice="baratx")
    if topic == "support":
        return _engage_support(username, post_text, voice="baratx")
    if topic == "short":
        return _engage_short(username, post_text, voice="baratx")

    by_topic = {
        "geopolitics": [
            f"{who} geopolitics is loud — what’s the India stake in that story?",
            f"Okay {who}. Neighbour, trade, or great-power game — which lens are you using?",
        ],
        "reels_speed": [
            f"{who} reels vs a real argument — which one do you trust more with your own time?",
            f"Ha {who}. Do you still finish thoughts, or has the feed trained that out?",
        ],
        "genz": [
            f"{who} fair. What’s one place you still go slow on purpose?",
            f"{who} “Gen Z is fast” is half marketing. What does your crowd actually care about?",
        ],
        "startup": [
            f"{who} what’s the boring part of that idea that usually kills it?",
            f"Noted {who}. Who’s the customer in one sentence — not the pitch deck version?",
        ],
        "cricket": [
            f"{who} for or against — clean side. Why?",
            f"Okay {who}, who’s actually wrong in that take?",
        ],
        "city": [
            f"{who} which city, and what’s the street-level version of that?",
            f"Felt that {who}. Commute or civic — which one are you mad about today?",
        ],
        "campus": [
            f"{who} campus pressure hits different. What would you change first?",
            f"Respect {who}. Exam grind or life admin — which is worse right now?",
        ],
        "work": [
            f"{who} money, dignity, or both — which bit is the post really about?",
            f"Hmm {who}. What won’t people say out loud at work about this?",
        ],
        "politics": [
            f"{who} keep it concrete — one policy or local example?",
            f"Square heard you {who}. What’s the version where you live?",
        ],
        "ai": [
            f"{who} we don’t want AI slop here. What’s the human bit only you can add?",
            f"Fair {who}. Tool for you, or is it flattening how people talk?",
        ],
        "food": [
            f"{who} name the city and the dish — then we can actually fight about it.",
            f"Okay {who}, best plate this month?",
        ],
        "climate": [
            f"{who} what are you seeing on your street, not the headline?",
            f"Heavy {who}. One local fix that isn’t a slogan?",
        ],
        "culture": [
            f"{who} hot take or soft take — which are you claiming?",
            f"Saw that {who}. Would you say it the same way to friends IRL?",
        ],
        "question": [
            f"Good question {who}. What’s your own answer before the room piles on?",
            f"{who} curious — who do you most want an answer from?",
        ],
        "general": [
            f"Hey {who} — what’s the bit you care about most in that?",
            f"{who} okay, listening. What made you post it today?",
            f"Got you {who}. Who around you would push back on that?",
        ],
    }
    pool = list(by_topic.get(topic, by_topic["general"]))
    if bit and topic in ("general", "question") and len(bit) > 3:
        pool.append(f"{who} on “{bit}” — what happened right before you typed that?")
    text = _clip(random.choice(pool))
    # Never ship the old slop even if someone reintroduces a phrase.
    if _looks_like_slop(text):
        text = _clip(f"Hey {who} — what’s going on, in one plain sentence?")
    return text


def _engage_sharath(username: str, post_text: str) -> str:
    who = _handle(username)
    topic = detect_topic(post_text)
    bit = _snippet(post_text, 7)
    if topic == "feedback":
        return _engage_feedback(username, post_text, voice="sharath")
    if topic == "support":
        return _engage_support(username, post_text, voice="sharath")
    if topic == "short":
        return _engage_short(username, post_text, voice="sharath")

    by_topic = {
        "geopolitics": [
            f"{who} Sharath — skip the cable-TV heat. What’s the real Indian interest here?",
            f"{who} fair. Who benefits if India stays quiet on that?",
        ],
        "reels_speed": [
            f"{who} I think boredom got farmed, not just “Gen Z speed”. You feel that?",
            f"Sharath — {who}, defend the reel era for me in one line.",
        ],
        "genz": [
            f"{who} millennials invented the scroll. What does your lot do better?",
            f"Real talk {who}: who around you still goes deep?",
        ],
        "startup": [
            f"{who} what’s broken in your world right now — not the LinkedIn version?",
            f"{who} if you had a week and no slides, what would you ship?",
        ],
        "cricket": [
            f"{who} peak India argument. Who’s wrong?",
            f"Haha {who}. Cricket or ego — honest answer?",
        ],
        "city": [
            f"{who} paint the street you’re on. National slogans can wait.",
            f"{who} if your CM read this, what one line should sting?",
        ],
        "campus": [
            f"{who} what should adults stop pretending about campus?",
            f"Listening {who}. Would you tell a younger sibling the same thing?",
        ],
        "work": [
            f"{who} what would you quit if money wasn’t the issue?",
            f"Felt that {who}. Dignity over title — agree, or am I soft?",
        ],
        "politics": [
            f"{who} party labels are easy. What’s the mechanism?",
            f"I’m in {who}. Local proof from your state?",
        ],
        "ai": [
            f"{who} if a bot writes the take, this place dies. What’s only you can add?",
            f"Sharath — {who}, allergic to AI slop. Keep it messy and human.",
        ],
        "food": [
            f"{who} pick a city side if you’re starting a food fight.",
            f"Okay {who}, overrated or underrated?",
        ],
        "climate": [
            f"{who} what are you seeing with your own eyes?",
            f"Heavy {who}. One fix that isn’t “awareness”?",
        ],
        "culture": [
            f"{who} nostalgia or calling a bluff?",
            f"Hooked {who}. What’s the unpopular half?",
        ],
        "question": [
            f"{who} gut answer in one line first — then I’ll pile on.",
            f"Good prompt {who}. My bias: platforms pay for speed. Yours?",
        ],
        "general": [
            f"Sharath here — {who}, that landed. What are you actually asking for?",
            f"Reading you {who}. What should someone do after reading this?",
            f"{who} plain words — what happened?",
        ],
    }
    pool = list(by_topic.get(topic, by_topic["general"]))
    if bit and topic not in ("support", "short"):
        pool.append(f"{who} re: “{bit}” — am I reading that right?")
    text = _clip(random.choice(pool))
    if _looks_like_slop(text):
        text = _clip(f"{who} Sharath — say that again with one more concrete detail?")
    return text


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


def _official_reply_count(db: Session, post_id: str, official_ids: list[str]) -> int:
    if not official_ids:
        return 0
    return (
        db.query(models.Reply.id)
        .filter(models.Reply.post_id == post_id, models.Reply.author_id.in_(official_ids))
        .count()
    )


def _pick_voice(
    admin: Optional[models.User],
    sharath: Optional[models.User],
    topic: str,
) -> Optional[models.User]:
    """One human voice per post — product bugs → @baratx, else either."""
    if topic == "support" and admin:
        return admin
    choices = [u for u in (admin, sharath) if u is not None]
    if not choices:
        return None
    return random.choice(choices)


def _add_reply(
    db: Session,
    *,
    post: models.Post,
    official: models.User,
    text: str,
    recipient_id: str,
    create_notification,
) -> Optional[models.Reply]:
    if not text or official.id == recipient_id:
        return None
    if _looks_like_slop(text):
        logger.warning("Blocked slop reply for post %s", post.id)
        return None
    # Cap: at most one reply per official account per post
    if _reply_count(db, post.id, official.id) >= 1:
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
    Both @baratx and @sharath reply on every community post (distinct copy).
    Idempotent for the poller — fills any missing official voice.
    """
    if engage_disabled():
        return {"ok": True, "skipped": True, "reason": "disabled"}

    if _author_is_official(author):
        return {"ok": True, "skipped": True, "reason": "official_author"}

    text = (post.text or "").strip()
    if len(text) < 2:
        return {"ok": True, "skipped": True, "reason": "empty"}

    admin, sharath = _official_pair(db)
    voices = [u for u in (admin, sharath) if u is not None]
    if not voices:
        return {"ok": False, "error": "officials_missing"}

    topic = detect_topic(text)
    # Support bugs → @baratx first in the list; still both reply.
    if topic == "support" and admin and sharath:
        voices = [admin, sharath]

    created: list[str] = []
    for voice in voices:
        if _reply_count(db, post.id, voice.id) >= 1:
            continue
        if is_first_post:
            body = (
                _welcome_baratx(author.username, text)
                if voice.username == ADMIN_USERNAME
                else _welcome_sharath(author.username, text)
            )
            tag = f"{voice.username}_welcome"
        else:
            body = (
                _engage_baratx(author.username, text)
                if voice.username == ADMIN_USERNAME
                else _engage_sharath(author.username, text)
            )
            tag = f"{voice.username}_engage"
        r = _add_reply(
            db,
            post=post,
            official=voice,
            text=body,
            recipient_id=author.id,
            create_notification=create_notification,
        )
        if r:
            created.append(tag)

    if not created:
        return {"ok": True, "skipped": True, "reason": "already_engaged", "topic": topic}

    return {
        "ok": True,
        "created": created,
        "topic": topic,
        "first": is_first_post,
        "voices": [v.username for v in voices],
    }


def purge_engage_slop_replies(db: Session, *, only_slop_phrases: bool = False) -> dict:
    """
    Delete auto-engage replies from @baratx / @sharath.

    Default: wipe all replies by those accounts (they were almost entirely auto-engage;
    digests are posts, not replies). Set only_slop_phrases=True to delete phrase matches only.
    Also clears reply likes + notifications pointing at those replies.
    """
    officials = (
        db.query(models.User)
        .filter(models.User.username.in_((ADMIN_USERNAME, SHARATH_USERNAME)))
        .all()
    )
    if not officials:
        return {"ok": False, "error": "officials_missing", "deleted": 0}
    ids = [u.id for u in officials]
    q = db.query(models.Reply).filter(models.Reply.author_id.in_(ids))
    rows = q.all()
    to_delete: list[models.Reply] = []
    for row in rows:
        if only_slop_phrases and not _looks_like_slop(row.text or ""):
            continue
        to_delete.append(row)

    deleted = 0
    for row in to_delete:
        rid = row.id
        db.query(models.ReplyLike).filter(models.ReplyLike.reply_id == rid).delete(
            synchronize_session=False
        )
        db.query(models.Notification).filter(models.Notification.reply_id == rid).delete(
            synchronize_session=False
        )
        # Nested replies pointing at this as parent
        db.query(models.Reply).filter(models.Reply.parent_reply_id == rid).update(
            {models.Reply.parent_reply_id: None},
            synchronize_session=False,
        )
        db.delete(row)
        deleted += 1
    if deleted:
        db.commit()
    logger.info("Purged %s official engage replies (only_slop=%s)", deleted, only_slop_phrases)
    return {"ok": True, "deleted": deleted, "only_slop_phrases": only_slop_phrases}


def backfill_missing_replies(db: Session, *, create_notification, limit: int = BATCH_LIMIT) -> dict:
    """Monitor recent community posts missing official replies and fill them."""
    if engage_disabled():
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

    official_ids = [admin.id, sharath.id]
    touched = 0
    for post in posts:
        author = post.author
        if _author_is_official(author):
            continue
        if _official_reply_count(db, post.id, official_ids) >= 1:
            continue

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
        is_first = not has_once

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
_boot_purge_done = False


def start_engagement_scheduler(*, create_notification) -> None:
    global _scheduler_started, _boot_purge_done
    if _scheduler_started:
        return
    if engage_disabled():
        logger.info(
            "Official engage scheduler OFF by default "
            "(set ENABLE_OFFICIAL_ENGAGE=1 to opt in)"
        )
        return

    def loop() -> None:
        global _boot_purge_done
        time.sleep(12)
        while True:
            try:
                db = SessionLocal()
                try:
                    # One-shot cleanup of twin-bot / slop replies (default on; set PURGE_ENGAGE_SLOP_ON_BOOT=0 to skip)
                    if not _boot_purge_done:
                        flag = os.environ.get("PURGE_ENGAGE_SLOP_ON_BOOT", "1").strip().lower()
                        if flag not in ("0", "false", "no"):
                            res = purge_engage_slop_replies(db, only_slop_phrases=False)
                            logger.info("Boot purge of official engage replies: %s", res)
                        _boot_purge_done = True
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
