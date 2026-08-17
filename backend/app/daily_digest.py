"""Daily peak digest, credible arena glimpses + @baratx / @sharath engagement.

Posts only at 3 IST peak windows (morning / midday / evening):
  1) @baratx posts a news glimpse (credible sources only)
  2) @sharath posts a response take on the same story
  3) @sharath replies on the admin post; @baratx replies on Sharath's post
  4) Mutual likes on both posts and both replies

We never invent facts beyond the headline + named publisher.
"""

from __future__ import annotations

import hashlib
import io
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app import media_store, models, rss
from app.topics_data import ACTIVE_ARENA_KEYS, TOPICS_BY_ARENA

logger = logging.getLogger("baratx.daily_digest")

IST = ZoneInfo("Asia/Kolkata")

ADMIN_USERNAME = "baratx"
SHARATH_USERNAME = "sharath"
DIGEST_AUTHORS = (ADMIN_USERNAME, SHARATH_USERNAME)

# Three peak windows, do not spray the feed all day.
PEAK_SLOTS = (
    (9, 0, "morning"),
    (13, 30, "midday"),
    (20, 0, "evening"),
)
SLOT_MARKERS = {
    "morning": "#BXMorning",
    "midday": "#BXMidday",
    "evening": "#BXEvening",
}
POST_MARKER = "#BarathXDaily"

# Per peak slot: one dense arena first (Startups-weighted), avoid six thin empty rooms.
ARENAS_PER_SLOT = 1
# Soft floors for headline selection (tests + collector).
MIN_POSTS_IF_QUALITY = 2
MAX_POSTS_PER_DAY = 6  # 3 slots × 1 arena × 2 voices
MAX_POSTS_PER_ARENA = 2
MAX_POSTS_PER_AUTHOR = 6
MIN_SCORE_TO_POST = 12.0

ARENA_WEIGHT = {
    "startups": 3.5,  # densify builders first (audit niche decision)
    "politics": 1.5,
    "news": 1.2,
    "sports": 0.8,
    "entertainment": 0.4,
    "spirituality": 0.6,
}

# Prefer press / wire / named desk queries, then filter by credible publisher.
ARENA_TRENDING_QUERIES = {
    "sports": "India sports news today PTI OR ANI OR The Hindu",
    "politics": "India politics Parliament press conference PIB OR PTI",
    "entertainment": "Bollywood entertainment news India The Hindu OR Indian Express",
    "news": "India breaking news today PTI OR Reuters OR PIB",
    "spirituality": "India temple festival spirituality news The Hindu",
    "startups": "India startup funding Economic Times OR LiveMint OR Inc42 OR PIB",
}

BRAND_ORANGE = (255, 103, 31)
BRAND_NAVY = (15, 23, 42)
BRAND_CREAM = (255, 248, 242)
BRAND_WHITE = (255, 255, 255)

_MOTTO_BOOST = (
    "india",
    "bharat",
    "delhi",
    "mumbai",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
    "kolkata",
    "pune",
    "modi",
    "parliament",
    "lok sabha",
    "election",
    "supreme court",
    "policy",
    "budget",
    "gst",
    "startup",
    "funding",
    "unicorn",
    "isro",
    "ipl",
    "cricket",
    "press conference",
    "pib",
    "minister",
)
_SOFT_PENALTY = (
    "tips to",
    "in pictures",
    "horoscope",
    "zodiac",
    "best of",
    "viral video",
    "you won't believe",
    "click here",
    "netflix top",
    "recipe",
    "weight loss",
    "rumour",
    "rumor",
    "allegedly unconfirmed",
)


def _today_ist() -> datetime.date:
    return datetime.now(IST).date()


