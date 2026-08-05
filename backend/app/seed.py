"""Idempotent official BaratX accounts + starter posts for cold-start density."""

from __future__ import annotations

import logging
import secrets

from sqlalchemy.orm import Session

from app import auth, models

logger = logging.getLogger("baratx.seed")

OFFICIAL_ACCOUNTS = [
    {
        "username": "baratx",
        "display_name": "BaratX",
        "bio": "Official BaratX — product updates and India conversation prompts.",
        "posts": [
            "BaratX is live. India’s public square — short posts, real conversation. Drop your city below.",
            "Rule for this square: reply > like. Say something someone can answer.",
        ],
    },
    {
        "username": "bharatvoices",
        "display_name": "Bharat Voices",
        "bio": "Official BaratX — culture, ideas, everyday India.",
        "posts": [
            "What’s one India story the feeds keep getting wrong? Reply with your take.",
        ],
    },
    {
        "username": "indiatech",
        "display_name": "India Tech Daily",
        "bio": "Official BaratX — startups, policy, and builders across India.",
        "posts": [
            "Builders in Hyderabad / Bangalore / Delhi — what are you shipping this week?",
        ],
    },
]

OFFICIAL_USERNAMES = [a["username"] for a in OFFICIAL_ACCOUNTS]


def seed_official_accounts(db: Session) -> None:
    """Create official accounts + starter posts if missing. Safe to run every boot."""
    created_any = False
    for acct in OFFICIAL_ACCOUNTS:
        user = db.query(models.User).filter(models.User.username == acct["username"]).first()
        if not user:
            user = models.User(
                username=acct["username"],
                display_name=acct["display_name"],
                bio=acct["bio"],
                email=f"{acct['username']}@barathx.com",
                password_hash=auth.hash_password(secrets.token_urlsafe(32)),
                is_email_verified=True,
            )
            db.add(user)
            db.flush()
            created_any = True
            logger.info("Seeded official account @%s", acct["username"])
        else:
            # Keep bios current without overwriting user edits to display name.
            if not (user.bio or "").strip():
                user.bio = acct["bio"]

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


def follow_official_accounts(db: Session, user: models.User) -> int:
    """Auto-follow official BaratX accounts. Returns number of new follows."""
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
