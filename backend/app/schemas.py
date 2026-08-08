import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.phoneutil import normalize_phone

# Letters/numbers first; allow . _ - (Instagram/Twitter-style handles)
USERNAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,19}$")


def normalize_username(v: str) -> str:
    v = (v or "").strip().lstrip("@")
    if not USERNAME_RE.match(v):
        raise ValueError(
            "Username must be 3–20 characters: start with a letter or number; "
            "letters, numbers, underscore, period, or hyphen only"
        )
    if ".." in v or "--" in v or v.endswith(".") or v.endswith("-"):
        raise ValueError("Username can’t end with . or - or contain .. / --")
    return v.lower()


class EmailSignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    display_name: str
    confirm_age_18: bool = False

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        return normalize_username(v)

    @field_validator("password")
    @classmethod
    def valid_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("confirm_age_18")
    @classmethod
    def must_confirm_age(cls, v):
        if not v:
            raise ValueError("You must be 18 or older to join BarathX")
        return True


class EmailLoginRequest(BaseModel):
    # Accepts email address or username (field name kept for API compatibility).
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def valid_login_id(cls, v):
        v = (v or "").strip()
        if len(v) < 3:
            raise ValueError("Enter your email or username")
        return v


class PhoneOtpRequest(BaseModel):
    phone: str
    # Optional UI hint: "IN" | "US" when number is entered without +country
    region: Optional[str] = None

    @model_validator(mode="after")
    def normalize(self):
        self.phone = normalize_phone(self.phone, default_region=self.region)
        return self


class PhoneSignupVerify(BaseModel):
    phone: str
    otp: str
    username: str
    display_name: str
    region: Optional[str] = None
    confirm_age_18: bool = False

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        return normalize_username(v)

    @field_validator("confirm_age_18")
    @classmethod
    def must_confirm_age(cls, v):
        if not v:
            raise ValueError("You must be 18 or older to join BarathX")
        return True

    @model_validator(mode="after")
    def normalize(self):
        self.phone = normalize_phone(self.phone, default_region=self.region)
        return self


class PhoneLoginVerify(BaseModel):
    phone: str
    otp: str
    region: Optional[str] = None

    @model_validator(mode="after")
    def normalize(self):
        self.phone = normalize_phone(self.phone, default_region=self.region)
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email_verification_sent: bool = False
    # Only populated in development when outbound email is not configured.
    dev_verify_url: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def valid_reset_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class GoogleAuthRequest(BaseModel):
    id_token: str
    # Required only when Google creates a new BarathX account (18+ gate).
    confirm_age_18: Optional[bool] = None


class MessageResponse(BaseModel):
    message: str
    email_verification_sent: bool = False
    # Dev-only helpers when outbound email is not configured.
    dev_verify_url: Optional[str] = None
    dev_reset_url: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None

    @field_validator("display_name")
    @classmethod
    def valid_display_name(cls, v):
        if v is None:
            return v
        name = v.strip()
        if len(name) < 1 or len(name) > 50:
            raise ValueError("Display name must be 1–50 characters")
        return name

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if v is None:
            return v
        return normalize_username(v)

    @field_validator("bio")
    @classmethod
    def valid_bio(cls, v):
        if v is None:
            return v
        if len(v) > 280:
            raise ValueError("Bio must be 280 characters or fewer")
        return v

    @field_validator("language")
    @classmethod
    def valid_language(cls, v):
        if v is None:
            return v
        if v not in ("en", "hi", "te"):
            raise ValueError("Language must be en, hi, or te")
        return v

    @field_validator("theme")
    @classmethod
    def valid_theme(cls, v):
        if v is None:
            return v
        if v not in ("saffron", "midnight", "monsoon", "ink"):
            raise ValueError("Theme must be saffron, midnight, monsoon, or ink")
        return v


class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    language: str
    theme: str = "midnight"
    bio: str
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    badge: str = "none"  # none | gold | blue
    is_official: bool = False
    created_at: datetime
    follower_count: int = 0
    following_count: int = 0
    is_following: bool = False

    class Config:
        from_attributes = True


class AuthorOut(BaseModel):
    id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    badge: str = "none"
    is_official: bool = False

    class Config:
        from_attributes = True


