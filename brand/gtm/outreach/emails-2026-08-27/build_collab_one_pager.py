#!/usr/bin/env python3
"""BarathX creator-collab one-pager PDF — latest live screens (login + product)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

OUT = Path(__file__).resolve().parent
LIVE = OUT / "screens-live"
PDF_OUT = OUT / "BarathX-Creator-Collab-One-Pager.pdf"
LOGO = Path(__file__).resolve().parents[4] / "brand" / "baratx-logo-avatar.png"

# A4 points
PW, PH = A4
MARGIN = 36
SAFFRON = (255 / 255, 153 / 255, 51 / 255)
DARK = (13 / 255, 13 / 255, 18 / 255)


def font_path(bold: bool = False) -> str:
    if bold:
        for p in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ):
            if Path(p).exists():
                return p
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).exists():
            return p
    raise SystemExit("No TTF fonts found")


def phone_thumb(src: Path, max_h: int = 280) -> Path:
    """Crop/scale mobile screenshot to a clean phone thumb PNG."""
    out = OUT / "_slide_assets" / f"thumb-{src.stem}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    # scale to max height
    scale = max_h / im.height
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    # rounded frame
    pad = 6
    frame = Image.new("RGB", (nw + pad * 2, nh + pad * 2), (28, 28, 34))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, nw + pad * 2 - 1, nh + pad * 2 - 1], radius=22, outline=(255, 153, 51), width=3)
    frame.paste(im, (pad, pad))
    frame.save(out, quality=92)
    return out


def draw_wrapped(c, text: str, x: float, y: float, max_w: float, font: str, size: float, leading: float, fill=(0.12, 0.12, 0.14)):
    c.setFillColorRGB(*fill)
    c.setFont(font, size)
    words = text.split()
    line = ""
    cy = y
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, font, size) <= max_w:
            line = trial
        else:
            c.drawString(x, cy, line)
            cy -= leading
            line = w
    if line:
        c.drawString(x, cy, line)
        cy -= leading
    return cy


def build() -> Path:
    # Register fonts
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont("BXBody", font_path(False)))
    pdfmetrics.registerFont(TTFont("BXBold", font_path(True)))

    need = {
        "landing": LIVE / "m-landing.png",
        "login": LIVE / "m-login.png",
        "square": LIVE / "ui-square.png",
        "arenas": LIVE / "ui-arenas.png",
        "live": LIVE / "ui-live.png",
    }
    for k, p in need.items():
        if not p.exists() or p.stat().st_size < 40_000:
            raise SystemExit(f"Missing/stale screen: {p}")

    thumbs = {k: phone_thumb(p, 250 if k != "landing" else 260) for k, p in need.items()}

    c = pdfcanvas.Canvas(str(PDF_OUT), pagesize=A4)

    # Header bar
    c.setFillColorRGB(*DARK)
    c.rect(0, PH - 78, PW, 78, fill=1, stroke=0)
    c.setFillColorRGB(*SAFFRON)
    c.rect(0, PH - 82, PW, 4, fill=1, stroke=0)

    if LOGO.exists():
        c.drawImage(ImageReader(str(LOGO)), MARGIN, PH - 68, width=40, height=40, mask="auto")
    c.setFillColorRGB(1, 1, 1)
    c.setFont("BXBold", 18)
    c.drawString(MARGIN + 52, PH - 42, "BarathX")
    c.setFont("BXBody", 10)
    c.setFillColorRGB(0.85, 0.85, 0.9)
    c.drawString(MARGIN + 52, PH - 58, "Creator collab brief  ·  India’s public square")

    c.setFillColorRGB(*SAFFRON)
    c.setFont("BXBold", 9)
    c.drawRightString(PW - MARGIN, PH - 40, "barathx.com")
    c.setFillColorRGB(0.85, 0.85, 0.9)
    c.setFont("BXBody", 8)
    c.drawRightString(PW - MARGIN, PH - 54, "@getbaratx")

    y = PH - 110
    c.setFillColorRGB(0.1, 0.1, 0.12)
    c.setFont("BXBold", 16)
    c.drawString(MARGIN, y, "What we want people to feel")
    y -= 18
    y = draw_wrapped(
        c,
        "India finally has a place where its opinions matter — not as content for someone else’s feed, "
        "but as a public square we built for ourselves. Pride. Relief. Courage to take a side. Belonging.",
        MARGIN,
        y,
        PW - 2 * MARGIN,
        "BXBody",
        10,
        13,
    )
    y -= 8
    c.setFillColorRGB(*SAFFRON)
    c.setFont("BXBold", 10)
    c.drawString(MARGIN, y, "North star: India’s moment to build its own digital public square — BarathX is that home.")

    y -= 28
    c.setFillColorRGB(0.1, 0.1, 0.12)
    c.setFont("BXBold", 14)
    c.drawString(MARGIN, y, "What we’re building")
    y -= 16
    y = draw_wrapped(
        c,
        "BarathX is a conversation network for India: Square (questions & takes), Arenas (pick a side / debates), "
        "and Live (argue in real time). Human takes only. No AI slop. Soft launch live now.",
        MARGIN,
        y,
        PW - 2 * MARGIN,
        "BXBody",
        10,
        13,
    )

    y -= 10
    bullets = [
        "Square — one question, your take, real replies (not Reels)",
        "Arenas — Agree / Disagree / It depends — debates that stay on the record",
        "Live — sided rooms, human voices",
        "Built by Indians, for Indians, owned by Indians",
    ]
    for b in bullets:
        c.setFillColorRGB(*SAFFRON)
        c.circle(MARGIN + 4, y + 3, 2.5, fill=1, stroke=0)
        c.setFillColorRGB(0.15, 0.15, 0.18)
        c.setFont("BXBody", 9.5)
        c.drawString(MARGIN + 14, y, b)
        y -= 14

    y -= 8
    c.setFillColorRGB(0.1, 0.1, 0.12)
    c.setFont("BXBold", 14)
    c.drawString(MARGIN, y, "Latest product screens")
    y -= 6

    # 5 thumbs in a row (may wrap to 2 rows on A4)
    labels = [
        ("landing", "Landing"),
        ("login", "Login"),
        ("square", "Square"),
        ("arenas", "Arenas"),
        ("live", "Live"),
    ]
    gap = 10
    usable = PW - 2 * MARGIN
    thumb_w = (usable - 4 * gap) / 5
    row_y = y - 200
    x = MARGIN
    for key, label in labels:
        thumb = thumbs[key]
        im = Image.open(thumb)
        # fit into thumb_w
        scale = min(thumb_w / im.width, 190 / im.height)
        tw, th = im.width * scale, im.height * scale
        c.drawImage(ImageReader(str(thumb)), x + (thumb_w - tw) / 2, row_y, width=tw, height=th, preserveAspectRatio=True, mask="auto")
        c.setFillColorRGB(0.25, 0.25, 0.3)
        c.setFont("BXBold", 8)
        c.drawCentredString(x + thumb_w / 2, row_y - 12, label)
        x += thumb_w + gap

    y = row_y - 36
    c.setFillColorRGB(0.1, 0.1, 0.12)
    c.setFont("BXBold", 14)
    c.drawString(MARGIN, y, "Collab ask")
    y -= 16
    y = draw_wrapped(
        c,
        "We’re partnering with creators/pages whose audiences already talk and argue. "
        "Formats we like: Reel, Story, short mention, or Live on BarathX. Your voice stays yours — we send a crisp brief + assets.",
        MARGIN,
        y,
        PW - 2 * MARGIN,
        "BXBody",
        10,
        13,
    )
    y -= 6
    y = draw_wrapped(
        c,
        "Please reply with: (1) your promotion / collab rate, (2) formats you offer, (3) typical turnaround. "
        "We’ll confirm scope and send creatives if it’s a fit.",
        MARGIN,
        y,
        PW - 2 * MARGIN,
        "BXBody",
        10,
        13,
    )

    y -= 18
    c.setFillColorRGB(*DARK)
    c.roundRect(MARGIN, y - 70, PW - 2 * MARGIN, 78, 8, fill=1, stroke=0)
    c.setFillColorRGB(*SAFFRON)
    c.setFont("BXBold", 11)
    c.drawString(MARGIN + 14, y - 18, "Contact")
    c.setFillColorRGB(1, 1, 1)
    c.setFont("BXBody", 9.5)
    c.drawString(MARGIN + 14, y - 34, "Sharath · Founder · BarathX")
    c.drawString(MARGIN + 14, y - 48, "hello@barathx.com  ·  contact@barathx.com  ·  https://barathx.com")
    c.setFont("BXBody", 8.5)
    c.setFillColorRGB(0.85, 0.85, 0.9)
    c.drawString(
        MARGIN + 14,
        y - 62,
        "IG/X @getbaratx  ·  WA channel + community linked on site",
    )

    c.setFillColorRGB(0.55, 0.55, 0.6)
    c.setFont("BXBody", 7.5)
    c.drawCentredString(PW / 2, 22, "Screens captured from live BarathX · Aug 2026 · Soft launch")

    c.save()
    print(f"Wrote {PDF_OUT} ({PDF_OUT.stat().st_size} bytes)")
    return PDF_OUT


if __name__ == "__main__":
    build()
