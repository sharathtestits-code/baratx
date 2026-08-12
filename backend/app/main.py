import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app import auth, email as email_service, google_auth, media_store, models, rewards, schemas, seed, sms, text_parse
from app.database import Base, SessionLocal, engine, get_db
from app.extra_routes import register_extra_routes
from app.social_surfaces import register_social_surfaces
from app.spa_serve import spa_shell_allowed, wants_spa_document

Base.metadata.create_all(bind=engine)


def run_migrations():
    """
    Base.metadata.create_all() only creates tables that don't exist yet — it
    never alters existing tables. Add missing columns safely on startup.
    """
    url = str(engine.url)
    with engine.connect() as conn:
        if url.startswith("sqlite"):
            existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
            if "avatar_url" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
            if "cover_url" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN cover_url VARCHAR"))
            if "theme" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR DEFAULT 'saffron'"))
            if "badge" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN badge VARCHAR DEFAULT 'none'"))
            if "is_official" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_official BOOLEAN DEFAULT 0"))
            if "has_posted_once" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN has_posted_once BOOLEAN DEFAULT 0"))

            post_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(posts)"))}
            if "quoted_post_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN quoted_post_id VARCHAR"))
            if "community_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN community_id VARCHAR"))
            if "space_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN space_id VARCHAR"))
            if "debate_side" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN debate_side VARCHAR"))

            # communities arena flags
            try:
                community_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(communities)"))}
                if community_cols:
                    if "is_arena" not in community_cols:
                        conn.execute(text("ALTER TABLE communities ADD COLUMN is_arena BOOLEAN DEFAULT 0"))
                    if "arena_key" not in community_cols:
                        conn.execute(text("ALTER TABLE communities ADD COLUMN arena_key VARCHAR"))
            except Exception:
                pass

            # spaces debate fields
            try:
                space_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(spaces)"))}
                if space_cols:
                    if "kind" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN kind VARCHAR DEFAULT 'room'"))
                    if "community_id" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN community_id VARCHAR"))
                    if "side_for_label" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN side_for_label VARCHAR DEFAULT 'For'"))
                    if "side_against_label" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN side_against_label VARCHAR DEFAULT 'Against'"))
                    if "topic_id" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN topic_id VARCHAR"))
                    if "source_url" not in space_cols:
                        conn.execute(text("ALTER TABLE spaces ADD COLUMN source_url VARCHAR"))
            except Exception:
                pass

            reply_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(replies)"))}
            if "parent_reply_id" not in reply_cols:
                conn.execute(text("ALTER TABLE replies ADD COLUMN parent_reply_id VARCHAR"))

            notif_tables = {
                row[0]
                for row in conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
                )
            }
            if "notifications" in notif_tables:
                notif_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(notifications)"))}
                if "kind" not in notif_cols and "type" in notif_cols:
                    conn.execute(text("ALTER TABLE notifications RENAME COLUMN type TO kind"))
                elif "kind" not in notif_cols:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN kind VARCHAR"))
                if "message" not in notif_cols:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN message VARCHAR"))
        else:
            # Postgres / other: add missing columns if tables already exist.
            def cols(table: str) -> set[str]:
                rows = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :t"
                    ),
                    {"t": table},
                )
                return {r[0] for r in rows}

            user_cols = cols("users")
            if user_cols:
                if "avatar_url" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
                if "cover_url" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN cover_url VARCHAR"))
                if "theme" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR DEFAULT 'saffron'"))
                if "badge" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN badge VARCHAR DEFAULT 'none'"))
                if "is_official" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_official BOOLEAN DEFAULT FALSE"))
                if "has_posted_once" not in user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN has_posted_once BOOLEAN DEFAULT FALSE"))

            post_cols = cols("posts")
            if post_cols and "quoted_post_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN quoted_post_id VARCHAR"))
            if post_cols and "community_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN community_id VARCHAR"))
            if post_cols and "space_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN space_id VARCHAR"))
            if post_cols and "debate_side" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN debate_side VARCHAR"))

            community_cols = cols("communities")
            if community_cols:
                if "is_arena" not in community_cols:
                    conn.execute(text("ALTER TABLE communities ADD COLUMN is_arena BOOLEAN DEFAULT FALSE"))
                if "arena_key" not in community_cols:
                    conn.execute(text("ALTER TABLE communities ADD COLUMN arena_key VARCHAR"))

            space_cols = cols("spaces")
            if space_cols:
                if "kind" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN kind VARCHAR DEFAULT 'room'"))
                if "community_id" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN community_id VARCHAR"))
                if "side_for_label" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN side_for_label VARCHAR DEFAULT 'For'"))
                if "side_against_label" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN side_against_label VARCHAR DEFAULT 'Against'"))
                if "topic_id" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN topic_id VARCHAR"))
                if "source_url" not in space_cols:
                    conn.execute(text("ALTER TABLE spaces ADD COLUMN source_url VARCHAR"))

            reply_cols = cols("replies")
            if reply_cols and "parent_reply_id" not in reply_cols:
                conn.execute(text("ALTER TABLE replies ADD COLUMN parent_reply_id VARCHAR"))

            notif_cols = cols("notifications")
            if notif_cols and "kind" not in notif_cols:
                if "type" in notif_cols:
                    conn.execute(text("ALTER TABLE notifications RENAME COLUMN type TO kind"))
                else:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN kind VARCHAR"))
            if notif_cols and "message" not in notif_cols:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN message VARCHAR"))

        # Lifetime first-post flag: backfill anyone who already has posts.
        try:
            conn.execute(
                text(
                    "UPDATE users SET has_posted_once = TRUE "
                    "WHERE COALESCE(has_posted_once, FALSE) = FALSE "
                    "AND id IN (SELECT DISTINCT author_id FROM posts)"
                )
            )
        except Exception:
            pass

        conn.commit()


run_migrations()

# Cold-start density: official BarathX accounts + starter posts + communities.
with SessionLocal() as _seed_db:
    try:
        seed.seed_official_accounts(_seed_db)
    except Exception:  # noqa: BLE001 — never block API boot on seed
        import logging

        logging.getLogger("baratx").exception("Official account seed failed")
    try:
        seed.seed_default_communities(_seed_db)
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger("baratx").exception("Community seed failed")
    try:
        seed.seed_arenas(_seed_db)
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger("baratx").exception("Arena seed failed")
    try:
        from app import topic_ops

        topic_ops.seed_topics(_seed_db)
        # Second pass catches any partial failure from the first boot attempt.
        if topic_ops.topics_need_seed(_seed_db):
            topic_ops.seed_topics(_seed_db)
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger("baratx").exception("Topic seed failed")
    try:
        from app import topic_ops

        # Best-effort unpaid RSS prompts on boot (non-blocking if network fails).
        topic_ops.refresh_debate_prompts(_seed_db, force=False, per_topic=1, max_topics=24)
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger("baratx").exception("Prompt refresh on boot failed")


app = FastAPI(title="BarathX API", version="0.5.0")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


def mvp_version_info() -> dict:
    """Prod MVP label from VERSION file or MVP_VERSION / VITE_MVP_VERSION env."""
    env_n = (os.environ.get("MVP_VERSION") or os.environ.get("VITE_MVP_VERSION") or "").strip()
    n = env_n if env_n.isdigit() else ""
    if not n:
        for candidate in (
            Path(__file__).resolve().parents[2] / "VERSION",
            Path("/app/VERSION"),
            Path.cwd() / "VERSION",
        ):
            try:
                raw = candidate.read_text(encoding="utf-8").strip()
                if raw.isdigit():
                    n = raw
                    break
            except OSError:
                continue
    if not n:
        n = "1"
    return {"version": n, "mvp": f"MVP{n}"}


_MVP = mvp_version_info()
app.version = _MVP["mvp"]
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "").strip()
_cors_raw = os.environ.get("CORS_ORIGINS", "").strip()
if _cors_raw:
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
elif ENVIRONMENT == "production":
    CORS_ORIGINS = [
        "https://barathx.com",
        "https://baratx.pages.dev",
        # Capacitor native shells (Android https scheme / iOS capacitor scheme)
        "https://localhost",
        "capacitor://localhost",
        "ionic://localhost",
        "http://localhost",
    ]
else:
    CORS_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = media_store.BASE_DIR
MEDIA_DIR = media_store.MEDIA_DIR
os.makedirs(MEDIA_DIR, exist_ok=True)


@app.get("/media/{name}")
def serve_media(name: str):
    """Serve durable DB media (and legacy local files if still present)."""
    loaded = media_store.load_bytes(name)
    if not loaded:
        raise HTTPException(status_code=404, detail="Media not found")
    data, content_type = loaded
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


# Keep StaticFiles as a secondary mount for any odd local paths during local dev.
# Primary serving is the route above (DB-backed on Railway).
if not media_store.use_db_store() and not media_store.s3_enabled():
    app.mount("/media-files", StaticFiles(directory=MEDIA_DIR), name="media_files")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_POST_LENGTH = 500
MAX_REPLY_LENGTH = 220
MAX_AVATAR_BYTES = 3 * 1024 * 1024  # 3MB
MAX_COVER_BYTES = 5 * 1024 * 1024  # 5MB

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)

OTP_TTL_MINUTES = 5
EMAIL_VERIFY_TTL_HOURS = 24
PASSWORD_RESET_TTL_HOURS = 1


def _otp_response(code: str, sms_sent: bool = False) -> dict:
    """Never leak OTP codes in production when SMS was actually sent."""
    body = {
        "message": "OTP sent" if (ENVIRONMENT == "production" or sms_sent) else "OTP generated (demo mode)",
        "expires_in_minutes": OTP_TTL_MINUTES,
        "sms_sent": sms_sent,
    }
    if ENVIRONMENT != "production" or not sms_sent:
        body["dev_otp"] = code
    else:
        print("[otp] generated for production request (not returned in response)")
    return body


