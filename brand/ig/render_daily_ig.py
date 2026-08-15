#!/usr/bin/env python3
"""
Daily Instagram creatives — rotating templates so posts don’t look identical.

Usage:
  python3 brand/ig/render_daily_ig.py --date 2026-08-16
  python3 brand/ig/render_daily_ig.py --date 2026-08-16 --all-slots

Slots (CONTENT-RULES):
  morning  → bold hook / pain (signup-excite energy)
  midday   → how-it-works / product proof
  evening  → launch-pain / debate prompt
"""

from __future__ import annotations

import argparse
import hashlib
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "brand" / "social" / "daily"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"
W = H = 1080

FONT_SANS = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"

SAFFRON = (255, 153, 51)
CREAM = (255, 248, 235)
DARK = (13, 13, 18)
GREEN = (19, 136, 8)
NAVY = (0, 0, 128)

SLOTS = ("morning", "midday", "evening")

# Trending-style template keys — rotate by date+slot hash
TEMPLATES = ("bold_hook", "split_debate", "story_card", "neon_proof", "quote_slab")

COPY = {
    "morning": {
        "eyebrow": "Soft launch",
        "headline": "WhatsApp takes\ndisappear by Monday",
        "sub": "Put one on the record.",
        "cta": "Join free → barathx.com",
    },
    "midday": {
        "eyebrow": "How it works",
        "headline": "Square · Arenas · Live",
        "sub": "Drop a take. Pick a side. Argue it live.",
        "cta": "Leave your first take → barathx.com",
    },
    "evening": {
        "eyebrow": "Tonight’s question",
        "headline": "What should India\nargue about tonight?",
        "sub": "Human takes only. No AI slop.",
        "cta": "Answer in the Square → barathx.com",
    },
}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def load_logo(size: int) -> Image.Image:
    img = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def pick_templates_for_day(day: str) -> dict[str, str]:
    """Assign a unique template to each slot for the day."""
    assigned: dict[str, str] = {}
    used: set[str] = set()
    for slot in SLOTS:
        for offset in range(len(TEMPLATES) * 2):
            h = hashlib.sha1(f"{day}:{slot}:{offset}".encode()).hexdigest()
            tmpl = TEMPLATES[(int(h[:8], 16) + offset) % len(TEMPLATES)]
            if tmpl not in used:
                assigned[slot] = tmpl
                used.add(tmpl)
                break
        else:
            assigned[slot] = TEMPLATES[len(assigned) % len(TEMPLATES)]
    return assigned


def pick_template(day: str, slot: str) -> str:
    return pick_templates_for_day(day)[slot]


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_multiline(draw, text, fnt, xy, fill, gap=8, align="left"):
    x, y = xy
    for line in text.split("\n"):
        tw, th = text_size(draw, line, fnt)
        lx = x if align == "left" else (W - tw) // 2 if align == "center" else x - tw
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += th + gap
    return y


def bg_gradient(top, bottom) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=c)
    return img


def stamp_brand(layer: Image.Image, draw: ImageDraw.ImageDraw, y: int = 48) -> int:
    logo = load_logo(72)
    layer.paste(logo, (56, y), logo)
    f = font(FONT_SANS, 36)
    draw.text((56 + 84, y + 18), "BarathX", font=f, fill=CREAM)
    return y + 100


