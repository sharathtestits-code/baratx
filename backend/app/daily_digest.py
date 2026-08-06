"""Daily trending digest — multi-arena posts as @sharath + @baratx.

Pulls Google News RSS across all arenas, scores for BaratX motto fit
(India's public square — real civic takes, not spam), and posts 3–5
quality items/day with a per-arena cap so politics doesn't own the feed.
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

# Volume: post 3–5 when quality exists. Max 2 per arena so all floors get airtime.
MIN_POSTS_IF_QUALITY = 3
MAX_POSTS_PER_DAY = 5
MAX_POSTS_PER_ARENA = 2
MAX_POSTS_PER_AUTHOR = 3  # within the daily 5, split across both voices
POST_MARKER = "#BaratXDaily"

# Soft floor — below this we skip (never pad with junk to hit the min).
MIN_SCORE_TO_POST = 12.0
# Slight prefer politics (civic pulse) without excluding other arenas.
ARENA_WEIGHT = {
    "politics": 2.5,
    "news": 1.5,
    "sports": 1.0,
    "entertainment": 0.5,
    "spirituality": 1.0,
}

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

# BaratX motto keywords — civic debate / India public square.
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
    "vote",
    "voter",
    "constitution",
    "supreme court",
    "high court",
    "policy",
    "budget",
    "rupee",
    "gst",
    "farmers",
    "civic",
    "municipal",
    "mayor",
    "cm ",
    "governor",
    "isro",
    "ipl",
    "cricket",
    "world cup",
    "olympics",
    "protest",
    "bill",
    "act ",
    "rti",
    "corruption",
    "scam",
    "temple",
    "mosque",
    "church",
    "faith",
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


def _score_headline(title: str, arena: str = "") -> float:
    """Higher = more post-worthy and closer to BaratX motto (civic square)."""
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
    for kw in _MOTTO_BOOST:
        if kw in low:
            score += 2.2
    for bad in _SOFT_PENALTY:
        if bad in low:
            score -= 8
    if "?" in t:
        score += 2
    # Debate-shaped language
    for cue in ("should", "why", "vs", "versus", "debate", "controversy", "row over", "slams"):
        if cue in low:
            score += 1.5
    score += ARENA_WEIGHT.get(arena, 0.0)
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


def posts_today_count(db: Session, author_id: Optional[str] = None) -> int:
    start = datetime.combine(_today_ist(), datetime.min.time(), tzinfo=IST).astimezone(
        timezone.utc
    )
    q = db.query(models.Post).filter(
        models.Post.created_at >= start,
        models.Post.text.contains(POST_MARKER),
    )
    if author_id:
        q = q.filter(models.Post.author_id == author_id)
    return q.count()


def collect_candidates(db: Session, *, per_arena: int = 5) -> list[dict]:
    """Scan all arenas + rotating topics; return motto-scored candidates."""
    day = _today_ist().toordinal()
    candidates: list[dict] = []

    for arena in sorted(ACTIVE_ARENA_KEYS):
        query = ARENA_TRENDING_QUERIES.get(arena) or f"India {arena} news"
        for item in rss.fetch_rss_items(query, limit=per_arena):
            title = item.get("title") or ""
            score = _score_headline(title, arena)
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
            for item in rss.fetch_rss_items(q, limit=3):
                title = item.get("title") or ""
                score = _score_headline(title, arena) + 1.5
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


def select_posts(
    candidates: list[dict],
    *,
    max_posts: int = MAX_POSTS_PER_DAY,
    max_per_arena: int = MAX_POSTS_PER_ARENA,
    min_score: float = MIN_SCORE_TO_POST,
) -> list[dict]:
    """Pick up to max_posts with arena diversity. Never pad weak stories."""
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
    """Create 3–5 motto-aligned posts across arenas as @sharath and @baratx."""
    authors = []
    for username in DIGEST_AUTHORS:
        row = db.query(models.User).filter(models.User.username == username).first()
        if row:
            authors.append(row)
    if not authors:
        return {"ok": False, "error": "digest_accounts_missing", "created": 0}

    already_total = posts_today_count(db)
    if already_total >= max_posts and not force:
        return {
            "ok": True,
            "skipped": True,
            "reason": "already_posted_today",
            "created": 0,
            "already": already_total,
            "target": f"{MIN_POSTS_IF_QUALITY}-{max_posts}",
        }

    remaining_slots = max_posts if force else max(0, max_posts - already_total)
    if remaining_slots <= 0:
        return {
            "ok": True,
            "skipped": True,
            "reason": "slots_full",
            "created": 0,
            "already": already_total,
        }

    candidates = collect_candidates(db)
    selected = select_posts(candidates, max_posts=remaining_slots)

    # Prefer hitting the min when enough quality exists; select_posts already
    # quality-gates — if we have fewer than MIN, we still post what passed.
    created_posts = []
    used_titles = set()
    author_counts = {a.id: posts_today_count(db, a.id) for a in authors}
    author_idx = 0

    for c in selected:
        title_key = c["title"].lower()
        if title_key in used_titles:
            continue

        # Round-robin authors, respecting per-author cap.
        author = None
        for offset in range(len(authors)):
            candidate_author = authors[(author_idx + offset) % len(authors)]
            if author_counts.get(candidate_author.id, 0) >= MAX_POSTS_PER_AUTHOR and not force:
                continue
            if _already_posted_similar(db, candidate_author.id, c["title"]):
                continue
            # Skip if any digest author already covered this story recently.
            other_hit = False
            for other in authors:
                if other.id != candidate_author.id and _already_posted_similar(
                    db, other.id, c["title"]
                ):
                    other_hit = True
                    break
            if other_hit:
                continue
            author = candidate_author
            author_idx = (author_idx + offset + 1) % len(authors)
            break
        if not author:
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
        author_counts[author.id] = author_counts.get(author.id, 0) + 1

    if created_posts:
        db.commit()
    else:
        db.rollback()

    return {
        "ok": True,
        "created": len(created_posts),
        "posts": created_posts,
        "candidates_scanned": len(candidates),
        "selected_quality": len(selected),
        "day": str(_today_ist()),
        "authors": [a.username for a in authors],
        "policy": {
            "min_if_quality": MIN_POSTS_IF_QUALITY,
            "max_per_day": max_posts,
            "max_per_arena": MAX_POSTS_PER_ARENA,
            "min_score": MIN_SCORE_TO_POST,
            "arenas": list(ACTIVE_ARENA_KEYS),
        },
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
    """Fire once near 09:05 IST every day inside the API process.

    Also catch up shortly after boot if today's digest has not run yet
    (so a deploy / restart can start posts without waiting for morning).
    """
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_DAILY_DIGEST", "").strip().lower() in ("1", "true", "yes"):
            logger.info("Daily digest scheduler disabled via DISABLE_DAILY_DIGEST")
            return
        _scheduler_started = True

    def _run_once(*, label: str) -> None:
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            result = run_daily_digest(
                db,
                force=False,
                attach_hashtags=attach_hashtags,
                notify_mentions=notify_mentions,
            )
            logger.info("Daily digest %s result: %s", label, result)
        except Exception:  # noqa: BLE001
            logger.exception("Daily digest %s failed", label)
            try:
                db.rollback()
            except Exception:  # noqa: BLE001
                pass
        finally:
            db.close()

    def boot_catchup():
        # Let migrations/seed settle, then fill today's slots if empty.
        time.sleep(45)
        _run_once(label="boot-catchup")

    def loop():
        while True:
            wait = _seconds_until_next_run()
            logger.info("Daily digest sleeping %.0fs until next IST run", wait)
            time.sleep(wait)
            _run_once(label="scheduled")
            time.sleep(60)  # avoid double-fire in the same minute

    threading.Thread(target=boot_catchup, name="baratx-daily-digest-boot", daemon=True).start()
    threading.Thread(target=loop, name="baratx-daily-digest", daemon=True).start()
    logger.info(
        "Daily digest scheduler started (authors=%s, target=%s-%s/day, max/arena=%s, IST ~09:05 + boot catch-up)",
        ",".join(DIGEST_AUTHORS),
        MIN_POSTS_IF_QUALITY,
        MAX_POSTS_PER_DAY,
        MAX_POSTS_PER_ARENA,
    )
