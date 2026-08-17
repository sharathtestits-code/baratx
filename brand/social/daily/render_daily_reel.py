#!/usr/bin/env python3
"""Build a ~20s 9:16 BarathX reel for daily packs (WA Status / Reels / Shorts / X)."""

from __future__ import annotations

import argparse
import glob
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from features import Feature, feature_by_key, feature_for_date

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-16"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1920
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)

def _font_paths() -> tuple[str, str]:
    bold = (
        glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
    )
    regular = (
        glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Regular.ttf", recursive=True)
        or bold
    )
    if not bold:
        raise SystemExit("No usable Bold TTF found under /usr/share/fonts")
    return bold[0], regular[0]


FONT_B, FONT_R = _font_paths()

SCREEN_FILES = {
    "square": "square-mobile.png",
    "arenas": "arenas-mobile.png",
    "live": "live-mobile.png",
    "explore": "explore-mobile.png",
    "home": "home-mobile.png",
    "rewards": "rewards-mobile.png",
    "landing": "landing-mobile.png",
    "search": "search-mobile.png",
}


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def _screen(key: str) -> Path:
    name = SCREEN_FILES.get(key, "square-mobile.png")
    path = LIVE / name
    return path if path.exists() else LIVE / "square-mobile.png"


def frame_phone(screen: Path, *, kicker: str, title: str, trend: str) -> Image.Image:
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
    d.text((48, 200), title[:28], font=fnt(52), fill=WHITE)
    if trend:
        d.text((48, 280), (trend[:48] + ("…" if len(trend) > 48 else "")), font=fnt(26, False), fill=MUTED)

    ui = Image.open(screen).convert("RGB")
    max_h, max_w = 1180, 700
    scale = min(max_w / ui.width, max_h / ui.height)
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 14
    frame_w, frame_h = nw + pad * 2, nh + pad * 2
    frame = Image.new("RGB", (frame_w, frame_h), (28, 28, 34))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame_w - 1, frame_h - 1], radius=48, outline=SAFFRON, width=4)
    frame.paste(ui, (pad, pad))
    base.paste(frame, ((W - frame_w) // 2, 360))

    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Join free → barathx.com", font=fnt(34), fill=DARK)
    return base


def title_card(feature: Feature, trend: str) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    logo = Image.open(LOGO).convert("RGBA").resize((140, 140), Image.Resampling.LANCZOS)
    mask = Image.new("L", (140, 140), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 139, 139], fill=255)
    circ = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, ((W - 140) // 2, 420), circ)
    d.text((W // 2 - 150, 620), "BarathX", font=fnt(64), fill=WHITE)
    d.text((120, 720), "India’s public square", font=fnt(40), fill=SAFFRON)
    d.text((100, 820), f"Today · {feature.name}", font=fnt(44), fill=CREAM)
    if trend:
        d.text((80, 920), trend[:42] + ("…" if len(trend) > 42 else ""), font=fnt(28, False), fill=MUTED)
    d.text((140, 1080), "Human takes only. No AI slop.", font=fnt(28, False), fill=MUTED)
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Soft launch → barathx.com", font=fnt(34), fill=DARK)
    return base


def cta_card(feature: Feature) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    d.text((80, 640), "Your move.", font=fnt(72), fill=WHITE)
    d.text((80, 760), feature.one_liner[:40], font=fnt(36), fill=SAFFRON)
    d.text((80, 860), "Leave one honest take.", font=fnt(40, False), fill=MUTED)
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), "Open barathx.com now", font=fnt(34), fill=DARK)
    return base


def build_reel(*, out_dir: Path, feature: Feature, trend: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="bx-reel-"))

    # ~20 seconds total
    slides = [
        ("00-title.jpg", title_card(feature, trend), 3.0),
        (
            "01-feature.jpg",
            frame_phone(
                _screen(feature.screen),
                kicker=f"Feature · {feature.name}",
                title=feature.bullets[0] if feature.bullets else feature.name,
                trend=trend,
            ),
            4.0,
        ),
        (
            "02-square.jpg",
            frame_phone(_screen("square"), kicker="Square", title="Drop a take", trend=trend),
            3.5,
        ),
        (
            "03-arenas.jpg",
            frame_phone(_screen("arenas"), kicker="Arenas", title="Pick a side", trend=trend),
            3.5,
        ),
        (
            "04-live.jpg",
            frame_phone(_screen("live"), kicker="Live", title="Argue it live", trend=trend),
            3.5,
        ),
        ("05-cta.jpg", cta_card(feature), 2.5),
    ]
    # 3+4+3.5+3.5+3.5+2.5 = 20.0s

    concat_lines = []
    for name, img, dur in slides:
        path = tmp / name
        img.save(path, quality=92)
        concat_lines.append(f"file '{path}'\n")
        concat_lines.append(f"duration {dur}\n")
    concat_lines.append(f"file '{tmp / slides[-1][0]}'\n")
    list_path = tmp / "list.txt"
    list_path.write_text("".join(concat_lines), encoding="utf-8")

    out_mp4 = out_dir / "barathx-daily-reel-20s.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-vf",
        "fps=30,format=yuv420p",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-t",
        "20",
        str(out_mp4),
    ]
    subprocess.check_call(cmd)
    slides[1][1].save(out_dir / "barathx-daily-reel-poster.jpg", quality=92)
    print(f"wrote {out_mp4} ({out_mp4.stat().st_size} bytes)")
    return out_mp4


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--feature", default="")
    p.add_argument("--trend", default="")
    args = p.parse_args()
    d = date.fromisoformat(args.date)
    feature = feature_by_key(args.feature) or feature_for_date(d)
    trend = args.trend.strip() or "India is talking"
    out_dir = ROOT / "brand" / "social" / "daily" / args.date
    build_reel(out_dir=out_dir, feature=feature, trend=trend)


if __name__ == "__main__":
    main()
