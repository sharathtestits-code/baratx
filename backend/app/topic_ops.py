"""Seed topics + unpaid RSS debate prompts."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models, rss
from app.topics_data import TOPICS_BY_ARENA, all_topics, debate_sides_for

logger = logging.getLogger("baratx.topics")

# Throttle prompt refresh in-process (multi-worker may still overlap — fine for v1).
_LAST_PROMPT_REFRESH: Optional[datetime] = None
_REFRESH_COOLDOWN = timedelta(minutes=20)

# Renames when topic keys change between deploys.
_TOPIC_KEY_MIGRATIONS = {
    ("news", "startups"): "startup-news",
}


def ensure_topics(db: Session) -> dict:
    """
    Idempotent upsert of the full taxonomy.
    Safe to call on boot and on /topics if the DB is behind the code.
    """
    return seed_topics(db)


def seed_topics(db: Session) -> dict:
    """Upsert the 30×N topic taxonomy. Safe every boot. Returns counts."""
    migrated = 0
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
            # Move interests/debates off the old row, then drop it.
            db.query(models.UserTopicInterest).filter(
                models.UserTopicInterest.topic_id == row.id
            ).update(
                {models.UserTopicInterest.topic_id: clash.id},
                synchronize_session=False,
            )
            db.query(models.Space).filter(models.Space.topic_id == row.id).update(
                {models.Space.topic_id: clash.id},
                synchronize_session=False,
            )
            db.delete(row)
        else:
            row.key = new_key
        migrated += 1
    if migrated:
        try:
            db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
            logger.exception("Topic key migration failed")

    created = 0
    updated = 0
    for row in all_topics():
        existing = (
            db.query(models.Topic)
            .filter(models.Topic.arena_key == row["arena_key"], models.Topic.key == row["key"])
            .first()
        )
        if existing:
            dirty = False
            if existing.name != row["name"]:
                existing.name = row["name"]
                dirty = True
            blurb = row.get("blurb") or ""
            if (existing.blurb or "") != blurb:
                existing.blurb = blurb
                dirty = True
            rss_q = row.get("rss_query") or ""
            if (existing.rss_query or "") != rss_q:
                existing.rss_query = rss_q
                dirty = True
            if dirty:
                updated += 1
            continue
        try:
            db.add(
                models.Topic(
                    arena_key=row["arena_key"],
                    key=row["key"],
                    name=row["name"],
                    blurb=row.get("blurb") or "",
                    rss_query=row.get("rss_query") or "",
                )
            )
            db.flush()
            created += 1
        except Exception:  # noqa: BLE001
            db.rollback()
            logger.exception(
                "Failed to insert topic %s/%s", row.get("arena_key"), row.get("key")
            )

    try:
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("Topic seed commit failed")
        return {"created": 0, "updated": 0, "migrated": migrated, "error": "commit_failed"}

    by_arena = {
        arena: db.query(models.Topic).filter(models.Topic.arena_key == arena).count()
        for arena in TOPICS_BY_ARENA
    }
    logger.info(
        "Topics seeded created=%s updated=%s migrated=%s by_arena=%s",
        created,
        updated,
        migrated,
        by_arena,
    )
    return {
        "created": created,
        "updated": updated,
        "migrated": migrated,
        "by_arena": by_arena,
        "expected_per_arena": {k: len(v) for k, v in TOPICS_BY_ARENA.items()},
    }


def topics_need_seed(db: Session) -> bool:
    """True when any arena is missing topics vs the code taxonomy."""
    for arena_key, rows in TOPICS_BY_ARENA.items():
        n = db.query(models.Topic).filter(models.Topic.arena_key == arena_key).count()
        if n < len(rows):
            return True
    return False


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

    # Heal taxonomy before prompting so new arenas get coverage.
    if topics_need_seed(db):
        seed_topics(db)

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