def issue_otp(db: Session, phone: str, purpose: str) -> dict:
    try:
        sms.check_otp_rate_limit(phone)
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    code = auth.generate_otp()
    otp = models.OTP(
        phone=phone,
        code=code,
        purpose=purpose,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
    )
    db.add(otp)
    db.commit()
    sms_sent = sms.send_otp_sms(phone, code)
    if not sms_sent:
        print(f"[otp] {purpose} for {phone}: {code} (SMS not sent)")
        # MSG91 configured but send failed — don't silently fall back to leaking OTP in prod UI
        if ENVIRONMENT == "production" and sms.sms_configured():
            raise HTTPException(
                status_code=502,
                detail="Could not send SMS OTP. Check the number and try again, or use Google/email.",
            )
        if ENVIRONMENT == "production" and not sms.sms_configured():
            print("[otp] WARNING: MSG91 not configured — returning demo OTP in response")
    return _otp_response(code, sms_sent=sms_sent)


def issue_email_verification(db: Session, user: models.User) -> tuple[bool, Optional[str]]:
    """Create a verification token and attempt to email it. Returns (sent, dev_url)."""
    if not user.email:
        return False, None

    # Invalidate prior unused tokens for this user
    prior = (
        db.query(models.EmailVerificationToken)
        .filter(
            models.EmailVerificationToken.user_id == user.id,
            models.EmailVerificationToken.consumed == False,  # noqa: E712
        )
        .all()
    )
    for row in prior:
        row.consumed = True

    raw = secrets.token_urlsafe(32)
    row = models.EmailVerificationToken(
        user_id=user.id,
        token=raw,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFY_TTL_HOURS),
    )
    db.add(row)
    db.commit()

    try:
        sent, verify_url = email_service.send_verification_email(
            user.email, user.display_name, raw
        )
    except Exception as exc:  # noqa: BLE001 — surface as soft failure; account still created
        print(f"[email] failed to send verification to {user.email}: {exc}")
        verify_url = email_service.build_verify_url(raw)
        sent = False

    dev_url = None
    if not sent and ENVIRONMENT != "production":
        dev_url = verify_url
        print(f"[email] DEV verify URL for {user.email}: {verify_url}")
    return sent, dev_url


async def save_upload_image(image: UploadFile, max_bytes: int) -> str:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Image must be JPEG, PNG, GIF, or WEBP")

    contents = await image.read()
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"Image must be {max_bytes // (1024 * 1024)}MB or smaller")

    return media_store.save_bytes(
        contents,
        content_type=image.content_type or "application/octet-stream",
        filename=image.filename,
    )


def delete_media_file(url: Optional[str]):
    media_store.delete_url(url)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user_id = auth.decode_access_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if not creds:
        return None
    user_id = auth.decode_access_token(creds.credentials)
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()


def serialize_user(user: models.User, current_user: Optional[models.User]) -> schemas.UserOut:
    is_following = False
    if current_user:
        is_following = any(f.followed_id == user.id for f in current_user.following)
    badge = (getattr(user, "badge", None) or "none").strip().lower()
    if badge not in ("none", "gold", "blue"):
        badge = "none"
    is_official = bool(getattr(user, "is_official", False) or badge == "blue")
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        phone=user.phone,
        language=user.language,
        theme=getattr(user, "theme", None) or "midnight",
        bio=user.bio,
        is_email_verified=user.is_email_verified,
        is_phone_verified=user.is_phone_verified,
        badge=badge,
        is_official=is_official,
        created_at=user.created_at,
        avatar_url=user.avatar_url,
        cover_url=user.cover_url,
        follower_count=len(user.followers),
        following_count=len(user.following),
        is_following=is_following,
    )


def author_out(user: models.User) -> schemas.AuthorOut:
    badge = (getattr(user, "badge", None) or "none").strip().lower()
    if badge not in ("none", "gold", "blue"):
        badge = "none"
    return schemas.AuthorOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        badge=badge,
        is_official=bool(getattr(user, "is_official", False) or badge == "blue"),
    )


def serialize_post(post: models.Post, current_user: Optional[models.User]) -> schemas.PostOut:
    liked_by_me = False
    reposted_by_me = False
    bookmarked_by_me = False
    if current_user:
        liked_by_me = any(like.user_id == current_user.id for like in post.likes)
        reposted_by_me = any(r.user_id == current_user.id for r in post.reposts)
        from sqlalchemy.orm import object_session

        sess = object_session(post)
        if sess is not None:
            bookmarked_by_me = (
                sess.query(models.Bookmark.id)
                .filter(models.Bookmark.user_id == current_user.id, models.Bookmark.post_id == post.id)
                .first()
                is not None
            )

    quoted = None
    if getattr(post, "quoted_post_id", None) and post.quoted_post is not None:
        qp = post.quoted_post
        quoted = schemas.QuotedPostOut(
            id=qp.id,
            text=text_parse.sanitize_user_text(qp.text or ""),
            image_url=qp.image_url,
            created_at=qp.created_at,
            author=author_out(qp.author),
        )

    tags = text_parse.extract_hashtags(post.text)
    safe_text = text_parse.sanitize_user_text(post.text or "")

    return schemas.PostOut(
        id=post.id,
        text=safe_text,
        image_url=post.image_url,
        created_at=post.created_at,
        author=author_out(post.author),
        like_count=len(post.likes),
        reply_count=len(post.replies),
        repost_count=len(post.reposts),
        liked_by_me=liked_by_me,
        reposted_by_me=reposted_by_me,
        bookmarked_by_me=bookmarked_by_me,
        quoted_post=quoted,
        hashtags=tags,
        debate_side=getattr(post, "debate_side", None),
        space_id=getattr(post, "space_id", None),
    )


def serialize_reply(reply: models.Reply, current_user: Optional[models.User]) -> schemas.ReplyOut:
    liked_by_me = False
    if current_user:
        liked_by_me = any(like.user_id == current_user.id for like in reply.likes)
    return schemas.ReplyOut(
        id=reply.id,
        post_id=reply.post_id,
        text=text_parse.sanitize_user_text(reply.text or ""),
        created_at=reply.created_at,
        author=author_out(reply.author),
        like_count=len(reply.likes),
        liked_by_me=liked_by_me,
        parent_reply_id=getattr(reply, "parent_reply_id", None),
    )


def attach_hashtags(db: Session, post: models.Post, text: str):
    for tag in text_parse.extract_hashtags(text):
        ht = db.query(models.Hashtag).filter(models.Hashtag.tag == tag).first()
        if not ht:
            ht = models.Hashtag(tag=tag)
            db.add(ht)
            db.flush()
        exists = (
            db.query(models.PostHashtag)
            .filter(models.PostHashtag.post_id == post.id, models.PostHashtag.hashtag_id == ht.id)
            .first()
        )
        if not exists:
            db.add(models.PostHashtag(post_id=post.id, hashtag_id=ht.id))


def notify_mentions(
    db: Session,
    actor_id: str,
    text: str,
    post_id: Optional[str] = None,
    reply_id: Optional[str] = None,
    exclude_ids: Optional[set] = None,
):
    """Notify users tagged with @username in a post or reply (skips actor + exclude_ids)."""
    skip = set(exclude_ids or set())
    skip.add(actor_id)
    for username in text_parse.extract_mentions(text):
        user = (
            db.query(models.User)
            .filter(models.User.username.ilike(username))
            .first()
        )
        if user and user.id not in skip:
            create_notification(
                db,
                recipient_id=user.id,
                actor_id=actor_id,
                kind="mention",
                post_id=post_id,
                reply_id=reply_id,
            )
            skip.add(user.id)


def hidden_author_ids(db: Session, current_user: Optional[models.User]) -> set[str]:
    if not current_user:
        return set()
    blocked = {
        r[0]
        for r in db.query(models.Block.blocked_id).filter(models.Block.blocker_id == current_user.id).all()
    }
    blocked_by = {
        r[0]
        for r in db.query(models.Block.blocker_id).filter(models.Block.blocked_id == current_user.id).all()
    }
    muted = {
        r[0]
        for r in db.query(models.Mute.muted_id).filter(models.Mute.muter_id == current_user.id).all()
    }
    return blocked | blocked_by | muted


def create_notification(
    db: Session,
    *,
    recipient_id: str,
    actor_id: str,
    kind: str,
    post_id: Optional[str] = None,
    reply_id: Optional[str] = None,
    message: Optional[str] = None,
):
    if recipient_id == actor_id:
        return
    db.add(
        models.Notification(
            recipient_id=recipient_id,
            actor_id=actor_id,
            kind=kind,
            post_id=post_id,
            reply_id=reply_id,
            message=(message or None),
        )
    )
    # Retention: email when possible (never fail the social action).
    try:
        recipient = db.query(models.User).filter(models.User.id == recipient_id).first()
        actor = db.query(models.User).filter(models.User.id == actor_id).first()
        if not recipient or not actor or not recipient.email:
            return
        preview = message
        if not preview and reply_id:
            reply = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
            if reply:
                preview = reply.text
        elif not preview and post_id:
            post = db.query(models.Post).filter(models.Post.id == post_id).first()
            if post:
                preview = post.text
        email_service.send_activity_email(
            recipient.email,
            recipient.display_name or recipient.username,
            actor.display_name or actor.username,
            actor.username,
            kind,
            preview=preview,
            post_id=post_id,
        )
    except Exception:  # noqa: BLE001
        pass


