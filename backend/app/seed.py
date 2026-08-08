"""Idempotent official BarathX accounts + starter posts for cold-start density."""

from __future__ import annotations

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app import auth, models

logger = logging.getLogger("baratx.seed")

OFFICIAL_ACCOUNTS = [
    {
        "username": "baratx",
        "display_name": "BarathX",
        "bio": "Official BarathX — product updates and India conversation prompts.",
        "badge": "blue",
        "posts": [
            "BarathX is live. India’s public square — short posts, real conversation. Drop your city below.",
            "Rule for this square: reply > like. Say something someone can answer.",
        ],
    },
    {
        "username": "sharath",
        "display_name": "Sharath",
        "bio": "Founder of BarathX. Building India’s public square.",
        "badge": "blue",
        "posts": [
            "I’m Sharath — building BarathX so India gets a real public square, not another firehose. Tell me what you want here.",
        ],
    },
    {
        "username": "bharatvoices",
        "display_name": "Bharat Voices",
        "bio": "Official BarathX — culture, ideas, everyday India.",
        "badge": "gold",
        "posts": [
            "What’s one India story the feeds keep getting wrong? Reply with your take.",
        ],
    },
    {
        "username": "indiatech",
        "display_name": "India Tech Daily",
        "bio": "Official BarathX — startups, policy, and builders across India.",
        "badge": "gold",
        "posts": [
            "Builders in Hyderabad / Bangalore / Delhi — what are you shipping this week?",
        ],
    },
]

OFFICIAL_USERNAMES = [a["username"] for a in OFFICIAL_ACCOUNTS]
BLUE_BADGE_USERNAMES = {a["username"] for a in OFFICIAL_ACCOUNTS if a.get("badge") == "blue"}
# Founder blue accounts that cannot be demoted or deleted.
PROTECTED_BLUE_USERNAMES = {"baratx", "sharath"}


def _apply_badge(user: models.User, badge: str) -> None:
    badge = (badge or "none").strip().lower()
    if badge not in ("none", "gold", "blue"):
        badge = "none"
    user.badge = badge
    user.is_official = badge == "blue"


def seed_official_accounts(db: Session) -> None:
    """Create official accounts + starter posts if missing. Safe to run every boot."""
    created_any = False
    official_password = os.environ.get("OFFICIAL_ACCOUNT_PASSWORD", "").strip()
    for acct in OFFICIAL_ACCOUNTS:
        user = db.query(models.User).filter(models.User.username == acct["username"]).first()
        want_badge = (acct.get("badge") or "gold").strip().lower()
        if not user:
            pwd = official_password or secrets.token_urlsafe(32)
            user = models.User(
                username=acct["username"],
                display_name=acct["display_name"],
                bio=acct["bio"],
                email=f"{acct['username']}@barathx.com",
                password_hash=auth.hash_password(pwd),
                is_email_verified=True,
            )
            _apply_badge(user, want_badge)
            db.add(user)
            db.flush()
            created_any = True
            logger.info("Seeded official account @%s (%s)", acct["username"], want_badge)
        else:
            if user.display_name != acct["display_name"]:
                user.display_name = acct["display_name"]
                created_any = True
            if not (user.bio or "").strip() or "BaratX" in (user.bio or ""):
                user.bio = acct["bio"]
                created_any = True
            current = (getattr(user, "badge", None) or "none").strip().lower()
            # Promote seeded brand accounts up to their intended badge; never demote a live blue.
            if want_badge == "blue" and current != "blue":
                _apply_badge(user, "blue")
                created_any = True
            elif want_badge == "gold" and current == "none":
                _apply_badge(user, "gold")
                created_any = True
            elif current == "blue":
                user.is_official = True
            if official_password:
                user.password_hash = auth.hash_password(official_password)
                created_any = True

        existing_posts = (
            db.query(models.Post).filter(models.Post.author_id == user.id).count()
        )
        if existing_posts == 0:
            for text in acct["posts"]:
                db.add(models.Post(author_id=user.id, text=text))
            created_any = True

    if created_any:
        db.commit()
    else:
        db.rollback()


DEFAULT_COMMUNITIES = [
    {
        "slug": "hyderabad",
        "name": "Hyderabad",
        "description": "City talk — food, traffic, startups, and weekend plans.",
    },
    {
        "slug": "builders",
        "name": "Builders",
        "description": "Shipping products in India. Share what you’re building.",
    },
    {
        "slug": "india-tech",
        "name": "India Tech",
        "description": "Startups, policy, and product news across India.",
    },
]


def seed_default_communities(db: Session) -> None:
    """Create a few starter communities owned by @baratx if missing."""
    host = db.query(models.User).filter(models.User.username == "baratx").first()
    if not host:
        return
    created_any = False
    for c in DEFAULT_COMMUNITIES:
        exists = db.query(models.Community).filter(models.Community.slug == c["slug"]).first()
        if exists:
            continue
        community = models.Community(
            slug=c["slug"],
            name=c["name"],
            description=c["description"],
            created_by=host.id,
            is_arena=False,
        )
        db.add(community)
        db.flush()
        db.add(models.CommunityMember(community_id=community.id, user_id=host.id))
        created_any = True
        logger.info("Seeded community /%s", c["slug"])
    if created_any:
        db.commit()
    else:
        db.rollback()