def _wrap(text: str, width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if len(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _score_headline(title: str, arena: str = "", *, credible: bool = False) -> float:
    """Higher = more post-worthy. Credible publishers get a hard boost."""
    t = (title or "").strip()
    if len(t) < 28:
        return 0.0
    score = 10.0
    if 40 <= len(t) <= 110:
        score += 8
    elif len(t) > 140:
        score -= 4
    low = t.lower()
    for kw in _MOTTO_BOOST:
        if kw in low:
            score += 2.2
    for bad in _SOFT_PENALTY:
        if bad in low:
            score -= 8
    if "?" in t:
        score += 2
    for cue in ("should", "why", "vs", "versus", "debate", "controversy", "row over", "slams"):
        if cue in low:
            score += 1.5
    score += ARENA_WEIGHT.get(arena, 0.0)
    if credible:
        score += 10.0
    else:
        score -= 6.0  # prefer named desks; unknown sources rarely clear the bar
    return score


def _already_posted_similar(db: Session, author_id: str, title: str) -> bool:
    key = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()[:60]
    if not key:
        return True
    since = datetime.now(timezone.utc) - timedelta(days=5)
    rows = (
        db.query(models.Post)
        .filter(models.Post.author_id == author_id, models.Post.created_at >= since)
        .all()
    )
    for p in rows:
        blob = re.sub(r"[^a-z0-9]+", " ", (p.text or "").lower())
        if key[:40] in blob:
            return True
    return False


def posts_today_count(db: Session, author_id: Optional[str] = None, *, slot: str | None = None) -> int:
    start = datetime.combine(_today_ist(), datetime.min.time(), tzinfo=IST).astimezone(
        timezone.utc
    )
    q = db.query(models.Post).filter(
        models.Post.created_at >= start,
        models.Post.text.contains(POST_MARKER),
    )
    if author_id:
        q = q.filter(models.Post.author_id == author_id)
    if slot:
        marker = SLOT_MARKERS.get(slot)
        if marker:
            q = q.filter(models.Post.text.contains(marker))
    return q.count()


def arenas_for_slot(slot: str) -> list[str]:
    """Rotate arenas across peak slots so every floor gets daily coverage."""
    arenas = sorted(ACTIVE_ARENA_KEYS)
    if not arenas:
        return []
    day = _today_ist().toordinal()
    slot_idx = {"morning": 0, "midday": 1, "evening": 2}.get(slot, 0)
    start = (day + slot_idx * ARENAS_PER_SLOT) % len(arenas)
    picked = []
    for i in range(min(ARENAS_PER_SLOT, len(arenas))):
        picked.append(arenas[(start + i) % len(arenas)])
    return picked


def collect_candidates(db: Session, *, per_arena: int = 6, arenas: list[str] | None = None) -> list[dict]:
    """Scan arenas for credible headlines only."""
    day = _today_ist().toordinal()
    candidates: list[dict] = []
    arena_list = arenas or sorted(ACTIVE_ARENA_KEYS)

    for arena in arena_list:
        query = ARENA_TRENDING_QUERIES.get(arena) or f"India {arena} news PTI OR The Hindu"
        for item in rss.fetch_rss_items(query, limit=per_arena, credible_only=True):
            title = item.get("title") or ""
            score = _score_headline(title, arena, credible=bool(item.get("credible")))
            if score < 8:
                continue
            candidates.append(
                {
                    "title": title,
                    "link": item.get("link") or "",
                    "source": item.get("source") or "",
                    "arena": arena,
                    "topic": arena,
                    "score": score,
                    "query": query,
                    "credible": True,
                }
            )

        topics = TOPICS_BY_ARENA.get(arena) or []
        if topics:
            pick = topics[day % len(topics)]
            q = pick.get("rss_query") or pick.get("name") or arena
            for item in rss.fetch_rss_items(q, limit=4, credible_only=True):
                title = item.get("title") or ""
                score = _score_headline(title, arena, credible=True) + 1.5
                if score < 8:
                    continue
                candidates.append(
                    {
                        "title": title,
                        "link": item.get("link") or "",
                        "source": item.get("source") or "",
                        "arena": arena,
                        "topic": pick.get("key") or arena,
                        "score": score,
                        "query": q,
                        "credible": True,
                    }
                )

    seen = set()
    uniq = []
    for c in sorted(candidates, key=lambda x: -x["score"]):
        fp = hashlib.sha1(c["title"].lower().encode()).hexdigest()[:16]
        if fp in seen:
            continue
        seen.add(fp)
        uniq.append(c)
    return uniq


def select_posts(
    candidates: list[dict],
    *,
    max_posts: int = MAX_POSTS_PER_DAY,
    max_per_arena: int = MAX_POSTS_PER_ARENA,
    min_score: float = MIN_SCORE_TO_POST,
) -> list[dict]:
    arena_counts: dict[str, int] = {}
    picked: list[dict] = []
    for c in candidates:
        if len(picked) >= max_posts:
            break
        if c["score"] < min_score:
            continue
        arena = c.get("arena") or "news"
        if arena_counts.get(arena, 0) >= max_per_arena:
            continue
        picked.append(c)
        arena_counts[arena] = arena_counts.get(arena, 0) + 1
    return picked


def render_brand_card(*, headline: str, arena: str, source: str = "") -> bytes:
    w = h = 1080
    img = Image.new("RGB", (w, h), BRAND_CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 140], fill=BRAND_ORANGE)
    draw.rectangle([0, h - 120, w, h], fill=BRAND_NAVY)
    draw.rectangle([0, 140, 28, h - 120], fill=BRAND_ORANGE)
    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
        font_arena = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_foot = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except OSError:
        font_brand = font_arena = font_body = font_foot = ImageFont.load_default()

    draw.text((48, 42), "BarathX", fill=BRAND_WHITE, font=font_brand)
    label = (arena or "news").upper()
    if source:
        label = f"{label} · {source[:28].upper()}"
    draw.text((48, 180), label, fill=BRAND_ORANGE, font=font_arena)
    lines = _wrap(headline, 28)[:7]
    y = 280
    for line in lines:
        draw.text((56, y), line, fill=BRAND_NAVY, font=font_body)
        y += 70
    draw.text((48, h - 78), "India’s public square · barathx.com", fill=BRAND_WHITE, font=font_foot)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def compose_admin_glimpse(*, title: str, arena: str, source: str, slot: str) -> str:
    """Admin morning/peak glimpse, stick to the headline + named source only."""
    tag = f"#{(arena or 'news').replace(' ', '')}"
    slot_marker = SLOT_MARKERS.get(slot, "")
    clean = (title or "").strip()
    src = (source or "").strip()
    lines = [
        f"Worth arguing · {(arena or 'news').title()}",
        clean,
    ]
    if src:
        lines.append(f"via {src}")
    if (arena or "").lower() == "startups":
        lines.append("Fund it or Pass?")
    else:
        lines.append("Agree or push back?")
    lines.append(f"{tag} {POST_MARKER} {slot_marker}".strip())
    return "\n".join(lines)[:500]


def compose_sharath_take(*, title: str, arena: str, source: str, slot: str) -> str:
    """Sharath response post, opinion framing only; no invented facts."""
    slot_marker = SLOT_MARKERS.get(slot, "#BXMorning")
    tag = f"#{arena.capitalize()}" if arena else "#India"
    parts = [
        f"My take on this {arena or 'news'} story:",
        "",
        title.strip(),
        "",
        f"(via {source})" if source else "",
        "Reply with evidence, not just heat.",
        f"{tag} {POST_MARKER} {slot_marker}",
    ]
    text = "\n".join(p for p in parts if p is not None).strip()
    # collapse accidental blank runs
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:500]


