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


class PasswordResetToken(Base):
    """One-time tokens emailed for forgot-password / reset."""

    __tablename__ = "password_reset_tokens"

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
    quoted_post_id = Column(String, ForeignKey("posts.id"), nullable=True, index=True)
    community_id = Column(String, ForeignKey("communities.id"), nullable=True, index=True)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="post", cascade="all, delete-orphan")
    reposts = relationship("Repost", back_populates="post", cascade="all, delete-orphan")
    quoted_post = relationship("Post", remote_side=[id], foreign_keys=[quoted_post_id])
    community = relationship("Community", back_populates="posts", foreign_keys=[community_id])
    space = relationship("Space", back_populates="posts", foreign_keys=[space_id])


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
    parent_reply_id = Column(String, ForeignKey("replies.id"), nullable=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    post = relationship("Post", back_populates="replies")
    author = relationship("User", back_populates="replies")
    likes = relationship("ReplyLike", back_populates="reply", cascade="all, delete-orphan")
    parent = relationship("Reply", remote_side=[id], foreign_keys=[parent_reply_id])


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


class Notification(Base):
    """In-app notifications for follow / like / reply / repost / mention / message."""

    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # follow | like | reply | repost | mention | message
    post_id = Column(String, ForeignKey("posts.id"), nullable=True, index=True)
    reply_id = Column(String, ForeignKey("replies.id"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    recipient = relationship("User", foreign_keys=[recipient_id])
    actor = relationship("User", foreign_keys=[actor_id])
    post = relationship("Post")
    reply = relationship("Reply")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_bookmark_user_post"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User")
    post = relationship("Post")


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    blocker_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    blocked_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Mute(Base):
    __tablename__ = "mutes"
    __table_args__ = (UniqueConstraint("muter_id", "muted_id", name="uq_mute_pair"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    muter_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    muted_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    target_user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    target_post_id = Column(String, ForeignKey("posts.id"), nullable=True, index=True)
    reason = Column(String, nullable=False, default="")
    details = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(String, primary_key=True, default=gen_uuid)
    tag = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PostHashtag(Base):
    __tablename__ = "post_hashtags"
    __table_args__ = (UniqueConstraint("post_id", "hashtag_id", name="uq_post_hashtag"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False, index=True)
    hashtag_id = Column(String, ForeignKey("hashtags.id"), nullable=False, index=True)


class DirectMessage(Base):
    __tablename__ = "direct_messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])


class UserList(Base):
    """Named list of accounts owned by a user (X-style Lists)."""

    __tablename__ = "user_lists"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("ListMember", back_populates="user_list", cascade="all, delete-orphan")


class ListMember(Base):
    __tablename__ = "list_members"
    __table_args__ = (UniqueConstraint("list_id", "user_id", name="uq_list_member"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    list_id = Column(String, ForeignKey("user_lists.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_list = relationship("UserList", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])


class Community(Base):
    __tablename__ = "communities"

    id = Column(String, primary_key=True, default=gen_uuid)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="", nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("CommunityMember", back_populates="community", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="community", foreign_keys="Post.community_id")


class CommunityMember(Base):
    __tablename__ = "community_members"
    __table_args__ = (UniqueConstraint("community_id", "user_id", name="uq_community_member"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    community_id = Column(String, ForeignKey("communities.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    community = relationship("Community", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])


class Space(Base):
    """Text discussion room (not live audio)."""

    __tablename__ = "spaces"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    host_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default="open", nullable=False, index=True)  # open | closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    closes_at = Column(DateTime, nullable=True)

    host = relationship("User", foreign_keys=[host_id])
    posts = relationship("Post", back_populates="space", foreign_keys="Post.space_id")
