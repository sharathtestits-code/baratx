"""Instagram carousel publisher + IST peak scheduler for @getbaratx.

Publishes BarathX grunge carousels via Meta Graph API. Slides are pulled by Meta
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

# Grunge "What is BarathX" pack (6 slides). Override with INSTAGRAM_IMAGE_BASE.
DEFAULT_IMAGE_BASE = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    "cursor/ig-carousel-what-is-2af5/brand/ig/carousel/grunge-what"
)
SLIDE_COUNT = 6
SLIDE_EXT = "jpg"

# India peak windows — up to 3 posts/day.
PEAK_SLOTS = (
    (9, 0, "morning"),
    (13, 30, "midday"),
    (20, 0, "evening"),
)

# Founder-voice captions — sound like a real human building in public.
# Standing approval from founder (2026-08-10): post on IST peak slots with this
# grunge template; captions may be AI-assisted but must stay founder-tone.
# Privacy mentioned sparingly (midday pack).
CAPTIONS = {
    "morning": [
        (
            "okay real talk before the day gets loud —\n\n"
            "i’m building BarathX because india deserved a square that isn’t "
            "someone else’s product with desi stickers.\n\n"
            "drop a take. pick a side. get a real reply.\n"
            "human takes only. no ai slop.\n\n"
            "we’re early. that’s kind of the point — come argue with actual "
            "people, not a feed.\n"
            "→ https://barathx.com · comment BX and i’ll send it.\n\n"
            "#BarathX #India #GenZ #PublicSquare #PickASide #BuildInPublic"
        ),
        (
            "founder morning note —\n\n"
            "BarathX = India’s public square.\n"
            "Square · Arenas · Live.\n\n"
            "not a performance feed. just the take you’d only say to friends — "
            "said in public.\n\n"
            "come leave yours → https://barathx.com\n\n"
            "#BarathX #India #GenZ #Debate #CampusLife #PublicSquare"
        ),
    ],
    "midday": [
        (
            "quick one from me —\n\n"
            "whatsapp buries your best takes.\n"
            "reels don’t want your opinion. they want your thumb.\n\n"
            "on BarathX you pick a side and argue it. sports, cinema, campus, "
            "startups — out loud.\n\n"
            "and we don’t sell your personal data. non‑negotiable.\n\n"
            "sign up → https://barathx.com\n"
            "or comment BX for an invite.\n\n"
            "#BarathX #India #GenZ #Privacy #PickASide #PublicSquare"
        ),
        (
            "midday check —\n\n"
            "if your hottest take died in a group chat today, that’s the product "
            "gap. i’m fixing it.\n\n"
            "BarathX: drop it, pick a side, fight it out with people who care.\n"
            "we don’t sell your data.\n\n"
            "→ https://barathx.com · comment BX\n\n"
            "#BarathX #India #GenZ #PublicSquare #PickASide #Privacy"
        ),
    ],
    "evening": [
        (
            "end of day, from the founder —\n\n"
            "every app we grew up on was built for someone else’s culture.\n"
            "language. norms. what “counts” as a take.\n\n"
            "BarathX is india’s own public square.\n"
            "drop a take. pick a side. real replies — not a performance.\n\n"
            "swipe, then just join.\n"
            "https://barathx.com\n\n"
            "#BarathX #India #GenZ #PublicSquare #BuildInPublic #DesiApp"
        ),
        (
            "one ask tonight — leave one honest take on BarathX.\n\n"
            "no reels firehose inside. no ai slop.\n"
            "just sides, arenas, and people who showed up for the same fight.\n\n"
            "i’m building this for us.\n"
            "→ https://barathx.com · comment BX\n\n"
            "#BarathX #India #GenZ #PickASide #PublicSquare"
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


def _image_base() -> str:
    return (_env("INSTAGRAM_IMAGE_BASE") or DEFAULT_IMAGE_BASE).rstrip("/")


def _slide_urls(image_base_url: str | None = None) -> list[str]:
    base = (image_base_url or _image_base()).rstrip("/")
    ext = (_env("INSTAGRAM_SLIDE_EXT") or SLIDE_EXT).lstrip(".")
    count = int(_env("INSTAGRAM_SLIDE_COUNT") or SLIDE_COUNT)
    return [f"{base}/slide-{i:02d}.{ext}" for i in range(1, count + 1)]


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


def publish_carousel(*, pack: str = "evening", image_base_url: str | None = None) -> dict:
    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not token or not ig_user_id:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID not set")

    caption = _caption(pack)
    urls = _slide_urls(image_base_url)

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
        "caption_preview": caption.split("\n", 1)[0],
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
        "Instagram scheduler started (@getbaratx) slots=%s base=%s",
        ",".join(f"{h:02d}:{m:02d}/{p}" for h, m, p in PEAK_SLOTS),
        _image_base(),
    )
