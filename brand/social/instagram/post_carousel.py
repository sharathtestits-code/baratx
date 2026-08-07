#!/usr/bin/env python3
"""Post BaratX carousel to Instagram via Meta Graph API.

Requires env (or ~/.config/baratx/instagram.env):
  INSTAGRAM_ACCESS_TOKEN
  INSTAGRAM_BUSINESS_ACCOUNT_ID

Usage:
  python3 brand/social/instagram/post_carousel.py --pack morning --image-base-url https://...
  python3 brand/social/instagram/post_carousel.py --pack evening --dry-run
  python3 brand/social/instagram/post_carousel.py --schedule   # 3×/day IST peak times
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "brand" / "carousel" / "export"
CAPTIONS = ROOT / "brand" / "social" / "instagram" / "captions.json"
GRAPH = "https://graph.facebook.com/v21.0"
IST = ZoneInfo("Asia/Kolkata")

# India peak windows — 3 posts/day max.
PEAK_SLOTS = (
    (9, 0, "morning"),    # morning scroll
    (13, 30, "evening"),  # lunch / afternoon
    (20, 0, "evening"),   # prime evening
)

DEFAULT_IMAGE_BASE = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/main/brand/carousel/export"
)

_scheduler_started = False
_scheduler_lock = threading.Lock()


def _env(name: str) -> str:
    val = (os.environ.get(name) or "").strip()
    if not val:
        secret = Path.home() / ".config" / "baratx" / "instagram.env"
        if secret.exists():
            for line in secret.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == name:
                    val = v.strip().strip('"').strip("'")
                    break
    if not val:
        raise SystemExit(f"Missing {name}. See brand/social/instagram/README.md")
    return val


def _load_caption(pack: str) -> str:
    data = json.loads(CAPTIONS.read_text())
    packs = data.get(pack) or []
    if not packs:
        raise SystemExit(f"No captions for pack={pack}")
    idx = time.gmtime().tm_yday % len(packs)
    # Also rotate by hour so morning/evening same day can differ
    idx = (idx + datetime.now(IST).hour) % len(packs)
    return packs[idx].strip()


def _slide_paths() -> list[Path]:
    paths = sorted(EXPORT.glob("slide-*.png"))
    if len(paths) < 2:
        raise SystemExit(f"Need carousel slides in {EXPORT}")
    return paths[:10]


def _post_json(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="ignore")
        raise SystemExit(f"Graph API error {e.code}: {err}") from e


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode())


def create_carousel(*, image_urls: list[str], caption: str, token: str, ig_user_id: str) -> dict:
    """image_urls must be publicly reachable HTTPS URLs (Meta fetches them)."""
    child_ids = []
    for url in image_urls:
        child = _post_json(
            f"{GRAPH}/{ig_user_id}/media",
            {
                "image_url": url,
                "is_carousel_item": "true",
                "access_token": token,
            },
        )
        child_ids.append(child["id"])
        # Brief pause helps avoid IG rate hiccups on 10-item carousels
        time.sleep(0.4)

    parent = _post_json(
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
        status = _get_json(
            f"{GRAPH}/{creation_id}?fields=status_code&access_token={urllib.parse.quote(token)}"
        )
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise SystemExit(f"Container error: {status}")
        time.sleep(3)

    published = _post_json(
        f"{GRAPH}/{ig_user_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    return {"creation_id": creation_id, "publish": published, "children": child_ids}


def publish_pack(*, pack: str, image_base_url: str) -> dict:
    caption = _load_caption(pack)
    slides = _slide_paths()
    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    base = image_base_url.rstrip("/")
    urls = [f"{base}/{p.name}" for p in slides]
    result = create_carousel(image_urls=urls, caption=caption, token=token, ig_user_id=ig_user_id)
    result["pack"] = pack
    result["caption_chars"] = len(caption)
    result["slides"] = len(slides)
    result["when_ist"] = datetime.now(IST).isoformat()
    return result


def _seconds_until_slot(hour: int, minute: int) -> float:
    now = datetime.now(IST)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    return max(30.0, (target - now).total_seconds())


def start_instagram_scheduler(*, image_base_url: str = DEFAULT_IMAGE_BASE) -> None:
    """Fire carousels at India peak times (up to 3/day)."""
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        if os.environ.get("DISABLE_INSTAGRAM_SCHEDULE", "").strip().lower() in ("1", "true", "yes"):
            print("Instagram scheduler disabled via DISABLE_INSTAGRAM_SCHEDULE")
            return
        _scheduler_started = True

    def loop():
        while True:
            # Pick the soonest upcoming slot
            waits = [(_seconds_until_slot(h, m), pack) for h, m, pack in PEAK_SLOTS]
            waits.sort(key=lambda x: x[0])
            wait, pack = waits[0]
            print(f"[ig-schedule] sleeping {wait:.0f}s until next {pack} slot (IST)")
            time.sleep(wait)
            try:
                result = publish_pack(pack=pack, image_base_url=image_base_url)
                print(f"[ig-schedule] published: {json.dumps(result)}")
            except Exception as exc:  # noqa: BLE001
                print(f"[ig-schedule] publish failed: {exc}")
            time.sleep(90)  # avoid double-fire in same minute

    t = threading.Thread(target=loop, name="baratx-ig-schedule", daemon=True)
    t.start()
    print(
        "[ig-schedule] started — slots IST "
        + ", ".join(f"{h:02d}:{m:02d}/{p}" for h, m, p in PEAK_SLOTS)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", choices=("morning", "evening"), default="morning")
    parser.add_argument("--image-base-url", default=DEFAULT_IMAGE_BASE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run in-process 3×/day IST peak scheduler (blocking)",
    )
    args = parser.parse_args()

    if args.schedule:
        start_instagram_scheduler(image_base_url=args.image_base_url)
        while True:
            time.sleep(3600)

    caption = _load_caption(args.pack)
    slides = _slide_paths()
    print(f"pack={args.pack} slides={len(slides)} caption_chars={len(caption)}")

    if args.dry_run:
        print("--- caption ---")
        print(caption)
        print("--- slides ---")
        for p in slides:
            print(p)
        return

    result = publish_pack(pack=args.pack, image_base_url=args.image_base_url)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