class QuotedPostOut(BaseModel):
    id: str
    text: str
    image_url: Optional[str] = None
    created_at: datetime
    author: AuthorOut

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    id: str
    text: str
    image_url: Optional[str] = None
    created_at: datetime
    author: AuthorOut
    like_count: int = 0
    reply_count: int = 0
    repost_count: int = 0
    liked_by_me: bool = False
    reposted_by_me: bool = False
    bookmarked_by_me: bool = False
    quoted_post: Optional[QuotedPostOut] = None
    hashtags: list[str] = []
    debate_side: Optional[str] = None

    class Config:
        from_attributes = True


class ReplyCreate(BaseModel):
    text: str
    parent_reply_id: Optional[str] = None

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Reply cannot be empty")
        if len(v) > 220:
            raise ValueError("Reply must be 220 characters or fewer")
        return v


class ReplyOut(BaseModel):
    id: str
    post_id: str
    text: str
    created_at: datetime
    author: AuthorOut
    like_count: int = 0
    liked_by_me: bool = False
    parent_reply_id: Optional[str] = None

    class Config:
        from_attributes = True


class FeedItemOut(BaseModel):
    post: PostOut
    reposted_by: Optional[AuthorOut] = None
    item_time: datetime  # timestamp to sort feed by (post.created_at or repost.created_at)


class UserSearchOut(BaseModel):
    id: str
    username: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    is_following: bool = False

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    users: list[UserSearchOut]
    posts: list[PostOut]


class NotificationOut(BaseModel):
    id: str
    type: str  # follow | like | reply | repost | mention | message | badge
    created_at: datetime
    is_read: bool
    actor: AuthorOut
    post_id: Optional[str] = None
    post_preview: Optional[str] = None
    reply_preview: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    unread_count: int


class UnreadCountOut(BaseModel):
    unread_count: int


class ReportCreate(BaseModel):
    reason: str
    details: str = ""
    target_username: Optional[str] = None
    target_post_id: Optional[str] = None

    @field_validator("reason")
    @classmethod
    def valid_reason(cls, v):
        v = (v or "").strip()
        if len(v) < 3 or len(v) > 80:
            raise ValueError("Reason must be 3–80 characters")
        return v

    @field_validator("details")
    @classmethod
    def valid_details(cls, v):
        if v is None:
            return ""
        if len(v) > 500:
            raise ValueError("Details must be 500 characters or fewer")
        return v


