import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)

    password_hash = Column(String, nullable=False)

    language = Column(String, default="en", nullable=False)  # en | hi | te
    bio = Column(String, default="", nullable=False)

    avatar_url = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)

    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="author", cascade="all, delete-orphan")
    reply_likes = relationship("ReplyLike", back_populates="user", cascade="all, delete-orphan")
    reposts = relationship("Repost", back_populates="user", cascade="all, delete-orphan")

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan",
    )


class OTP(Base):
    """Stores short-lived OTP codes for phone signup/login (demo: no real SMS sent)."""

    __tablename__ = "otps"

    id = Column(String, primary_key=True, default=gen_uuid)
    phone = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # "signup" | "login"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    consumed = Column(Boolean, default=False, nullable=False)


class EmailVerificationToken(Base):
    """One-time tokens emailed after signup to confirm the user's address."""

    __tablename__ = "email_verification_tokens"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    consumed = Column(Boolean, default=False, nullable=False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=gen_uuid)
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="post", cascade="all, delete-orphan")
    reposts = relationship("Repost", back_populates="post", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_like_user_post"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Reply(Base):
    __tablename__ = "replies"

    id = Column(String, primary_key=True, default=gen_uuid)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, index=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    post = relationship("Post", back_populates="replies")
    author = relationship("User", back_populates="replies")
    likes = relationship("ReplyLike", back_populates="reply", cascade="all, delete-orphan")


class ReplyLike(Base):
    __tablename__ = "reply_likes"
    __table_args__ = (UniqueConstraint("user_id", "reply_id", name="uq_like_user_reply"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    reply_id = Column(String, ForeignKey("replies.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reply_likes")
    reply = relationship("Reply", back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    follower_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # who clicks follow
    followed_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # who gets followed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")


class Repost(Base):
    __tablename__ = "reposts"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_repost_user_post"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # who reposted
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, index=True)  # original post
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="reposts")
    post = relationship("Post", back_populates="reposts")
