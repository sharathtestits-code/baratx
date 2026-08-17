#!/usr/bin/env python3
"""LinkedIn company page cover (1584×396) + logo square helper."""

from __future__ import annotations

import glob
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "brand" / "linkedin"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1584, 396
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (160, 160, 168)

FONT_B = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_R = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True) or [FONT_B]
)[0]


def f(size: int, bold: bool = True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    for i, y in enumerate(range(0, H, 6)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2))
    d.rectangle([0, 0, 14, H], fill=SAFFRON)
    d.rectangle([0, H - 10, W, H], fill=SAFFRON)

    logo = Image.open(LOGO).convert("RGBA").resize((120, 120), Image.Resampling.LANCZOS)
    mask = Image.new("L", (120, 120), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 119, 119], fill=255)
    circ = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    layer = base.convert("RGBA")
    layer.paste(circ, (56, (H - 120) // 2), circ)
    d2 = ImageDraw.Draw(layer)
    d2.text((210, 110), "BarathX", font=f(64), fill=CREAM)
    d2.text((210, 190), "India’s public square", font=f(36), fill=SAFFRON)
    d2.text(
        (210, 250),
        "Pick a side. Argue it live. · Soft launch · barathx.com",
        font=f(24, bold=False),
        fill=MUTED,
    )
    d2.text((W - 320, 300), "Square · Arenas · Live", font=f(22), fill=SAFFRON)
    cover = layer.convert("RGB")
    cover_path = OUT / "barathx-linkedin-company-cover.jpg"
    cover.save(cover_path, quality=94, optimize=True)

    # Logo 300×300 for LinkedIn company logo
    mark = Image.new("RGB", (300, 300), DARK)
    md = ImageDraw.Draw(mark)
    md.ellipse([18, 18, 281, 281], fill=(28, 28, 34))
    big = Image.open(LOGO).convert("RGBA").resize((220, 220), Image.Resampling.LANCZOS)
    mm = Image.new("L", (220, 220), 0)
    ImageDraw.Draw(mm).ellipse([0, 0, 219, 219], fill=255)
    mc = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    mc.paste(big, (0, 0), mm)
    ml = mark.convert("RGBA")
    ml.paste(mc, (40, 40), mc)
    logo_path = OUT / "barathx-linkedin-company-logo.jpg"
    ml.convert("RGB").save(logo_path, quality=94, optimize=True)

    print(cover_path)
    print(logo_path)


if __name__ == "__main__":
    main()
