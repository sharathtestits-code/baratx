"""India-now trending for Explore — RSS-scored topics + headlines (no paid Trends API).

Uses the same Google News IN feeds + credible scoring as daily digest.
Falls back to curated topic taxonomy when RSS is thin.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any, Optional

from app import rss
from app.daily_digest import ARENA_TRENDING_QUERIES, _score_headline
from app.topics_data import ACTIVE_ARENA_KEYS, TOPICS_BY_ARENA

logger = logging.getLogger("baratx.trending")

CACHE_TTL_SEC = 15 * 60
HEADLINES_PER_LANE = 8
TOPICS_PER_LANE = 8

# Query / chip aliases → arena lane (+ optional topic keyword filter).
LANE_ALIASES: dict[str, dict[str, Any]] = {
    "india": {"lane": "india", "label": "India now"},
    "trending": {"lane": "india", "label": "India now"},
    "news": {"lane": "news", "label": "News"},
    "politics": {"lane": "politics", "label": "Politics"},
    "cricket": {"lane": "sports", "label": "Cricket", "topic_re": r"cricket|ipl|wpl|team.?india|icc|t20"},
    "ipl": {"lane": "sports", "label": "IPL", "topic_re": r"ipl|cricket"},
    "sports": {"lane": "sports", "label": "Sports"},
    "startups": {"lane": "startups", "label": "Startups"},
    "entertainment": {"lane": "entertainment", "label": "Entertainment"},
    "spirituality": {"lane": "spirituality", "label": "Spirituality"},
    "geopolitics": {"lane": "politics", "label": "Geopolitics", "topic_re": r"geopolit|foreign|defence|border"},
}

_EXTRA_LANE_QUERIES = {
    "cricket": "India cricket IPL OR Team India OR BCCI PTI OR The Hindu",
    "ipl": "IPL cricket India today PTI OR The Hindu",
    "geopolitics": "India geopolitics foreign policy Indo-Pacific PTI OR The Hindu",
    "india": "India trending news today PTI OR Reuters OR The Hindu",
}

_cache_lock = threading.Lock()
_cache: dict[str, tuple[float, dict]] = {}


def resolve_lane(raw: str | None) -> dict[str, Any]:
    """Map free text / lane param to a trending lane config."""
    text = re.sub(r"\s+", " ", (raw or "").strip().lower())
    text = text.lstrip("#@")
    if not text:
        return {"lane": "india", "label": "India now", "query_key": "india"}

    padded = f" {text} "
    # Prefer specific arenas over generic "trending" / "india".
    priority = (
        "geopolitics",
        "cricket",
        "ipl",
        "politics",
        "startups",
        "entertainment",
        "spirituality",
        "sports",
        "news",
        "trending",
        "india",
    )
    for alias in priority:
        conf_base = LANE_ALIASES.get(alias)
        if not conf_base:
            continue
        if text == alias or text.startswith(alias + " ") or f" {alias} " in padded:
            conf = dict(conf_base)
            conf["query_key"] = alias
            return conf

    if text in ACTIVE_ARENA_KEYS:
        return {"lane": text, "label": text.title(), "query_key": text}

    return {"lane": "india", "label": "India now", "query_key": "india", "free_text": text}


def _cache_get(key: str) -> Optional[dict]:
    with _cache_lock:
        hit = _cache.get(key)
        if not hit:
            return None
        expires, payload = hit
        if time.time() > expires:
            _cache.pop(key, None)
            return None
        return payload


def _cache_set(key: str, payload: dict) -> None:
    with _cache_lock:
        _cache[key] = (time.time() + CACHE_TTL_SEC, payload)


def _topics_for_lane(conf: dict[str, Any]) -> list[dict]:
    lane = conf.get("lane") or "india"
    topic_re = conf.get("topic_re")
    pattern = re.compile(topic_re, re.I) if topic_re else None
    free = (conf.get("free_text") or "").strip()

    out: list[dict] = []
    arenas = list(ACTIVE_ARENA_KEYS) if lane == "india" else [lane]
    for arena in arenas:
        for t in TOPICS_BY_ARENA.get(arena, []):
            blob = f"{t.get('name','')} {t.get('key','')} {t.get('blurb','')} {t.get('rss_query','')}"
            if pattern and not pattern.search(blob):
                continue
            if free and free not in blob.lower() and free not in (t.get("rss_query") or "").lower():
                # For unresolved free text, keep broad India mix (already lane=india).
                if lane != "india":
                    continue
            out.append(
                {
                    "kind": "topic",
                    "key": t["key"],
                    "name": t["name"],
                    "arena_key": arena,
                    "blurb": t.get("blurb") or "",
                    "score": 1.0,
                    "href": f"/arenas/{arena}",
                }
            )
    return out


def _fetch_headlines(conf: dict[str, Any], *, limit: int) -> list[dict]:
    lane = conf.get("lane") or "india"
    query_key = conf.get("query_key") or lane
    queries: list[str] = []

    extra = _EXTRA_LANE_QUERIES.get(query_key)
    if extra:
        queries.append(extra)
    if lane in ARENA_TRENDING_QUERIES:
        queries.append(ARENA_TRENDING_QUERIES[lane])
    elif lane == "india":
        queries.extend(
            [
                ARENA_TRENDING_QUERIES["news"],
                ARENA_TRENDING_QUERIES["politics"],
                ARENA_TRENDING_QUERIES["sports"],
            ]
        )

    # Topic RSS for cricket / geopolitics filters.
    for t in _topics_for_lane(conf)[:6]:
        arena = t["arena_key"]
        for topic in TOPICS_BY_ARENA.get(arena, []):
            if topic["key"] == t["key"] and topic.get("rss_query"):
                queries.append(topic["rss_query"])
                break

    seen: set[str] = set()
    scored: list[dict] = []
    for q in queries:
        for item in rss.fetch_rss_items(q, limit=6, credible_only=True):
            title = (item.get("title") or "").strip()
            if not title:
                continue
            key = re.sub(r"[^a-z0-9]+", "", title.lower())[:80]
            if not key or key in seen:
                continue
            seen.add(key)
            score = _score_headline(title, lane if lane != "india" else "news", credible=True)
            scored.append(
                {
                    "kind": "headline",
                    "title": title,
                    "source": item.get("source") or "",
                    "url": item.get("link") or "",
                    "arena_key": lane if lane in ACTIVE_ARENA_KEYS else "news",
                    "score": score,
                    "search_q": title.split(":")[0][:48].strip(),
                }
            )
        if len(scored) >= limit * 2:
            break

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def _rank_topics_with_headlines(topics: list[dict], headlines: list[dict]) -> list[dict]:
    """Boost topics whose name/key appears in hot headlines."""
    blob = " ".join(h["title"].lower() for h in headlines)
    ranked = []
    for t in topics:
        score = 2.0
        name = (t.get("name") or "").lower()
        key = (t.get("key") or "").replace("-", " ").lower()
        if name and name in blob:
            score += 8
        if key and key in blob:
            score += 5
        for token in re.split(r"[\s/]+", name):
            if len(token) >= 4 and token in blob:
                score += 1.5
        row = dict(t)
        row["score"] = score
        ranked.append(row)
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def get_trending(
    *,
    q: str | None = None,
    lane: str | None = None,
    limit: int = 8,
) -> dict:
    """Return India-now trending topics + headlines for Explore."""
    limit = max(3, min(int(limit or 8), 16))
    conf = resolve_lane(lane or q)
    cache_key = f"{conf.get('query_key')}:{conf.get('lane')}:{conf.get('topic_re')}:{limit}"

    cached = _cache_get(cache_key)
    if cached is not None:
        out = dict(cached)
        out["cached"] = True
        return out

    topics = _topics_for_lane(conf)
    headlines: list[dict] = []
    source = "taxonomy"
    try:
        headlines = _fetch_headlines(conf, limit=max(limit, HEADLINES_PER_LANE))
        if headlines:
            source = "rss+taxonomy"
    except Exception:  # noqa: BLE001
        logger.exception("trending RSS failed")

    ranked_topics = _rank_topics_with_headlines(topics, headlines)[: max(limit, TOPICS_PER_LANE)]
    # Always show some topics even if RSS empty.
    if not ranked_topics:
        ranked_topics = _topics_for_lane({"lane": "india"})[:TOPICS_PER_LANE]

    payload = {
        "ok": True,
        "lane": conf.get("lane"),
        "label": conf.get("label") or "India now",
        "query_key": conf.get("query_key"),
        "source": source,
        "cached": False,
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "topics": ranked_topics[:limit],
        "headlines": headlines[:limit],
        "arenas": (
            [{"key": conf["lane"], "name": conf.get("label") or conf["lane"].title(), "href": f"/arenas/{conf['lane']}"}]
            if conf.get("lane") in ACTIVE_ARENA_KEYS
            else [{"key": k, "name": k.title(), "href": f"/arenas/{k}"} for k in ("news", "politics", "sports", "startups")]
        ),
    }
    _cache_set(cache_key, payload)
    return payload
