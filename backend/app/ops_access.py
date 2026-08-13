"""Ops console access — controlled by Railway API env (not Vite build-time vars).

OPS_OWNER_USERNAMES — comma/space-separated usernames who may open the console UI
  (default: sharath). Example: testits,sharath

OPS_CONSOLE_PATH — secret path for the console UI (default: /bx-ops).
  Example: /hq-9f3k-console

Unlocking money actions still requires ADMIN_SECRET separately.
"""

from __future__ import annotations

import os
import re
from typing import Optional

_DEFAULT_OWNERS = ("sharath",)
_DEFAULT_PATH = "/bx-ops"


def ops_owner_usernames() -> set[str]:
    raw = (os.environ.get("OPS_OWNER_USERNAMES") or "").strip()
    if not raw:
        return set(_DEFAULT_OWNERS)
    return {s.strip().lower() for s in re.split(r"[\s,]+", raw) if s.strip()}


def ops_console_path() -> str:
    raw = (os.environ.get("OPS_CONSOLE_PATH") or _DEFAULT_PATH).strip()
    if not raw.startswith("/"):
        raw = f"/{raw}"
    raw = raw.rstrip("/") or _DEFAULT_PATH
    # Never allow colliding with public app routes
    blocked = {"/admin", "/feed", "/login", "/signup", "/", "/api"}
    if raw.lower() in blocked:
        return _DEFAULT_PATH
    return raw


def is_ops_owner_username(username: Optional[str]) -> bool:
    if not username:
        return False
    return str(username).strip().lower() in ops_owner_usernames()


def is_ops_owner_user(user) -> bool:
    return is_ops_owner_username(getattr(user, "username", None))
