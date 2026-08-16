#!/usr/bin/env python3
"""
Render BarathX IG carousel packs — product UI + crisp dark/saffron type.

Writes 6 slides (1080×1080 JPG) into each pack folder used by the
Instagram scheduler (backend/app/instagram_publish.py):

  brand/ig/carousel/signup-excite/   → morning
  brand/ig/carousel/how-it-works/    → midday
  brand/ig/carousel/launch-pain/     → evening
  brand/ig/carousel/live-product/    → optional / admin

Usage:
  python3 brand/ig/render_product_carousels.py
  python3 brand/ig/render_product_carousels.py --pack morning
"""

from __future__ import annotations

import argparse
import glob
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "brand" / "ig" / "carousel"
SCREENS = ROOT / "brand" / "social" / "whatsapp" / "screens"
CAROUSEL_SCREENS = ROOT / "brand" / "carousel" / "screens"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W = H = 1080
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)

FONT = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_REG = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
    or [FONT]
)[0]


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


def scan_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 8)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    d.rectangle([0, 0, 18, H], fill=SAFFRON)
    return img, d


def stamp_brand(base: Image.Image, d: ImageDraw.ImageDraw, *, y: int = 36, pill: str = "") -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((56, 56), Image.Resampling.LANCZOS)
    mask = Image.new("L", (56, 56), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 55, 55], fill=255)
    circ = Image.new("RGBA", (56, 56), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, (40, y), circ)
    d.text((112, y + 10), "BarathX", font=fnt(32), fill=CREAM)
    if pill:
        bb = d.textbbox((0, 0), pill, font=fnt(20))
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x0 = W - 40 - tw - 28
        d.rounded_rectangle([x0, y + 6, x0 + tw + 28, y + 6 + th + 16], radius=20, fill=SAFFRON)
        d.text((x0 + 14, y + 14), pill, font=fnt(20), fill=DARK)


def cta_bar(d: ImageDraw.ImageDraw, text: str) -> None:
    d.rectangle([0, H - 70, W, H], fill=SAFFRON)
    d.text((40, H - 52), text, font=fnt(26), fill=DARK)


def load_phone(path: Path, target_h: int) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    tw = max(1, int(target_h * im.width / im.height))
    im = im.resize((tw, target_h), Image.Resampling.LANCZOS)
    pad = 12
    frame = Image.new("RGBA", (tw + pad * 2, target_h + pad * 2), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=40, fill=(28, 28, 34, 255))
    fd.rounded_rectangle(
        [2, 2, frame.width - 3, frame.height - 3],
        radius=38,
        outline=(*SAFFRON, 200),
        width=3,
    )
    mask = Image.new("L", (tw, target_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, target_h - 1], radius=26, fill=255)
    screen = Image.new("RGBA", (tw, target_h), (0, 0, 0, 0))
    screen.paste(im, (0, 0), mask)
    frame.paste(screen, (pad, pad), screen)

    shadow = Image.new("RGBA", (frame.width + 36, frame.height + 36), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [16, 20, 16 + frame.width, 24 + frame.height],
        radius=44,
        fill=(0, 0, 0, 110),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    out = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, shadow)
    out.paste(frame, (16, 12), frame)
    return out


def screen(name: str) -> Path:
    mapping = {
        "square": SCREENS / "bx-site-square-b.jpg",
        "square2": SCREENS / "bx-site-square-c.jpg",
        "arenas": SCREENS / "bx-site-arenas.jpg",
        "live": SCREENS / "bx-site-live.jpg",
        "home": SCREENS / "bx-site-home.jpg",
        "signup": SCREENS / "bx-site-signup.png",
        "landing": SCREENS / "bx-site-landing.png",
        "feed": CAROUSEL_SCREENS / "m03-feed.png",
        "compose": CAROUSEL_SCREENS / "07-compose.png",
        "profile": CAROUSEL_SCREENS / "m06-profile.png",
    }
    path = mapping[name]
    if not path.exists():
        # fallbacks
        for alt in mapping.values():
            if alt.exists():
                return alt
        raise FileNotFoundError(name)
    return path