ARENA_TOPICS = [
    {
        "key": "sports",
        "slug": "sports",
        "name": "Sports",
        "description": "Cricket, football, and every match India argues about.",
    },
    {
        "key": "politics",
        "slug": "politics",
        "name": "Politics",
        "description": "Policy, parties, and the fights that shape the country.",
    },
    {
        "key": "entertainment",
        "slug": "entertainment",
        "name": "Entertainment",
        "description": "Bollywood, Tollywood, music, and celebrity culture.",
    },
    {
        "key": "news",
        "slug": "news",
        "name": "News",
        "description": "Breaking stories and the takes India can’t ignore.",
    },
    {
        "key": "spirituality",
        "slug": "spirituality",
        "name": "Spirituality",
        "description": "Faith, yoga, festivals, and the searches shaping modern India.",
    },
    {
        "key": "startups",
        "slug": "startups",
        "name": "Startups",
        "description": "Funding, founders, and the India builder economy — Fund it or Pass.",
    },
]

SAMPLE_DEBATES = [
    {
        "arena_key": "sports",
        "title": "Will India win the next big series?",
        "side_for": "Yes — India wins",
        "side_against": "No — they fall short",
    },
    {
        "arena_key": "politics",
        "title": "Is India heading in the right direction?",
        "side_for": "Right direction",
        "side_against": "Wrong direction",
    },
    {
        "arena_key": "entertainment",
        "title": "Are remakes killing original Indian cinema?",
        "side_for": "Yes — remakes dominate",
        "side_against": "No — originals still win",
    },
    {
        "arena_key": "news",
        "title": "Do Indian news channels create more heat than light?",
        "side_for": "More heat",
        "side_against": "Still essential",
    },
    {
        "arena_key": "spirituality",
        "title": "Is bhajan clubbing devotion — or just a new nightlife product?",
        "side_for": "Resonates",
        "side_against": "Skeptical",
    },
    {
        "arena_key": "spirituality",
        "title": "Can apps replace ashrams for daily spiritual practice?",
        "side_for": "Resonates",
        "side_against": "Skeptical",
    },
    {
        "arena_key": "startups",
        "title": "Should India prioritize profitability over growth-at-all-costs?",
        "side_for": "Fund it",
        "side_against": "Pass",
    },
]


def seed_arenas(db: Session) -> None:
    """Seed active arenas + starter debates (including Startups)."""
    host = db.query(models.User).filter(models.User.username == "baratx").first()
    if not host:
        return
    created_any = False
    arenas_by_key = {}
    for topic in ARENA_TOPICS:
        row = (
            db.query(models.Community)
            .filter(
                (models.Community.arena_key == topic["key"])
                | (models.Community.slug == topic["slug"])
            )
            .first()
        )
        if row:
            changed = False
            if not getattr(row, "is_arena", False) or row.arena_key != topic["key"]:
                row.is_arena = True
                row.arena_key = topic["key"]
                changed = True
            if row.name != topic["name"] or row.description != topic["description"]:
                row.name = topic["name"]
                row.description = topic["description"]
                changed = True
            if changed:
                created_any = True
            arenas_by_key[topic["key"]] = row
            continue
        community = models.Community(
            slug=topic["slug"],
            name=topic["name"],
            description=topic["description"],
            created_by=host.id,
            is_arena=True,
            arena_key=topic["key"],
        )
        db.add(community)
        db.flush()
        db.add(models.CommunityMember(community_id=community.id, user_id=host.id))
        arenas_by_key[topic["key"]] = community
        created_any = True
        logger.info("Seeded arena /%s", topic["slug"])

    now = datetime.now(timezone.utc)
    for debate in SAMPLE_DEBATES:
        arena = arenas_by_key.get(debate["arena_key"])
        if not arena:
            continue
        exists = (
            db.query(models.Space)
            .filter(
                models.Space.community_id == arena.id,
                models.Space.kind == "debate",
                models.Space.title == debate["title"],
            )
            .first()
        )
        if exists:
            continue
        db.add(
            models.Space(
                title=debate["title"],
                host_id=host.id,
                status="open",
                kind="debate",
                community_id=arena.id,
                side_for_label=debate["side_for"],
                side_against_label=debate["side_against"],
                closes_at=now + timedelta(days=7),
            )
        )
        created_any = True
        logger.info("Seeded debate: %s", debate["title"])

    if created_any:
        db.commit()
    else:
        db.rollback()


def follow_official_accounts(db: Session, user: models.User) -> int:
    """Auto-follow official BarathX accounts. Returns number of new follows."""
    added = 0
    for username in OFFICIAL_USERNAMES:
        target = db.query(models.User).filter(models.User.username == username).first()
        if not target or target.id == user.id:
            continue
        exists = (
            db.query(models.Follow)
            .filter(
                models.Follow.follower_id == user.id,
                models.Follow.followed_id == target.id,
            )
            .first()
        )
        if exists:
            continue
        db.add(models.Follow(follower_id=user.id, followed_id=target.id))
        added += 1
    return added
