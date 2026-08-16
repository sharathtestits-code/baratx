#!/usr/bin/env python3
"""
Render BarathX daily cross-post mockups (WhatsApp + X + LinkedIn).

1080×1080 JPGs with product UI + trend hook copy.
Adds a subtle MOCKUP / FOR APPROVAL ribbon until you approve.
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SCREENS = ROOT / "brand" / "social" / "whatsapp" / "screens"
LIVE = SCREENS / "live-2026-08-16"  # current product UI captures
CAROUSEL = ROOT / "brand" / "carousel" / "screens"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"
DAILY = Path(__file__).resolve().parent

W = H = 1080
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)
TEAL = (46, 196, 182)
SLATE = (28, 30, 38)

FONT_B = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_R = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True) or [FONT_B]
)[0]


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 8)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    d.rectangle([0, 0, 14, H], fill=SAFFRON)
    return img, d


def stamp(base: Image.Image, d: ImageDraw.ImageDraw, *, pill: str) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((52, 52), Image.Resampling.LANCZOS)
    mask = Image.new("L", (52, 52), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 51, 51], fill=255)
    circ = Image.new("RGBA", (52, 52), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, (36, 32), circ)
    d.text((102, 42), "BarathX", font=fnt(28), fill=CREAM)
    bb = d.textbbox((0, 0), pill, font=fnt(18))
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = W - 36 - tw - 24
    d.rounded_rectangle([x0, 36, x0 + tw + 24, 36 + th + 14], radius=16, fill=SAFFRON)
    d.text((x0 + 12, 43), pill, font=fnt(18), fill=DARK)


def cta(d: ImageDraw.ImageDraw, text: str) -> None:
    d.rectangle([0, H - 64, W, H], fill=SAFFRON)
    d.text((36, H - 46), text, font=fnt(24), fill=DARK)


def approval_ribbon(base: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([(W - 260, 0), (W, 0), (W, 260)], fill=(255, 103, 31, 230))
    # rotate text via temp
    tmp = Image.new("RGBA", (220, 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 4), "MOCKUP · APPROVE", font=fnt(18), fill=DARK)
    tmp = tmp.rotate(45, expand=True, resample=Image.Resampling.BICUBIC)
    overlay.paste(tmp, (W - 210, 18), tmp)
    base.paste(Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB"))


def phone(path: Path, h: int = 560) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    tw = max(1, int(h * im.width / im.height))
    im = im.resize((tw, h), Image.Resampling.LANCZOS)
    pad = 10
    frame = Image.new("RGBA", (tw + pad * 2, h + pad * 2), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=36, fill=(28, 28, 34, 255))
    fd.rounded_rectangle([2, 2, frame.width - 3, frame.height - 3], radius=34, outline=(*SAFFRON, 200), width=3)
    mask = Image.new("L", (tw, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, h - 1], radius=24, fill=255)
    screen = Image.new("RGBA", (tw, h), (0, 0, 0, 0))
    screen.paste(im, (0, 0), mask)
    frame.paste(screen, (pad, pad), screen)
    shadow = Image.new("RGBA", (frame.width + 28, frame.height + 28), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([12, 16, 12 + frame.width, 20 + frame.height], radius=40, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    out = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, shadow)
    out.paste(frame, (12, 8), frame)
    return out


def screen(name: str) -> Path:
    # Prefer fresh live captures of current BarathX UI (Home / Square / Arenas / Live).
    m = {
        "square": LIVE / "square-mobile.png",
        "square2": LIVE / "square-foryou-mobile.png",
        "arenas": LIVE / "arenas-mobile.png",
        "live": LIVE / "live-mobile.png",
        "home": LIVE / "home-mobile.png",
        "signup": LIVE / "signup-mobile.png",
        "landing": LIVE / "landing-mobile.png",
        "feed": LIVE / "square-mobile.png",
        "compose": LIVE / "square-mobile.png",
        "search": LIVE / "search-mobile.png",
        "profile": LIVE / "profile-mobile.png",
        "landing_desk": LIVE / "landing-desktop.png",
        "home_desk": LIVE / "home-desktop.png",
        "square_desk": LIVE / "square-desktop.png",
        "live_desk": LIVE / "live-desktop.png",
        "arenas_desk": LIVE / "arenas-desktop.png",
    }
    # Fallbacks to older brand screens / carousel if a live file is missing.
    fallback = {
        "square": SCREENS / "bx-site-square-b.jpg",
        "square2": SCREENS / "bx-site-square-c.jpg",
        "arenas": SCREENS / "bx-site-arenas.jpg",
        "live": SCREENS / "bx-site-live.jpg",
        "home": SCREENS / "bx-site-home.jpg",
        "signup": SCREENS / "bx-site-signup.png",
        "landing": SCREENS / "bx-site-landing.png",
        "feed": CAROUSEL / "m03-feed.png",
        "compose": CAROUSEL / "07-compose.png",
        "search": CAROUSEL / "m05-search.png",
        "profile": CAROUSEL / "m06-profile.png",
    }
    p = m.get(name)
    if p and p.exists():
        return p
    fb = fallback.get(name)
    if fb and fb.exists():
        return fb
    for alt in list(m.values()) + list(fallback.values()):
        if alt.exists():
            return alt
    raise FileNotFoundError(name)


def morning_genz(*, for_approval: bool) -> Image.Image:
    """Trend: Gen Z voice / campus debate energy — takes die in comments."""
    base, d = canvas()
    stamp(base, d, pill="AM · TREND")
    d.text((36, 110), "GEN Z HAS TAKES", font=fnt(22), fill=SAFFRON)
    d.text((36, 150), "Reels bury them.", font=fnt(52), fill=WHITE)
    d.text((36, 218), "Chats delete them.", font=fnt(52), fill=SAFFRON)
    d.text(
        (36, 300),
        "BarathX keeps them on the record —\nSquare · Arenas · Live. Human only.",
        font=fnt(26, bold=False),
        fill=MUTED,
    )
    chips = ["On the record", "Pick a side", "No AI slop"]
    x = 36
    for c in chips:
        bb = d.textbbox((0, 0), c, font=fnt(18))
        tw = bb[2] - bb[0]
        d.rectangle([x, 400, x + tw + 20, 438], outline=SAFFRON, width=2)
        d.text((x + 10, 408), c, font=fnt(18), fill=WHITE)
        x += tw + 32

    ph = phone(screen("square"), 480)
    ph = ph.resize((int(ph.width * 0.88), int(ph.height * 0.88)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 20, 430), ph)
    d2 = ImageDraw.Draw(layer)
    cta(d2, "Join free → barathx.com")
    out = layer.convert("RGB")
    if for_approval:
        approval_ribbon(out)
    return out


def evening_human(*, for_approval: bool) -> Image.Image:
    """Highlight: human-first + AI demotion + soft launch promo."""
    base, d = canvas()
    stamp(base, d, pill="PM · HIGHLIGHT")
    d.text((36, 110), "FEEDS ARE FULL OF AI", font=fnt(22), fill=SAFFRON)
    d.text((36, 150), "We rank humans", font=fnt(52), fill=WHITE)
    d.text((36, 218), "first.", font=fnt(52), fill=SAFFRON)
    d.text(
        (36, 300),
        "AI drafts get flagged. Real replies rise.\nSoft launch — first voices get seen.",
        font=fnt(26, bold=False),
        fill=MUTED,
    )

    items = [
        ("Square", "Takes that stay"),
        ("Arenas", "Agree / Disagree"),
        ("Live", "Argue it live"),
        ("Founding", "Earned, not bought"),
    ]
    y = 420
    for title, sub in items:
        d.ellipse([44, y + 8, 60, y + 24], fill=SAFFRON)
        d.text((76, y), f"{title} — {sub}", font=fnt(28), fill=CREAM)
        y += 52

    ph = phone(screen("live"), 420)
    ph = ph.resize((int(ph.width * 0.78), int(ph.height * 0.78)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 16, 520), ph)
    d2 = ImageDraw.Draw(layer)
    cta(d2, "Leave one honest take → barathx.com")
    out = layer.convert("RGB")
    if for_approval:
        approval_ribbon(out)
    return out


def morning_linkedin(*, for_approval: bool) -> Image.Image:
    """LinkedIn-leaning: professional identity / public square."""
    base, d = canvas()
    stamp(base, d, pill="AM · LINKEDIN")
    d.text((36, 120), "STOP PERFORMING.", font=fnt(22), fill=SAFFRON)
    d.text((36, 165), "Start arguing", font=fnt(54), fill=WHITE)
    d.text((36, 235), "on the record.", font=fnt(54), fill=SAFFRON)
    d.rounded_rectangle([36, 340, W - 36, 620], radius=22, fill=SLATE)
    d.text((60, 380), "What BarathX gives that feeds don’t", font=fnt(26), fill=SAFFRON)
    for i, line in enumerate(
        [
            "Takes that stay (not buried comments)",
            "Forced sides — real stakes",
            "Live rooms for human argument",
            "Human-first ranking — AI demoted",
        ]
    ):
        d.text((60, 440 + i * 42), f"→  {line}", font=fnt(24, bold=False), fill=CREAM)
    cta(d, "Soft launch open → barathx.com")
    if for_approval:
        approval_ribbon(base)
    return base


def evening_whatsapp(*, for_approval: bool) -> Image.Image:
    """Family/community WA style — current product: Square · Arenas · Live."""
    base, d = canvas()
    stamp(base, d, pill="PM · WHATSAPP")
    d.text((36, 120), "TONIGHT ON BARATHX", font=fnt(22), fill=SAFFRON)
    d.text((36, 165), "Drop. Pick.", font=fnt(54), fill=WHITE)
    d.text((36, 235), "Argue live.", font=fnt(54), fill=SAFFRON)

    # Current mobile UI only (no legacy desktop compose / old screens).
    phones = [("square", "Drop"), ("arenas", "Pick"), ("live", "Argue")]
    layer = base.convert("RGBA")
    xs = [40, 380, 720]
    for (name, label), x in zip(phones, xs):
        ph = phone(screen(name), 400)
        ph = ph.resize((int(ph.width * 0.72), int(ph.height * 0.72)), Image.Resampling.LANCZOS)
        layer.paste(ph, (x, 340), ph)
    d2 = ImageDraw.Draw(layer)
    for (name, label), x in zip(phones, xs):
        d2.text((x + 40, 880), label, font=fnt(24), fill=SAFFRON)
    cta(d2, "Open → barathx.com")
    out = layer.convert("RGB")
    if for_approval:
        approval_ribbon(out)
    return out


SLOTS = {
    "morning-shared": morning_genz,
    "evening-shared": evening_human,
    "morning-linkedin": morning_linkedin,
    "evening-whatsapp": evening_whatsapp,
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="IST date YYYY-MM-DD")
    p.add_argument("--approve", action="store_true", help="Render final (no MOCKUP ribbon)")
    args = p.parse_args()
    out_dir = DAILY / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    for_approval = not args.approve
    print(f"Rendering daily mockups → {out_dir} (approval={for_approval})")
    mapping = {
        "morning-shared.jpg": morning_genz,
        "evening-shared.jpg": evening_human,
        "morning-linkedin.jpg": morning_linkedin,
        "evening-whatsapp.jpg": evening_whatsapp,
    }
    for name, fn in mapping.items():
        img = fn(for_approval=for_approval)
        path = out_dir / name
        img.save(path, quality=92, optimize=True)
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
