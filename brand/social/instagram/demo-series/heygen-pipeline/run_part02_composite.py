#!/usr/bin/env python3
"""Part 2 Arenas — generate HeyGen VO (optional) + composite into left 35% zone.

Modes:
  A) You already exported from HeyGen UI:
       python3 run_part02_composite.py --avatar ~/Downloads/my-clone.webm

  B) API generate from VO script (needs HEYGEN_* env):
       python3 run_part02_composite.py --generate

  C) Smoke test (no API key):
       python3 run_part02_composite.py --smoke

Base reel is fetched from the open Part 2 branch if missing locally.
"""

from __future__ import annotations

import argparse
import subprocess
import urllib.request
from pathlib import Path

from composite_avatar import composite, make_smoke_avatar
from heygen_client import create_avatar_video, download, wait_for_video
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # brand/
REPO = HERE.parents[4]
PART2 = HERE.parent / "PART-02-arenas"
CACHE = HERE / "cache"
VO = HERE / "PART02_VO.txt"

BASE_CANDIDATES = [
    PART2 / "barathx-PART2-arenas-25s.mp4",
    REPO / "brand/social/daily/2026-08-28/barathx-PART2-arenas-25s.mp4",
]
BASE_URL = (
    "https://raw.githubusercontent.com/sharathtestits-code/baratx/"
    "cursor/arenas-part2-25s-2af5/brand/social/daily/2026-08-28/barathx-PART2-arenas-25s.mp4"
)


def ensure_base() -> Path:
    for c in BASE_CANDIDATES:
        if c.exists() and c.stat().st_size > 10_000:
            return c
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / "barathx-PART2-arenas-25s-BASE.mp4"
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    print(f"Downloading Part 2 base from GitHub…\n  {BASE_URL}")
    urllib.request.urlretrieve(BASE_URL, dest)
    return dest


def generate_avatar(out: Path) -> Path:
    avatar_id = os.environ.get("HEYGEN_AVATAR_ID", "").strip()
    voice_id = os.environ.get("HEYGEN_VOICE_ID", "").strip()
    if not avatar_id or not voice_id:
        raise SystemExit("Set HEYGEN_AVATAR_ID and HEYGEN_VOICE_ID for --generate")
    script = VO.read_text(encoding="utf-8").strip()
    print("Creating HeyGen avatar video…")
    vid = create_avatar_video(
        script=script,
        avatar_id=avatar_id,
        voice_id=voice_id,
        title="BarathX Part 2 Arenas VO",
        aspect_ratio="9:16",
        remove_background=True,
        output_format="webm",
    )
    info = wait_for_video(vid)
    url = info.get("video_url")
    if not url:
        raise SystemExit(f"No video_url: {info}")
    download(url, out)
    return out


def poster(mp4: Path, jpg: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "1.2", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(jpg)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--avatar", type=Path, help="Local HeyGen export")
    p.add_argument("--generate", action="store_true", help="Call HeyGen API using PART02_VO.txt")
    p.add_argument("--smoke", action="store_true", help="Synthetic avatar (no API)")
    p.add_argument(
        "--out",
        type=Path,
        default=CACHE / "barathx-PART2-arenas-25s-HEYGEN.mp4",
    )
    args = p.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    base = ensure_base()
    print(f"Base: {base}")

    if args.generate:
        avatar = generate_avatar(CACHE / "part02-avatar.webm")
    elif args.smoke:
        avatar = make_smoke_avatar(CACHE / "part02-smoke-avatar.mp4", duration=21.0)
    elif args.avatar:
        avatar = args.avatar
    else:
        raise SystemExit("Choose --avatar PATH, --generate, or --smoke")

    print(f"Avatar: {avatar}")
    out = composite(base=base, avatar=avatar, out=args.out, avatar_end_s=21.0)
    jpg = out.with_suffix(".poster.jpg")
    poster(out, jpg)

    # Convenience copies for download / daily pack
    daily = REPO / "brand/social/daily/2026-08-28"
    daily.mkdir(parents=True, exist_ok=True)
    (daily / "barathx-PART2-arenas-25s-HEYGEN.mp4").write_bytes(out.read_bytes())
    downloads = Path("/opt/cursor/artifacts/downloads")
    if downloads.exists() or True:
        downloads.mkdir(parents=True, exist_ok=True)
        (downloads / "BarathX-Part2-Arenas-25s-HEYGEN.mp4").write_bytes(out.read_bytes())

    print(f"Wrote {out}")
    print(f"Poster {jpg}")
    print(f"Daily  {daily / 'barathx-PART2-arenas-25s-HEYGEN.mp4'}")


if __name__ == "__main__":
    main()