def compose_sharath_reply_to_admin() -> str:
    return (
        "Adding my view: this belongs on the square, debate the claim, cite the source, "
        "don’t just pile on. What’s your city reading into it?"
    )


def compose_admin_reply_to_sharath() -> str:
    return (
        "Fair. BarathX stays on the record: headline + publisher only, then your take. "
        "Reply with receipts. #BarathXDaily"
    )


def compose_post_text(*, title: str, arena: str, link: str = "", author: str = "sharath") -> str:
    """Legacy helper kept for compatibility / tests."""
    if author == ADMIN_USERNAME:
        return compose_admin_glimpse(title=title, arena=arena, source="", slot="morning")
    return compose_sharath_take(title=title, arena=arena, source="", slot="morning")


def _user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def _ensure_post_like(db: Session, user_id: str, post_id: str) -> None:
    exists = (
        db.query(models.Like)
        .filter(models.Like.user_id == user_id, models.Like.post_id == post_id)
        .first()
    )
    if not exists:
        db.add(models.Like(user_id=user_id, post_id=post_id))


def _ensure_reply_like(db: Session, user_id: str, reply_id: str) -> None:
    exists = (
        db.query(models.ReplyLike)
        .filter(models.ReplyLike.user_id == user_id, models.ReplyLike.reply_id == reply_id)
        .first()
    )
    if not exists:
        db.add(models.ReplyLike(user_id=user_id, reply_id=reply_id))


