#!/usr/bin/env python3
"""
Render BarathX IG carousel packs — product UI + crisp dark/saffron type.

Writes 6 slides (1080×1080 JPG) into each pack folder used by the
Instagram scheduler (backend/app/instagram_publish.py):

  brand/ig/carousel/signup-excite/   → morning
  brand/ig/carousel/how-it-works/    → midday
  brand/ig/carousel/launch-pain/     → evening
  brand/ig/carousel/live-product/    → optional / admin

Hard rule: morning / midday / evening packs MUST NOT share identical
slide files. Each pack uses a different layout set + screen mix.

Usage:
  python3 brand/ig/render_product_carousels.py
  python3 brand/ig/render_product_carousels.py --pack signup-excite
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
INK = (6, 8, 12)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
TEAL = (46, 196, 182)
MUTED = (150, 150, 160)
SLATE = (28, 30, 38)

FONT = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_REG = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
    or [FONT]
)[0]


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT if bold else FONT_REG, size)


def scan_canvas(*, accent: tuple[int, int, int] = SAFFRON, bar: str = "left") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 8)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    if bar == "left":
        d.rectangle([0, 0, 18, H], fill=accent)
    elif bar == "top":
        d.rectangle([0, 0, W, 14], fill=accent)
    elif bar == "right":
        d.rectangle([W - 18, 0, W, H], fill=accent)
    elif bar == "corner":
        d.polygon([(0, 0), (160, 0), (0, 160)], fill=accent)
    return img, d


def stamp_brand(
    base: Image.Image,
    d: ImageDraw.ImageDraw,
    *,
    y: int = 36,
    pill: str = "",
    accent: tuple[int, int, int] = SAFFRON,
) -> None:
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
        d.rounded_rectangle([x0, y + 6, x0 + tw + 28, y + 6 + th + 16], radius=20, fill=accent)
        d.text((x0 + 14, y + 14), pill, font=fnt(20), fill=DARK)


def cta_bar(d: ImageDraw.ImageDraw, text: str, *, accent: tuple[int, int, int] = SAFFRON) -> None:
    d.rectangle([0, H - 70, W, H], fill=accent)
    d.text((40, H - 52), text, font=fnt(26), fill=DARK)


def load_phone(path: Path, target_h: int, *, frame_accent: tuple[int, int, int] = SAFFRON) -> Image.Image:
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
        outline=(*frame_accent, 200),
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
        "square_raw": SCREENS / "bx-site-square-raw.jpg",
        "arenas": SCREENS / "bx-site-arenas.jpg",
        "live": SCREENS / "bx-site-live.jpg",
        "home": SCREENS / "bx-site-home.jpg",
        "signup": SCREENS / "bx-site-signup.png",
        "landing": SCREENS / "bx-site-landing.png",
        "feed": CAROUSEL_SCREENS / "m03-feed.png",
        "feed_desk": CAROUSEL_SCREENS / "03-feed.png",
        "compose": CAROUSEL_SCREENS / "07-compose.png",
        "profile": CAROUSEL_SCREENS / "m06-profile.png",
        "detail": CAROUSEL_SCREENS / "m04-post-detail.png",
        "search": CAROUSEL_SCREENS / "m05-search.png",
        "signup_desk": CAROUSEL_SCREENS / "02-signup-or-login.png",
        "landing_desk": CAROUSEL_SCREENS / "01-landing.png",
    }
    path = mapping[name]
    if not path.exists():
        for alt in mapping.values():
            if alt.exists():
                return alt
        raise FileNotFoundError(name)
    return path


# --- Layout family A: morning energy (left bar, saffron) ---


def slide_type_hero(
    *,
    kicker: str,
    line1: str,
    line2: str,
    sub: str,
    pill: str,
    cta: str,
    bullets: list[str] | None = None,
    accent: tuple[int, int, int] = SAFFRON,
    bar: str = "left",
) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar=bar)
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 130), kicker.upper(), font=fnt(24), fill=accent)
    d.text((40, 178), line1, font=fnt(64), fill=WHITE)
    d.text((40, 258), line2, font=fnt(64), fill=accent)
    d.text((40, 350), sub, font=fnt(28, bold=False), fill=MUTED)
    d.rectangle([40, 420, 280, 428], fill=accent)
    y = 460
    for b in bullets or [
        "Square — takes that stay",
        "Arenas — pick a side",
        "Live — argue it live",
    ]:
        d.ellipse([48, y + 10, 64, y + 26], fill=accent)
        d.text((80, y), b, font=fnt(30), fill=CREAM)
        y += 56
    cta_bar(d, cta, accent=accent)
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
    side: str = "right",
    accent: tuple[int, int, int] = SAFFRON,
    bar: str = "left",
) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar=bar)
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 120), kicker.upper(), font=fnt(24), fill=accent)
    d.text((40, 164), title, font=fnt(52), fill=WHITE)
    if title2:
        d.text((40, 228), title2, font=fnt(52), fill=accent)
    d.text((40, 300 if title2 else 236), sub, font=fnt(26, bold=False), fill=MUTED)

    phone = load_phone(screen(screen_name), phone_h, frame_accent=accent)
    scale = 0.92
    ph = phone.resize((int(phone.width * scale), int(phone.height * scale)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    x = W - ph.width - 8 if side == "right" else 24
    layer.paste(ph, (x, 290), ph)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, cta, accent=accent)
    return layer.convert("RGB")


def slide_triple(
    *,
    kicker: str,
    title: str,
    title2: str,
    phones: list[tuple[str, str, str]],
    pill: str,
    cta: str,
    accent: tuple[int, int, int] = SAFFRON,
    bar: str = "left",
) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar=bar)
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 110), kicker.upper(), font=fnt(24), fill=accent)
    d.text((40, 150), title, font=fnt(46), fill=WHITE)
    d.text((40, 206), title2, font=fnt(46), fill=accent)

    layer = base.convert("RGBA")
    xs = [36, 360, 684]
    for (sname, label, blurb), x in zip(phones, xs):
        phone = load_phone(screen(sname), 500, frame_accent=accent)
        ph = phone.resize((int(phone.width * 0.86), int(phone.height * 0.86)), Image.Resampling.LANCZOS)
        layer.paste(ph, (x, 290), ph)
    d2 = ImageDraw.Draw(layer)
    for (sname, label, blurb), x in zip(phones, xs):
        d2.text((x + 24, 955), label, font=fnt(24), fill=accent)
        d2.text((x + 24, 988), blurb, font=fnt(20, bold=False), fill=MUTED)
    cta_bar(d2, cta, accent=accent)
    return layer.convert("RGB")


def slide_signup_path(*, pill: str, accent: tuple[int, int, int] = SAFFRON) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar="left")
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 120), "START HERE", font=fnt(24), fill=accent)
    d.text((40, 164), "Pick a side.", font=fnt(56), fill=WHITE)
    d.text((40, 232), "Argue it live.", font=fnt(56), fill=accent)
    d.text((40, 310), "Human takes only. No AI slop.", font=fnt(26, bold=False), fill=MUTED)

    chips = ["Live debates", "Google / phone", "Private email"]
    x = 40
    for c in chips:
        bb = d.textbbox((0, 0), c, font=fnt(18))
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.rectangle([x, 360, x + tw + 22, 360 + th + 14], outline=accent, width=2)
        d.text((x + 11, 367), c, font=fnt(18), fill=WHITE)
        x += tw + 34

    p1 = load_phone(screen("live"), 520, frame_accent=accent)
    p2 = load_phone(screen("signup"), 520, frame_accent=accent)
    p1 = p1.resize((int(p1.width * 0.76), int(p1.height * 0.76)), Image.Resampling.LANCZOS)
    p2 = p2.resize((int(p2.width * 0.76), int(p2.height * 0.76)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(p1, (40, 410), p1)
    layer.paste(p2, (W - p2.width - 30, 430), p2)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, "Create account free → barathx.com", accent=accent)
    return layer.convert("RGB")


def slide_cta_close(
    *,
    pill: str,
    kicker: str = "YOUR MOVE",
    line1: str = "Leave one",
    line2: str = "honest take.",
    sub: str = "60 seconds to sign up. First voices get seen.",
    steps: list[str] | None = None,
    cta: str = "Join free → barathx.com",
    accent: tuple[int, int, int] = SAFFRON,
    bar: str = "left",
) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar=bar)
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 200), kicker, font=fnt(26), fill=accent)
    d.text((40, 260), line1, font=fnt(72), fill=WHITE)
    d.text((40, 350), line2, font=fnt(72), fill=accent)
    d.text((40, 460), sub, font=fnt(28, bold=False), fill=MUTED)
    d.rectangle([40, 530, 320, 538], fill=accent)
    for i, line in enumerate(
        steps
        or [
            "1. Open barathx.com",
            "2. Sign up (Google / phone / email)",
            "3. Drop your first take in the Square",
        ]
    ):
        d.text((40, 580 + i * 56), line, font=fnt(32), fill=CREAM)
    cta_bar(d, cta, accent=accent)
    return base


# --- Layout family B: midday how-it-works (top bar, teal accent) ---


def slide_big_step(
    *,
    step: str,
    title: str,
    title2: str,
    sub: str,
    screen_name: str,
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas(accent=TEAL, bar="top")
    stamp_brand(base, d, pill=pill, accent=TEAL)
    d.rounded_rectangle([40, 118, 210, 178], radius=18, fill=TEAL)
    d.text((58, 132), step, font=fnt(28), fill=DARK)
    d.text((40, 200), title, font=fnt(54), fill=WHITE)
    d.text((40, 268), title2, font=fnt(54), fill=TEAL)
    d.text((40, 350), sub, font=fnt(26, bold=False), fill=MUTED)

    phone = load_phone(screen(screen_name), 580, frame_accent=TEAL)
    ph = phone.resize((int(phone.width * 0.9), int(phone.height * 0.9)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 20, 320), ph)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, cta, accent=TEAL)
    return layer.convert("RGB")


def slide_mid_duo(
    *,
    kicker: str,
    title: str,
    title2: str,
    left: tuple[str, str],
    right: tuple[str, str],
    pill: str,
    cta: str,
    accent: tuple[int, int, int] = TEAL,
    bar: str = "top",
) -> Image.Image:
    base, d = scan_canvas(accent=accent, bar=bar)
    stamp_brand(base, d, pill=pill, accent=accent)
    d.text((40, 120), kicker.upper(), font=fnt(24), fill=accent)
    d.text((40, 164), title, font=fnt(50), fill=WHITE)
    d.text((40, 228), title2, font=fnt(50), fill=accent)

    p1 = load_phone(screen(left[0]), 540, frame_accent=accent)
    p2 = load_phone(screen(right[0]), 540, frame_accent=accent)
    p1 = p1.resize((int(p1.width * 0.78), int(p1.height * 0.78)), Image.Resampling.LANCZOS)
    p2 = p2.resize((int(p2.width * 0.78), int(p2.height * 0.78)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(p1, (48, 320), p1)
    layer.paste(p2, (W - p2.width - 40, 360), p2)
    d2 = ImageDraw.Draw(layer)
    d2.text((64, 930), left[1], font=fnt(26), fill=accent)
    d2.text((W - p2.width - 20, 970), right[1], font=fnt(26), fill=CREAM)
    cta_bar(d2, cta, accent=accent)
    return layer.convert("RGB")


def slide_flow_strip(
    *,
    kicker: str,
    title: str,
    title2: str,
    screens: list[tuple[str, str]],
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas(accent=TEAL, bar="top")
    stamp_brand(base, d, pill=pill, accent=TEAL)
    d.text((40, 110), kicker.upper(), font=fnt(22), fill=TEAL)
    d.text((40, 150), title, font=fnt(48), fill=WHITE)
    d.text((40, 210), title2, font=fnt(48), fill=TEAL)

    layer = base.convert("RGBA")
    xs = [28, 370, 712]
    for (sname, label), x in zip(screens, xs):
        phone = load_phone(screen(sname), 470, frame_accent=TEAL)
        ph = phone.resize((int(phone.width * 0.84), int(phone.height * 0.84)), Image.Resampling.LANCZOS)
        layer.paste(ph, (x, 300), ph)
    d2 = ImageDraw.Draw(layer)
    for (sname, label), x in zip(screens, xs):
        d2.text((x + 18, 940), label, font=fnt(24), fill=CREAM)
    # arrows between phones
    for x in (330, 672):
        d2.polygon([(x, 560), (x + 28, 575), (x, 590)], fill=TEAL)
    cta_bar(d2, cta, accent=TEAL)
    return layer.convert("RGB")


# --- Layout family C: evening pain (right bar / corner, cream-on-ink) ---


def slide_pain_hero(
    *,
    kicker: str,
    line1: str,
    line2: str,
    sub: str,
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas(accent=SAFFRON, bar="corner")
    # soft ink panel
    d.rounded_rectangle([36, 120, W - 36, 980], radius=28, fill=SLATE)
    stamp_brand(base, d, pill=pill, accent=SAFFRON)
    d.text((64, 180), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((64, 240), line1, font=fnt(58), fill=WHITE)
    d.text((64, 320), line2, font=fnt(58), fill=SAFFRON)
    d.text((64, 420), sub, font=fnt(28, bold=False), fill=MUTED)
    pains = [
        "Reels steal your thumb — not your take",
        "Group chats bury the good argument",
        "Feeds reward performance, not honesty",
    ]
    y = 520
    for p in pains:
        d.rectangle([64, y, 72, y + 36], fill=SAFFRON)
        d.text((92, y), p, font=fnt(28), fill=CREAM)
        y += 70
    cta_bar(d, cta, accent=SAFFRON)
    return base


def slide_phone_stack(
    *,
    kicker: str,
    title: str,
    title2: str,
    sub: str,
    front: str,
    back: str,
    pill: str,
    cta: str,
) -> Image.Image:
    base, d = scan_canvas(accent=SAFFRON, bar="right")
    stamp_brand(base, d, pill=pill, accent=SAFFRON)
    d.text((40, 120), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((40, 164), title, font=fnt(50), fill=WHITE)
    d.text((40, 228), title2, font=fnt(50), fill=SAFFRON)
    d.text((40, 310), sub, font=fnt(26, bold=False), fill=MUTED)

    back_ph = load_phone(screen(back), 500, frame_accent=SAFFRON)
    front_ph = load_phone(screen(front), 560, frame_accent=SAFFRON)
    back_ph = back_ph.resize((int(back_ph.width * 0.82), int(back_ph.height * 0.82)), Image.Resampling.LANCZOS)
    front_ph = front_ph.resize((int(front_ph.width * 0.88), int(front_ph.height * 0.88)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(back_ph, (W - back_ph.width - 40, 300), back_ph)
    layer.paste(front_ph, (W - front_ph.width - 120, 360), front_ph)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, cta, accent=SAFFRON)
    return layer.convert("RGB")


def slide_contrast_split(
    *,
    left_title: str,
    left_lines: list[str],
    right_title: str,
    right_screen: str,
    pill: str,
    cta: str,
) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W // 2, H], fill=INK)
    d.rectangle([W // 2, 0, W, H], fill=SLATE)
    stamp_brand(base, d, pill=pill, accent=SAFFRON)
    d.text((40, 140), "WITHOUT", font=fnt(22), fill=MUTED)
    d.text((40, 180), left_title, font=fnt(40), fill=WHITE)
    y = 280
    for line in left_lines:
        d.text((40, y), f"×  {line}", font=fnt(26), fill=(200, 120, 110))
        y += 56
    d.text((W // 2 + 36, 140), "WITH BARATHX", font=fnt(22), fill=SAFFRON)
    d.text((W // 2 + 36, 180), right_title, font=fnt(36), fill=CREAM)

    phone = load_phone(screen(right_screen), 520, frame_accent=SAFFRON)
    ph = phone.resize((int(phone.width * 0.86), int(phone.height * 0.86)), Image.Resampling.LANCZOS)
    layer = base.convert("RGBA")
    layer.paste(ph, (W // 2 + 40, 260), ph)
    d2 = ImageDraw.Draw(layer)
    cta_bar(d2, cta, accent=SAFFRON)
    return layer.convert("RGB")


def slide_evening_close(*, pill: str) -> Image.Image:
    return slide_cta_close(
        pill=pill,
        kicker="TONIGHT",
        line1="One take.",
        line2="On the record.",
        sub="Stop letting the best argument die in a chat.",
        steps=[
            "1. Open barathx.com",
            "2. Create your account",
            "3. Post in Square — pick a side",
        ],
        cta="Sign up tonight → barathx.com",
        accent=SAFFRON,
        bar="right",
    )


def slide_midday_close(*, pill: str) -> Image.Image:
    return slide_cta_close(
        pill=pill,
        kicker="TRY IT NOW",
        line1="Three moves.",
        line2="Real replies.",
        sub="No algorithm cosplay. Just argument.",
        steps=[
            "1. Drop a take in the Square",
            "2. Enter an Arena — pick a side",
            "3. Jump Live when it gets hot",
        ],
        cta="Start on barathx.com",
        accent=TEAL,
        bar="top",
    )


def slide_morning_close(*, pill: str) -> Image.Image:
    return slide_cta_close(
        pill=pill,
        kicker="FIRST VOICES",
        line1="We’re early.",
        line2="Get seen.",
        sub="Soft launch. Small on purpose. Human takes only.",
        steps=[
            "1. Open barathx.com",
            "2. Sign up in ~60 seconds",
            "3. Leave one honest take",
        ],
        cta="Join free → barathx.com",
        accent=SAFFRON,
        bar="left",
    )


def slide_live_product_close(*, pill: str) -> Image.Image:
    return slide_cta_close(
        pill=pill,
        kicker="PRODUCT PROOF",
        line1="Not a teaser.",
        line2="The app.",
        sub="Square · Arenas · Live — shipping for India.",
        steps=[
            "1. Browse the Square",
            "2. Open an Arena",
            "3. Go Live with a take",
        ],
        cta="Open BarathX → barathx.com",
        accent=SAFFRON,
        bar="corner",
    )


PACKS: dict[str, list] = {
    # morning — signup energy (left bar / saffron / landing+signup focus)
    "signup-excite": [
        lambda: slide_type_hero(
            kicker="Soft launch",
            line1="Stop performing.",
            line2="Start arguing.",
            sub="BarathX is India’s public square — for takes that deserve a side.",
            pill="01 / 06",
            cta="Join free → barathx.com",
            bullets=[
                "Takes that stay on the record",
                "Sides you actually pick",
                "Live rooms for real voices",
            ],
        ),
        lambda: slide_phone(
            kicker="The product",
            title="Landing that",
            title2="means business.",
            sub="Not another scroll app — a square for India.",
            screen_name="landing",
            pill="02 / 06",
            cta="See it live → barathx.com",
            side="right",
        ),
        lambda: slide_phone(
            kicker="Home",
            title="Your hub for",
            title2="real debate.",
            sub="Feed, Square entry, arenas — one place.",
            screen_name="home",
            pill="03 / 06",
            cta="Open Home → barathx.com",
            side="left",
            phone_h=600,
        ),
        lambda: slide_signup_path(pill="04 / 06"),
        lambda: slide_phone(
            kicker="Profile",
            title="Your voice,",
            title2="your record.",
            sub="Build a trail of honest takes — not empty likes.",
            screen_name="profile",
            pill="05 / 06",
            cta="Create yours → barathx.com",
        ),
        lambda: slide_morning_close(pill="06 / 06"),
    ],
    # midday — how it works (top bar / teal / step flow)
    "how-it-works": [
        lambda: slide_type_hero(
            kicker="How it works",
            line1="Drop. Pick.",
            line2="Argue live.",
            sub="Three moves. Real replies. No AI slop.",
            pill="01 / 06",
            cta="Leave your first take → barathx.com",
            bullets=[
                "1 — Post in the Square",
                "2 — Pick a side in Arenas",
                "3 — Jump into Live",
            ],
            accent=TEAL,
            bar="top",
        ),
        lambda: slide_big_step(
            step="STEP 01",
            title="Drop a take",
            title2="in the Square.",
            sub="Short posts. Real conversation. Stays on record.",
            screen_name="square",
            pill="02 / 06",
            cta="Try the Square → barathx.com",
        ),
        lambda: slide_big_step(
            step="STEP 02",
            title="Pick a side.",
            title2="No fence.",
            sub="Sports · Politics · Entertainment · more.",
            screen_name="arenas",
            pill="03 / 06",
            cta="Enter an Arena → barathx.com",
        ),
        lambda: slide_big_step(
            step="STEP 03",
            title="Compose.",
            title2="Say it clean.",
            sub="Write the take you actually believe.",
            screen_name="compose",
            pill="04 / 06",
            cta="Write yours → barathx.com",
        ),
        lambda: slide_flow_strip(
            kicker="Then go deeper",
            title="Detail → search",
            title2="→ Live.",
            screens=[
                ("detail", "Thread"),
                ("search", "Find"),
                ("live", "Live"),
            ],
            pill="05 / 06",
            cta="Argue it live → barathx.com",
        ),
        lambda: slide_midday_close(pill="06 / 06"),
    ],
    # evening — launch pain (corner/right / stacked phones / contrast)
    "launch-pain": [
        lambda: slide_pain_hero(
            kicker="Tonight",
            line1="Group chats bury",
            line2="your best takes.",
            sub="BarathX is where India actually argues — on the record.",
            pill="01 / 06",
            cta="Sign up tonight → barathx.com",
        ),
        lambda: slide_contrast_split(
            left_title="Other apps",
            left_lines=[
                "Thumb-trap reels",
                "Vanishing chat takes",
                "AI sludge in the feed",
                "No side = no stakes",
            ],
            right_title="Public square",
            right_screen="square2",
            pill="02 / 06",
            cta="Leave one honest take → barathx.com",
        ),
        lambda: slide_phone_stack(
            kicker="Fix",
            title="Square keeps",
            title2="the debate.",
            sub="Human takes only. Threads that don’t disappear.",
            front="feed",
            back="detail",
            pill="03 / 06",
            cta="Open Square → barathx.com",
        ),
        lambda: slide_mid_duo(
            kicker="Proof",
            title="Search people.",
            title2="Find the fight.",
            left=("search", "Discover"),
            right=("live", "Go Live"),
            pill="04 / 06",
            cta="Join free → barathx.com",
            accent=SAFFRON,
            bar="right",
        ),
        lambda: slide_phone(
            kicker="Signup",
            title="60 seconds.",
            title2="You’re in.",
            sub="Google, phone, or email — then one take.",
            screen_name="signup_desk",
            pill="05 / 06",
            cta="Create account → barathx.com",
            side="right",
            accent=SAFFRON,
            bar="right",
        ),
        lambda: slide_evening_close(pill="06 / 06"),
    ],
    # optional admin / live-product — distinct from morning
    "live-product": [
        lambda: slide_type_hero(
            kicker="Live product",
            line1="This is the",
            line2="actual app.",
            sub="Screens from BarathX soft launch — not mockups for show.",
            pill="01 / 06",
            cta="Open barathx.com",
            bullets=[
                "Square feed in production",
                "Arenas with sides",
                "Live rooms shipping",
            ],
            accent=SAFFRON,
            bar="corner",
        ),
        lambda: slide_phone(
            kicker="Feed",
            title="For you,",
            title2="not for bots.",
            sub="Human ranking. AI drafts get demoted.",
            screen_name="feed_desk",
            pill="02 / 06",
            cta="Scroll the Square → barathx.com",
            side="left",
            bar="corner",
        ),
        lambda: slide_triple(
            kicker="Surfaces",
            title="Three rooms.",
            title2="One square.",
            phones=[
                ("square_raw", "Square", "Takes"),
                ("arenas", "Arenas", "Sides"),
                ("live", "Live", "Voice"),
            ],
            pill="03 / 06",
            cta="Explore → barathx.com",
            bar="corner",
        ),
        lambda: slide_phone(
            kicker="Thread",
            title="Argue in",
            title2="the detail.",
            sub="Replies that stay. Humans first.",
            screen_name="detail",
            pill="04 / 06",
            cta="Open a thread → barathx.com",
            bar="corner",
        ),
        lambda: slide_mid_duo(
            kicker="Entry",
            title="Landing →",
            title2="signup.",
            left=("landing_desk", "Landing"),
            right=("signup", "Signup"),
            pill="05 / 06",
            cta="Create account → barathx.com",
        ),
        lambda: slide_live_product_close(pill="06 / 06"),
    ],
}


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
        "Each daily pack (signup-excite / how-it-works / launch-pain) uses a "
        "distinct layout family so posts never look like the same carousel.\n"
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
