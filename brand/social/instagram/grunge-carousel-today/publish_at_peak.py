#!/usr/bin/env python3
"""Publish today's grunge carousel to Instagram at the next IST peak slot.

Peak slots (IST): 09:00, 13:30, 20:00.
Caption uses BaratX; URL remains barathx.com.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
GRAPH = "https://graph.facebook.com/v21.0"
PEAK_SLOTS = ((9, 0), (13, 30), (20, 0))
BRANCH = "cursor/grunge-carousel-today-2af5"
IMAGE_BASE = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    f"{BRANCH}/brand/social/instagram/grunge-carousel-today"
)
SLIDES = [
    "01-join-landing.png",
    "02-live-feed.png",
    "03-post-replies.png",
    "04-explore-india.png",
    "05-compose-prompts.png",
    "06-cta-comment-bx.png",
]
CAPTION = """Everyone's got a take. Few will post it.

BaratX is India's public square — short posts, real conversation.
Join free at barathx.com

Or comment BX for an invite.

#BaratX #BX #India #PublicSquare #SpeakYourTake"""


def _env(name: str) -> str:
    val = (os.environ.get(name) or "").strip()
    if val:
        return val
    secret = Path.home() / ".config" / "baratx" / "instagram.env"
    if secret.exists():
        for line in secret.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == name:
                return v.strip().strip('"').strip("'")
    return ""


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="ignore")
        raise RuntimeError(f"Graph API {e.code}: {err}") from e


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode())


def next_peak() -> datetime:
    now = datetime.now(IST)
    candidates = []
    for h, m in PEAK_SLOTS:
        t = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if t <= now:
            t += timedelta(days=1)
        candidates.append(t)
    return min(candidates)


def publish() -> dict:
    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not token or not ig_user_id:
        raise RuntimeError("Missing INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID")

    # quick token check
    try:
        _get(
            f"{GRAPH}/{ig_user_id}?fields=username&access_token={urllib.parse.quote(token)}"
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Instagram token invalid/expired — refresh ~/.config/baratx/instagram.env: {exc}"
        ) from exc

    urls = [f"{IMAGE_BASE}/{name}" for name in SLIDES]
    child_ids = []
    for url in urls:
        child = _post_form(
            f"{GRAPH}/{ig_user_id}/media",
            {"image_url": url, "is_carousel_item": "true", "access_token": token},
        )
        child_ids.append(child["id"])
        time.sleep(0.5)

    parent = _post_form(
        f"{GRAPH}/{ig_user_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": CAPTION,
            "access_token": token,
        },
    )
    creation_id = parent["id"]
    for _ in range(40):
        status = _get(
            f"{GRAPH}/{creation_id}?fields=status_code&access_token={urllib.parse.quote(token)}"
        )
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") == "ERROR":
            raise RuntimeError(f"container error: {status}")
        time.sleep(3)

    published = _post_form(
        f"{GRAPH}/{ig_user_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    return {
        "ok": True,
        "media_id": published.get("id"),
        "creation_id": creation_id,
        "when_ist": datetime.now(IST).isoformat(),
        "caption_brand": "BaratX",
    }


def main() -> None:
    force = "--now" in sys.argv
    target = datetime.now(IST) if force else next_peak()
    print(f"[ig] now={datetime.now(IST).isoformat()} target_peak={target.isoformat()}")
    if not force:
        wait = max(5.0, (target - datetime.now(IST)).total_seconds())
        print(f"[ig] sleeping {wait:.0f}s until peak…")
        time.sleep(wait)
    # small jitter so we land just after the slot minute
    time.sleep(2)
    result = publish()
    out = Path(__file__).resolve().parent / "LAST_PUBLISH.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
