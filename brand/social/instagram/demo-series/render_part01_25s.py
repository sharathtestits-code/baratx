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
SCREENS_ROOT = ROOT / "brand" / "social" / "whatsapp" / "screens"
# Canonical Part 1 pack folder (stable download path) + today's daily alias
PACK_DAY = "2026-08-25"
OUT_DIR = (
    ROOT
    / "brand"
    / "social"
    / "instagram"
    / "demo-series"
    / "PART-01-square-v5"
)
DAILY = ROOT / "brand" / "social" / "daily" / PACK_DAY
DAILY_TODAY = ROOT / "brand" / "social" / "daily" / TODAY
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

NEED_SCREENS = (
    "square-mobile.png",
    "square-compose-mobile.png",
    "square-engage-mobile.png",
)

# Exact 25.0s — scroll-stop hook → Square immediately → discovery cliffhanger
BEATS: list[tuple[str, str, str, str, float]] = [
    # screen_file, kicker, title, sub, seconds
    ("__hook__", "", "", "", 3.5),
    (
        "square-mobile.png",
        "Part 1 · Square",
        "Questions & conversations",
        "One question. Your take.",
        6.0,
    ),
    (
        "square-compose-mobile.png",
        "Drop a take",
        "10 real opinions > 1,000 empty likes",
        "Short post. Real replies.",
        5.0,
    ),
    (
        "square-engage-mobile.png",
        "On the Square",
        "Human takes. Live talk.",
        "No AI slop.",
        4.5,
    ),
    (
        "arenas-mobile.png",
        "Coming next",
        "Part 2 — Arenas",
        "Debates. Pick a side.",
        2.5,
    ),
    ("__end__", "", "", "", 3.5),
]
# 3.5+6+5+4.5+2.5+3.5 = 25.0


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


def resolve_live() -> Path:
    """Newest live-YYYY-MM-DD folder with required screens (never older than that pick)."""
    candidates: list[Path] = []
    for p in SCREENS_ROOT.glob("live-20*"):
        if not p.is_dir():
            continue
        ok = all((p / n).exists() and (p / n).stat().st_size >= 80_000 for n in NEED_SCREENS)
        if ok:
            candidates.append(p)
    if not candidates:
        raise SystemExit(
            f"No usable live-* screens under {SCREENS_ROOT}\n"
            "Run: /tmp/bx-pw/bin/python brand/social/capture_live_screens_today.py"
        )
    return sorted(candidates, key=lambda x: x.name)[-1]


def hook_card() -> Image.Image:
    """Scroll-stop opener — question first, not a feature label."""
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 96, ((W - 96) // 2, 220))
    d.text((W // 2 - 110, 340), "BarathX", font=fnt(36), fill=MUTED)

    lines = [
        "WOULD YOU RATHER",
        "GET 1,000 LIKES…",
        "",
        "OR 10 REAL",
        "OPINIONS?",
    ]
    y = 520
    for line in lines:
        if not line:
            y += 36
            continue
        font = fnt(64 if "OR" not in line and "OPINIONS" not in line else 68)
        fill = SAFFRON if line.startswith("OR") or line == "OPINIONS?" else WHITE
        if line == "OPINIONS?":
            fill = SAFFRON
        tw = d.textlength(line, font=font)
        d.text(((W - tw) / 2, y), line, font=font, fill=fill)
        y += 86

    d.text(
        (W // 2 - 280, 1180),
        "Part 1 · Square — watch what that looks like",
        font=fnt(26, False),
        fill=MUTED,
    )
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Discovery series · follow for Part 2", font=fnt(30), fill=DARK)
    return base


def end_card() -> Image.Image:
    """Discovery cliffhanger — reason to follow for the next feature."""
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 110, ((W - 110) // 2, 360))

    d.text((80, 540), "This is a discovery.", font=fnt(40), fill=MUTED)
    rows = [
        ("Part 1", "Square", "questions & conversations", True),
        ("Part 2", "Arenas", "debates — next", False),
        ("Part 3", "???", "next feature — soon", False),
    ]
    y = 640
    for part, name, blurb, done in rows:
        d.text((80, y), part, font=fnt(28), fill=SAFFRON if not done else MUTED)
        d.text((220, y), name, font=fnt(36), fill=WHITE if done else CREAM)
        d.text((80, y + 48), blurb, font=fnt(26, False), fill=MUTED)
        y += 120

    d.text((80, 1080), "Follow @getbaratx", font=fnt(40), fill=CREAM)
    d.text((80, 1150), "so you don’t miss Part 2.", font=fnt(32, False), fill=MUTED)
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
    # Poster = Square beat (after hook) so thumbnail shows product, not only text
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "4.0", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(jpg)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    live = resolve_live()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY.mkdir(parents=True, exist_ok=True)
    DAILY_TODAY.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)

    total = sum(b[-1] for b in BEATS)
    if abs(total - 25.0) > 0.01:
        raise SystemExit(f"Beat sum must be 25.0s, got {total}")

    # arenas teaser is optional — fall back to home if missing
    with tempfile.TemporaryDirectory(prefix="bx-p1-live-") as td:
        tmp = Path(td)
        clips: list[Path] = []
        for i, (screen, kicker, title, sub, dur) in enumerate(BEATS):
            if screen == "__hook__":
                img = hook_card()
            elif screen == "__end__":
                img = end_card()
            else:
                path = live / screen
                if not path.exists() or path.stat().st_size < 80_000:
                    alt = live / "home-mobile.png"
                    path = alt if alt.exists() else live / "square-mobile.png"
                img = phone_frame(path, kicker=kicker, title=title, sub=sub)
            clips.append(jpg_clip(img, tmp / f"{i:02d}.jpg", dur))

        out = OUT_DIR / "barathx-demo-PART1-25s.mp4"
        concat(clips, out, tmp)
        poster = OUT_DIR / "barathx-demo-PART1-25s-poster.jpg"
        poster_from(out, poster)

        for folder in {DAILY, DAILY_TODAY}:
            folder.mkdir(parents=True, exist_ok=True)
            for name in ("barathx-part1-25s.mp4", "barathx-daily-reel-25s.mp4"):
                (folder / name).write_bytes(out.read_bytes())
            (folder / "barathx-part1-25s-poster.jpg").write_bytes(poster.read_bytes())

        (DOWNLOADS / "barathx-part1-25s-LATEST.mp4").write_bytes(out.read_bytes())
        (DOWNLOADS / "BarathX-Part1-Square-25s.mp4").write_bytes(out.read_bytes())
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
        print(f"LIVE={live}")
        print(f"Wrote {out} ({probe}s)")
        print(f"Download: {DOWNLOADS / 'BarathX-Part1-Square-25s.mp4'}")
        print(f"Daily: {DAILY / 'barathx-part1-25s.mp4'}")


if __name__ == "__main__":
    main()