class MessageCreate(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message must be 1000 characters or fewer")
        return v


class MessageOut(BaseModel):
    id: str
    text: str
    created_at: datetime
    is_read: bool
    sender: AuthorOut
    recipient: AuthorOut

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    user: AuthorOut
    last_message: MessageOut
    unread_count: int


class AdminStatsOut(BaseModel):
    total_users: int
    users_last_24h: int
    users_last_7d: int
    with_email: int
    with_phone: int
    email_verified: int
    phone_verified: int
    total_posts: int = 0
    posts_last_24h: int = 0
    users_with_posts: int = 0
    posters_last_24h: int = 0


class AdminUserRow(BaseModel):
    id: str
    username: str
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    badge: str = "none"
    is_official: bool = False
    created_at: datetime
    signup_method: str


class AdminUsersOut(BaseModel):
    total: int
    limit: int
    offset: int
    users: list[AdminUserRow]


class BadgeUpdate(BaseModel):
    badge: str
    # When false, badge still changes but the target is not notified.
    notify: bool = True

    @field_validator("badge")
    @classmethod
    def valid_badge(cls, v):
        v = (v or "").strip().lower()
        if v not in ("none", "gold", "blue"):
            raise ValueError("badge must be none, gold, or blue")
        return v


class AdminPostCreate(BaseModel):
    text: str
    username: Optional[str] = "baratx"

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Post cannot be empty")
        if len(v) > 500:
            raise ValueError("Post must be 500 characters or fewer")
        return v

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if v is None or not str(v).strip():
            return "baratx"
        return str(v).strip().lstrip("@").lower()


class AdminReplyCreate(BaseModel):
    post_id: str
    text: str
    username: Optional[str] = "baratx"

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Reply cannot be empty")
        if len(v) > 220:
            raise ValueError("Reply must be 220 characters or fewer")
        return v

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if v is None or not str(v).strip():
            return "baratx"
        return str(v).strip().lstrip("@").lower()


class AdminRecentPostsOut(BaseModel):
    total: int
    posts: list[PostOut]


# ---------- Lists / Communities / Spaces ----------


class UserListCreate(BaseModel):
    name: str
    description: Optional[str] = ""

    @field_validator("name")
    @classmethod
    def valid_name(cls, v):
        v = (v or "").strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError("List name must be 1–50 characters")
        return v

    @field_validator("description")
    @classmethod
    def valid_description(cls, v):
        if v is None:
            return ""
        if len(v) > 160:
            raise ValueError("Description must be 160 characters or fewer")
        return v


class UserListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError("List name must be 1–50 characters")
        return v

    @field_validator("description")
    @classmethod
    def valid_description(cls, v):
        if v is None:
            return v
        if len(v) > 160:
            raise ValueError("Description must be 160 characters or fewer")
        return v


class UserListOut(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    member_count: int
    owner: AuthorOut
    is_owner: bool = True


class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    slug: Optional[str] = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, v):
        v = (v or "").strip()
        if len(v) < 2 or len(v) > 60:
            raise ValueError("Community name must be 2–60 characters")
        return v

    @field_validator("description")
    @classmethod
    def valid_description(cls, v):
        if v is None:
            return ""
        if len(v) > 280:
            raise ValueError("Description must be 280 characters or fewer")
        return v

    @field_validator("slug")
    @classmethod
    def valid_slug(cls, v):
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        return v


class CommunityOut(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    created_at: datetime
    member_count: int
    is_member: bool = False
    is_arena: bool = False
    arena_key: Optional[str] = None
    creator: Optional[AuthorOut] = None


class SpaceCreate(BaseModel):
    title: str
    duration_hours: Optional[int] = 24
    kind: Optional[str] = "room"  # room | debate
    arena_key: Optional[str] = None
    community_id: Optional[str] = None
    topic_id: Optional[str] = None
    side_for_label: Optional[str] = "For"
    side_against_label: Optional[str] = "Against"

    @field_validator("title")
    @classmethod
    def valid_title(cls, v):
        v = (v or "").strip()
        if len(v) < 2 or len(v) > 140:
            raise ValueError("Space title must be 2–140 characters")
        return v

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, v):
        v = (v or "room").strip().lower()
        if v not in ("room", "debate"):
            raise ValueError("kind must be room or debate")
        return v


class SpaceOut(BaseModel):
    id: str
    title: str
    status: str
    kind: str = "room"
    created_at: datetime
    closes_at: Optional[datetime] = None
    post_count: int = 0
    is_host: bool = False
    host: Optional[AuthorOut] = None
    community_id: Optional[str] = None
    arena_key: Optional[str] = None
    arena_name: Optional[str] = None
    topic_id: Optional[str] = None
    topic_key: Optional[str] = None
    topic_name: Optional[str] = None
    source_url: Optional[str] = None
    side_for_label: str = "For"
    side_against_label: str = "Against"
    for_count: int = 0
    against_count: int = 0
    my_side: Optional[str] = None


class StanceCreate(BaseModel):
    side: str

    @field_validator("side")
    @classmethod
    def valid_side(cls, v):
        v = (v or "").strip().lower()
        if v not in ("for", "against"):
            raise ValueError("side must be for or against")
        return v


class LiveTalkStateUpdate(BaseModel):
    muted: Optional[bool] = None
    video_enabled: Optional[bool] = None


class LiveTalkPinBody(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        v = (v or "").strip().lstrip("@").lower()
        if len(v) < 2:
            raise ValueError("username required")
        return v


class LiveTalkMessageCreate(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if len(v) < 1 or len(v) > 500:
            raise ValueError("Message must be 1–500 characters")
        return v


class LiveTalkRemoveBody(BaseModel):
    reason: str = "community guidelines"

    @field_validator("reason")
    @classmethod
    def valid_reason(cls, v):
        v = (v or "community guidelines").strip()
        if len(v) < 3 or len(v) > 120:
            raise ValueError("Reason must be 3–120 characters")
        return v


class LiveTalkParticipantOut(BaseModel):
    user: AuthorOut
    muted: bool = True
    video_enabled: bool = False
    joined_at: datetime
    is_self: bool = False
    is_pinned: bool = False
    is_host: bool = False


class LiveTalkMessageOut(BaseModel):
    id: str
    text: str
    created_at: datetime
    sender: AuthorOut


class LiveTalkReactionCreate(BaseModel):
    emoji: str

    @field_validator("emoji")
    @classmethod
    def valid_emoji(cls, v):
        v = (v or "").strip()
        allowed = {"👍", "👎", "❤️", "😂", "👏", "🔥", "😮", "🎉"}
        if v not in allowed:
            raise ValueError("Pick a supported reaction")
        return v


class LiveTalkReactionOut(BaseModel):
    id: str
    emoji: str
    created_at: datetime
    user: AuthorOut


class LiveTalkStateOut(BaseModel):
    space_id: str
    max_participants: int = 15
    participant_count: int = 0
    in_talk: bool = False
    my_muted: bool = True
    my_video: bool = False
    participants: list[LiveTalkParticipantOut] = []
    messages: list[LiveTalkMessageOut] = []
    reactions: list[LiveTalkReactionOut] = []
    pinned_usernames: list[str] = []


class TopicOut(BaseModel):
    id: str
    arena_key: str
    key: str
    name: str
    blurb: str = ""
    is_following: bool = False
    open_debate_count: int = 0


class TopicInterestUpdate(BaseModel):
    topic_ids: list[str]
    replace: bool = True


class ArenaJoinMany(BaseModel):
    keys: list[str]


class ArenaOut(BaseModel):
    key: str
    slug: str
    name: str
    description: str
    member_count: int = 0
    is_member: bool = False
    open_debate_count: int = 0
    community_id: str


class SurfacePostCreate(BaseModel):
    text: str
    debate_side: Optional[str] = None

    @field_validator("text")
    @classmethod
    def valid_text(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Post cannot be empty")
        if len(v) > 280:
            raise ValueError("Post must be 280 characters or fewer")
        return v

    @field_validator("debate_side")
    @classmethod
    def valid_debate_side(cls, v):
        if v is None or v == "":
            return None
        v = v.strip().lower()
        if v not in ("for", "against"):
            raise ValueError("debate_side must be for or against")
        return v


class FoundingStatusOut(BaseModel):
    cap: int
    amount_inr: int
    min_problem_chars: int
    slots_remaining: int
    open: bool
    my_status: Optional[str] = None  # eligible | payable | paid | None
    my_kind: Optional[str] = None  # problem | debate
    my_quality: Optional[dict] = None
    qualify_arenas: list[str] = []
    civic_arenas: list[str] = []
    eval: Optional[dict] = None


class FoundingRewardRow(BaseModel):
    id: str
    user_id: str
    username: str
    display_name: str
    kind: str
    amount_inr: int
    status: str
    qualifying_post_id: Optional[str] = None
    qualifying_space_id: Optional[str] = None
    note: str = ""
    created_at: datetime
    paid_at: Optional[datetime] = None
    quality: Optional[dict] = None


class FoundingRewardsOut(BaseModel):
    cap: int
    amount_inr: int
    slots_remaining: int
    eligible_count: int
    payable_count: int = 0
    paid_count: int
    rewards: list[FoundingRewardRow]
    eval: Optional[dict] = None


class FoundingMarkPaid(BaseModel):
    note: Optional[str] = ""


class RaceLeaderRow(BaseModel):
    post_id: str
    text: str
    like_count: int
    prize_inr: int
    author_id: str
    username: str
    display_name: str
    created_at: datetime


class RaceStatusOut(BaseModel):
    period_key: str
    starts_at: datetime
    ends_at: datetime
    cadence_days: int
    prize_min: int
    prize_max: int
    min_likes_to_win: int
    eval: str
    leader: Optional[RaceLeaderRow] = None
    leaderboard: list[RaceLeaderRow] = []
    my_best: Optional[RaceLeaderRow] = None
    my_rank: Optional[int] = None
    period_paid: bool = False
    period_winner_username: Optional[str] = None


class RewardsOpsOut(BaseModel):
    """Read-only queue for blue accounts (payout actions stay on /admin)."""
    founding: FoundingRewardsOut
    race: RaceStatusOut
    note: str = "Blue can review progress. Mark paid / lock winner stays on /admin with ADMIN_SECRET."


class RaceRewardRow(BaseModel):
    id: str
    period_key: str
    user_id: str
    username: str
    post_id: str
    like_count: int
    amount_inr: int
    status: str
    note: str = ""
    created_at: datetime
    paid_at: Optional[datetime] = None
    period_starts_at: datetime
    period_ends_at: datetime


class RaceRewardsOut(BaseModel):
    current: RaceStatusOut
    rewards: list[RaceRewardRow]


class RaceCloseRequest(BaseModel):
    period_key: Optional[str] = None
    post_id: Optional[str] = None
    note: Optional[str] = ""


class RaceMarkPaid(BaseModel):
    note: Optional[str] = ""