def serialize_notification(n: models.Notification) -> schemas.NotificationOut:
    preview = None
    reply_preview = None
    if n.post is not None:
        preview = (n.post.text or "")[:140]
    if n.reply is not None:
        reply_preview = (n.reply.text or "")[:140]
    actor = n.actor
    if actor is None:
        actor = schemas.AuthorOut(
            id=n.actor_id or "unknown",
            username="deleted",
            display_name="Deleted account",
            avatar_url=None,
            badge="none",
            is_official=False,
        )
    else:
        actor = author_out(actor)
    return schemas.NotificationOut(
        id=n.id,
        type=n.kind,
        created_at=n.created_at,
        is_read=n.is_read,
        actor=actor,
        post_id=n.post_id,
        post_preview=preview,
        reply_preview=reply_preview,
        message=getattr(n, "message", None),
    )


@app.get("/health")
def health():
    info = mvp_version_info()
    return {"status": "ok", "mvp": info["mvp"], "version": info["version"], "environment": ENVIRONMENT}


# ---------- Admin (password-protected signup insights) ----------

def require_admin(x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret")):
    if not ADMIN_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Admin is not configured on this environment.",
        )
    if not x_admin_secret or not secrets.compare_digest(x_admin_secret, ADMIN_SECRET):
        raise HTTPException(status_code=401, detail="Invalid admin secret")
    return True


def _signup_method(user: models.User) -> str:
    if user.phone and not user.email:
        return "phone"
    if user.email:
        return "email"
    if user.phone:
        return "phone"
    return "unknown"


