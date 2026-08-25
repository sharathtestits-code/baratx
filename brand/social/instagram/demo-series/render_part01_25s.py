#!/usr/bin/env python3
"""BarathX Part 1 — Square — exact 25.0s from TODAY's live screens only.

Uses brand/social/whatsapp/screens/live-YYYY-MM-DD/ (capture first).
Does NOT reuse older live-* folders or archived screen recordings.
"""

from __future__ import annotations

import glob
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
TODAY = date.today().isoformat()
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / f"live-{TODAY}"
OUT_DIR = (
    ROOT
    / "brand"
    / "social"
    / "instagram"
    / "demo-series"
    / "PART-01-square-v5"
)
DAILY = ROOT / "brand" / "social" / "daily" / TODAY
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"
DOWNLOADS = Path("/opt/cursor/artifacts/downloads")
SHOTS = Path("/opt/cursor/artifacts/screenshots")

W, H = 1080, 1920
FPS = 30
DARK = (13, 13, 18)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 153, 51)
MUTED = (160, 160, 170)

# Exact 25.0s
BEATS: list[tuple[str, str, str, str, float]] = [
    # screen_file, kicker, title, sub, seconds
    ("__title__", "Features · Part 1", "Square", "Daily series · latest UI", 2.0),
    (
        "landing-mobile.png",
        "Soft launch",
        "India has opinions. Now it has a home.",
        "Agree · Disagree · It depends",
        4.0,
    ),
    (
        "square-mobile.png",
        "Square",
        "One question. Your take.",
        "No Reels required.",
        5.0,
    ),
    (
        "square-compose-mobile.png",
        "Drop a take",
        "Short post. Real replies.",
        "Photo · Live · Community",
        5.0,
    ),
    (
        "square-engage-mobile.png",
        "On the Square",
        "Live now + human takes",
        "Human first. No AI slop.",
        4.5,
    ),
    (
        "home-mobile.png",
        "Home hub",
        "Overview · Tagged · Following",
        "Then Arenas tomorrow",
        2.0,
    ),
    ("__end__", "Part 2 →", "Arenas & debates", "Drops tomorrow · @getbaratx", 2.5),
]
# 2+4+5+5+4.5+2+2.5 = 25.0


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


def wrap(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def require_live() -> None:
    if not LIVE.is_dir():
        raise SystemExit(
            f"Missing TODAY screens: {LIVE}\n"
            "Run: /tmp/bx-pw/bin/python brand/social/capture_live_screens_today.py"
        )
    need = [
        "landing-mobile.png",
        "square-mobile.png",
        "square-compose-mobile.png",
        "square-engage-mobile.png",
        "home-mobile.png",
    ]
    missing = [n for n in need if not (LIVE / n).exists() or (LIVE / n).stat().st_size < 80_000]
    if missing:
        raise SystemExit(f"Stale/missing screens in {LIVE}: {missing}")


def title_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 160, ((W - 160) // 2, 420))
    d.text((W // 2 - 170, 640), "BarathX", font=fnt(72), fill=WHITE)
    d.text((W // 2 - 220, 740), "Features · Part 1", font=fnt(40), fill=SAFFRON)
    d.text((W // 2 - 120, 820), "Square", font=fnt(56), fill=CREAM)
    d.text((W // 2 - 260, 940), "Latest UI · filmed today", font=fnt(28, False), fill=MUTED)
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


def phone_frame(screen: Path, *, kicker: str, title: str, sub: str) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 14], fill=SAFFRON)
    paste_logo(base, 72, (48, 48))
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)
    d.text((48, 150), kicker.upper(), font=fnt(24), fill=SAFFRON)
    y = 196
    for line in wrap(d, title, fnt(44), 980)[:3]:
        d.text((48, y), line, font=fnt(44), fill=WHITE)
        y += 54
    if sub:
        for line in wrap(d, sub, fnt(28, False), 980)[:2]:
            d.text((48, y + 6), line, font=fnt(28, False), fill=MUTED)
            y += 38

    ui = Image.open(screen).convert("RGB")
    max_h, max_w = 1120, 700
    scale = min(max_w / ui.width, max_h / ui.height)
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 14
    frame = Image.new("RGB", (nw + pad * 2, nh + pad * 2), (28, 28, 34))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle(
        [0, 0, nw + pad * 2 - 1, nh + pad * 2 - 1], radius=48, outline=SAFFRON, width=4
    )
    frame.paste(ui, (pad, pad))
    top = min(y + 36, 360)
    base.paste(frame, ((W - frame.width) // 2, top))
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Join free → barathx.com", font=fnt(32), fill=DARK)
    return base


def jpg_clip(img: Image.Image, path: Path, duration: float) -> Path:
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


def concat(clips: list[Path], out: Path, tmp: Path) -> None:
    list_path = tmp / "_concat.txt"
    list_path.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
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
        ["ffmpeg", "-y", "-ss", "6.5", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(jpg)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    require_live()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)

    total = sum(b[-1] for b in BEATS)
    if abs(total - 25.0) > 0.01:
        raise SystemExit(f"Beat sum must be 25.0s, got {total}")

    with tempfile.TemporaryDirectory(prefix="bx-p1-live-") as td:
        tmp = Path(td)
        clips: list[Path] = []
        for i, (screen, kicker, title, sub, dur) in enumerate(BEATS):
            if screen == "__title__":
                img = title_card()
            elif screen == "__end__":
                img = end_card()
            else:
                path = LIVE / screen
                img = phone_frame(path, kicker=kicker, title=title, sub=sub)
            clips.append(jpg_clip(img, tmp / f"{i:02d}.jpg", dur))

        out = OUT_DIR / "barathx-demo-PART1-25s.mp4"
        concat(clips, out, tmp)
        poster = OUT_DIR / "barathx-demo-PART1-25s-poster.jpg"
        poster_from(out, poster)

        for dest in (DAILY / "barathx-part1-25s.mp4", DAILY / "barathx-daily-reel-25s.mp4"):
            dest.write_bytes(out.read_bytes())
        (DAILY / "barathx-part1-25s-poster.jpg").write_bytes(poster.read_bytes())

        # Download aliases (clear names)
        (DOWNLOADS / "barathx-part1-25s-LATEST.mp4").write_bytes(out.read_bytes())
        (DOWNLOADS / "barathx-demo-PART1-25s.mp4").write_bytes(out.read_bytes())
        (SHOTS / "barathx-part1-25s-poster.jpg").write_bytes(poster.read_bytes())

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
        print(f"LIVE={LIVE}")
        print(f"Wrote {out} ({probe}s)")
        print(f"Download: {DOWNLOADS / 'barathx-part1-25s-LATEST.mp4'}")
        print(f"Daily: {DAILY / 'barathx-part1-25s.mp4'}")


if __name__ == "__main__":
    main()
