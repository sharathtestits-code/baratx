"""Seed topics + unpaid RSS debate prompts."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models, rss
from app.topics_data import all_topics, debate_sides_for

logger = logging.getLogger("baratx.topics")

# Throttle prompt refresh in-process (multi-worker may still overlap — fine for v1).
_LAST_PROMPT_REFRESH: Optional[datetime] = None
_REFRESH_COOLDOWN = timedelta(minutes=20)

# Renames when topic keys change between deploys.
_TOPIC_KEY_MIGRATIONS = {
    ("news", "startups"): "startup-news",
}


def seed_topics(db: Session) -> None:
    """Upsert the 30×N topic taxonomy. Safe every boot."""
    for (arena_key, old_key), new_key in _TOPIC_KEY_MIGRATIONS.items():
        row = (
            db.query(models.Topic)
            .filter(models.Topic.arena_key == arena_key, models.Topic.key == old_key)
            .first()
        )
        if not row:
            continue
        clash = (
            db.query(models.Topic)
            .filter(models.Topic.arena_key == arena_key, models.Topic.key == new_key)
            .first()
        )
        if clash:
            db.delete(row)
        else:
            row.key = new_key

    created = 0
    for row in all_topics():
        existing = (
            db.query(models.Topic)
            .filter(models.Topic.arena_key == row["arena_key"], models.Topic.key == row["key"])
            .first()
        )
        if existing:
            existing.name = row["name"]
            existing.blurb = row.get("blurb") or ""
            existing.rss_query = row.get("rss_query") or ""
            continue
        db.add(
            models.Topic(
                arena_key=row["arena_key"],
                key=row["key"],
                name=row["name"],
                blurb=row.get("blurb") or "",
                rss_query=row.get("rss_query") or "",
            )
        )
        created += 1
    if created:
        db.commit()
        logger.info("Seeded %s topics", created)
    else:
        db.commit()  # persist blurb/rss updates


def refresh_debate_prompts(
    db: Session,
    *,
    force: bool = False,
    per_topic: int = 2,
    max_topics: int = 24,
) -> dict:
    """
    Pull unpaid Google News RSS for a subset of topics and open debate Spaces.
    Returns {created, skipped, topics_tried}.
    """
    global _LAST_PROMPT_REFRESH
    now = datetime.now(timezone.utc)
    if not force and _LAST_PROMPT_REFRESH and now - _LAST_PROMPT_REFRESH < _REFRESH_COOLDOWN:
        return {"created": 0, "skipped": 0, "topics_tried": 0, "throttled": True}

    host = db.query(models.User).filter(models.User.username == "baratx").first()
    if not host:
        return {"created": 0, "skipped": 0, "topics_tried": 0, "error": "no baratx host"}

    arenas = {
        c.arena_key: c
        for c in db.query(models.Community)
        .filter(models.Community.is_arena == True)  # noqa: E712
        .all()
        if c.arena_key
    }
    topics = db.query(models.Topic).order_by(models.Topic.arena_key.asc(), models.Topic.name.asc()).all()
    if not topics:
        return {"created": 0, "skipped": 0, "topics_tried": 0, "error": "no topics"}

    # Rotate which topics get refreshed using hour buckets so all get love over time.
    hour_bucket = now.hour % 4
    selected = [t for i, t in enumerate(topics) if i % 4 == hour_bucket][:max_topics]
    if force:
        selected = topics[:max_topics]

    created = 0
    skipped = 0
    for topic in selected:
        arena = arenas.get(topic.arena_key)
        if not arena:
            skipped += 1
            continue
        items = rss.fetch_rss_items(topic.rss_query or topic.name, limit=per_topic)
        if not items:
            skipped += 1
            continue
        for item in items:
            link = (item.get("link") or "").strip()
            title = rss.headline_to_debate_title(item.get("title") or "")
            if link:
                exists = (
                    db.query(models.Space)
                    .filter(models.Space.source_url == link, models.Space.kind == "debate")
                    .first()
                )
                if exists:
                    skipped += 1
                    continue
            # Also dedupe similar titles in same topic (last 3 days)
            recent = (
                db.query(models.Space)
                .filter(
                    models.Space.topic_id == topic.id,
                    models.Space.kind == "debate",
                    models.Space.title == title,
                )
                .first()
            )
            if recent:
                skipped += 1
                continue
            side_for, side_against = debate_sides_for(topic.arena_key)
            db.add(
                models.Space(
                    title=title,
                    host_id=host.id,
                    status="open",
                    kind="debate",
                    community_id=arena.id,
                    topic_id=topic.id,
                    source_url=link or None,
                    side_for_label=side_for,
                    side_against_label=side_against,
                    closes_at=now + timedelta(days=3),
                )
            )
            created += 1
    if created:
        db.commit()
    else:
        db.rollback()
    _LAST_PROMPT_REFRESH = now
    logger.info("Prompt refresh created=%s skipped=%s topics=%s", created, skipped, len(selected))
    return {"created": created, "skipped": skipped, "topics_tried": len(selected), "throttled": False}
