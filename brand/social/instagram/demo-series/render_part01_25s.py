#!/usr/bin/env python3
"""BarathX demo series — Part 1 (Square) cut to exactly 25.0s, 9:16.

Rebuilds from PART-01-square-v4 screen-recording middle with corrected
BarathX title + Part 2 cliffhanger cards.
"""

from __future__ import annotations

import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]  # …/demo-series → workspace
SRC = (
    ROOT
    / "brand"
    / "social"
    / "instagram"
    / "demo-series"
    / "PART-01-square-v4"
    / "baratx-demo-PART1-v4.mp4"
)
OUT_DIR = (
    ROOT
    / "brand"
    / "social"
    / "instagram"
    / "demo-series"
    / "PART-01-square-v5"
)
DAILY = ROOT / "brand" / "social" / "daily" / "2026-08-25"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1920
FPS = 30
DARK = (13, 13, 18)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 153, 51)
MUTED = (160, 160, 170)

TITLE_S = 2.0
DEMO_S = 20.5
END_S = 2.5
# Source: skip old title (~0–2.0), keep UI until end card (~30.0)
SRC_IN = 2.0
SRC_OUT = 30.0
# TOTAL = 25.0


def _font_paths() -> tuple[str, str]:
    bold = (
        glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
    )
    regular = (
        glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
        or bold
    )
    if not bold:
        raise SystemExit("No Bold TTF under /usr/share/fonts")
    return bold[0], regular[0]


FONT_B, FONT_R = _font_paths()


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def paste_logo(base: Image.Image, size: int, xy: tuple[int, int]) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, xy, circ)


def title_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 160, ((W - 160) // 2, 420))
    d.text((W // 2 - 170, 640), "BarathX", font=fnt(72), fill=WHITE)
    d.text((W // 2 - 220, 740), "Features · Part 1", font=fnt(40), fill=SAFFRON)
    d.text((W // 2 - 120, 820), "Square", font=fnt(56), fill=CREAM)
    d.text(
        (W // 2 - 280, 940),
        "Write · AI Assist · engage · menu",
        font=fnt(28, False),
        fill=MUTED,
    )
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Daily series · Part 1 of 7", font=fnt(32), fill=DARK)
    return base


def end_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 120, ((W - 120) // 2, 480))
    d.text((W // 2 - 140, 660), "Part 2 →", font=fnt(64), fill=SAFFRON)
    d.text((W // 2 - 220, 760), "Arenas & debates", font=fnt(44), fill=WHITE)
    d.text((W // 2 - 200, 860), "Drops tomorrow", font=fnt(36, False), fill=MUTED)
    d.text((W // 2 - 180, 980), "Follow @getbaratx", font=fnt(32), fill=CREAM)
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Join free → barathx.com", font=fnt(32), fill=DARK)
    return base


def jpg_clip(img: Image.Image, path: Path, duration: float) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=93)
    out = path.with_suffix(".mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(path),
            "-t",
            f"{duration:.3f}",
            "-r",
            str(FPS),
            "-vf",
            f"scale={W}:{H},format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def demo_clip(tmp: Path) -> Path:
    if not SRC.exists():
        raise SystemExit(f"Missing source reel: {SRC}")
    src_dur = SRC_OUT - SRC_IN
    speed = src_dur / DEMO_S
    out = tmp / "demo.mp4"
    # setpts compresses; trim first
    vf = (
        f"trim=start={SRC_IN}:end={SRC_OUT},setpts=PTS-STARTPTS,"
        f"setpts=PTS/{speed},"
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(SRC),
            "-vf",
            vf,
            "-an",
            "-t",
            f"{DEMO_S:.3f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def concat(clips: list[Path], out: Path, tmp: Path) -> None:
    list_path = tmp / "_concat.txt"
    list_path.write_text(
        "".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def poster_from(mp4: Path, jpg: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            "0.4",
            "-i",
            str(mp4),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(jpg),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bx-p1-25s-") as td:
        tmp = Path(td)
        title = jpg_clip(title_card(), tmp / "title.jpg", TITLE_S)
        demo = demo_clip(tmp)
        end = jpg_clip(end_card(), tmp / "end.jpg", END_S)

        out_name = "barathx-demo-PART1-25s.mp4"
        out = OUT_DIR / out_name
        concat([title, demo, end], out, tmp)

        poster = OUT_DIR / "barathx-demo-PART1-25s-poster.jpg"
        poster_from(out, poster)

        # Daily pack aliases (same file for IG / X / WA)
        for dest in (
            DAILY / "barathx-part1-25s.mp4",
            DAILY / "barathx-daily-reel-25s.mp4",
        ):
            dest.write_bytes(out.read_bytes())
        (DAILY / "barathx-part1-25s-poster.jpg").write_bytes(poster.read_bytes())

        # Probe
        probe = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(out),
            ],
            text=True,
        ).strip()
        print(f"Wrote {out} ({probe}s)")
        print(f"Poster {poster}")
        print(f"Daily aliases → {DAILY}")


if __name__ == "__main__":
    main()
