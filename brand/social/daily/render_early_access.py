#!/usr/bin/env python3
"""Early-access post creatives — same format as daily crosspost mockups."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_daily_crosspost import (  # noqa: E402
    CREAM,
    MUTED,
    SAFFRON,
    SLATE,
    W,
    WHITE,
    canvas,
    cta,
    fnt,
    phone,
    screen,
    stamp,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "2026-08-17" / "early-access"


def ea_shared() -> object:
    """WA + X — early access / first voices."""
    base, d = canvas()
    stamp(base, d, pill="EARLY ACCESS")
    d.text((36, 110), "YOU’RE EARLY", font=fnt(22), fill=SAFFRON)
    d.text((36, 150), "First voices", font=fnt(52), fill=WHITE)
    d.text((36, 218), "get seen.", font=fnt(52), fill=SAFFRON)
    d.text(
        (36, 300),
        "Soft launch members shape India’s public square.\n"
        "Drop takes. Pick sides. Argue live.",
        font=fnt(26, bold=False),
        fill=MUTED,
    )
    chips = ["Square", "Arenas", "Live", "Human only"]
    x = 36
    for c in chips:
        bb = d.textbbox((0, 0), c, font=fnt(18))
        tw = bb[2] - bb[0]
        d.rectangle([x, 400, x + tw + 20, 438], outline=SAFFRON, width=2)
        d.text((x + 10, 408), c, font=fnt(18), fill=WHITE)
        x += tw + 28

    ph = phone(screen("home"), 480)
    ph = ph.resize((int(ph.width * 0.88), int(ph.height * 0.88)))
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 20, 430), ph)
    d2 = ImageDraw.Draw(layer)
    cta(d2, "Open your square → barathx.com")
    return layer.convert("RGB")


def ea_whatsapp() -> object:
    """Triple phone — Drop / Pick / Argue for early community."""
    base, d = canvas()
    stamp(base, d, pill="EARLY · WA")
    d.text((36, 120), "EARLY ACCESS", font=fnt(22), fill=SAFFRON)
    d.text((36, 165), "You’re in.", font=fnt(54), fill=WHITE)
    d.text((36, 235), "Use the square.", font=fnt(54), fill=SAFFRON)

    phones = [("square", "Drop"), ("arenas", "Pick"), ("live", "Argue")]
    layer = base.convert("RGBA")
    xs = [40, 380, 720]
    for (name, label), x in zip(phones, xs):
        ph = phone(screen(name), 400)
        ph = ph.resize((int(ph.width * 0.72), int(ph.height * 0.72)))
        layer.paste(ph, (x, 340), ph)
    d2 = ImageDraw.Draw(layer)
    for (name, label), x in zip(phones, xs):
        d2.text((x + 40, 880), label, font=fnt(24), fill=SAFFRON)
    cta(d2, "Leave one take → barathx.com")
    return layer.convert("RGB")


def ea_linkedin() -> object:
    base, d = canvas()
    stamp(base, d, pill="EARLY · LI")
    d.text((36, 120), "SOFT LAUNCH", font=fnt(22), fill=SAFFRON)
    d.text((36, 165), "Early access", font=fnt(54), fill=WHITE)
    d.text((36, 235), "isn’t a waitlist.", font=fnt(54), fill=SAFFRON)
    d.rounded_rectangle([36, 340, W - 36, 720], radius=22, fill=SLATE)
    d.text((60, 380), "What early members get to do now", font=fnt(26), fill=SAFFRON)
    for i, line in enumerate(
        [
            "Post in the Square — takes stay on the record",
            "Enter Arenas — Agree / Disagree, real stakes",
            "Go Live — argue with humans, not bots",
            "Earn Founding — by real debate, not signup",
        ]
    ):
        d.text((60, 450 + i * 52), f"→  {line}", font=fnt(24, bold=False), fill=CREAM)
    cta(d, "Continue on barathx.com")
    return base


def ea_founding() -> object:
    """Founding surface for early access (public line — no ₹)."""
    base, d = canvas()
    stamp(base, d, pill="FOUNDING")
    d.text((36, 110), "FOUNDING 100", font=fnt(22), fill=SAFFRON)
    d.text((36, 150), "Earned by", font=fnt(52), fill=WHITE)
    d.text((36, 218), "real debate.", font=fnt(52), fill=SAFFRON)
    d.text(
        (36, 300),
        "100 Founding spots, earned by opening a debate\n"
        "that gets real engagement, not by signing up.",
        font=fnt(26, bold=False),
        fill=MUTED,
    )
    ph = phone(screen("rewards"), 520)
    ph = ph.resize((int(ph.width * 0.86), int(ph.height * 0.86)))
    layer = base.convert("RGBA")
    layer.paste(ph, (W - ph.width - 16, 420), ph)
    d2 = ImageDraw.Draw(layer)
    cta(d2, "Open Rewards → barathx.com/rewards")
    return layer.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mapping = {
        "ea-shared.jpg": ea_shared,
        "ea-whatsapp.jpg": ea_whatsapp,
        "ea-linkedin.jpg": ea_linkedin,
        "ea-founding.jpg": ea_founding,
    }
    print(f"Rendering early-access creatives → {OUT}")
    for name, fn in mapping.items():
        img = fn()
        path = OUT / name
        img.save(path, quality=92, optimize=True)
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
