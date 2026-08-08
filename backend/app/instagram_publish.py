"""Instagram carousel publisher + IST peak scheduler for @getbaratx.

Publishes BaratX app carousels via Meta Graph API. Slides are pulled by Meta
from public GitHub raw URLs (no image bytes in the API container).

Trending IG music cannot be attached via Graph API for feed carousels.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger("baratx.instagram")

IST = ZoneInfo("Asia/Kolkata")
GRAPH = "https://graph.facebook.com/v21.0"
DEFAULT_IMAGE_BASE = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/main/brand/carousel/export"
)

# India peak windows — up to 3 posts/day.
PEAK_SLOTS = (
    (9, 0, "morning"),
    (13, 30, "evening"),
    (20, 0, "evening"),
)

CAPTIONS = {
    "morning": [
        (
            "India doesn’t need another foreign firehose.\n"
            "It needs a public square.\n\n"
            "BaratX\n"
            "India's public square\n"
            "Short posts. Real conversation.\n\n"
            "→ https://barathx.com\n"
            "Follow on X → https://x.com/getbaratx\n"
            "Join WhatsApp community → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o\n"
            "Or comment BX for an invite.\n\n"
            "#BaratX #BX #IndiaPublicSquare #MakeInIndia #IndianApp "
            "#SocialMediaIndia #PublicSquare"
        ),
        (
            "Stop scrolling. Start arguing.\n\n"
            "BaratX\n"
            "India's public square\n\n"
            "Inside BaratX:\n"
            "• Home feed that feels Indian\n"
            "• Arenas for real fights\n"
            "• Replies > empty likes\n\n"
            "→ https://barathx.com\n"
            "Follow on X → https://x.com/getbaratx\n"
            "Join WhatsApp community → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o\n"
            "Or comment BX for an invite.\n\n"
            "#BaratX #BX #IndianStartup #TechIndia #JoinBaratX"
        ),
    ],
    "evening": [
        (
            "Your city has a take. The feed should hear it.\n\n"
            "BaratX\n"
            "India's public square\n\n"
            "Post one real problem from your street / ward / campus.\n"
            "Founding voices get seen — and rewarded for real civic posts.\n\n"
            "→ https://barathx.com\n"
            "Follow on X → https://x.com/getbaratx\n"
            "Join WhatsApp community → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o\n"
            "Or comment BX for an invite.\n\n"
            "#BaratX #BX #CivicTech #PublicSquare #Founding100"
        ),
        (
            "Every social app you use was built for someone else.\n\n"
            "BaratX\n"
            "India's public square\n"
            "Short posts. Real conversation.\n\n"
            "→ https://barathx.com\n"
            "Follow on X → https://x.com/getbaratx\n"
            "Join WhatsApp community → https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o\n"
            "Or comment BX for an invite.\n\n"
            "#BaratX #BX #IndiaFirst #DesiApp #JoinBaratX #PublicSquare"
        ),
    ],
}

_scheduler_started = False
_scheduler_lock = threading.Lock()


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


def _caption(pack: str) -> str:
    rows = CAPTIONS.get(pack) or CAPTIONS["evening"]
    idx = (datetime.now(IST).timetuple().tm_yday + datetime.now(IST).hour) % len(rows)
    return rows[idx]


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


def publish_carousel(*, pack: str = "evening", image_base_url: str = DEFAULT_IMAGE_BASE) -> dict:
    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not token or not ig_user_id:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID not set")

    caption = _caption(pack)
    base = image_base_url.rstrip("/")
    urls = [f"{base}/slide-{i:02d}.png" for i in range(1, 11)]

    child_ids = []
    for url in urls:
        child = _post_form(
            f"{GRAPH}/{ig_user_id}/media",
            {"image_url": url, "is_carousel_item": "true", "access_token": token},
        )
        child_ids.append(child["id"])
        time.sleep(0.4)

    parent = _post_form(
        f"{GRAPH}/{ig_user_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
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
        "pack": pack,
        "creation_id": creation_id,
        "media_id": published.get("id"),
        "when_ist": datetime.now(IST).isoformat(),
    }


def _seconds_until(hour: int, minute: int) -> float:
    now = datetime.now(IST)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return max(30.0, (target - now).total_seconds())


def start_instagram_scheduler() -> None:
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_INSTAGRAM_SCHEDULE", "").strip().lower() in ("1", "true", "yes"):
            logger.info("Instagram scheduler disabled")
            return
        if not _env("INSTAGRAM_ACCESS_TOKEN") or not _env("INSTAGRAM_BUSINESS_ACCOUNT_ID"):
            logger.info("Instagram scheduler idle — credentials not configured")
            return
        _scheduler_started = True

    def loop():
        while True:
            waits = [(_seconds_until(h, m), pack) for h, m, pack in PEAK_SLOTS]
            waits.sort(key=lambda x: x[0])
            wait, pack = waits[0]
            logger.info("Instagram schedule sleeping %.0fs until %s slot", wait, pack)
            time.sleep(wait)
            try:
                result = publish_carousel(pack=pack)
                logger.info("Instagram published: %s", result)
            except Exception:  # noqa: BLE001
                logger.exception("Instagram scheduled publish failed")
            time.sleep(90)

    threading.Thread(target=loop, name="baratx-ig-schedule", daemon=True).start()
    logger.info(
        "Instagram scheduler started (@getbaratx) slots=%s",
        ",".join(f"{h:02d}:{m:02d}/{p}" for h, m, p in PEAK_SLOTS),
    )
