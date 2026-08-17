#!/usr/bin/env python3
"""Render BarathX email pitch deck slides (1920×1080 JPG)."""

from __future__ import annotations

import glob
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "slides"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1920, 1080
DARK = (10, 10, 14)
INK = (16, 18, 24)
SLATE = (28, 30, 38)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)
TEAL = (46, 196, 182)
RED = (220, 110, 100)

FONT_B = glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)[0]
FONT_R = (
    glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True) or [FONT_B]
)[0]
FONT_S = (
    glob.glob("/usr/share/fonts/**/*DejaVuSans-Bold*.ttf", recursive=True)
    or glob.glob("/usr/share/fonts/**/*LiberationSans-Bold*.ttf", recursive=True)
    or [FONT_B]
)[0]


def f(size: int, *, bold: bool = True, display: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_S if display else (FONT_B if bold else FONT_R)
    return ImageFont.truetype(path, size)


def canvas(*, bar: str = "left") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 6)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    if bar == "left":
        d.rectangle([0, 0, 14, H], fill=SAFFRON)
    elif bar == "top":
        d.rectangle([0, 0, W, 10], fill=SAFFRON)
    elif bar == "accent":
        d.rectangle([0, 0, 14, H], fill=SAFFRON)
        d.rectangle([0, H - 12, W, H], fill=SAFFRON)
    return img, d


def brand(base: Image.Image, d: ImageDraw.ImageDraw, *, pill: str = "") -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
    mask = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 63, 63], fill=255)
    circ = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, (48, 40), circ)
    d.text((128, 52), "BarathX", font=f(36), fill=CREAM)
    if pill:
        bb = d.textbbox((0, 0), pill, font=f(22))
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x0 = W - 56 - tw - 36
        d.rounded_rectangle([x0, 46, x0 + tw + 36, 46 + th + 20], radius=22, fill=SAFFRON)
        d.text((x0 + 18, 56), pill, font=f(22), fill=DARK)


def footer(d: ImageDraw.ImageDraw, text: str = "barathx.com · India’s public square") -> None:
    d.text((48, H - 56), text, font=f(22, bold=False), fill=MUTED)


def bullets(
    d: ImageDraw.ImageDraw,
    items: list[str],
    *,
    x: int = 56,
    y: int = 320,
    gap: int = 64,
    color: tuple[int, int, int] = CREAM,
    size: int = 34,
    accent: tuple[int, int, int] = SAFFRON,
) -> None:
    for i, line in enumerate(items):
        yy = y + i * gap
        d.ellipse([x, yy + 12, x + 18, yy + 30], fill=accent)
        d.text((x + 40, yy), line, font=f(size, bold=False), fill=color)


def save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.save(path, quality=92, optimize=True)
    print(f"  {path}")
    return path


# --- Slides ---


def slide_01_cover() -> Image.Image:
    base, d = canvas(bar="accent")
    brand(base, d, pill="EMAIL PITCH")
    d.text((56, 220), "BarathX", font=f(120, display=True), fill=WHITE)
    d.text((56, 370), "India’s public square", font=f(64), fill=SAFFRON)
    d.text(
        (56, 480),
        "What we give people that other platforms don’t —\nand how we promote & pay for real debate.",
        font=f(36, bold=False),
        fill=MUTED,
    )
    d.rectangle([56, 620, 320, 628], fill=SAFFRON)
    d.text((56, 670), "Soft launch · Live now at barathx.com", font=f(32), fill=CREAM)
    d.text((56, 730), "Apps coming soon · Human takes only", font=f(28, bold=False), fill=MUTED)
    footer(d, "Confidential for partners / investors / ops · hello@barathx.com")
    return base


def slide_02_problem() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="01  PROBLEM")
    d.text((56, 150), "India’s best arguments", font=f(64, display=True), fill=WHITE)
    d.text((56, 230), "disappear.", font=f(64, display=True), fill=SAFFRON)
    cards = [
        ("WhatsApp", "Takes die in the group\nby Monday morning"),
        ("Instagram", "Comments buried.\nReels want your thumb."),
        ("X / feeds", "Noise, bots, AI sludge.\nLikes without answers."),
    ]
    for i, (title, body) in enumerate(cards):
        x = 56 + i * 600
        d.rounded_rectangle([x, 360, x + 540, 720], radius=24, fill=SLATE)
        d.text((x + 36, 400), title, font=f(36), fill=SAFFRON)
        d.text((x + 36, 480), body, font=f(30, bold=False), fill=CREAM)
    footer(d)
    return base


