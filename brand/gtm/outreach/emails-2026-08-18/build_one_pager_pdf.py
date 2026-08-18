#!/usr/bin/env python3
"""Build BarathX one-page PDF for cold outreach (no fees)."""

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "BarathX-One-Pager.pdf"

NAVY = HexColor("#0B1F3A")
INK = HexColor("#1A1A1A")
MUTED = HexColor("#4A5563")
RULE = HexColor("#D6D0C6")
BG_BAND = HexColor("#F7F4EF")
ACCENT = HexColor("#C45C26")


def draw_wrapped(c, text, x, y, max_width, font="Helvetica", size=11, leading=16, color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    lines = []
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, font, size) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    for i, ln in enumerate(lines):
        c.drawString(x, y - i * leading, ln)
    return len(lines) * leading


def build():
    width, height = A4
    c = canvas.Canvas(str(OUT), pagesize=A4)
    margin = 18 * mm
    content_w = width - 2 * margin

    # Header band
    c.setFillColor(NAVY)
    c.rect(0, height - 42 * mm, width, 42 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(margin, height - 20 * mm, "BarathX")
    c.setFont("Helvetica", 12)
    c.drawString(margin, height - 28 * mm, "India’s public square — one-pager")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#E8B88A"))
    c.drawString(margin, height - 35 * mm, "Built by Indians · for Indians · owned by Indians")

    y = height - 55 * mm

    def section(title):
        nonlocal y
        c.setFillColor(ACCENT)
        c.rect(margin, y + 3, 8, 8, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin + 14, y + 3, title)
        y -= 8 * mm

    section("What it is")
    used = draw_wrapped(
        c,
        "BarathX is a place to drop a take, pick a side, and get real replies — Square · Arenas · Live. Human takes only. No AI slop.",
        margin,
        y,
        content_w,
        size=11,
        leading=15,
    )
    y -= used + 4 * mm
    used = draw_wrapped(
        c,
        "Hot takes die in WhatsApp. Reels reward the scroll, not the opinion. We’re building the square those conversations deserve.",
        margin,
        y,
        content_w,
        size=11,
        leading=15,
        color=MUTED,
    )
    y -= used + 8 * mm

    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(margin, y + 4 * mm, width - margin, y + 4 * mm)
    y -= 4 * mm

    section("What we’re trying to achieve")
    used = draw_wrapped(
        c,
        "Make honest public debate normal for young India — on a platform that belongs here. Soft launch is live. We’re growing through creators whose audiences already talk, argue, and care.",
        margin,
        y,
        content_w,
        size=11,
        leading=15,
    )
    y -= used + 8 * mm

    c.line(margin, y + 4 * mm, width - margin, y + 4 * mm)
    y -= 4 * mm

    section("Why this collab")
    used = draw_wrapped(
        c,
        "Your audience already debates in comments and DMs. We’d rather partner with pages people trust than buy empty reach. Creative stays with you. We share a short brief + exclusive link if we move forward.",
        margin,
        y,
        content_w,
        size=11,
        leading=15,
    )
    y -= used + 8 * mm

    c.line(margin, y + 4 * mm, width - margin, y + 4 * mm)
    y -= 4 * mm

    section("Next step")
    used = draw_wrapped(
        c,
        "Reply with how partnerships usually work on your side (format, timeline, who decides). Spelling on creatives: BarathX.",
        margin,
        y,
        content_w,
        size=11,
        leading=15,
    )
    y -= used + 12 * mm

    # Soft info box
    box_h = 28 * mm
    c.setFillColor(BG_BAND)
    c.roundRect(margin, y - box_h + 8 * mm, content_w, box_h, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 6 * mm, y, "Links")
    c.setFont("Helvetica", 11)
    c.setFillColor(INK)
    c.drawString(margin + 6 * mm, y - 7 * mm, "https://barathx.com")
    c.drawString(margin + 6 * mm, y - 14 * mm, "Instagram @getbarathx")

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawString(margin, 14 * mm, "BarathX · Creator / media intro · No fee language in this brief")
    c.drawRightString(width - margin, 14 * mm, "1 of 1")

    c.showPage()
    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
