import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app import auth, email as email_service, google_auth, models, schemas, sms, text_parse
from app.database import Base, SessionLocal, engine, get_db
from app.extra_routes import register_extra_routes

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

            post_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(posts)"))}
            if "quoted_post_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN quoted_post_id VARCHAR"))

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

            post_cols = cols("posts")
            if post_cols and "quoted_post_id" not in post_cols:
                conn.execute(text("ALTER TABLE posts ADD COLUMN quoted_post_id VARCHAR"))

            reply_cols = cols("replies")
            if reply_cols and "parent_reply_id" not in reply_cols:
                conn.execute(text("ALTER TABLE replies ADD COLUMN parent_reply_id VARCHAR"))

            notif_cols = cols("notifications")
            if notif_cols and "kind" not in notif_cols:
                if "type" in notif_cols:
                    conn.execute(text("ALTER TABLE notifications RENAME COLUMN type TO kind"))
                else:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN kind VARCHAR"))

        conn.commit()


run_migrations()

app = FastAPI(title="BaratX API", version="0.5.0")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "").strip()
_cors_raw = os.environ.get("CORS_ORIGINS", "").strip()
if _cors_raw:
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
elif ENVIRONMENT == "production":
    CORS_ORIGINS = ["https://barathx.com", "https://baratx.pages.dev"]
else:
    CORS_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_POST_LENGTH = 500
MAX_REPLY_LENGTH = 500
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

    ext = os.path.splitext(image.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    return f"/media/{filename}"


def delete_media_file(url: Optional[str]):
    if not url:
        return
    filepath = os.path.join(BASE_DIR, url.lstrip("/"))
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


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
    return schemas.UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        phone=user.phone,
        language=user.language,
        bio=user.bio,
        is_email_verified=user.is_email_verified,
        is_phone_verified=user.is_phone_verified,
        created_at=user.created_at,
        avatar_url=user.avatar_url,
        cover_url=user.cover_url,
        follower_count=len(user.followers),
        following_count=len(user.following),
        is_following=is_following,
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
            text=qp.text,
            image_url=qp.image_url,
            created_at=qp.created_at,
            author=schemas.AuthorOut.model_validate(qp.author),
        )

    tags = text_parse.extract_hashtags(post.text)

    return schemas.PostOut(
        id=post.id,
        text=post.text,
        image_url=post.image_url,
        created_at=post.created_at,
        author=schemas.AuthorOut.model_validate(post.author),
        like_count=len(post.likes),
        reply_count=len(post.replies),
        repost_count=len(post.reposts),
        liked_by_me=liked_by_me,
        reposted_by_me=reposted_by_me,
        bookmarked_by_me=bookmarked_by_me,
        quoted_post=quoted,
        hashtags=tags,
    )


def serialize_reply(reply: models.Reply, current_user: Optional[models.User]) -> schemas.ReplyOut:
    liked_by_me = False
    if current_user:
        liked_by_me = any(like.user_id == current_user.id for like in reply.likes)
    return schemas.ReplyOut(
        id=reply.id,
        post_id=reply.post_id,
        text=reply.text,
        created_at=reply.created_at,
        author=schemas.AuthorOut.model_validate(reply.author),
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


def notify_mentions(db: Session, actor_id: str, text: str, post_id: Optional[str] = None, reply_id: Optional[str] = None):
    for username in text_parse.extract_mentions(text):
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            create_notification(
                db,
                recipient_id=user.id,
                actor_id=actor_id,
                kind="mention",
                post_id=post_id,
                reply_id=reply_id,
            )


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
        )
    )


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
        )
    else:
        actor = schemas.AuthorOut.model_validate(actor)
    return schemas.NotificationOut(
        id=n.id,
        type=n.kind,
        created_at=n.created_at,
        is_read=n.is_read,
        actor=actor,
        post_id=n.post_id,
        post_preview=preview,
        reply_preview=reply_preview,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Admin (password-protected signup insights) ----------

def require_admin(x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret")):
    if not ADMIN_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Admin is not configured. Set ADMIN_SECRET on the API service.",
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
                created_at=u.created_at,
                signup_method=_signup_method(u),
            )
            for u in rows
        ],
    )


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
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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
    return schemas.MessageResponse(message="Email confirmed. Your BaratX account is active.")


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
        )
        db.add(user)
        db.commit()
        db.refresh(user)
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
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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


@app.get("/users/{username}/posts", response_model=list[schemas.PostOut])
def get_user_posts(
    username: str,
    limit: int = 20,
    before: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    limit = max(1, min(limit, 50))
    query = db.query(models.Post).filter(models.Post.author_id == user.id).order_by(models.Post.created_at.desc())
    if before:
        try:
            cursor = datetime.fromisoformat(before)
            query = query.filter(models.Post.created_at < cursor)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'before' timestamp")
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
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    text = text.strip()
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

        ext = os.path.splitext(image.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(MEDIA_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(contents)
        image_url = f"/media/{filename}"

    post = models.Post(
        author_id=current_user.id,
        text=text,
        image_url=image_url,
        quoted_post_id=quoted_post_id,
    )
    db.add(post)
    db.flush()
    attach_hashtags(db, post, text)
    notify_mentions(db, current_user.id, text, post_id=post.id)
    db.commit()
    db.refresh(post)
    return serialize_post(post, current_user)


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

    post_query = db.query(models.Post).order_by(models.Post.created_at.desc())
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
    posts = post_query.limit(limit * 3).all()
    reposts = repost_query.limit(limit * 3).all()
    hidden = hidden_author_ids(db, current_user)

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
                reposted_by=schemas.AuthorOut.model_validate(r.user),
                item_time=r.created_at,
            )
        )

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
        filepath = os.path.join(BASE_DIR, post.image_url.lstrip("/"))
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

    db.delete(post)
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

    text = payload.text.strip()
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
    create_notification(
        db,
        recipient_id=post.author_id,
        actor_id=current_user.id,
        kind="reply",
        post_id=post.id,
        reply_id=reply.id,
    )
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
    notify_mentions(db, current_user.id, text, post_id=post.id, reply_id=reply.id)
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

    return schemas.SearchResults(
        users=[schemas.UserSearchOut.model_validate(u) for u in users],
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


register_extra_routes(
    app,
    get_current_user=get_current_user,
    get_current_user_optional=get_current_user_optional,
    serialize_user=serialize_user,
    serialize_post=serialize_post,
    create_notification=create_notification,
)