def slide_03_gap() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="02  THE GAP")
    d.text((56, 150), "What other platforms", font=f(56, display=True), fill=WHITE)
    d.text((56, 220), "are not providing", font=f(56, display=True), fill=SAFFRON)

    left = [
        "A place where a take stays on the record",
        "Forced sides (Agree / Disagree) — real stakes",
        "Live rooms built for argument, not performance",
        "Human ranking — AI drafts demoted / flagged",
        "Identity: “I think out loud” not “I scroll”",
    ]
    d.rounded_rectangle([56, 320, 1860, 920], radius=28, fill=SLATE)
    d.text((90, 360), "MISSING TODAY", font=f(24), fill=SAFFRON)
    bullets(d, left, x=90, y=420, gap=70, size=36)
    footer(d)
    return base


def slide_04_unique() -> Image.Image:
    """HIGHLIGHT slide — what BarathX uniquely gives."""
    base, d = canvas(bar="accent")
    brand(base, d, pill="03  HIGHLIGHT")
    d.text((56, 140), "What BarathX gives", font=f(56, display=True), fill=WHITE)
    d.text((56, 210), "that others don’t", font=f(56, display=True), fill=SAFFRON)

    items = [
        ("ON THE RECORD", "Takes don’t vanish in a chat or get buried by an algorithm."),
        ("PICK A SIDE", "Arenas force Agree / Disagree — no fence-sitting theater."),
        ("ARGUE LIVE", "Jump into Live rooms — up to 15 voices, human only."),
        ("HUMAN FIRST", "AI-looking drafts flagged & demoted. Real replies rise."),
        ("EARLY VOICE", "Soft launch — first voices get seen, not drowned."),
        ("EARNED STATUS", "Founding spots earned by real debate — not signup farming."),
    ]
    for i, (title, body) in enumerate(items):
        col, row = i % 3, i // 3
        x, y = 56 + col * 620, 320 + row * 300
        d.rounded_rectangle([x, y, x + 580, y + 260], radius=22, fill=SLATE)
        d.rectangle([x, y, x + 12, y + 260], fill=SAFFRON)
        d.text((x + 36, y + 36), title, font=f(28), fill=SAFFRON)
        d.text((x + 36, y + 100), body, font=f(26, bold=False), fill=CREAM)
    footer(d)
    return base


def slide_05_vs() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="04  VS PLATFORMS")
    d.text((56, 140), "BarathX vs everyone else", font=f(52, display=True), fill=WHITE)

    headers = ["", "WhatsApp", "Instagram", "X / feeds", "BarathX"]
    rows = [
        ("Take stays", "×", "×", "~", "✓"),
        ("Pick a side", "×", "×", "×", "✓"),
        ("Live argument", "~", "×", "~", "✓"),
        ("Human ranking", "×", "×", "×", "✓"),
        ("No AI sludge", "×", "×", "×", "✓"),
    ]
    xs = [56, 420, 720, 1040, 1400]
    for i, h in enumerate(headers):
        d.text((xs[i], 250), h, font=f(28), fill=SAFFRON if i == 4 else MUTED)
    for r, row in enumerate(rows):
        y = 330 + r * 100
        d.line([(56, y - 20), (1860, y - 20)], fill=(40, 40, 48), width=1)
        for c, cell in enumerate(row):
            color = TEAL if cell == "✓" else (RED if cell == "×" else CREAM)
            weight = True if c == 0 or cell in ("✓", "×") else False
            d.text((xs[c], y), cell, font=f(30, bold=weight), fill=color if c else CREAM)
    footer(d, "✓ = designed for it · ~ = partial / not the product job")
    return base