def _create_post(
    db: Session,
    *,
    author: models.User,
    text: str,
    headline: str,
    arena: str,
    source: str,
    attach_hashtags,
    notify_mentions,
) -> models.Post:
    try:
        png = render_brand_card(headline=headline, arena=arena, source=source)
        image_url = media_store.save_bytes(
            png, content_type="image/png", filename="baratx-daily.png"
        )
    except Exception:  # noqa: BLE001
        logger.exception("Brand card render failed")
        image_url = None
    post = models.Post(author_id=author.id, text=text, image_url=image_url)
    db.add(post)
    db.flush()
    if attach_hashtags:
        attach_hashtags(db, post, text)
    if notify_mentions:
        notify_mentions(db, author.id, text, post_id=post.id)
    return post


def _create_reply(db: Session, *, author: models.User, post: models.Post, text: str) -> models.Reply:
    reply = models.Reply(post_id=post.id, author_id=author.id, text=text, parent_reply_id=None)
    db.add(reply)
    db.flush()
    return reply


def run_peak_digest(
    db: Session,
    *,
    slot: str,
    force: bool = False,
    attach_hashtags=None,
    notify_mentions=None,
) -> dict:
    """Run one peak window: admin glimpse + Sharath take + cross replies + likes."""
    if slot not in SLOT_MARKERS:
        return {"ok": False, "error": "invalid_slot", "slot": slot}

    admin = _user_by_username(db, ADMIN_USERNAME)
    sharath = _user_by_username(db, SHARATH_USERNAME)
    if not admin or not sharath:
        return {"ok": False, "error": "digest_accounts_missing", "created": 0}

    # Each voice posts once per arena in the slot → 2 * arenas_per_slot posts.
    expected = ARENAS_PER_SLOT * 2
    already = posts_today_count(db, slot=slot)
    if already >= expected and not force:
        return {
            "ok": True,
            "skipped": True,
            "reason": "slot_already_posted",
            "slot": slot,
            "created": 0,
            "already": already,
        }

    arenas = arenas_for_slot(slot)
    candidates = collect_candidates(db, arenas=arenas)
    # One best credible story per arena
    selected = select_posts(candidates, max_posts=len(arenas), max_per_arena=1)
    if not selected:
        return {
            "ok": True,
            "skipped": True,
            "reason": "no_credible_headlines",
            "slot": slot,
            "arenas": arenas,
            "created": 0,
            "candidates_scanned": len(candidates),
        }

    created = []
    for c in selected:
        title = c["title"]
        arena = c["arena"]
        source = c.get("source") or ""

        if _already_posted_similar(db, admin.id, title) or _already_posted_similar(
            db, sharath.id, title
        ):
            continue

        admin_text = compose_admin_glimpse(
            title=title, arena=arena, source=source, slot=slot
        )
        sharath_text = compose_sharath_take(
            title=title, arena=arena, source=source, slot=slot
        )

        admin_post = _create_post(
            db,
            author=admin,
            text=admin_text,
            headline=title,
            arena=arena,
            source=source,
            attach_hashtags=attach_hashtags,
            notify_mentions=notify_mentions,
        )
        sharath_post = _create_post(
            db,
            author=sharath,
            text=sharath_text,
            headline=title,
            arena=arena,
            source=source,
            attach_hashtags=attach_hashtags,
            notify_mentions=notify_mentions,
        )

        sharath_on_admin = _create_reply(
            db, author=sharath, post=admin_post, text=compose_sharath_reply_to_admin()
        )
        admin_on_sharath = _create_reply(
            db, author=admin, post=sharath_post, text=compose_admin_reply_to_sharath()
        )

        # Mutual likes: posts + replies
        _ensure_post_like(db, sharath.id, admin_post.id)
        _ensure_post_like(db, admin.id, sharath_post.id)
        _ensure_reply_like(db, admin.id, sharath_on_admin.id)
        _ensure_reply_like(db, sharath.id, admin_on_sharath.id)

        created.append(
            {
                "arena": arena,
                "title": title,
                "source": source,
                "admin_post_id": admin_post.id,
                "sharath_post_id": sharath_post.id,
                "score": c["score"],
            }
        )

    if created:
        db.commit()
    else:
        db.rollback()

    return {
        "ok": True,
        "slot": slot,
        "created_pairs": len(created),
        "created": len(created) * 2,
        "pairs": created,
        "arenas": arenas,
        "candidates_scanned": len(candidates),
        "day": str(_today_ist()),
        "policy": {
            "peak_slots": [s[2] for s in PEAK_SLOTS],
            "arenas_per_slot": ARENAS_PER_SLOT,
            "credible_only": True,
            "engagement": "admin_post+sharath_post+cross_replies+mutual_likes",
        },
    }


