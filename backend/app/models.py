import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class MediaAsset(Base):
    """Durable media bytes (survives Railway redeploys when S3/R2 is not configured)."""

    __tablename__ = "media_assets"

    id = Column(String, primary_key=True, default=gen_uuid)
    content_type = Column(String, nullable=False, default="application/octet-stream")
    filename = Column(String, nullable=True)
    size = Column(Integer, nullable=False, default=0)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)

    password_hash = Column(String, nullable=False)

    language = Column(String, default="en", nullable=False)  # en | hi | te
    theme = Column(String, default="midnight", nullable=False)  # midnight | saffron | monsoon | ink
    bio = Column(String, default="", nullable=False)

    avatar_url = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)

    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    # none | gold | blue — blue = official verified; gold can be promoted to blue by blue accounts
    badge = Column(String, default="none", nullable=False, index=True)
    is_official = Column(Boolean, default=False, nullable=False, index=True)
    # Lifetime flag: official first-post welcome fires once even if all posts are deleted.
    has_posted_once = Column(Boolean, default=False, nullable=False)
    # Activity emails (likes/replies/follows). Users can unsubscribe from Settings or email footer.
    email_activity_enabled = Column(Boolean, default=True, nullable=False)
    # Bumped on password reset / security events to invalidate existing JWTs.
    token_version = Column(Integer, default=0, nullable=False)
    # DPDP: affirmative consent to privacy notice (Data Principal).
    privacy_accepted_at = Column(DateTime, nullable=True)
    privacy_notice_version = Column(String, nullable=True)

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
    """Short-lived phone OTP rows. `code` stores a bcrypt hash of the OTP (never plaintext)."""

    __tablename__ = "otps"

    id = Column(String, primary_key=True, default=gen_uuid)
    phone = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)  # bcrypt hash of the 6-digit OTP
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
    debate_side = Column(String, nullable=True)  # for | against (arena debates only)
    # Heuristic AI-slop flag — demoted in feeds so human takes stay on top.
    likely_ai = Column(Boolean, default=False, nullable=False, index=True)
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
    # Heuristic AI-slop flag — human replies sort above these.
    likely_ai = Column(Boolean, default=False, nullable=False, index=True)
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
    """In-app notifications for follow / like / reply / repost / mention / message / badge."""

    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # follow | like | reply | repost | mention | message | badge
    post_id = Column(String, ForeignKey("posts.id"), nullable=True, index=True)
    reply_id = Column(String, ForeignKey("replies.id"), nullable=True)
    message = Column(String, nullable=True)  # optional free-text (e.g. badge changes)
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
    # Arena topic homes: sports | politics | entertainment | news | spirituality
    is_arena = Column(Boolean, default=False, nullable=False, index=True)
    arena_key = Column(String, nullable=True, unique=True, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("CommunityMember", back_populates="community", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="community", foreign_keys="Post.community_id")
    debates = relationship("Space", back_populates="community", foreign_keys="Space.community_id")


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
    """Text discussion room or arena debate (not live audio)."""

    __tablename__ = "spaces"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    host_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default="open", nullable=False, index=True)  # open | closed
    kind = Column(String, default="room", nullable=False, index=True)  # room | debate
    community_id = Column(String, ForeignKey("communities.id"), nullable=True, index=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True, index=True)
    source_url = Column(String, nullable=True, index=True)  # RSS / news link for prompts
    side_for_label = Column(String, default="For", nullable=False)
    side_against_label = Column(String, default="Against", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    closes_at = Column(DateTime, nullable=True)

    host = relationship("User", foreign_keys=[host_id])
    community = relationship("Community", back_populates="debates", foreign_keys=[community_id])
    topic = relationship("Topic", back_populates="debates", foreign_keys=[topic_id])
    posts = relationship("Post", back_populates="space", foreign_keys="Post.space_id")
    stances = relationship("SpaceStance", back_populates="space", cascade="all, delete-orphan")


class SpaceStance(Base):
    """User picks For/Against in an arena debate."""

    __tablename__ = "space_stances"
    __table_args__ = (UniqueConstraint("space_id", "user_id", name="uq_space_stance"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    side = Column(String, nullable=False)  # for | against
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    space = relationship("Space", back_populates="stances")
    user = relationship("User", foreign_keys=[user_id])


class LiveTalkParticipant(Base):
    """Someone on the Live Talk seat (audio room under a Space). Soft cap ~15."""

    __tablename__ = "live_talk_participants"
    __table_args__ = (UniqueConstraint("space_id", "user_id", name="uq_live_talk_seat"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    muted = Column(Boolean, default=True, nullable=False)
    video_enabled = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    left_at = Column(DateTime, nullable=True)
    removed_at = Column(DateTime, nullable=True)
    removed_reason = Column(String, default="", nullable=False)

    space = relationship("Space", foreign_keys=[space_id])
    user = relationship("User", foreign_keys=[user_id])


class LiveTalkPin(Base):
    """Per-viewer pin of a talk participant (self or others) — only for that viewer."""

    __tablename__ = "live_talk_pins"
    __table_args__ = (
        UniqueConstraint("space_id", "viewer_id", "pinned_user_id", name="uq_live_talk_pin"),
    )

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    viewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    pinned_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LiveTalkMessage(Base):
    """In-call chat visible only to people currently (or recently) on the Talk."""

    __tablename__ = "live_talk_messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    sender = relationship("User", foreign_keys=[sender_id])


class LiveTalkReaction(Base):
    """Ephemeral in-call reactions (👍 ❤️ 😂 …) shown to people on the Talk."""

    __tablename__ = "live_talk_reactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    emoji = Column(String, nullable=False, default="👍")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", foreign_keys=[user_id])


class LiveTalkSignal(Base):
    """WebRTC signaling (offer / answer / ICE) between two talk participants."""

    __tablename__ = "live_talk_signals"

    id = Column(String, primary_key=True, default=gen_uuid)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=False, index=True)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False, index=True)  # offer | answer | ice
    payload = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    delivered = Column(Boolean, default=False, nullable=False, index=True)


class ModerationStrike(Base):
    """Auto-moderation strikes — stack toward account removal."""

    __tablename__ = "moderation_strikes"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False, default="report", index=True)
    detail = Column(String, default="", nullable=False)
    space_id = Column(String, ForeignKey("spaces.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Topic(Base):
    """Subtopic under an arena (e.g. IPL under Sports)."""

    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("arena_key", "key", name="uq_topic_arena_key"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    arena_key = Column(String, nullable=False, index=True)
    key = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    blurb = Column(String, default="", nullable=False)
    rss_query = Column(String, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    interests = relationship("UserTopicInterest", back_populates="topic", cascade="all, delete-orphan")
    debates = relationship("Space", back_populates="topic", foreign_keys="Space.topic_id")


class UserTopicInterest(Base):
    """Topics a user chose — drives personalized debate prompts."""

    __tablename__ = "user_topic_interests"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),)

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])
    topic = relationship("Topic", back_populates="interests")


class FoundingReward(Base):
    """First-N incentive: one real problem post or any-arena debate."""

    __tablename__ = "founding_rewards"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    kind = Column(String, nullable=False)  # problem | debate
    amount_inr = Column(Integer, nullable=False, default=150)
    # eligible (floor met) → payable (community rating bar) → paid
    status = Column(String, nullable=False, default="eligible", index=True)
    qualifying_post_id = Column(String, ForeignKey("posts.id"), nullable=True)
    qualifying_space_id = Column(String, ForeignKey("spaces.id"), nullable=True)
    note = Column(String, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])


class RaceReward(Base):
    """Biweekly Square Race — highest-liked Home post wins ₹150–₹500."""

    __tablename__ = "race_rewards"

    id = Column(String, primary_key=True, default=gen_uuid)
    period_key = Column(String, unique=True, nullable=False, index=True)
    period_starts_at = Column(DateTime, nullable=False)
    period_ends_at = Column(DateTime, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    like_count = Column(Integer, nullable=False, default=0)
    amount_inr = Column(Integer, nullable=False, default=150)
    username_snapshot = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="payable", index=True)  # payable | paid
    note = Column(String, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    post = relationship("Post", foreign_keys=[post_id])


class ProductIssue(Base):
    """Early-member (first 1000) product bugs / concerns board."""

    __tablename__ = "product_issues"

    id = Column(String, primary_key=True, default=gen_uuid)
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    kind = Column(String, nullable=False, default="bug", index=True)  # bug | concern | idea
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    author = relationship("User", foreign_keys=[author_id])
