#!/usr/bin/env python3
"""Build a short 9:16 mobile UI reel for BarathX (WhatsApp / Reels / Shorts)."""

from __future__ import annotations

import argparse
import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-16"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1920  # 9:16 reel
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)

FONT_B = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_R = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True) or [FONT_B]
)[0]


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def frame_phone(screen: Path, *, kicker: str, title: str) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 14], fill=SAFFRON)

    logo = Image.open(LOGO).convert("RGBA").resize((72, 72), Image.Resampling.LANCZOS)
    mask = Image.new("L", (72, 72), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 71, 71], fill=255)
    circ = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, (48, 48), circ)
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)

    d.text((48, 150), kicker.upper(), font=fnt(26), fill=SAFFRON)
    d.text((48, 200), title, font=fnt(56), fill=WHITE)

    # phone frame
    ui = Image.open(screen).convert("RGB")
    # fit into phone area
    max_h = 1320
    max_w = 720
    scale = min(max_w / ui.width, max_h / ui.height)
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)

    pad = 14
    frame_w, frame_h = nw + pad * 2, nh + pad * 2
    frame = Image.new("RGB", (frame_w, frame_h), (28, 28, 34))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame_w - 1, frame_h - 1], radius=48, outline=SAFFRON, width=4)
    frame.paste(ui, (pad, pad))

    x = (W - frame_w) // 2
    y = 320
    base.paste(frame, (x, y))

    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Join free → barathx.com", font=fnt(34), fill=DARK)
    return base


def title_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    logo = Image.open(LOGO).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
    mask = Image.new("L", (160, 160), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 159, 159], fill=255)
    circ = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, ((W - 160) // 2, 520), circ)
    d.text((W // 2 - 160, 740), "BarathX", font=fnt(72), fill=WHITE)
    d.text((120, 860), "India’s public square", font=fnt(44), fill=SAFFRON)
    d.text((160, 960), "Drop. Pick. Argue live.", font=fnt(40, bold=False), fill=MUTED)
    d.text((200, 1100), "Human takes only. No AI slop.", font=fnt(30, bold=False), fill=MUTED)
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Soft launch → barathx.com", font=fnt(34), fill=DARK)
    return base


def cta_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    d.text((80, 700), "Your move.", font=fnt(72), fill=WHITE)
    d.text((80, 820), "Leave one honest take.", font=fnt(48), fill=SAFFRON)
    d.text((80, 940), "Square · Arenas · Live", font=fnt(36, bold=False), fill=MUTED)
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Open barathx.com now", font=fnt(34), fill=DARK)
    return base


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="2026-08-17")
    args = p.parse_args()
    out_dir = ROOT / "brand" / "social" / "daily" / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="bx-reel-"))

    slides = [
        ("00-title.jpg", title_card(), 1.6),
        ("01-home.jpg", frame_phone(LIVE / "home-mobile.png", kicker="01 Home", title="Your hub"), 2.0),
        ("02-square.jpg", frame_phone(LIVE / "square-mobile.png", kicker="02 Square", title="Drop a take"), 2.2),
        ("03-arenas.jpg", frame_phone(LIVE / "arenas-mobile.png", kicker="03 Arenas", title="Pick a side"), 2.2),
        ("04-live.jpg", frame_phone(LIVE / "live-mobile.png", kicker="04 Live", title="Argue it live"), 2.2),
        ("05-cta.jpg", cta_card(), 1.8),
    ]

    concat_lines = []
    for name, img, dur in slides:
        path = tmp / name
        img.save(path, quality=92)
        concat_lines.append(f"file '{path}'\n")
        concat_lines.append(f"duration {dur}\n")
    # last frame needs a trailing file entry for concat demuxer
    concat_lines.append(f"file '{tmp / slides[-1][0]}'\n")
    list_path = tmp / "list.txt"
    list_path.write_text("".join(concat_lines), encoding="utf-8")

    out_mp4 = out_dir / "barathx-mobile-ui-reel.mp4"
    # xfade-less simple concat; scale ensure even dims
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    subprocess.check_call(cmd)
    # also write a poster frame
    slides[2][1].save(out_dir / "barathx-mobile-ui-reel-poster.jpg", quality=92)
    print(f"wrote {out_mp4} ({out_mp4.stat().st_size} bytes)")
    print(f"poster {out_dir / 'barathx-mobile-ui-reel-poster.jpg'}")


if __name__ == "__main__":
    main()
