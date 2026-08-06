#!/usr/bin/env python3
"""Post BaratX carousel to Instagram via Meta Graph API.

Requires env:
  INSTAGRAM_ACCESS_TOKEN
  INSTAGRAM_BUSINESS_ACCOUNT_ID

Usage:
  python3 brand/social/instagram/post_carousel.py --pack morning
  python3 brand/social/instagram/post_carousel.py --pack evening --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "brand" / "carousel" / "export"
CAPTIONS = ROOT / "brand" / "social" / "instagram" / "captions.json"
GRAPH = "https://graph.facebook.com/v21.0"


def _env(name: str) -> str:
    val = (os.environ.get(name) or "").strip()
    if not val:
        # Optional local secret file (gitignored / outside repo)
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
    # Rotate by day-of-year
    idx = time.gmtime().tm_yday % len(packs)
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
        with urllib.request.urlopen(req, timeout=60) as resp:
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

    # Wait until finished
    for _ in range(30):
        status = _get_json(
            f"{GRAPH}/{creation_id}?fields=status_code&access_token={urllib.parse.quote(token)}"
        )
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise SystemExit(f"Container error: {status}")
        time.sleep(2)

    published = _post_json(
        f"{GRAPH}/{ig_user_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    return {"creation_id": creation_id, "publish": published, "children": child_ids}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", choices=("morning", "evening"), default="morning")
    parser.add_argument(
        "--image-base-url",
        default="",
        help="Public HTTPS base that serves slide-01.png … (required to publish)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    caption = _load_caption(args.pack)
    slides = _slide_paths()
    print(f"pack={args.pack} slides={len(slides)} caption_chars={len(caption)}")

    if args.dry_run or not args.image_base_url:
        print("--- caption ---")
        print(caption)
        print("--- slides ---")
        for p in slides:
            print(p)
        if not args.image_base_url:
            print(
                "\nDry output only. To publish, host slides publicly and pass "
                "--image-base-url https://…/path (Meta must fetch each PNG)."
            )
        return

    token = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    base = args.image_base_url.rstrip("/")
    urls = [f"{base}/{p.name}" for p in slides]
    result = create_carousel(image_urls=urls, caption=caption, token=token, ig_user_id=ig_user_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
