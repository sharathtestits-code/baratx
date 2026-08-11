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

# Rotate visual packs by slot — do NOT ship the same creative 3×/day.
# Override any pack with INSTAGRAM_IMAGE_BASE_* or global INSTAGRAM_IMAGE_BASE.
_RAW = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    "cursor/ig-carousel-what-is-2af5/brand/ig/carousel"
)
PACK_IMAGE_BASE = {
    "morning": f"{_RAW}/signup-excite",  # why join / first take — signup energy
    "midday": f"{_RAW}/how-it-works",  # mechanic depth (not grunge repeat)
    "evening": f"{_RAW}/launch-pain",  # pain dunk — different from morning
}
DEFAULT_IMAGE_BASE = PACK_IMAGE_BASE["morning"]
SLIDE_COUNT = 6
SLIDE_EXT = "jpg"

# India peak windows — up to 3 posts/day.
PEAK_SLOTS = (
    (9, 0, "morning"),
    (13, 30, "midday"),
    (20, 0, "evening"),
)

# Cross-post social links (always BarathX product; handles as provided).
LINK_SITE = "https://barathx.com"
LINK_IG = "https://www.instagram.com/getbarathx/"
LINK_X = "https://x.com/getbaratx"
LINK_WA = "https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o"

# Footers appended to captions (platform-specific cross-links).
FOOTER_IG = (
    f"app → {LINK_SITE}\n"
    f"X → {LINK_X}\n"
    f"WhatsApp → {LINK_WA}"
)
FOOTER_X = (
    f"app → {LINK_SITE}\n"
    f"IG → {LINK_IG}\n"
    f"WhatsApp → {LINK_WA}"
)

# Founder-voice captions — sound like a real human building in public.
# Standing approval from founder (2026-08-10): post on IST peak slots with this
# grunge template; captions may be AI-assisted but must stay founder-tone.
# Privacy mentioned sparingly (midday pack).
# IG posts always include X + WhatsApp (FOOTER_IG).
CAPTIONS = {
    "morning": [
        (
            "your take deserves a side — not a like.\n\n"
            "on BarathX you pick Agree or Disagree and people actually argue back.\n"
            "Square · Arenas · Live. human takes only. no ai slop.\n\n"
            "we’re early. first voices get seen.\n"
            "create an account, leave one honest take.\n"
            "comment BX if you want the invite personally.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #PublicSquare #PickASide #BuildInPublic"
        ),
        (
            "stop performing. start arguing.\n\n"
            "BarathX = India’s public square.\n"
            "drop a take → pick a side → get a real reply.\n\n"
            "takes 60 seconds to sign up. we’re small on purpose.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #Debate #CampusLife #PublicSquare"
        ),
    ],
    "midday": [
        (
            "how BarathX actually works —\n\n"
            "1. drop a take in the Square\n"
            "2. pick a side (no fence)\n"
            "3. jump an Arena or go Live\n\n"
            "real replies. not a performance feed.\n"
            "sign up and leave your first take today.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #Privacy #PickASide #PublicSquare"
        ),
        (
            "midday check —\n\n"
            "if your hottest take died in a group chat today, that’s the product "
            "gap. i’m fixing it.\n\n"
            "BarathX: drop it, pick a side, fight it out.\n"
            "create an account → leave one take.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #PublicSquare #PickASide #Privacy"
        ),
    ],
    "evening": [
        (
            "end of day —\n\n"
            "whatsapp buries your best takes.\n"
            "reels want your thumb, not your opinion.\n\n"
            "BarathX is the square where india actually argues.\n"
            "sign up. leave one honest take tonight.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #PublicSquare #BuildInPublic #DesiApp"
        ),
        (
            "one ask tonight — leave one honest take on BarathX.\n\n"
            "no reels firehose inside. no ai slop.\n"
            "just sides, arenas, and people who showed up for the same fight.\n\n"
            "create your account. i’m building this for us.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
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


def _image_base(pack: str | None = None) -> str:
    pack = (pack or "midday").strip().lower()
    # Per-slot override, then global, then pack default.
    specific = _env(f"INSTAGRAM_IMAGE_BASE_{pack.upper()}")
    if specific:
        return specific.rstrip("/")
    global_base = _env("INSTAGRAM_IMAGE_BASE")
    # Only use global if it doesn't force one pack for every slot.
    if global_base and _env("INSTAGRAM_FORCE_SINGLE_PACK").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return global_base.rstrip("/")
    return (PACK_IMAGE_BASE.get(pack) or DEFAULT_IMAGE_BASE).rstrip("/")


def _slide_urls(image_base_url: str | None = None, pack: str | None = None) -> list[str]:
    base = (image_base_url or _image_base(pack)).rstrip("/")
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
    urls = _slide_urls(image_base_url, pack=pack)

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
        {p: _image_base(p) for _, _, p in PEAK_SLOTS},
    )