def render_bold_hook(copy: dict) -> Image.Image:
    base = bg_gradient((28, 16, 8), DARK).convert("RGBA")
    draw = ImageDraw.Draw(base)
    # Diagonal saffron slash
    draw.polygon([(0, 0), (W, 0), (W, 220), (0, 520)], fill=(*SAFFRON, 40))
    y = stamp_brand(base, draw)
    draw.text((56, y), copy["eyebrow"].upper(), font=font(FONT_SANS, 28), fill=SAFFRON)
    y = draw_multiline(draw, copy["headline"], font(FONT_SANS, 72), (56, y + 36), CREAM, gap=6)
    draw.text((56, y + 28), copy["sub"], font=font(FONT_REG, 34), fill=(255, 220, 180))
    # CTA bar
    draw.rounded_rectangle([56, H - 160, W - 56, H - 70], radius=28, fill=SAFFRON)
    tw, th = text_size(draw, copy["cta"], font(FONT_SANS, 32))
    draw.text(((W - tw) // 2, H - 160 + (90 - th) // 2), copy["cta"], font=font(FONT_SANS, 32), fill=DARK)
    return base.convert("RGB")


def render_split_debate(copy: dict) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, W // 2, H], fill=(60, 30, 10))
    draw.rectangle([W // 2, 0, W, H], fill=(10, 40, 20))
    draw.line([(W // 2, 80), (W // 2, H - 80)], fill=CREAM, width=4)
    draw.text((80, 120), "AGREE", font=font(FONT_SANS, 40), fill=SAFFRON)
    draw.text((W // 2 + 80, 120), "DISAGREE", font=font(FONT_SANS, 40), fill=(120, 220, 140))
    # Center card
    draw.rounded_rectangle([90, 320, W - 90, 820], radius=32, fill=(13, 13, 18, ))
    # pillow RGB only — redraw as solid
    draw.rounded_rectangle([90, 320, W - 90, 820], radius=32, fill=(20, 22, 28))
    draw.rounded_rectangle([90, 320, W - 90, 820], radius=32, outline=SAFFRON, width=3)
    y = 380
    draw.text((120, y), copy["eyebrow"].upper(), font=font(FONT_SANS, 26), fill=SAFFRON)
    y = draw_multiline(draw, copy["headline"], font(FONT_SANS, 54), (120, y + 40), CREAM, gap=8)
    draw.text((120, y + 30), copy["sub"], font=font(FONT_REG, 30), fill=(200, 200, 210))
    logo = load_logo(64)
    base.paste(logo, ((W - 64) // 2, H - 180), logo)
    tw, _ = text_size(draw, copy["cta"], font(FONT_SANS, 28))
    draw.text(((W - tw) // 2, H - 100), copy["cta"], font=font(FONT_SANS, 28), fill=CREAM)
    return base


def render_story_card(copy: dict) -> Image.Image:
    base = bg_gradient((18, 18, 28), (40, 20, 8)).convert("RGBA")
    draw = ImageDraw.Draw(base)
    # Fake “story” progress bars
    gap = 12
    bar_w = (W - 56 * 2 - gap * 2) // 3
    for i in range(3):
        x0 = 56 + i * (bar_w + gap)
        draw.rounded_rectangle([x0, 40, x0 + bar_w, 48], radius=4, fill=(255, 255, 255, 60))
        if i == 0:
            draw.rounded_rectangle([x0, 40, x0 + bar_w, 48], radius=4, fill=SAFFRON)
    y = stamp_brand(base, draw, 70)
    draw.rounded_rectangle([56, y, W - 56, H - 200], radius=36, fill=(255, 255, 255, 18))
    y += 48
    draw.text((88, y), copy["eyebrow"].upper(), font=font(FONT_SANS, 26), fill=SAFFRON)
    y = draw_multiline(draw, copy["headline"], font(FONT_SERIF, 58), (88, y + 36), CREAM, gap=10)
    draw.text((88, y + 36), copy["sub"], font=font(FONT_REG, 32), fill=(230, 220, 200))
    draw.rounded_rectangle([88, H - 170, W - 88, H - 90], radius=24, fill=SAFFRON)
    tw, th = text_size(draw, copy["cta"], font(FONT_SANS, 30))
    draw.text(((W - tw) // 2, H - 170 + (80 - th) // 2), copy["cta"], font=font(FONT_SANS, 30), fill=DARK)
    return base.convert("RGB")


def render_neon_proof(copy: dict) -> Image.Image:
    base = Image.new("RGB", (W, H), (8, 10, 16))
    draw = ImageDraw.Draw(base)
    # Grid
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(30, 34, 48), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(30, 34, 48), width=1)
    # Soft saffron glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-200, -120, 500, 480], fill=(255, 153, 51, 90))
    base = Image.alpha_composite(base.convert("RGBA"), glow)
    draw = ImageDraw.Draw(base)
    y = stamp_brand(base, draw)
    chips = ["Square", "Arenas", "Live"]
    x = 56
    for c in chips:
        tw, th = text_size(draw, c, font(FONT_SANS, 26))
        draw.rounded_rectangle([x, y, x + tw + 36, y + 48], radius=24, outline=SAFFRON, width=2)
        draw.text((x + 18, y + 10), c, font=font(FONT_SANS, 26), fill=CREAM)
        x += tw + 52
    y = draw_multiline(draw, copy["headline"], font(FONT_SANS, 64), (56, y + 80), CREAM, gap=8)
    draw.text((56, y + 24), copy["sub"], font=font(FONT_REG, 32), fill=(180, 190, 210))
    draw.text((56, H - 120), copy["cta"], font=font(FONT_SANS, 30), fill=SAFFRON)
    return base.convert("RGB")


def render_quote_slab(copy: dict) -> Image.Image:
    base = bg_gradient((250, 244, 235), (255, 220, 180))
    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, W, 28], fill=SAFFRON)
    draw.rectangle([0, H - 28, W, H], fill=GREEN)
    logo = load_logo(80)
    base.paste(logo, ((W - 80) // 2, 70), logo)
    draw.text(((W - text_size(draw, "BarathX", font(FONT_SANS, 40))[0]) // 2, 170), "BarathX", font=font(FONT_SANS, 40), fill=DARK)
    # Quote marks
    draw.text((70, 280), "“", font=font(FONT_SERIF, 160), fill=SAFFRON)
    y = draw_multiline(draw, copy["headline"], font(FONT_SERIF, 56), (0, 420), DARK, gap=10, align="center")
    tw, _ = text_size(draw, copy["sub"], font(FONT_REG, 30))
    draw.text(((W - tw) // 2, y + 36), copy["sub"], font=font(FONT_REG, 30), fill=(80, 60, 40))
    tw, _ = text_size(draw, copy["cta"], font(FONT_SANS, 28))
    draw.text(((W - tw) // 2, H - 120), copy["cta"], font=font(FONT_SANS, 28), fill=NAVY)
    return base


RENDERERS = {
    "bold_hook": render_bold_hook,
    "split_debate": render_split_debate,
    "story_card": render_story_card,
    "neon_proof": render_neon_proof,
    "quote_slab": render_quote_slab,
}


def render_slot(day: str, slot: str, out_dir: Path) -> Path:
    tmpl = pick_template(day, slot)
    copy = COPY[slot]
    img = RENDERERS[tmpl](copy)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"ig-{slot}-{tmpl}.jpg"
    img.save(out, quality=92, optimize=True)
    # Also write stable alias used by packs
    alias = out_dir / f"ig-{slot}.jpg"
    img.save(alias, quality=92, optimize=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--slot", choices=SLOTS, default=None)
    parser.add_argument("--all-slots", action="store_true")
    args = parser.parse_args()
    day = args.date
    out_dir = OUT_ROOT / day
    slots = list(SLOTS) if args.all_slots or not args.slot else [args.slot]
    print(f"Daily IG templates for {day}:")
    for slot in slots:
        tmpl = pick_template(day, slot)
        path = render_slot(day, slot, out_dir)
        print(f"  {slot:8} → {tmpl:12} → {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
