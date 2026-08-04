import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
PHONE_RE = re.compile(r"^\+?[1-9]\d{9,14}$")  # loose E.164-ish check


class EmailSignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    display_name: str

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3-20 chars: letters, numbers, underscore only")
        return v

    @field_validator("password")
    @classmethod
    def valid_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PhoneOtpRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, v):
        if not PHONE_RE.match(v):
            raise ValueError("Enter a valid phone number with country code, e.g. +919876543210")
        return v


class PhoneSignupVerify(BaseModel):
    phone: str
    otp: str
    username: str
    display_name: str

    @field_validator("username")
    @classmethod
    def valid_username(cls, v):
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3-20 chars: letters, numbers, underscore only")
        return v


class PhoneLoginVerify(BaseModel):
    phone: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None

    @field_validator("display_name")
    @classmethod
    def valid_display_name(cls, v):
        if v is None:
            return v
        name = v.strip()
        if len(name) < 1 or len(name) > 50:
            raise ValueError("Display name must be 1–50 characters")
        return name

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


class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    language: str
    bio: str
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
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

    class Config:
        from_attributes = True


class ReplyCreate(BaseModel):
    text: str


class ReplyOut(BaseModel):
    id: str
    post_id: str
    text: str
    created_at: datetime
    author: AuthorOut
    like_count: int = 0
    liked_by_me: bool = False

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

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    users: list[UserSearchOut]
    posts: list[PostOut]