def slide_type_hero(
    *,
    kicker: str,
    line1: str,
    line2: str,
    sub: str,
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas()
    stamp_brand(base, d, pill=pill)
    d.text((40, 130), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((40, 178), line1, font=fnt(64), fill=WHITE)
    d.text((40, 258), line2, font=fnt(64), fill=SAFFRON)
    d.text((40, 350), sub, font=fnt(28, bold=False), fill=MUTED)
    # accent rule
    d.rectangle([40, 420, 280, 428], fill=SAFFRON)
    bullets = [
        "Square — takes that stay",
        "Arenas — pick a side",
        "Live — argue it live",
    ]
    y = 460
    for b in bullets:
        d.ellipse([48, y + 10, 64, y + 26], fill=SAFFRON)
        d.text((80, y), b, font=fnt(30), fill=CREAM)
        y += 56
    cta_bar(d, cta)
    return base


def slide_phone(
    *,
    kicker: str,
    title: str,
    title2: str,
    sub: str,
    screen_name: str,
    pill: str,
    cta: str,
    phone_h: int = 620,
) -> Image.Image:
    base, d = scan_canvas()
    stamp_brand(base, d, pill=pill)
    d.text((40, 120), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((40, 164), title, font=fnt(52), fill=WHITE)
    if title2:
        d.text((40, 228), title2, font=fnt(52), fill=SAFFRON)
    d.text((40, 300 if title2 else 236), sub, font=fnt(26, bold=False), fill=MUTED)

    phone = load_phone(screen(screen_name), phone_h)
    scale = 0.92
    ph = phone.resize((int(phone.width * scale), int(phone.height * scale)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 8, 290), ph)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, cta)
    return layer.convert("RGB")


def slide_triple(
    *,
    kicker: str,
    title: str,
    title2: str,
    phones: list[tuple[str, str, str]],
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas()
    stamp_brand(base, d, pill=pill)
    d.text((40, 110), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((40, 150), title, font=fnt(46), fill=WHITE)
    d.text((40, 206), title2, font=fnt(46), fill=SAFFRON)

    layer = base.convert("RGBA")
    xs = [36, 360, 684]
    for (sname, label, blurb), x in zip(phones, xs):
        phone = load_phone(screen(sname), 500)
        ph = phone.resize((int(phone.width * 0.86), int(phone.height * 0.86)), Image.Resampling.LANCZOS)
        layer.paste(ph, (x, 290), ph)
    d2 = ImageDraw.Draw(layer)
    for (sname, label, blurb), x in zip(phones, xs):
        d2.text((x + 24, 955), label, font=fnt(24), fill=SAFFRON)
        d2.text((x + 24, 988), blurb, font=fnt(20, bold=False), fill=MUTED)
    cta_bar(d2, cta)
    return layer.convert("RGB")


def slide_signup_path(*, pill: str) -> Image.Image:
    base, d = scan_canvas()
    stamp_brand(base, d, pill=pill)
    d.text((40, 120), "START HERE", font=fnt(24), fill=SAFFRON)
    d.text((40, 164), "Pick a side.", font=fnt(56), fill=WHITE)
    d.text((40, 232), "Argue it live.", font=fnt(56), fill=SAFFRON)
    d.text((40, 310), "Human takes only. No AI slop.", font=fnt(26, bold=False), fill=MUTED)

    chips = ["Live debates", "Google / phone", "Private email"]
    x = 40
    for c in chips:
        bb = d.textbbox((0, 0), c, font=fnt(18))
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.rectangle([x, 360, x + tw + 22, 360 + th + 14], outline=SAFFRON, width=2)
        d.text((x + 11, 367), c, font=fnt(18), fill=WHITE)
        x += tw + 34

    p1 = load_phone(screen("live"), 520)
    p2 = load_phone(screen("signup"), 520)
    p1 = p1.resize((int(p1.width * 0.76), int(p1.height * 0.76)), Image.Resampling.LANCZOS)
    p2 = p2.resize((int(p2.width * 0.76), int(p2.height * 0.76)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(p1, (40, 410), p1)
    layer.paste(p2, (W - p2.width - 30, 430), p2)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, "Create account free → barathx.com")
    return layer.convert("RGB")


def slide_cta_close(*, pill: str) -> Image.Image:
    base, d = scan_canvas()
    stamp_brand(base, d, pill=pill)
    d.text((40, 200), "YOUR MOVE", font=fnt(26), fill=SAFFRON)
    d.text((40, 260), "Leave one", font=fnt(72), fill=WHITE)
    d.text((40, 350), "honest take.", font=fnt(72), fill=SAFFRON)
    d.text((40, 460), "60 seconds to sign up. First voices get seen.", font=fnt(28, bold=False), fill=MUTED)
    d.rectangle([40, 530, 320, 538], fill=SAFFRON)
    for i, line in enumerate(
        [
            "1. Open barathx.com",
            "2. Sign up (Google / phone / email)",
            "3. Drop your first take in the Square",
        ]
    ):
        d.text((40, 580 + i * 56), line, font=fnt(32), fill=CREAM)
    cta_bar(d, "Join free → barathx.com")
    return base


PACKS: dict[str, list] = {
    # morning — signup energy
    "signup-excite": [
        lambda: slide_type_hero(
            kicker="Soft launch",
            line1="Stop performing.",
            line2="Start arguing.",
            sub="BarathX is India’s public square — for takes that deserve a side.",
            pill="01 / 06",
            cta="Join free → barathx.com",
        ),
        lambda: slide_phone(
            kicker="The problem",
            title="WhatsApp takes",
            title2="disappear.",
            sub="Yours don’t — Square keeps them on the record.",
            screen_name="feed",
            pill="02 / 06",
            cta="Put one take on record → barathx.com",
        ),
        lambda: slide_triple(
            kicker="Why join",
            title="Three things that",
            title2="make signup worth it",
            phones=[
                ("square", "Square", "Takes stay"),
                ("arenas", "Arenas", "Pick a side"),
                ("live", "Live", "Argue it"),
            ],
            pill="03 / 06",
            cta="Join free → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Product",
            title="Home that",
            title2="actually debates.",
            sub="Not another firehose. Sides, arenas, live.",
            screen_name="home",
            pill="04 / 06",
            cta="Open the app → barathx.com",
        ),
        lambda: slide_signup_path(pill="05 / 06"),
        lambda: slide_cta_close(pill="06 / 06"),
    ],
    # midday — how it works
    "how-it-works": [
        lambda: slide_type_hero(
            kicker="How it works",
            line1="Drop. Pick.",
            line2="Argue live.",
            sub="Three moves. Real replies. No AI slop.",
            pill="01 / 06",
            cta="Leave your first take → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Step 1",
            title="Drop a take",
            title2="in the Square.",
            sub="Short posts. Real conversation.",
            screen_name="square",
            pill="02 / 06",
            cta="Try the Square → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Step 2",
            title="Pick a side.",
            title2="No fence.",
            sub="Arenas: Sports · Politics · Entertainment · more.",
            screen_name="arenas",
            pill="03 / 06",
            cta="Enter an Arena → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Step 3",
            title="Jump Live.",
            title2="Argue it.",
            sub="Host or join — human voices only.",
            screen_name="live",
            pill="04 / 06",
            cta="Go Live → barathx.com",
        ),
        lambda: slide_triple(
            kicker="Proof",
            title="Real product.",
            title2="Not a pitch deck.",
            phones=[
                ("feed", "Feed", "For you"),
                ("home", "Home", "Your hub"),
                ("signup", "Signup", "60 sec"),
            ],
            pill="05 / 06",
            cta="Create account → barathx.com",
        ),
        lambda: slide_cta_close(pill="06 / 06"),
    ],
    # evening — launch pain
    "launch-pain": [
        lambda: slide_type_hero(
            kicker="Tonight",
            line1="Group chats",
            line2="bury your best takes.",
            sub="BarathX is where India actually argues.",
            pill="01 / 06",
            cta="Sign up tonight → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Pain",
            title="Reels want",
            title2="your thumb.",
            sub="We want your opinion — on the record.",
            screen_name="square2",
            pill="02 / 06",
            cta="Leave one honest take → barathx.com",
        ),
        lambda: slide_phone(
            kicker="Fix",
            title="Square keeps",
            title2="the debate.",
            sub="Human takes only. No AI slop.",
            screen_name="feed",
            pill="03 / 06",
            cta="Open Square → barathx.com",
        ),
        lambda: slide_triple(
            kicker="Features",
            title="Built for",
            title2="people who pick sides",
            phones=[
                ("square", "Square", "On record"),
                ("arenas", "Arenas", "No fence"),
                ("live", "Live", "Jump in"),
            ],
            pill="04 / 06",
            cta="Join free → barathx.com",
        ),
        lambda: slide_signup_path(pill="05 / 06"),
        lambda: slide_cta_close(pill="06 / 06"),
    ],
}

# Alias for live-product (same as signup-excite hero set)
PACKS["live-product"] = PACKS["signup-excite"]


def render_pack(name: str) -> Path:
    slides = PACKS[name]
    out_dir = OUT_ROOT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, factory in enumerate(slides, start=1):
        img = factory()
        path = out_dir / f"slide-{i:02d}.jpg"
        img.save(path, quality=92, optimize=True)
        print(f"  {path.relative_to(ROOT)}")
    (out_dir / "README.md").write_text(
        f"# {name}\n\n"
        "BarathX IG carousel pack — product UI + crisp dark/saffron type.\n"
        "Brand spelling: **BarathX** only.\n"
        "Regenerate: `python3 brand/ig/render_product_carousels.py`\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pack",
        choices=list(PACKS.keys()) + ["all"],
        default="all",
    )
    args = parser.parse_args()
    names = list(PACKS.keys()) if args.pack == "all" else [args.pack]
    print("Rendering product carousels:")
    for name in names:
        print(f"[{name}]")
        render_pack(name)


if __name__ == "__main__":
    main()