def run_daily_digest(
    db: Session,
    *,
    force: bool = False,
    max_posts: int = MAX_POSTS_PER_DAY,
    attach_hashtags=None,
    notify_mentions=None,
    slot: str | None = None,
) -> dict:
    """Back-compat entry: run a specific slot, or the current/next due peak slot."""
    if slot:
        return run_peak_digest(
            db,
            slot=slot,
            force=force,
            attach_hashtags=attach_hashtags,
            notify_mentions=notify_mentions,
        )

    now = datetime.now(IST)
    # Pick the latest peak slot that has already started today; else morning.
    due = "morning"
    for hour, minute, name in PEAK_SLOTS:
        edge = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= edge:
            due = name
    return run_peak_digest(
        db,
        slot=due,
        force=force,
        attach_hashtags=attach_hashtags,
        notify_mentions=notify_mentions,
    )


# ---------- In-process peak scheduler (IST) ----------

_scheduler_started = False
_scheduler_lock = threading.Lock()


def _seconds_until(hour: int, minute: int) -> float:
    now = datetime.now(IST)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    return max(30.0, (target - now).total_seconds())


def start_daily_digest_scheduler(*, attach_hashtags, notify_mentions) -> None:
    """Fire at 09:00 / 13:30 / 20:00 IST. Catch up missing slots after boot."""
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_DAILY_DIGEST", "").strip().lower() in ("1", "true", "yes"):
            logger.info("Daily digest scheduler disabled via DISABLE_DAILY_DIGEST")
            return
        # Default ON so @baratx / @sharath keep posting at IST peak slots.
        # Set DISABLE_DAILY_DIGEST=1 to pause. ENABLE_DAILY_DIGEST=1 is accepted but not required.
        _scheduler_started = True

    def _run_slot(slot: str, *, label: str) -> None:
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            result = run_peak_digest(
                db,
                slot=slot,
                force=False,
                attach_hashtags=attach_hashtags,
                notify_mentions=notify_mentions,
            )
            logger.info("Peak digest %s/%s result: %s", label, slot, result)
        except Exception:  # noqa: BLE001
            logger.exception("Peak digest %s/%s failed", label, slot)
            try:
                db.rollback()
            except Exception:  # noqa: BLE001
                pass
        finally:
            db.close()

    def boot_catchup():
        time.sleep(45)
        now = datetime.now(IST)
        for hour, minute, slot in PEAK_SLOTS:
            edge = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if now >= edge:
                _run_slot(slot, label="boot-catchup")

    def loop():
        while True:
            waits = [(_seconds_until(h, m), name) for h, m, name in PEAK_SLOTS]
            waits.sort(key=lambda x: x[0])
            wait, slot = waits[0]
            logger.info("Peak digest sleeping %.0fs until %s IST", wait, slot)
            time.sleep(wait)
            _run_slot(slot, label="scheduled")
            time.sleep(60)

    threading.Thread(target=boot_catchup, name="baratx-peak-digest-boot", daemon=True).start()
    threading.Thread(target=loop, name="baratx-peak-digest", daemon=True).start()
    logger.info(
        "Peak digest scheduler started (slots=%s, arenas/slot=%s, voices=%s+%s)",
        ",".join(f"{h:02d}:{m:02d}/{s}" for h, m, s in PEAK_SLOTS),
        ARENAS_PER_SLOT,
        ADMIN_USERNAME,
        SHARATH_USERNAME,
    )