@app.get("/admin/stats", response_model=schemas.AdminStatsOut)
def admin_stats(_: bool = Depends(require_admin), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    posters_subq = db.query(models.Post.author_id).distinct().subquery()
    posters_24h_subq = (
        db.query(models.Post.author_id)
        .filter(models.Post.created_at >= day_ago)
        .distinct()
        .subquery()
    )
    return schemas.AdminStatsOut(
        total_users=db.query(func.count(models.User.id)).scalar() or 0,
        users_last_24h=db.query(func.count(models.User.id))
        .filter(models.User.created_at >= day_ago)
        .scalar()
        or 0,
        users_last_7d=db.query(func.count(models.User.id))
        .filter(models.User.created_at >= week_ago)
        .scalar()
        or 0,
        with_email=db.query(func.count(models.User.id))
        .filter(models.User.email.isnot(None))
        .scalar()
        or 0,
        with_phone=db.query(func.count(models.User.id))
        .filter(models.User.phone.isnot(None))
        .scalar()
        or 0,
        email_verified=db.query(func.count(models.User.id))
        .filter(models.User.is_email_verified.is_(True))
        .scalar()
        or 0,
        phone_verified=db.query(func.count(models.User.id))
        .filter(models.User.is_phone_verified.is_(True))
        .scalar()
        or 0,
        total_posts=db.query(func.count(models.Post.id)).scalar() or 0,
        posts_last_24h=db.query(func.count(models.Post.id))
        .filter(models.Post.created_at >= day_ago)
        .scalar()
        or 0,
        users_with_posts=db.query(func.count()).select_from(posters_subq).scalar() or 0,
        posters_last_24h=db.query(func.count()).select_from(posters_24h_subq).scalar() or 0,
    )


@app.get("/suggestions")
def get_suggestions(
    surface: str = "square",
    arena: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    """Top 15–20 debate questions/problems for Square or an Arena tab."""
    from app import suggestions as suggestions_mod

    return suggestions_mod.list_suggestions(
        db, surface=surface, arena_key=arena, limit=limit
    )


@app.get("/admin/users", response_model=schemas.AdminUsersOut)
def admin_users(
    limit: int = 50,
    offset: int = 0,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    total = db.query(func.count(models.User.id)).scalar() or 0
    rows = (
        db.query(models.User)
        .order_by(models.User.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return schemas.AdminUsersOut(
        total=total,
        limit=limit,
        offset=offset,
        users=[
            schemas.AdminUserRow(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                email=u.email,
                phone=u.phone,
                is_email_verified=bool(u.is_email_verified),
                is_phone_verified=bool(u.is_phone_verified),
                badge=(getattr(u, "badge", None) or "none"),
                is_official=bool(getattr(u, "is_official", False) or (getattr(u, "badge", None) == "blue")),
                created_at=u.created_at,
                signup_method=_signup_method(u),
            )
            for u in rows
        ],
    )


@app.delete("/admin/users/{user_id}", response_model=schemas.MessageResponse)
def admin_delete_user(
    user_id: str,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Remove a misleading / abusive account. Protected blue founders cannot be deleted.
    Admins can act immediately — no queue wait. Auto-mod also deletes after repeated reports.
    """
    from app.moderation import purge_user

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username in seed.PROTECTED_BLUE_USERNAMES:
        raise HTTPException(status_code=400, detail="Cannot delete protected blue official accounts")
    username = user.username
    purge_user(db, user)
    db.commit()
    return schemas.MessageResponse(message=f"Deleted @{username}")


@app.delete("/admin/posts/{post_id}", response_model=schemas.MessageResponse)
def admin_delete_post(
    post_id: str,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Remove a misleading post."""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.query(models.Notification).filter(models.Notification.post_id == post.id).delete(
        synchronize_session=False
    )
    db.query(models.Bookmark).filter(models.Bookmark.post_id == post.id).delete(
        synchronize_session=False
    )
    db.query(models.PostHashtag).filter(models.PostHashtag.post_id == post.id).delete(
        synchronize_session=False
    )
    db.delete(post)
    db.commit()
    return schemas.MessageResponse(message="Post deleted")


@app.post("/admin/users/{user_id}/badge", response_model=schemas.AdminUserRow)
def admin_set_user_badge(
    user_id: str,
    payload: schemas.BadgeUpdate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin secret can set badges (including demote) without logging in as blue."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username in seed.PROTECTED_BLUE_USERNAMES and payload.badge != "blue":
        raise HTTPException(status_code=400, detail="Cannot demote protected blue founders")

    current = (getattr(user, "badge", None) or "none").strip().lower()
    if current not in ("none", "gold", "blue"):
        current = "none"
    new_badge = payload.badge
    if new_badge != current:
        if new_badge == "blue" and current not in ("gold", "blue"):
            # Admin may grant blue directly for ops, but prefer gold→blue in product UI.
            pass
        seed._apply_badge(user, new_badge)
        if payload.notify:
            try:
                # Notify as @baratx when possible.
                actor = db.query(models.User).filter(models.User.username == "baratx").first()
                if actor and actor.id != user.id:
                    if current == "blue" and new_badge == "gold":
                        msg = "demoted your blue official status to gold."
                    elif current == "gold" and new_badge == "none":
                        msg = "removed your gold status."
                    elif new_badge == "gold":
                        msg = "granted you gold status."
                    elif new_badge == "blue":
                        msg = "promoted you to blue official."
                    else:
                        msg = f"updated your account badge to {new_badge}."
                    create_notification(
                        db,
                        recipient_id=user.id,
                        actor_id=actor.id,
                        kind="badge",
                        message=msg,
                    )
            except Exception:  # noqa: BLE001
                pass
        db.commit()
        db.refresh(user)

    return schemas.AdminUserRow(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        phone=user.phone,
        is_email_verified=bool(user.is_email_verified),
        is_phone_verified=bool(user.is_phone_verified),
        badge=(getattr(user, "badge", None) or "none"),
        is_official=bool(getattr(user, "is_official", False) or (getattr(user, "badge", None) == "blue")),
        created_at=user.created_at,
        signup_method=_signup_method(user),
    )


@app.post("/admin/posts", response_model=schemas.PostOut)
def admin_create_post(
    payload: schemas.AdminPostCreate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Post as an official BarathX account using ADMIN_SECRET (no user login)."""
    author = _official_author(db, payload.username)

    post = models.Post(author_id=author.id, text=payload.text)
    db.add(post)
    db.flush()
    attach_hashtags(db, post, payload.text)
    notify_mentions(db, author.id, payload.text, post_id=post.id)
    db.commit()
    db.refresh(post)
    return serialize_post(post, author)


@app.get("/admin/recent-posts", response_model=schemas.AdminRecentPostsOut)
def admin_recent_posts(
    limit: int = 30,
    new_users_only: bool = True,
    days: int = 7,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Recent posts from community members — for welcoming new joiners with replies."""
    limit = max(1, min(limit, 100))
    days = max(1, min(days, 30))
    official = set(seed.OFFICIAL_USERNAMES)
    q = (
        db.query(models.Post)
        .join(models.User, models.User.id == models.Post.author_id)
        .filter(~models.User.username.in_(official))
    )
    if new_users_only:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        q = q.filter(models.User.created_at >= since)
    total = q.count()
    rows = q.order_by(models.Post.created_at.desc()).limit(limit).all()
    return schemas.AdminRecentPostsOut(
        total=total,
        posts=[serialize_post(p, None) for p in rows],
    )


@app.post("/admin/replies", response_model=schemas.ReplyOut)
def admin_create_reply(
    payload: schemas.AdminReplyCreate,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Reply as an official BarathX account using ADMIN_SECRET (no user login)."""
    author = _official_author(db, payload.username)
    post = db.query(models.Post).filter(models.Post.id == payload.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    text = text_parse.sanitize_user_text(payload.text).strip()
    reply = models.Reply(
        post_id=post.id,
        author_id=author.id,
        text=text,
        parent_reply_id=None,
    )
    db.add(reply)
    db.flush()
    create_notification(
        db,
        recipient_id=post.author_id,
        actor_id=author.id,
        kind="reply",
        post_id=post.id,
        reply_id=reply.id,
    )
    notify_mentions(
        db,
        author.id,
        text,
        post_id=post.id,
        reply_id=reply.id,
        exclude_ids={post.author_id},
    )
    db.commit()
    db.refresh(reply)
    return serialize_reply(reply, author)


@app.post("/admin/engage/purge-slop")
def admin_purge_engage_slop(
    only_slop_phrases: bool = False,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete @baratx / @sharath auto-engage replies (default: all of them)."""
    from app import engagement_replies

    return engagement_replies.purge_engage_slop_replies(db, only_slop_phrases=only_slop_phrases)


@app.post("/admin/backfill-post-notifications")
def admin_backfill_post_notifications(
    days: int = 14,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create missing 'post' Alerts for @baratx/@sharath on recent community posts."""
    days = max(1, min(days, 60))
    since = datetime.now(timezone.utc) - timedelta(days=days)
    officials = (
        db.query(models.User)
        .filter(models.User.username.in_(("baratx", "sharath")))
        .all()
    )
    if not officials:
        return {"ok": False, "error": "officials_missing", "created": 0}

    official_ids = {u.id for u in officials}
    official_names = set(seed.OFFICIAL_USERNAMES)
    posts = (
        db.query(models.Post)
        .join(models.User, models.User.id == models.Post.author_id)
        .filter(models.Post.created_at >= since)
        .filter(models.Post.community_id.is_(None))
        .filter(~models.User.username.in_(official_names))
        .order_by(models.Post.created_at.desc())
        .limit(200)
        .all()
    )
    created = 0
    for post in posts:
        for official in officials:
            exists = (
                db.query(models.Notification.id)
                .filter(
                    models.Notification.recipient_id == official.id,
                    models.Notification.actor_id == post.author_id,
                    models.Notification.kind == "post",
                    models.Notification.post_id == post.id,
                )
                .first()
            )
            if exists:
                continue
            if post.author_id in official_ids:
                continue
            create_notification(
                db,
                recipient_id=official.id,
                actor_id=post.author_id,
                kind="post",
                post_id=post.id,
                message=(post.text or "")[:140] or None,
            )
            created += 1
    db.commit()
    return {"ok": True, "created": created, "posts_scanned": len(posts)}


def _official_author(db: Session, username: str) -> models.User:
    if username not in set(seed.OFFICIAL_USERNAMES):
        raise HTTPException(
            status_code=400,
            detail=f"Can only act as official accounts: {', '.join(seed.OFFICIAL_USERNAMES)}",
        )
    author = db.query(models.User).filter(models.User.username == username).first()
    if not author:
        raise HTTPException(status_code=404, detail=f"@{username} not found — seed may not have run")
    return author


# ---------- Email signup / login ----------

@app.post("/auth/signup/email", response_model=schemas.TokenResponse)
def signup_email(payload: schemas.EmailSignupRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=payload.username,
        display_name=payload.display_name,
        email=payload.email,
        password_hash=auth.hash_password(payload.password),
        is_email_verified=False,
        badge="none",
        is_official=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    seed.follow_official_accounts(db, user)
    db.commit()

    sent, dev_url = issue_email_verification(db, user)

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(
        access_token=token,
        email_verification_sent=sent,
        dev_verify_url=dev_url,
    )


@app.post("/auth/verify-email", response_model=schemas.MessageResponse)
def verify_email(payload: schemas.VerifyEmailRequest, db: Session = Depends(get_db)):
    row = (
        db.query(models.EmailVerificationToken)
        .filter(
            models.EmailVerificationToken.token == payload.token,
            models.EmailVerificationToken.consumed == False,  # noqa: E712
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or already used verification link")

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification link expired — request a new one")

    user = db.query(models.User).filter(models.User.id == row.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    row.consumed = True
    user.is_email_verified = True
    db.commit()
    return schemas.MessageResponse(message="Email confirmed. Your BarathX account is active.")


@app.post("/auth/resend-verification", response_model=schemas.MessageResponse)
def resend_verification(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.email:
        raise HTTPException(status_code=400, detail="No email on this account")
    if current_user.is_email_verified:
        return schemas.MessageResponse(message="Email is already verified")

    sent, dev_url = issue_email_verification(db, current_user)
    if sent:
        return schemas.MessageResponse(
            message="Verification email sent. Check your inbox.",
            email_verification_sent=True,
        )
    if ENVIRONMENT == "production":
        raise HTTPException(
            status_code=503,
            detail="Email delivery is not configured yet. Try again later.",
        )
    return schemas.MessageResponse(
        message="Email provider not configured — use the development verify link.",
        email_verification_sent=False,
        dev_verify_url=dev_url,
    )


@app.post("/auth/forgot-password", response_model=schemas.MessageResponse)
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Always returns a generic success message to avoid email enumeration."""
    generic = schemas.MessageResponse(
        message="If that email is registered, we sent a password reset link."
    )
    user = db.query(models.User).filter(models.User.email == str(payload.email).lower()).first()
    if not user or not user.email:
        return generic

    prior = (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.user_id == user.id,
            models.PasswordResetToken.consumed == False,  # noqa: E712
        )
        .all()
    )
    for row in prior:
        row.consumed = True

    raw = secrets.token_urlsafe(32)
    row = models.PasswordResetToken(
        user_id=user.id,
        token=raw,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_TTL_HOURS),
    )
    db.add(row)
    db.commit()

    try:
        sent, reset_url = email_service.send_password_reset_email(
            user.email, user.display_name, raw
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[email] failed to send password reset to {user.email}: {exc}")
        sent = False
        reset_url = email_service.build_reset_url(raw)

    if sent:
        return generic
    if ENVIRONMENT == "production":
        raise HTTPException(
            status_code=503,
            detail="Email delivery is not configured yet. Try again later.",
        )
    return schemas.MessageResponse(
        message="Email provider not configured — use the development reset link.",
        dev_reset_url=reset_url,
    )


@app.post("/auth/reset-password", response_model=schemas.MessageResponse)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    row = (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.token == payload.token,
            models.PasswordResetToken.consumed == False,  # noqa: E712
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or already used reset link")

    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset link expired. Request a new one.")

    user = db.query(models.User).filter(models.User.id == row.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    row.consumed = True
    user.password_hash = auth.hash_password(payload.password)
    db.commit()
    return schemas.MessageResponse(message="Password updated. You can sign in with your new password.")


@app.post("/auth/login/email", response_model=schemas.TokenResponse)
def login_email(payload: schemas.EmailLoginRequest, db: Session = Depends(get_db)):
    ident = payload.email.strip()
    if "@" in ident:
        user = db.query(models.User).filter(models.User.email == ident.lower()).first()
    else:
        user = db.query(models.User).filter(models.User.username == ident).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email/username or password")

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


@app.post("/auth/google", response_model=schemas.TokenResponse)
def auth_google(payload: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    if not google_auth.google_configured():
        raise HTTPException(
            status_code=503,
            detail="Google sign-in is not configured. Set GOOGLE_CLIENT_ID on the API.",
        )
    try:
        claims = google_auth.verify_google_id_token(payload.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    email = claims["email"].lower().strip()
    display_name = (claims.get("name") or email.split("@")[0])[:50]
    picture = claims.get("picture")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        if not payload.confirm_age_18:
            raise HTTPException(
                status_code=400,
                detail="You must be 18 or older to join BarathX. Confirm your age to continue.",
            )
        base = "".join(ch for ch in email.split("@")[0].lower() if ch.isalnum() or ch == "_")[:16] or "user"
        username = base
        n = 0
        while db.query(models.User).filter(models.User.username == username).first():
            n += 1
            username = f"{base}{n}"[:20]

        user = models.User(
            username=username,
            display_name=display_name,
            email=email,
            password_hash=auth.hash_password(secrets.token_urlsafe(24)),
            is_email_verified=True,
            avatar_url=picture,
            badge="none",
            is_official=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        seed.follow_official_accounts(db, user)
        db.commit()
    else:
        if not user.is_email_verified:
            user.is_email_verified = True
            db.commit()

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


# ---------- Phone + OTP signup / login ----------
# Uses MSG91 when MSG91_AUTH_KEY + MSG91_TEMPLATE_ID are set; otherwise demo OTP
# (dev_otp) is returned for local testing. OTP requests are rate-limited.

@app.post("/auth/signup/phone/request-otp")
def signup_phone_request_otp(payload: schemas.PhoneOtpRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return issue_otp(db, payload.phone, "signup")


@app.post("/auth/signup/phone/verify", response_model=schemas.TokenResponse)
def signup_phone_verify(payload: schemas.PhoneSignupVerify, db: Session = Depends(get_db)):
    otp_row = (
        db.query(models.OTP)
        .filter(
            models.OTP.phone == payload.phone,
            models.OTP.purpose == "signup",
            models.OTP.consumed == False,  # noqa: E712
        )
        .order_by(models.OTP.created_at.desc())
        .first()
    )
    if not otp_row or otp_row.code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp_row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired, request a new one")

    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(models.User).filter(models.User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    otp_row.consumed = True

    user = models.User(
        username=payload.username,
        display_name=payload.display_name,
        phone=payload.phone,
        password_hash=auth.hash_password(auth.generate_otp() + payload.phone),  # unused placeholder hash
        is_phone_verified=True,
        badge="none",
        is_official=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    seed.follow_official_accounts(db, user)
    db.commit()

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


@app.post("/auth/login/phone/request-otp")
def login_phone_request_otp(payload: schemas.PhoneOtpRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == payload.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account with this phone number")
    return issue_otp(db, payload.phone, "login")


@app.post("/auth/login/phone/verify", response_model=schemas.TokenResponse)
def login_phone_verify(payload: schemas.PhoneLoginVerify, db: Session = Depends(get_db)):
    otp_row = (
        db.query(models.OTP)
        .filter(
            models.OTP.phone == payload.phone,
            models.OTP.purpose == "login",
            models.OTP.consumed == False,  # noqa: E712
        )
        .order_by(models.OTP.created_at.desc())
        .first()
    )
    if not otp_row or otp_row.code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if otp_row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired, request a new one")

    user = db.query(models.User).filter(models.User.phone == payload.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account with this phone number")

    otp_row.consumed = True
    db.commit()

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


# ---------- Profile ----------

@app.get("/users/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize_user(current_user, current_user)


@app.post("/users/me/bootstrap-follows", response_model=schemas.MessageResponse)
def bootstrap_follows(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """One-tap follow of official BarathX accounts (idempotent)."""
    added = seed.follow_official_accounts(db, current_user)
    db.commit()
    if added:
        return schemas.MessageResponse(message=f"Following {added} official BarathX account(s).")
    return schemas.MessageResponse(message="You’re already following official BarathX accounts.")


@app.patch("/users/me", response_model=schemas.UserOut)
def update_me(
    payload: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "display_name" in data:
        current_user.display_name = data["display_name"]
    if "bio" in data:
        current_user.bio = data["bio"]
    if "language" in data:
        current_user.language = data["language"]
    if "theme" in data:
        current_user.theme = data["theme"]
    if "username" in data:
        new_username = data["username"]
        reserved = set(seed.OFFICIAL_USERNAMES) | {
            "admin",
            "support",
            "barathx",
            "help",
            "official",
        }
        if new_username in reserved:
            raise HTTPException(status_code=400, detail="That username is reserved")
        if new_username != current_user.username:
            taken = (
                db.query(models.User)
                .filter(models.User.username == new_username, models.User.id != current_user.id)
                .first()
            )
            if taken:
                raise HTTPException(status_code=400, detail="Username already taken")
            current_user.username = new_username

    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user, current_user)


@app.get("/users/{username}", response_model=schemas.UserOut)
def get_public_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user, current_user)


@app.post("/users/{username}/badge", response_model=schemas.UserOut)
def set_user_badge(
    username: str,
    payload: schemas.BadgeUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Blue accounts manage badges: grant gold, promote gold→blue, demote blue→gold, gold→none."""
    actor_badge = (getattr(current_user, "badge", None) or "none").strip().lower()
    actor_ok = (
        actor_badge == "blue"
        or bool(getattr(current_user, "is_official", False))
        or current_user.username in seed.PROTECTED_BLUE_USERNAMES
    )
    if not actor_ok:
        raise HTTPException(status_code=403, detail="Only blue official accounts can manage badges")

    target = db.query(models.User).filter(models.User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own badge here")
    if target.username in seed.PROTECTED_BLUE_USERNAMES and payload.badge != "blue":
        raise HTTPException(status_code=400, detail="Cannot demote protected blue founders")

    current = (getattr(target, "badge", None) or "none").strip().lower()
    if current not in ("none", "gold", "blue"):
        current = "none"
    new_badge = payload.badge

    if new_badge == current:
        return serialize_user(target, current_user)

    if new_badge == "blue":
        if current != "gold":
            raise HTTPException(
                status_code=400,
                detail="Only gold accounts can be promoted to blue. Grant gold first.",
            )
    elif new_badge == "gold":
        # From none (grant) or from blue (demote for security) — both allowed.
        if current not in ("none", "blue"):
            raise HTTPException(status_code=400, detail="Cannot set gold from this status")
    elif new_badge == "none":
        # Gold → no color. Blue must step down to gold first.
        if current == "blue":
            raise HTTPException(status_code=400, detail="Demote blue to gold first, then remove gold")
        if current != "gold":
            raise HTTPException(status_code=400, detail="Only gold accounts can be cleared to no color")

    seed._apply_badge(target, new_badge)

    # Optional in-app notification — never block the badge change if notify fails.
    if payload.notify:
        try:
            if current == "blue" and new_badge == "gold":
                msg = "demoted your blue official status to gold."
            elif current == "gold" and new_badge == "none":
                msg = "removed your gold status."
            elif current == "none" and new_badge == "gold":
                msg = "granted you gold status."
            elif current == "gold" and new_badge == "blue":
                msg = "promoted you to blue official."
            else:
                msg = f"updated your account badge to {new_badge}."
            create_notification(
                db,
                recipient_id=target.id,
                actor_id=current_user.id,
                kind="badge",
                message=msg,
            )
        except Exception:  # noqa: BLE001
            pass

    db.commit()
    db.refresh(target)
    return serialize_user(target, current_user)


def _post_has_attached_media(url: Optional[str]) -> bool:
    u = (url or "").strip()
    if not u or u in ("null", "undefined"):
        return False
    low = u.lower()
    if "/media/" in low:
        return True
    if low.startswith("data:image/"):
        return True
    if low.startswith("http://") or low.startswith("https://"):
        return bool(re.search(r"\.(png|jpe?g|gif|webp|avif)(\?|#|$)", low) or "/media/" in low)
    return bool(re.search(r"\.(png|jpe?g|gif|webp|avif)(\?|#|$)", low))


@app.get("/users/{username}/posts", response_model=list[schemas.PostOut])
def get_user_posts(
    username: str,
    limit: int = 20,
    before: Optional[str] = None,
    tab: str = "square",  # square | echoes | media | arenas
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    limit = max(1, min(limit, 50))
    tab_key = (tab or "square").strip().lower()
    if tab_key not in ("square", "echoes", "media", "arenas"):
        raise HTTPException(status_code=400, detail="Invalid tab")

    if tab_key == "echoes":
        # Echoes = posts this user reposted (not engagement on their own posts).
        query = (
            db.query(models.Post)
            .join(models.Repost, models.Repost.post_id == models.Post.id)
            .filter(models.Repost.user_id == user.id)
            .order_by(models.Repost.created_at.desc())
        )
        if before:
            try:
                cursor = datetime.fromisoformat(before)
                query = query.filter(models.Repost.created_at < cursor)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid 'before' timestamp")
        posts = query.limit(limit).all()
        return [serialize_post(p, current_user) for p in posts]

    query = db.query(models.Post).filter(models.Post.author_id == user.id)
    if tab_key == "arenas":
        query = query.filter(models.Post.space_id.isnot(None))
    query = query.order_by(models.Post.created_at.desc())
    if before:
        try:
            cursor = datetime.fromisoformat(before)
            query = query.filter(models.Post.created_at < cursor)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' timestamp")

    if tab_key == "media":
        # Wider window, then keep only posts with a real attached image.
        candidates = query.limit(max(limit * 8, 80)).all()
        media_posts = [p for p in candidates if _post_has_attached_media(getattr(p, "image_url", None))]
        return [serialize_post(p, current_user) for p in media_posts[:limit]]

    posts = query.limit(limit).all()
    return [serialize_post(p, current_user) for p in posts]


# ---------- Avatar / cover photo ----------

@app.post("/users/me/avatar", response_model=schemas.UserOut)
async def upload_avatar(
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = await save_upload_image(image, MAX_AVATAR_BYTES)
    delete_media_file(current_user.avatar_url)
    current_user.avatar_url = url
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user, current_user)


@app.delete("/users/me/avatar", response_model=schemas.UserOut)
def remove_avatar(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_media_file(current_user.avatar_url)
    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user, current_user)


@app.post("/users/me/cover", response_model=schemas.UserOut)
async def upload_cover(
    image: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = await save_upload_image(image, MAX_COVER_BYTES)
    delete_media_file(current_user.cover_url)
    current_user.cover_url = url
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user, current_user)


@app.delete("/users/me/cover", response_model=schemas.UserOut)
def remove_cover(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_media_file(current_user.cover_url)
    current_user.cover_url = None
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user, current_user)


# ---------- Follow ----------

@app.post("/users/{username}/follow", response_model=schemas.UserOut)
def follow_user(
    username: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = db.query(models.User).filter(models.User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't follow yourself")

    existing = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == current_user.id, models.Follow.followed_id == target.id)
        .first()
    )
    if not existing:
        db.add(models.Follow(follower_id=current_user.id, followed_id=target.id))
        create_notification(
            db,
            recipient_id=target.id,
            actor_id=current_user.id,
            kind="follow",
        )
        db.commit()
        db.refresh(target)
        db.refresh(current_user)

    return serialize_user(target, current_user)


@app.delete("/users/{username}/follow", response_model=schemas.UserOut)
def unfollow_user(
    username: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = db.query(models.User).filter(models.User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == current_user.id, models.Follow.followed_id == target.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        db.refresh(target)
        db.refresh(current_user)

    return serialize_user(target, current_user)


@app.get("/users/{username}/followers", response_model=list[schemas.UserOut])
def list_followers(
    username: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = max(1, min(limit, 100))
    follows = (
        db.query(models.Follow)
        .filter(models.Follow.followed_id == user.id)
        .order_by(models.Follow.created_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_user(f.follower, current_user) for f in follows]


@app.get("/users/{username}/following", response_model=list[schemas.UserOut])
def list_following(
    username: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    limit = max(1, min(limit, 100))
    follows = (
        db.query(models.Follow)
        .filter(models.Follow.follower_id == user.id)
        .order_by(models.Follow.created_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_user(f.followed, current_user) for f in follows]


# ---------- Posts / feed ----------

@app.post("/posts", response_model=schemas.PostOut)
async def create_post(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    quote_post_id: Optional[str] = Form(None),
    civic_problem: Optional[str] = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    text = text_parse.sanitize_user_text(text).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Post text cannot be empty")
    if len(text) > MAX_POST_LENGTH:
        raise HTTPException(status_code=400, detail=f"Post must be {MAX_POST_LENGTH} characters or fewer")

    quoted_post_id = None
    if quote_post_id:
        quoted = db.query(models.Post).filter(models.Post.id == quote_post_id).first()
        if not quoted:
            raise HTTPException(status_code=404, detail="Quoted post not found")
        quoted_post_id = quoted.id

    image_url = None
    if image is not None and image.filename:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Image must be JPEG, PNG, GIF, or WEBP")

        contents = await image.read()
        if len(contents) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=400, detail="Image must be 5MB or smaller")

        image_url = media_store.save_bytes(
            contents,
            content_type=image.content_type or "application/octet-stream",
            filename=image.filename,
        )

    post = models.Post(
        author_id=current_user.id,
        text=text,
        image_url=image_url,
        quoted_post_id=quoted_post_id,
    )
    # Lifetime welcome: fire once per account even if every post is later deleted.
    is_first_post = not bool(getattr(current_user, "has_posted_once", False))
    if is_first_post:
        current_user.has_posted_once = True
    db.add(post)
    db.flush()
    attach_hashtags(db, post, text)
    notify_mentions(db, current_user.id, text, post_id=post.id)

    # Traction: @baratx + @sharath reply first.
    # First post → welcome + content-aware takes; every later post → human takes.
    # Official replies never count toward Founding / Race rewards.
    try:
        from app import engagement_replies

        engagement_replies.engage_on_new_post(
            db,
            post=post,
            author=current_user,
            is_first_post=is_first_post,
            create_notification=create_notification,
        )
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger("baratx").exception("Official engage on create_post failed")

    # Alert @baratx + @sharath when a community member posts (so Alerts isn't empty for ops).
    # Only skip seeded platform accounts — blue/gold badge members still notify.
    if current_user.username not in set(seed.OFFICIAL_USERNAMES):
        officials = (
            db.query(models.User)
            .filter(models.User.username.in_(("baratx", "sharath")))
            .all()
        )
        for official in officials:
            create_notification(
                db,
                recipient_id=official.id,
                actor_id=current_user.id,
                kind="post",
                post_id=post.id,
                message=(text[:140] if text else None),
            )

        # Followers: “someone you follow posted” → Alerts + email (login back).
        follower_rows = (
            db.query(models.Follow.follower_id)
            .filter(models.Follow.followed_id == current_user.id)
            .limit(200)
            .all()
        )
        official_ids = {o.id for o in officials}
        for (follower_id,) in follower_rows:
            if follower_id in official_ids or follower_id == current_user.id:
                continue
            create_notification(
                db,
                recipient_id=follower_id,
                actor_id=current_user.id,
                kind="post",
                post_id=post.id,
                message=(text[:140] if text else None),
            )

    # Founding 100: quiet reward for one real civic problem (≥50 chars, flagged).
    mark_problem = str(civic_problem or "").strip().lower() in ("1", "true", "yes", "on")
    founding_awarded = False
    founding_status = None
    founding_message = None
    if mark_problem:
        if not rewards.qualifies_as_problem(text):
            raise HTTPException(
                status_code=400,
                detail=f"Civic problems need at least {rewards.MIN_PROBLEM_CHARS} characters for Founding 100 floor.",
            )
        awarded = rewards.try_award(db, user=current_user, kind="problem", post_id=post.id)
        if awarded:
            founding_awarded = True
            founding_status = awarded.status
            founding_message = "Floor cleared — you're on Founding 100. India rates next."
        else:
            existing = rewards.my_reward(db, current_user.id)
            if existing:
                founding_status = existing.status
                founding_message = f"Already on Founding 100 ({existing.status})."
            elif getattr(current_user, "is_official", False) or (
                (getattr(current_user, "badge", None) or "").lower() == "blue"
            ):
                founding_message = "Official/blue accounts aren't eligible for Founding 100 — post still published."
            elif rewards.slots_remaining(db) <= 0:
                founding_message = "Founding 100 is full — post still published."
            else:
                founding_message = "Could not claim Founding 100 floor — post still published."

    db.commit()
    db.refresh(post)
    out = serialize_post(post, current_user)
    if mark_problem:
        payload = out.model_dump() if hasattr(out, "model_dump") else out.dict()
        payload.update(
            {
                "founding_awarded": founding_awarded,
                "founding_status": founding_status,
                "founding_message": founding_message,
            }
        )
        out = schemas.PostOut(**payload)
    return out


@app.get("/posts", response_model=list[schemas.FeedItemOut])
def list_posts(
    limit: int = 20,
    before: Optional[str] = None,  # ISO timestamp cursor for pagination
    feed: str = "global",  # "global" | "following"
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    limit = max(1, min(limit, 50))

    author_filter_ids = None
    if feed == "following":
        if not current_user:
            raise HTTPException(status_code=401, detail="Log in to view your following feed")
        author_filter_ids = [f.followed_id for f in current_user.following] + [current_user.id]

    # Home Square: include arena debate takes (space posts). Keep Communities off Home.
    post_query = (
        db.query(models.Post)
        .filter(models.Post.community_id.is_(None))
        .order_by(models.Post.created_at.desc())
    )
    repost_query = db.query(models.Repost).order_by(models.Repost.created_at.desc())

    if author_filter_ids is not None:
        post_query = post_query.filter(models.Post.author_id.in_(author_filter_ids))
        repost_query = repost_query.filter(models.Repost.user_id.in_(author_filter_ids))

    if before:
        try:
            cursor = datetime.fromisoformat(before)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' timestamp")
        post_query = post_query.filter(models.Post.created_at < cursor)
        repost_query = repost_query.filter(models.Repost.created_at < cursor)

    # pull a generous window from each side, then merge + trim — good enough at demo scale
    # For You (global): over-fetch so community takes aren't buried under digest flood.
    window = limit * (8 if feed == "global" else 3)
    posts = post_query.limit(window).all()
    reposts = repost_query.limit(limit * 3).all()
    hidden = hidden_author_ids(db, current_user)

    official_names = set(seed.OFFICIAL_USERNAMES)

    items = []
    for p in posts:
        if p.author_id in hidden:
            continue
        items.append(
            schemas.FeedItemOut(post=serialize_post(p, current_user), reposted_by=None, item_time=p.created_at)
        )
    for r in reposts:
        if r.user_id in hidden or (r.post and r.post.author_id in hidden):
            continue
        items.append(
            schemas.FeedItemOut(
                post=serialize_post(r.post, current_user),
                reposted_by=author_out(r.user),
                item_time=r.created_at,
            )
        )

    if feed == "global":
        # Square "For you": real member takes first (including blue/gold badges),
        # then seeded official digest accounts — follow not required.
        def _sort_key(i: schemas.FeedItemOut):
            author = getattr(i.post, "author", None)
            uname = (getattr(author, "username", None) or "").lower() if author else ""
            is_seed_official = uname in official_names
            ts = i.item_time.timestamp() if i.item_time else 0.0
            return (1 if is_seed_official else 0, -ts)

        items.sort(key=_sort_key)
    else:
        items.sort(key=lambda i: i.item_time, reverse=True)
    return items[:limit]


@app.get("/posts/{post_id}", response_model=schemas.PostOut)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return serialize_post(post, current_user)


@app.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")

    if post.image_url:
        delete_media_file(post.image_url)

    reply_ids = [
        r[0]
        for r in db.query(models.Reply.id).filter(models.Reply.post_id == post_id).all()
    ]

    # Explicit cleanup — Postgres enforces FKs that SQLite often skips.
    db.query(models.Notification).filter(models.Notification.post_id == post_id).delete(
        synchronize_session=False
    )
    if reply_ids:
        db.query(models.Notification).filter(models.Notification.reply_id.in_(reply_ids)).delete(
            synchronize_session=False
        )
        db.query(models.ReplyLike).filter(models.ReplyLike.reply_id.in_(reply_ids)).delete(
            synchronize_session=False
        )
        # Break self-FK on nested replies before delete.
        db.query(models.Reply).filter(models.Reply.post_id == post_id).update(
            {models.Reply.parent_reply_id: None}, synchronize_session=False
        )
        db.query(models.Reply).filter(models.Reply.post_id == post_id).delete(
            synchronize_session=False
        )

    db.query(models.Like).filter(models.Like.post_id == post_id).delete(synchronize_session=False)
    db.query(models.Repost).filter(models.Repost.post_id == post_id).delete(
        synchronize_session=False
    )
    db.query(models.Bookmark).filter(models.Bookmark.post_id == post_id).delete(
        synchronize_session=False
    )
    db.query(models.PostHashtag).filter(models.PostHashtag.post_id == post_id).delete(
        synchronize_session=False
    )
    db.query(models.Report).filter(models.Report.target_post_id == post_id).delete(
        synchronize_session=False
    )
    db.query(models.Post).filter(models.Post.quoted_post_id == post_id).update(
        {models.Post.quoted_post_id: None}, synchronize_session=False
    )

    # Debate tallies = people on a side. If this was the author's last sided
    # post in the room, clear their stance so the count matches active takes.
    space_id = getattr(post, "space_id", None)
    debate_side = getattr(post, "debate_side", None)
    author_id = post.author_id

    db.delete(post)
    db.flush()

    if space_id and debate_side in ("for", "against"):
        remaining = (
            db.query(models.Post.id)
            .filter(
                models.Post.space_id == space_id,
                models.Post.author_id == author_id,
                models.Post.debate_side == debate_side,
            )
            .first()
        )
        if remaining is None:
            db.query(models.SpaceStance).filter(
                models.SpaceStance.space_id == space_id,
                models.SpaceStance.user_id == author_id,
                models.SpaceStance.side == debate_side,
            ).delete(synchronize_session=False)

    db.commit()
    return {"message": "Post deleted"}


# ---------- Likes ----------

@app.post("/posts/{post_id}/like", response_model=schemas.PostOut)
def like_post(
    post_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(models.Like)
        .filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id)
        .first()
    )
    if not existing:
        db.add(models.Like(post_id=post_id, user_id=current_user.id))
        create_notification(
            db,
            recipient_id=post.author_id,
            actor_id=current_user.id,
            kind="like",
            post_id=post.id,
        )
        rewards.bump_founding_for_post(db, post_id)
        db.commit()
        db.refresh(post)

    return serialize_post(post, current_user)


@app.delete("/posts/{post_id}/like", response_model=schemas.PostOut)
def unlike_post(
    post_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(models.Like)
        .filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        db.refresh(post)

    return serialize_post(post, current_user)


# ---------- Reposts ----------

@app.post("/posts/{post_id}/repost", response_model=schemas.PostOut)
def repost_post(
    post_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(models.Repost)
        .filter(models.Repost.post_id == post_id, models.Repost.user_id == current_user.id)
        .first()
    )
    if not existing:
        db.add(models.Repost(post_id=post_id, user_id=current_user.id))
        create_notification(
            db,
            recipient_id=post.author_id,
            actor_id=current_user.id,
            kind="repost",
            post_id=post.id,
        )
        db.commit()
        db.refresh(post)

    return serialize_post(post, current_user)


@app.delete("/posts/{post_id}/repost", response_model=schemas.PostOut)
def unrepost_post(
    post_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = (
        db.query(models.Repost)
        .filter(models.Repost.post_id == post_id, models.Repost.user_id == current_user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        db.refresh(post)

    return serialize_post(post, current_user)


# ---------- Replies ----------

@app.post("/posts/{post_id}/replies", response_model=schemas.ReplyOut)
def create_reply(
    post_id: str,
    payload: schemas.ReplyCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    text = text_parse.sanitize_user_text(payload.text).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Reply text cannot be empty")
    if len(text) > MAX_REPLY_LENGTH:
        raise HTTPException(status_code=400, detail=f"Reply must be {MAX_REPLY_LENGTH} characters or fewer")

    parent_reply_id = payload.parent_reply_id
    if parent_reply_id:
        parent = db.query(models.Reply).filter(models.Reply.id == parent_reply_id).first()
        if not parent or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent reply")

    reply = models.Reply(
        post_id=post_id,
        author_id=current_user.id,
        text=text,
        parent_reply_id=parent_reply_id,
    )
    db.add(reply)
    db.flush()
    # Always notify the post owner when someone comments.
    notified = set()
    create_notification(
        db,
        recipient_id=post.author_id,
        actor_id=current_user.id,
        kind="reply",
        post_id=post.id,
        reply_id=reply.id,
    )
    notified.add(post.author_id)
    if parent_reply_id:
        parent = db.query(models.Reply).filter(models.Reply.id == parent_reply_id).first()
        if parent:
            create_notification(
                db,
                recipient_id=parent.author_id,
                actor_id=current_user.id,
                kind="reply",
                post_id=post.id,
                reply_id=reply.id,
            )
            notified.add(parent.author_id)
    notify_mentions(
        db,
        current_user.id,
        text,
        post_id=post.id,
        reply_id=reply.id,
        exclude_ids=notified,
    )
    rewards.bump_founding_for_post(db, post_id)
    db.commit()
    db.refresh(reply)
    return serialize_reply(reply, current_user)


@app.get("/posts/{post_id}/replies", response_model=list[schemas.ReplyOut])
def list_replies(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    replies = (
        db.query(models.Reply)
        .filter(models.Reply.post_id == post_id)
        .order_by(models.Reply.created_at.asc())
        .all()
    )
    return [serialize_reply(r, current_user) for r in replies]


# ---------- Reply likes ----------

@app.post("/replies/{reply_id}/like", response_model=schemas.ReplyOut)
def like_reply(
    reply_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reply = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    existing = (
        db.query(models.ReplyLike)
        .filter(models.ReplyLike.reply_id == reply_id, models.ReplyLike.user_id == current_user.id)
        .first()
    )
    if not existing:
        db.add(models.ReplyLike(reply_id=reply_id, user_id=current_user.id))
        db.commit()
        db.refresh(reply)

    return serialize_reply(reply, current_user)


@app.delete("/replies/{reply_id}/like", response_model=schemas.ReplyOut)
def unlike_reply(
    reply_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reply = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    existing = (
        db.query(models.ReplyLike)
        .filter(models.ReplyLike.reply_id == reply_id, models.ReplyLike.user_id == current_user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        db.refresh(reply)

    return serialize_reply(reply, current_user)


# ---------- Search ----------

@app.get("/search", response_model=schemas.SearchResults)
def search(
    q: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    q = q.strip()
    if not q:
        return schemas.SearchResults(users=[], posts=[])

    like_pattern = f"%{q}%"

    users = (
        db.query(models.User)
        .filter(or_(models.User.username.ilike(like_pattern), models.User.display_name.ilike(like_pattern)))
        .limit(20)
        .all()
    )

    posts = (
        db.query(models.Post)
        .filter(models.Post.text.ilike(like_pattern))
        .order_by(models.Post.created_at.desc())
        .limit(30)
        .all()
    )

    following_ids = set()
    if current_user is not None:
        following_ids = {f.followed_id for f in current_user.following}

    return schemas.SearchResults(
        users=[
            schemas.UserSearchOut(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                bio=u.bio or "",
                avatar_url=u.avatar_url,
                is_following=u.id in following_ids,
            )
            for u in users
        ],
        posts=[serialize_post(p, current_user) for p in posts],
    )


# ---------- Notifications ----------

@app.get("/notifications", response_model=schemas.NotificationListOut)
def list_notifications(
    limit: int = 40,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    items = (
        db.query(models.Notification)
        .options(
            joinedload(models.Notification.actor),
            joinedload(models.Notification.post),
            joinedload(models.Notification.reply),
        )
        .filter(models.Notification.recipient_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    unread = (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id,
            models.Notification.is_read == False,  # noqa: E712
        )
        .count()
    )
    return schemas.NotificationListOut(
        items=[serialize_notification(n) for n in items],
        unread_count=unread,
    )


@app.get("/notifications/unread-count", response_model=schemas.UnreadCountOut)
def notifications_unread_count(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    unread = (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id,
            models.Notification.is_read == False,  # noqa: E712
        )
        .count()
    )
    return schemas.UnreadCountOut(unread_count=unread)


@app.post("/notifications/read", response_model=schemas.UnreadCountOut)
def mark_notifications_read(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    (
        db.query(models.Notification)
        .filter(
            models.Notification.recipient_id == current_user.id,
            models.Notification.is_read == False,  # noqa: E712
        )
        .update({"is_read": True})
    )
    db.commit()
    return schemas.UnreadCountOut(unread_count=0)


@app.post("/admin/prompts/refresh")
def admin_refresh_prompts(
    force: bool = True,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Pull unpaid Google News RSS into debate prompts."""
    from app import topic_ops

    return topic_ops.refresh_debate_prompts(db, force=force, per_topic=2, max_topics=60)


@app.post("/admin/topics/seed")
def admin_seed_topics(
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Force-upsert the full 30×arena topic taxonomy (active arenas)."""
    from app import topic_ops

    return topic_ops.seed_topics(db)


@app.post("/admin/daily-digest")
def admin_daily_digest(
    force: bool = False,
    slot: str | None = None,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Run a peak digest slot (morning/midday/evening): @baratx glimpse + @sharath take,
    cross-replies, and mutual likes — credible news sources only.
    """
    from app import daily_digest

    return daily_digest.run_daily_digest(
        db,
        force=force,
        slot=slot,
        attach_hashtags=attach_hashtags,
        notify_mentions=notify_mentions,
    )


@app.post("/admin/instagram-carousel")
def admin_instagram_carousel(
    pack: str = "evening",
    _: bool = Depends(require_admin),
):
    """Publish BarathX app carousel to @getbarathx (Instagram Graph API)."""
    from app import instagram_publish

    pack = (pack or "evening").strip().lower()
    if pack not in ("morning", "midday", "evening"):
        pack = "evening"
    return instagram_publish.publish_carousel(pack=pack)


@app.get("/rewards/founding", response_model=schemas.FoundingStatusOut)
def founding_status(
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    """Quiet Founding 100 status — slots left + whether this user already earned."""
    return rewards.status_payload(db, current_user)


@app.get("/rewards/race", response_model=schemas.RaceStatusOut)
def race_status(
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    """Biweekly Square Race — highest likes win ₹150–₹500."""
    data = rewards.race_status_for_user(db, current_user)
    return schemas.RaceStatusOut(**data)


def _is_blue(user: models.User) -> bool:
    badge = (getattr(user, "badge", None) or "none").strip().lower()
    if badge == "blue" or getattr(user, "is_official", False):
        return True
    return (user.username or "").lower() in ("sharath", "baratx")


@app.get("/rewards/ops", response_model=schemas.RewardsOpsOut)
def rewards_ops_for_blue(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Blue accounts: read-only Founding queue + race board. Money actions stay in the ops console."""
    if not _is_blue(current_user):
        raise HTTPException(status_code=403, detail="Blue accounts only")
    # Reuse admin serializers without requiring the ops unlock here.
    founding = admin_founding_rewards(status=None, _=True, db=db)
    race = schemas.RaceStatusOut(**rewards.race_status_for_user(db, None))
    return schemas.RewardsOpsOut(founding=founding, race=race)


def _founding_row_out(r: models.FoundingReward, u: Optional[models.User], db: Session):
    if r.status == "eligible":
        rewards.refresh_founding_payable(db, r)
    return schemas.FoundingRewardRow(
        id=r.id,
        user_id=r.user_id,
        username=u.username if u else "?",
        display_name=u.display_name if u else "?",
        kind=r.kind,
        amount_inr=r.amount_inr,
        status=r.status,
        qualifying_post_id=r.qualifying_post_id,
        qualifying_space_id=r.qualifying_space_id,
        note=r.note or "",
        created_at=r.created_at,
        paid_at=r.paid_at,
        quality=rewards.quality_snapshot(db, r),
    )


@app.get("/admin/founding-rewards", response_model=schemas.FoundingRewardsOut)
def admin_founding_rewards(
    status: Optional[str] = None,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(models.FoundingReward).order_by(models.FoundingReward.created_at.asc())
    if status in ("eligible", "payable", "paid"):
        q = q.filter(models.FoundingReward.status == status)
    rows = q.all()
    user_ids = [r.user_id for r in rows]
    users = {
        u.id: u
        for u in db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    } if user_ids else {}
    out_rows = []
    for r in rows:
        out_rows.append(_founding_row_out(r, users.get(r.user_id), db))
    db.commit()
    eligible_count = (
        db.query(models.FoundingReward).filter(models.FoundingReward.status == "eligible").count()
    )
    payable_count = (
        db.query(models.FoundingReward).filter(models.FoundingReward.status == "payable").count()
    )
    paid_count = (
        db.query(models.FoundingReward).filter(models.FoundingReward.status == "paid").count()
    )
    return schemas.FoundingRewardsOut(
        cap=rewards.FOUNDING_CAP,
        amount_inr=rewards.FOUNDING_AMOUNT_INR,
        slots_remaining=rewards.slots_remaining(db),
        eligible_count=eligible_count,
        payable_count=payable_count,
        paid_count=paid_count,
        rewards=out_rows,
        eval={
            "floor": "Problem post (≥50 chars + flag) OR any-arena debate",
            "rating": f"≥{rewards.FOUNDING_MIN_LIKES} likes OR ≥{rewards.FOUNDING_MIN_REPLIES} reply from others (debates: stances/posts)",
            "payout": "Pay when status=payable (or after manual review)",
        },
    )


@app.post("/admin/founding-rewards/{reward_id}/paid", response_model=schemas.FoundingRewardRow)
def admin_mark_founding_paid(
    reward_id: str,
    payload: schemas.FoundingMarkPaid,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        row = rewards.mark_paid(db, reward_id, note=payload.note or "")
    except LookupError:
        raise HTTPException(status_code=404, detail="Reward not found")
    db.commit()
    db.refresh(row)
    u = db.query(models.User).filter(models.User.id == row.user_id).first()
    return _founding_row_out(row, u, db)


@app.get("/admin/race-rewards", response_model=schemas.RaceRewardsOut)
def admin_race_rewards(
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    current = schemas.RaceStatusOut(**rewards.race_status_for_user(db, None))
    rows = db.query(models.RaceReward).order_by(models.RaceReward.created_at.desc()).limit(40).all()
    out = [
        schemas.RaceRewardRow(
            id=r.id,
            period_key=r.period_key,
            user_id=r.user_id,
            username=r.username_snapshot or "?",
            post_id=r.post_id,
            like_count=r.like_count,
            amount_inr=r.amount_inr,
            status=r.status,
            note=r.note or "",
            created_at=r.created_at,
            paid_at=r.paid_at,
            period_starts_at=r.period_starts_at,
            period_ends_at=r.period_ends_at,
        )
        for r in rows
    ]
    return schemas.RaceRewardsOut(current=current, rewards=out)


@app.post("/admin/race-rewards/close", response_model=schemas.RaceRewardRow)
def admin_close_race(
    payload: schemas.RaceCloseRequest,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        row = rewards.close_race_winner(
            db,
            period_key=payload.period_key,
            post_id=payload.post_id,
            note=payload.note or "",
        )
    except LookupError as exc:
        detail = {
            "no_qualifying_leader": "No post with enough likes yet",
            "post_not_in_period": "Post not in this race period",
            "bad_period": "Invalid period key",
        }.get(str(exc), "Could not close race")
        raise HTTPException(status_code=400, detail=detail)
    db.commit()
    db.refresh(row)
    return schemas.RaceRewardRow(
        id=row.id,
        period_key=row.period_key,
        user_id=row.user_id,
        username=row.username_snapshot or "?",
        post_id=row.post_id,
        like_count=row.like_count,
        amount_inr=row.amount_inr,
        status=row.status,
        note=row.note or "",
        created_at=row.created_at,
        paid_at=row.paid_at,
        period_starts_at=row.period_starts_at,
        period_ends_at=row.period_ends_at,
    )


@app.post("/admin/race-rewards/{reward_id}/paid", response_model=schemas.RaceRewardRow)
def admin_mark_race_paid(
    reward_id: str,
    payload: schemas.RaceMarkPaid,
    _: bool = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        row = rewards.mark_race_paid(db, reward_id, note=payload.note or "")
    except LookupError:
        raise HTTPException(status_code=404, detail="Race reward not found")
    db.commit()
    db.refresh(row)
    return schemas.RaceRewardRow(
        id=row.id,
        period_key=row.period_key,
        user_id=row.user_id,
        username=row.username_snapshot or "?",
        post_id=row.post_id,
        like_count=row.like_count,
        amount_inr=row.amount_inr,
        status=row.status,
        note=row.note or "",
        created_at=row.created_at,
        paid_at=row.paid_at,
        period_starts_at=row.period_starts_at,
        period_ends_at=row.period_ends_at,
    )


register_extra_routes(
    app,
    get_current_user=get_current_user,
    get_current_user_optional=get_current_user_optional,
    serialize_user=serialize_user,
    serialize_post=serialize_post,
    create_notification=create_notification,
)

register_social_surfaces(
    app,
    get_current_user=get_current_user,
    get_current_user_optional=get_current_user_optional,
    serialize_user=serialize_user,
    serialize_post=serialize_post,
    attach_hashtags=attach_hashtags,
    notify_mentions=notify_mentions,
)

# Daily @sharath trending digest (~09:05 IST). Disable with DISABLE_DAILY_DIGEST=1.
try:
    from app import daily_digest

    daily_digest.start_daily_digest_scheduler(
        attach_hashtags=attach_hashtags,
        notify_mentions=notify_mentions,
    )
except Exception:  # noqa: BLE001
    import logging

    logging.getLogger("baratx").exception("Daily digest scheduler failed to start")

# Instagram @getbaratx carousels at IST peak times (needs INSTAGRAM_* env).
try:
    from app import instagram_publish

    instagram_publish.start_instagram_scheduler()
except Exception:  # noqa: BLE001
    import logging

    logging.getLogger("baratx").exception("Instagram scheduler failed to start")

# Always-on: @baratx + @sharath first replies on community posts.
# Disable with DISABLE_OFFICIAL_ENGAGE=1
try:
    from app import engagement_replies

    engagement_replies.start_engagement_scheduler(create_notification=create_notification)
except Exception:  # noqa: BLE001
    import logging

    logging.getLogger("baratx").exception("Official engage scheduler failed to start")


# Optional SPA (built into Docker as /app/frontend_dist) — same-origin Square UI on Railway.
_FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend_dist"


def _public_web_origin(request: Optional[Request] = None) -> str:
    """Canonical public web origin for OG tags (QA vs prod)."""
    try:
        origin = (email_service.FRONTEND_URL or "").rstrip("/")
    except Exception:
        origin = (os.environ.get("FRONTEND_URL") or "").rstrip("/")
    host = ""
    if request is not None:
        host = (request.headers.get("host") or "").lower()
    if host.startswith("qa.") or "qa.barathx.com" in host:
        return "https://qa.barathx.com"
    if origin:
        return origin
    return "https://barathx.com"


def _spa_index_response(request: Optional[Request] = None) -> Response:
    index = _FRONTEND_DIST / "index.html"
    html = index.read_text(encoding="utf-8")
    origin = _public_web_origin(request)
    if origin and origin != "https://barathx.com":
        html = html.replace("https://barathx.com/", f"{origin}/").replace(
            'content="https://barathx.com"', f'content="{origin}"'
        )
    return Response(content=html, media_type="text/html; charset=utf-8")


if _FRONTEND_DIST.is_dir():
    _assets = _FRONTEND_DIST / "assets"
    if _assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="frontend_assets")

    @app.middleware("http")
    async def spa_document_navigation(request: Request, call_next):
        """DEF-008: browser refresh/shared links must get index.html, not API JSON."""
        path = request.url.path
        header_map = {k.decode().lower(): v.decode() for k, v in request.scope.get("headers", [])}
        if wants_spa_document(method=request.method, headers=header_map) and spa_shell_allowed(path):
            candidate = _FRONTEND_DIST / path.lstrip("/")
            if path != "/" and candidate.is_file():
                return FileResponse(candidate)
            if (_FRONTEND_DIST / "index.html").is_file():
                return _spa_index_response(request)
        return await call_next(request)

    @app.get("/")
    def spa_index(request: Request):
        return _spa_index_response(request)

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str, request: Request):
        # Let unmatched non-API paths fall through to the React router.
        candidate = _FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        if (_FRONTEND_DIST / "index.html").is_file():
            return _spa_index_response(request)
        raise HTTPException(status_code=404, detail="Not found")