def slide_06_product() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="05  PRODUCT")
    d.text((56, 150), "Three surfaces. One square.", font=f(56, display=True), fill=WHITE)
    cards = [
        ("SQUARE", "Short takes.\nReal replies.\nOn the record."),
        ("ARENAS", "Sports · Politics ·\nEntertainment · more.\nAgree / Disagree."),
        ("LIVE", "Host or join.\nArgue it live.\nHuman voices only."),
    ]
    for i, (t, b) in enumerate(cards):
        x = 56 + i * 620
        d.rounded_rectangle([x, 320, x + 580, 820], radius=28, fill=SLATE)
        d.text((x + 40, 380), t, font=f(40), fill=SAFFRON)
        d.text((x + 40, 480), b, font=f(34, bold=False), fill=CREAM)
    footer(d, "Open barathx.com · browser on phone + desktop · apps coming soon")
    return base


def slide_07_trust() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="06  TRUST")
    d.text((56, 150), "Built for trust,", font=f(56, display=True), fill=WHITE)
    d.text((56, 230), "not growth cosplay.", font=f(56, display=True), fill=SAFFRON)
    bullets(
        d,
        [
            "We’re early on purpose — rooms stay real, not performed",
            "Human-first feed: likely-AI drafts tagged & demoted",
            "Mentions / tagged you — people find the fight that names them",
            "Privacy path (DPDP): consent, export, sign-out everywhere",
            "Early Issues board for first members — bugs & ideas heard",
            "Anti-scrape + session hardening — product for people, not bots",
        ],
        y=340,
        gap=72,
        size=34,
    )
    footer(d)
    return base


def slide_08_promo_public() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="07  PROMOTION")
    d.text((56, 140), "How we promote", font=f(56, display=True), fill=WHITE)
    d.text((56, 220), "(public surface)", font=f(48), fill=SAFFRON)

    d.rounded_rectangle([56, 320, 1860, 520], radius=24, fill=SLATE)
    d.text((90, 360), "CANONICAL PUBLIC LINE", font=f(22), fill=SAFFRON)
    d.text(
        (90, 420),
        "100 Founding spots, earned by opening a debate that gets\nreal engagement, not by signing up.",
        font=f(36),
        fill=CREAM,
    )

    bullets(
        d,
        [
            "Lead with exclusivity + earned entry — never cash-for-signup",
            "No rupee amounts in bios, ads, captions, carousels, outreach",
            "Entertain first: real Live clips > produced feature ads",
            "Identity sell: “people who actually have an opinion”",
            "Gate paid ads until rooms have real non-official replies",
        ],
        y=580,
        gap=60,
        size=30,
    )
    footer(d, "Public rule: never advertise Founding ₹ / UPI / cash")
    return base


def slide_09_pay() -> Image.Image:
    """INTERNAL economics — how we pay."""
    base, d = canvas(bar="top")
    brand(base, d, pill="08  HOW WE PAY")
    d.text((56, 140), "How we pay", font=f(56, display=True), fill=WHITE)
    d.text((56, 220), "(ops / partners only — not public creatives)", font=f(32, bold=False), fill=MUTED)

    # Founding card
    d.rounded_rectangle([56, 300, 930, 900], radius=28, fill=SLATE)
    d.text((90, 340), "FOUNDING 100", font=f(32), fill=SAFFRON)
    d.text((90, 400), "Surprise thank-you", font=f(40), fill=WHITE)
    bullets(
        d,
        [
            "Earn via real debate + engagement",
            "Private reveal after payable: ₹150",
            "No strings · admin marks paid (UPI)",
            "Budget ceiling ≈ ₹15,000 total",
            "Hide ₹ until after the behavior",
        ],
        x=90,
        y=480,
        gap=58,
        size=28,
    )

    # Race card
    d.rounded_rectangle([990, 300, 1860, 900], radius=28, fill=SLATE)
    d.text((1024, 340), "SQUARE RACE", font=f(32), fill=TEAL)
    d.text((1024, 400), "Every 14 days", font=f(40), fill=WHITE)
    bullets(
        d,
        [
            "Highest-liked Home post wins",
            "Min 25 likes to qualify",
            "Prize ₹150 – ₹500 (scales)",
            "Official / blue likes ignored",
            "Separate from Founding pitch",
        ],
        x=1024,
        y=480,
        gap=58,
        size=28,
        accent=TEAL,
    )
    footer(d, "Reward the behavior we want repeated — real debates, not installs")
    return base


