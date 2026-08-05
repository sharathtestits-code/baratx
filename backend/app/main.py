import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)


def run_migrations():
    """
    Base.metadata.create_all() only creates tables that don't exist yet — it
    never alters existing tables. SQLite has no automatic migration system,
    so when we add new columns to an already-existing table (like avatar_url/
    cover_url on users), we need to add them by hand here. Safe to run every
    startup: it only ALTERs a column in if it's actually missing.
    """
    if not str(engine.url).startswith("sqlite"):
        return
    with engine.connect() as conn:
        existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "avatar_url" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
        if "cover_url" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN cover_url VARCHAR"))
        conn.commit()


run_migrations()

app = FastAPI(title="BaratX API", version="0.4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only — restrict in production
    allow_credentials=False,  # we use Bearer tokens, not cookies, so no need for credentials mode
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
    if current_user:
        liked_by_me = any(like.user_id == current_user.id for like in post.likes)
        reposted_by_me = any(r.user_id == current_user.id for r in post.reposts)
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
    )


@app.get("/health")
def health():
    return {"status": "ok"}


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
        is_email_verified=False,  # demo: real deployment would send a verification email
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


@app.post("/auth/login/email", response_model=schemas.TokenResponse)
def login_email(payload: schemas.EmailLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = auth.create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


# ---------- Phone + OTP signup / login ----------
# NOTE: this is a demo stub. No real SMS is sent — the OTP is returned in the
# API response (dev_otp) so you can test the flow. Wire in an SMS provider
# (MSG91, Twilio Verify, etc.) before shipping this to real users.

@app.post("/auth/signup/phone/request-otp")
def signup_phone_request_otp(payload: schemas.PhoneOtpRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    code = auth.generate_otp()
    otp = models.OTP(
        phone=payload.phone,
        code=code,
        purpose="signup",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
    )
    db.add(otp)
    db.commit()

    # DEV ONLY: return the OTP directly instead of sending an SMS.
    return {"message": "OTP generated (demo mode, no SMS sent)", "dev_otp": code, "expires_in_minutes": OTP_TTL_MINUTES}


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

    code = auth.generate_otp()
    otp = models.OTP(
        phone=payload.phone,
        code=code,
        purpose="login",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES),
    )
    db.add(otp)
    db.commit()

    return {"message": "OTP generated (demo mode, no SMS sent)", "dev_otp": code, "expires_in_minutes": OTP_TTL_MINUTES}


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


# ---------- Posts / feed ----------

@app.post("/posts", response_model=schemas.PostOut)
async def create_post(
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Post text cannot be empty")
    if len(text) > MAX_POST_LENGTH:
        raise HTTPException(status_code=400, detail=f"Post must be {MAX_POST_LENGTH} characters or fewer")

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

    post = models.Post(author_id=current_user.id, text=text, image_url=image_url)
    db.add(post)
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
    posts = post_query.limit(limit * 2).all()
    reposts = repost_query.limit(limit * 2).all()

    items = []
    for p in posts:
        items.append(
            schemas.FeedItemOut(post=serialize_post(p, current_user), reposted_by=None, item_time=p.created_at)
        )
    for r in reposts:
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

    reply = models.Reply(post_id=post_id, author_id=current_user.id, text=text)
    db.add(reply)
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
