"""Instagram carousel publisher + IST peak scheduler for @getbarathx.

Publishes BarathX carousels via Meta Graph API. Slides are pulled by Meta
from public GitHub raw URLs on **main** (never a stale feature-branch pack).

Hard rules:
- Brand spelling is **BarathX** (never BaratX / BharathX on creatives or captions)
- Each IST slot MUST use a different visual pack (signup-excite / how-it-works / launch-pain)
- Old brand/carousel/export pack is retired — do not point DEFAULT_IMAGE_BASE there
- Do not reuse one pack for all three daily captions

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

# Always serve packs from main so Railway Git deploys cannot drift to old assets.
_RAW = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    "main/brand/ig/carousel"
)

# Rotate visual packs by slot — DIFFERENT pictures for DIFFERENT captions.
# Never ship the same creative 3×/day.
_RAW = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    "main/brand/ig/carousel"
)
PACK_IMAGE_BASE = {
    "morning": f"{_RAW}/signup-excite",  # signup energy + landing
    "midday": f"{_RAW}/how-it-works",  # Square / Arenas mechanics
    "evening": f"{_RAW}/launch-pain",  # pain dunk / tonight CTA
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

FOOTER_IG = (
    f"app → {LINK_SITE}\n"
    f"X → {LINK_X}\n"
    f"WhatsApp → {LINK_WA}"
)

CAPTIONS = {
    "morning": [
        (
            "this is BarathX — India’s public square.\n\n"
            "Square · Arenas · Live.\n"
            "pick a side. argue it live. human takes only — no AI slop.\n\n"
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
            "#BarathX #India #GenZ #PickASide #PublicSquare"
        ),
        (
            "midday check —\n\n"
            "if your hottest take died in a group chat today, that’s the product "
            "gap. i’m fixing it.\n\n"
            "BarathX: drop it, pick a side, fight it out.\n"
            "create an account → leave one take.\n"
            "comment BX.\n\n"
            f"{FOOTER_IG}\n\n"
            "#BarathX #India #GenZ #PublicSquare #PickASide"
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
    caption = rows[idx]
    # Guardrail: never ship the misspelled brand in captions.
    if "BaratX" in caption or "BharathX" in caption:
        raise RuntimeError("Caption contains banned brand misspelling (BaratX/BharathX)")
    return caption


def _image_base(pack: str | None = None) -> str:
    pack = (pack or "midday").strip().lower()
    specific = _env(f"INSTAGRAM_IMAGE_BASE_{pack.upper()}")
    if specific:
        base = specific.rstrip("/")
    else:
        global_base = _env("INSTAGRAM_IMAGE_BASE")
        if global_base and _env("INSTAGRAM_FORCE_SINGLE_PACK").strip().lower() in (
            "1",
            "true",
            "yes",
        ):
            base = global_base.rstrip("/")
        else:
            base = (PACK_IMAGE_BASE.get(pack) or DEFAULT_IMAGE_BASE).rstrip("/")

    # Never fall back to the retired plain export pack on main.
    if "/brand/carousel/export" in base:
        logger.warning("Blocked retired carousel export path; using live-product")
        return PACK_IMAGE_BASE["morning"]
    return base


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
        "image_base": _image_base(pack) if image_base_url is None else image_base_url,
        "slide_urls": urls,
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


def _slot_dt_on(day: datetime, hour: int, minute: int) -> datetime:
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _recent_media_times(token: str, ig_user_id: str, *, limit: int = 12) -> list[datetime]:
    """IST timestamps of recent IG media (for dedupe / catch-up)."""
    q = urllib.parse.urlencode(
        {
            "fields": "timestamp",
            "limit": str(limit),
            "access_token": token,
        }
    )
    data = _get(f"{GRAPH}/{ig_user_id}/media?{q}")
    out: list[datetime] = []
    for row in data.get("data") or []:
        raw = row.get("timestamp") or ""
        try:
            ts = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(IST)
            out.append(ts)
        except ValueError:
            continue
    return out


def _already_posted_near(slot: datetime, recent: list[datetime], *, window_min: int = 50) -> bool:
    for ts in recent:
        if abs((ts - slot).total_seconds()) <= window_min * 60:
            return True
    return False


def _publish_slot_if_needed(pack: str, slot: datetime, *, reason: str) -> dict | None:
    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    if not token or not ig_user_id:
        return None
    recent = _recent_media_times(token, ig_user_id)
    if _already_posted_near(slot, recent):
        logger.info("Skip %s (%s) — already have media near %s", pack, reason, slot.isoformat())
        return None
    logger.info("Publishing %s (%s) for slot %s", pack, reason, slot.isoformat())
    return publish_carousel(pack=pack)


def _catch_up_missed_slots() -> None:
    """After Railway redeploys, fire any of today's slots we already missed (within grace)."""
    now = datetime.now(IST)
    # Catch up if we're up to 3h after the slot (covers midday killed by a deploy).
    grace = timedelta(hours=3)
    for hour, minute, pack in PEAK_SLOTS:
        slot = _slot_dt_on(now, hour, minute)
        if slot <= now <= slot + grace:
            try:
                _publish_slot_if_needed(pack, slot, reason="catch-up")
            except Exception:  # noqa: BLE001
                logger.exception("Instagram catch-up failed for pack=%s", pack)
            time.sleep(5)


def start_instagram_scheduler() -> None:
    """Run all 3 IST peak slots (09:00 / 13:30 / 20:00) every day.

    Railway redeploys used to kill the sleeping thread and skip midday/evening.
    On boot we catch up any missed slot still inside a 3h grace window, and we
    dedupe against recent IG media so catch-up cannot double-post.
    """
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_INSTAGRAM_SCHEDULE", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ):
            logger.info("Instagram scheduler disabled")
            return
        if not _env("INSTAGRAM_ACCESS_TOKEN") or not _env("INSTAGRAM_BUSINESS_ACCOUNT_ID"):
            logger.info("Instagram scheduler idle — credentials not configured")
            return
        _scheduler_started = True

    def loop():
        try:
            _catch_up_missed_slots()
        except Exception:  # noqa: BLE001
            logger.exception("Instagram catch-up sweep failed")

        while True:
            now = datetime.now(IST)
            waits: list[tuple[float, str, datetime]] = []
            for hour, minute, pack in PEAK_SLOTS:
                slot = _slot_dt_on(now, hour, minute)
                if slot <= now:
                    slot = slot + timedelta(days=1)
                waits.append(((slot - now).total_seconds(), pack, slot))
            waits.sort(key=lambda x: x[0])
            wait, pack, slot = waits[0]
            wait = max(30.0, wait)
            logger.info(
                "Instagram schedule sleeping %.0fs until %s slot (%s IST)",
                wait,
                pack,
                slot.strftime("%Y-%m-%d %H:%M"),
            )
            time.sleep(wait)
            try:
                _publish_slot_if_needed(pack, slot, reason="scheduled")
            except Exception:  # noqa: BLE001
                logger.exception("Instagram scheduled publish failed for pack=%s", pack)
            time.sleep(90)

    threading.Thread(target=loop, name="baratx-ig-schedule", daemon=True).start()
    logger.info(
        "Instagram scheduler started (@getbarathx) 3 slots/day=%s base=%s",
        ",".join(f"{h:02d}:{m:02d}/{p}" for h, m, p in PEAK_SLOTS),
        {p: _image_base(p) for _, _, p in PEAK_SLOTS},
    )