def slide_10_rules() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="09  PAY RULES")
    d.text((56, 150), "Non-negotiable pay rules", font=f(52, display=True), fill=WHITE)

    do = [
        "Pay for real debates / real replies",
        "Surprise ₹ only after payable / paid",
        "Keep Founding public line ₹-free",
        "Manual UPI + human spam veto",
    ]
    dont = [
        "Don’t pay for installs / app opens",
        "Don’t put ₹150 in public Founding copy",
        "Don’t run ads into empty rooms",
        "Don’t invent traction numbers",
    ]
    d.rounded_rectangle([56, 280, 930, 900], radius=28, fill=SLATE)
    d.text((90, 320), "DO", font=f(32), fill=TEAL)
    bullets(d, do, x=90, y=400, gap=80, size=30, accent=TEAL)

    d.rounded_rectangle([990, 280, 1860, 900], radius=28, fill=SLATE)
    d.text((1024, 320), "DON’T", font=f(32), fill=RED)
    bullets(d, dont, x=1024, y=400, gap=80, size=30, accent=RED)
    footer(d)
    return base


def slide_11_ask() -> Image.Image:
    base, d = canvas()
    brand(base, d, pill="10  THE ASK")
    d.text((56, 150), "What we’re asking", font=f(56, display=True), fill=WHITE)
    steps = [
        ("1", "Try it", "Leave one honest take on barathx.com (2 minutes)."),
        ("2", "Share once", "If it clicks — Story / post / mention to your audience."),
        ("3", "Optional Live", "Host or join one Live on a topic you already own."),
    ]
    for i, (n, t, b) in enumerate(steps):
        y = 300 + i * 180
        d.rounded_rectangle([56, y, 1860, y + 150], radius=22, fill=SLATE)
        d.rounded_rectangle([90, y + 40, 170, y + 110], radius=16, fill=SAFFRON)
        d.text((112, y + 55), n, font=f(40), fill=DARK)
        d.text((210, y + 40), t, font=f(36), fill=WHITE)
        d.text((210, y + 95), b, font=f(28, bold=False), fill=MUTED)
    footer(d, "We’ll send caption + image ready to paste")
    return base


def slide_12_close() -> Image.Image:
    base, d = canvas(bar="accent")
    brand(base, d, pill="NEXT")
    d.text((56, 220), "Leave one take", font=f(72, display=True), fill=WHITE)
    d.text((56, 320), "on the record.", font=f(72, display=True), fill=SAFFRON)
    d.text(
        (56, 440),
        "BarathX — India’s public square.\nSoft launch live · Apps coming soon.",
        font=f(36, bold=False),
        fill=MUTED,
    )
    d.rectangle([56, 580, 280, 588], fill=SAFFRON)
    d.text((56, 630), "Sharath · Founder", font=f(34), fill=CREAM)
    d.text((56, 690), "hello@barathx.com", font=f(30, bold=False), fill=MUTED)
    d.text((56, 750), "https://barathx.com", font=f(30, bold=False), fill=MUTED)
    d.text((56, 810), "X / IG @getbaratx · WhatsApp channel + community", font=f(26, bold=False), fill=MUTED)
    footer(d, "Reply YES · STORY · CALL")
    return base


SLIDES = [
    ("01-cover.jpg", slide_01_cover),
    ("02-problem.jpg", slide_02_problem),
    ("03-gap.jpg", slide_03_gap),
    ("04-unique-highlight.jpg", slide_04_unique),
    ("05-vs-platforms.jpg", slide_05_vs),
    ("06-product.jpg", slide_06_product),
    ("07-trust.jpg", slide_07_trust),
    ("08-promotion-public.jpg", slide_08_promo_public),
    ("09-how-we-pay.jpg", slide_09_pay),
    ("10-pay-rules.jpg", slide_10_rules),
    ("11-the-ask.jpg", slide_11_ask),
    ("12-close.jpg", slide_12_close),
]


def main() -> None:
    print("Rendering email pitch deck slides:")
    for name, fn in SLIDES:
        save(fn(), name)


if __name__ == "__main__":
    main()
