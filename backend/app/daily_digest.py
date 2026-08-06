"""Daily trending digest — post 1–2 quality news takes as @sharath.

Pulls Google News RSS across arenas/topics, ranks for punchiness, renders a
BaratX-themed image, and posts from the founder account. Quality over volume.
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
# Split voice across brand + founder so the square feels alive.
DIGEST_AUTHORS = ("sharath", "baratx")
MAX_POSTS_PER_AUTHOR = 1
MAX_POSTS_PER_DAY = len(DIGEST_AUTHORS) * MAX_POSTS_PER_AUTHOR
POST_MARKER = "#BaratXDaily"

# Arena-level trending queries (broader than single subtopics).
ARENA_TRENDING_QUERIES = {
    "sports": "India sports news today",
    "politics": "India politics news today",
    "entertainment": "Bollywood entertainment news today India",
    "news": "India breaking news today",
    "spirituality": "India spirituality religion news today",
}

BRAND_ORANGE = (255, 103, 31)
BRAND_NAVY = (15, 23, 42)
BRAND_CREAM = (255, 248, 242)
BRAND_WHITE = (255, 255, 255)


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


def _score_headline(title: str) -> float:
    """Higher = more post-worthy. Prefer punchy, specific India stories."""
    t = (title or "").strip()
    if len(t) < 28:
        return 0.0
    score = 10.0
    # Prefer mid-length (mobile readable)
    if 40 <= len(t) <= 110:
        score += 8
    elif len(t) > 140:
        score -= 4
    low = t.lower()
    for kw in (
        "india",
        "delhi",
        "mumbai",
        "hyderabad",
        "bangalore",
        "bengaluru",
        "modi",
        "ipl",
        "cricket",
        "election",
        "budget",
        "isro",
        "rupee",
        "supreme court",
    ):
        if kw in low:
            score += 2
    # Soft-penalize listicles / evergreen noise
    for bad in ("tips to", "in pictures", "horoscope", "zodiac", "best of"):
        if bad in low:
            score -= 8
    if "?" in t:
        score += 2
    return score


def _already_posted_similar(db: Session, author_id: str, title: str) -> bool:
    """Avoid re-posting the same story in the last 5 days."""
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


def posts_today_count(db: Session, author_id: str) -> int:
    start = datetime.combine(_today_ist(), datetime.min.time(), tzinfo=IST).astimezone(
        timezone.utc
    )
    return (
        db.query(models.Post)
        .filter(
            models.Post.author_id == author_id,
            models.Post.created_at >= start,
            models.Post.text.contains(POST_MARKER),
        )
        .count()
    )


def collect_candidates(db: Session, *, per_arena: int = 3) -> list[dict]:
    """Scan arenas + a few rotating topics; return scored candidates."""
    day = _today_ist().toordinal()
    candidates: list[dict] = []

    for arena in sorted(ACTIVE_ARENA_KEYS):
        query = ARENA_TRENDING_QUERIES.get(arena) or f"India {arena} news"
        for item in rss.fetch_rss_items(query, limit=per_arena):
            title = item.get("title") or ""
            score = _score_headline(title)
            if score < 8:
                continue
            candidates.append(
                {
                    "title": title,
                    "link": item.get("link") or "",
                    "arena": arena,
                    "topic": arena,
                    "score": score,
                    "query": query,
                }
            )

        # One rotating subtopic per arena for fresher beats
        topics = TOPICS_BY_ARENA.get(arena) or []
        if topics:
            pick = topics[day % len(topics)]
            q = pick.get("rss_query") or pick.get("name") or arena
            for item in rss.fetch_rss_items(q, limit=2):
                title = item.get("title") or ""
                score = _score_headline(title) + 1.5  # slight boost for topic hit
                if score < 8:
                    continue
                candidates.append(
                    {
                        "title": title,
                        "link": item.get("link") or "",
                        "arena": arena,
                        "topic": pick.get("key") or arena,
                        "score": score,
                        "query": q,
                    }
                )

    # Dedup by title fingerprint
    seen = set()
    uniq = []
    for c in sorted(candidates, key=lambda x: -x["score"]):
        fp = hashlib.sha1(c["title"].lower().encode()).hexdigest()[:16]
        if fp in seen:
            continue
        seen.add(fp)
        uniq.append(c)
    return uniq


def render_brand_card(*, headline: str, arena: str) -> bytes:
    """1080×1080 BaratX saffron card — one image per digest post."""
    w = h = 1080
    img = Image.new("RGB", (w, h), BRAND_CREAM)
    draw = ImageDraw.Draw(img)

    # Top brand bar
    draw.rectangle([0, 0, w, 140], fill=BRAND_ORANGE)
    # Bottom navy strip
    draw.rectangle([0, h - 120, w, h], fill=BRAND_NAVY)
    # Accent rail
    draw.rectangle([0, 140, 28, h - 120], fill=BRAND_ORANGE)

    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
        font_arena = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_foot = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except OSError:
        font_brand = font_arena = font_body = font_foot = ImageFont.load_default()

    draw.text((48, 42), "BaratX", fill=BRAND_WHITE, font=font_brand)
    draw.text((48, 180), (arena or "news").upper(), fill=BRAND_ORANGE, font=font_arena)

    lines = _wrap(headline, 28)[:7]
    y = 280
    for line in lines:
        draw.text((56, y), line, fill=BRAND_NAVY, font=font_body)
        y += 70

    draw.text((48, h - 78), "India’s public square · barathx.com", fill=BRAND_WHITE, font=font_foot)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def compose_post_text(*, title: str, arena: str, link: str = "", author: str = "sharath") -> str:
    take = title.strip()
    if not take.endswith("?"):
        take = f"{take} — overblown, or are we sleeping on it?"
    tag = f"#{arena.capitalize()}" if arena else "#India"
    if author == "baratx":
        cta = "India — argue this out. Reply with your city take."
    else:
        cta = "What’s your take — reply, don’t just scroll."
    parts = [
        take,
        "",
        cta,
        f"{tag} {POST_MARKER}",
    ]
    if link and len(link) < 180:
        # Google News links are long redirects; skip if noisy
        if "news.google.com" not in link:
            parts.insert(2, link)
    text = "\n".join(parts).strip()
    return text[:500]


def run_daily_digest(
    db: Session,
    *,
    force: bool = False,
    max_posts: int = MAX_POSTS_PER_DAY,
    attach_hashtags=None,
    notify_mentions=None,
) -> dict:
    """Create up to max_posts trending posts as @sharath and @baratx for today (IST)."""
    authors = []
    for username in DIGEST_AUTHORS:
        row = db.query(models.User).filter(models.User.username == username).first()
        if row:
            authors.append(row)
    if not authors:
        return {"ok": False, "error": "digest_accounts_missing", "created": 0}

    already_total = sum(posts_today_count(db, a.id) for a in authors)
    if already_total >= max_posts and not force:
        return {
            "ok": True,
            "skipped": True,
            "reason": "already_posted_today",
            "created": 0,
            "already": already_total,
        }

    candidates = collect_candidates(db)
    created_posts = []
    used_titles = set()

    for author in authors:
        if len(created_posts) >= max_posts:
            break
        author_already = posts_today_count(db, author.id)
        if author_already >= MAX_POSTS_PER_AUTHOR and not force:
            continue
        for c in candidates:
            if len(created_posts) >= max_posts:
                break
            title_key = c["title"].lower()
            if title_key in used_titles:
                continue
            if _already_posted_similar(db, author.id, c["title"]):
                continue
            # Also skip if the other official already posted this story today.
            skip = False
            for other in authors:
                if other.id != author.id and _already_posted_similar(db, other.id, c["title"]):
                    skip = True
                    break
            if skip:
                continue

            text = compose_post_text(
                title=c["title"],
                arena=c["arena"],
                link=c.get("link") or "",
                author=author.username,
            )
            try:
                png = render_brand_card(headline=c["title"], arena=c["arena"])
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
            created_posts.append(
                {
                    "id": post.id,
                    "author": author.username,
                    "arena": c["arena"],
                    "topic": c["topic"],
                    "title": c["title"],
                    "score": c["score"],
                    "image": bool(image_url),
                }
            )
            used_titles.add(title_key)
            break  # one post per author per run

    if created_posts:
        db.commit()
    else:
        db.rollback()

    return {
        "ok": True,
        "created": len(created_posts),
        "posts": created_posts,
        "candidates_scanned": len(candidates),
        "day": str(_today_ist()),
        "authors": [a.username for a in authors],
    }


# ---------- In-process daily scheduler (IST morning) ----------

_scheduler_started = False
_scheduler_lock = threading.Lock()


def _seconds_until_next_run(hour: int = 9, minute: int = 5) -> float:
    now = datetime.now(IST)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    return max(30.0, (target - now).total_seconds())


def start_daily_digest_scheduler(*, attach_hashtags, notify_mentions) -> None:
    """Fire once near 09:05 IST every day inside the API process."""
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_DAILY_DIGEST", "").strip().lower() in ("1", "true", "yes"):
            logger.info("Daily digest scheduler disabled via DISABLE_DAILY_DIGEST")
            return
        _scheduler_started = True

    def loop():
        from app.database import SessionLocal

        while True:
            wait = _seconds_until_next_run()
            logger.info("Daily digest sleeping %.0fs until next IST run", wait)
            time.sleep(wait)
            db = SessionLocal()
            try:
                result = run_daily_digest(
                    db,
                    force=False,
                    attach_hashtags=attach_hashtags,
                    notify_mentions=notify_mentions,
                )
                logger.info("Daily digest result: %s", result)
            except Exception:  # noqa: BLE001
                logger.exception("Daily digest run failed")
                try:
                    db.rollback()
                except Exception:  # noqa: BLE001
                    pass
            finally:
                db.close()
            time.sleep(60)  # avoid double-fire in the same minute

    t = threading.Thread(target=loop, name="baratx-daily-digest", daemon=True)
    t.start()
    logger.info("Daily digest scheduler started (authors=%s, IST ~09:05)", ",".join(DIGEST_AUTHORS))
