#!/usr/bin/env python3
"""Two ~20s Gen Z BarathX reels (9:16) for 2026-08-21 — updated UI screens."""

from __future__ import annotations

import argparse
import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-21"
FALLBACK = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-19"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1920
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)
TEAL = (13, 148, 136)


def _font_paths() -> tuple[str, str]:
    bold = (
        glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
    )
    regular = (
        glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
        or bold
    )
    if not bold:
        raise SystemExit("No Bold TTF under /usr/share/fonts")
    return bold[0], regular[0]


FONT_B, FONT_R = _font_paths()


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def screen(name: str) -> Path:
    p = LIVE / name
    if p.exists() and p.stat().st_size > 80_000:
        return p
    q = FALLBACK / name
    return q if q.exists() else p


def paste_logo(base: Image.Image, size: int, xy: tuple[int, int]) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, xy, circ)


def footer(d: ImageDraw.ImageDraw, label: str) -> None:
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), label, font=fnt(32), fill=DARK)


def wrap(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def overlay_phone(
    path: Path,
    *,
    kicker: str,
    title: str,
    sub: str = "",
    badge: str = "",
) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 14], fill=SAFFRON)
    paste_logo(base, 72, (48, 48))
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)
    d.text((48, 150), kicker.upper(), font=fnt(24), fill=SAFFRON)

    y = 196
    for line in wrap(d, title, fnt(48), 980)[:3]:
        d.text((48, y), line, font=fnt(48), fill=WHITE)
        y += 58
    if sub:
        for line in wrap(d, sub, fnt(28, False), 980)[:2]:
            d.text((48, y + 8), line, font=fnt(28, False), fill=MUTED)
            y += 40

    ui = Image.open(path).convert("RGB")
    max_h, max_w = 1120, 680
    scale = min(max_w / ui.width, max_h / ui.height)
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 14
    frame = Image.new("RGB", (nw + pad * 2, nh + pad * 2), (28, 28, 34))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=44, outline=SAFFRON, width=4)
    frame.paste(ui, (pad, pad))
    base.paste(frame, ((W - frame.width) // 2, min(360, y + 40)))

    if badge:
        bw = int(d.textlength(badge, font=fnt(26)) + 36)
        bx, by = 48, H - 200
        d.rounded_rectangle([bx, by, bx + bw, by + 48], radius=24, fill=TEAL)
        d.text((bx + 18, by + 10), badge, font=fnt(26), fill=WHITE)

    footer(d, "Join free → barathx.com")
    return base


def text_card(*, kicker: str, lines: list[str], accent: str = "", cta: str = "Join free → barathx.com") -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    paste_logo(base, 120, ((W - 120) // 2, 320))
    d.text((W // 2 - 140, 480), "BarathX", font=fnt(56), fill=WHITE)
    d.text((80, 580), kicker.upper(), font=fnt(26), fill=SAFFRON)
    y = 640
    for i, line in enumerate(lines):
        size = 52 if i == 0 else 40
        for wl in wrap(d, line, fnt(size, i == 0), 920):
            d.text((80, y), wl, font=fnt(size, i == 0), fill=WHITE if i == 0 else CREAM)
            y += size + 14
        y += 10
    if accent:
        d.text((80, min(y + 40, 1200)), accent, font=fnt(34), fill=SAFFRON)
    footer(d, cta)
    return base


def encode(slides: list[tuple[str, Image.Image, float]], out_mp4: Path, poster: Path) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="bx-genz-reel-"))
    lines: list[str] = []
    for name, img, dur in slides:
        p = tmp / name
        img.save(p, quality=92)
        lines.append(f"file '{p}'\n")
        lines.append(f"duration {dur}\n")
    lines.append(f"file '{tmp / slides[-1][0]}'\n")
    list_path = tmp / "list.txt"
    list_path.write_text("".join(lines), encoding="utf-8")
    subprocess.check_call(
        [
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
            str(out_mp4),
        ]
    )
    slides[min(2, len(slides) - 1)][1].save(poster, quality=92)


def reel_a(out_dir: Path) -> Path:
    """Gen Z reel 1: take a side / It depends / no login wall."""
    slides = [
        (
            "a00.jpg",
            text_card(
                kicker="For Gen Z India",
                lines=[
                    "Tired of arguing in vanishing WhatsApp threads?",
                    "BarathX is the public square that keeps your take.",
                ],
                accent="Human takes only. No AI slop.",
            ),
            3.6,
        ),
        (
            "a01.jpg",
            overlay_phone(
                screen("landing-mobile.png"),
                kicker="New · Soft launch",
                title="India has opinions. Now it has a home.",
                sub="Pick a side. Meet your people.",
                badge="No login wall first",
            ),
            4.0,
        ),
        (
            "a02.jpg",
            overlay_phone(
                screen("landing-take-mobile.png"),
                kicker="Try it first",
                title="Agree. Disagree. It depends.",
                sub="Nuance is allowed. Binary fights optional.",
                badge="Safe first move",
            ),
            4.4,
        ),
        (
            "a03.jpg",
            overlay_phone(
                screen("square-mobile.png"),
                kicker="Then post",
                title="One sentence. Your reason.",
                sub="Sign up only when you reply, vote, or host.",
            ),
            3.8,
        ),
        (
            "a04.jpg",
            text_card(
                kicker="Your move",
                lines=["Take today’s side.", "Leave one honest take."],
                accent="barathx.com · soft launch",
                cta="Open barathx.com now",
            ),
            3.4,
        ),
    ]
    out = out_dir / "barathx-genz-reel-1-take-a-side.mp4"
    encode(slides, out, out_dir / "barathx-genz-reel-1-poster.jpg")
    slides[2][1].save(out_dir / "morning-shared.jpg", quality=92)
    slides[1][1].save(out_dir / "morning-linkedin.jpg", quality=92)
    return out


def reel_b(out_dir: Path) -> Path:
    """Gen Z reel 2: Home hub + live + Founding + human-first."""
    slides = [
        (
            "b00.jpg",
            text_card(
                kicker="Not another scroll app",
                lines=[
                    "Participation game.",
                    "Identity community.",
                    "Creator opportunity.",
                ],
                accent="BarathX · India’s conversation network",
            ),
            3.6,
        ),
        (
            "b01.jpg",
            overlay_phone(
                screen("home-hub-overview.png"),
                kicker="New · Home hub",
                title="Overview · Tagged · Following · My posts",
                sub="Your inbox, not feed chaos.",
                badge="Updated UI",
            ),
            4.0,
        ),
        (
            "b02.jpg",
            overlay_phone(
                screen("live-mobile.png"),
                kicker="Live rooms",
                title="Sided talk. Real context.",
                sub="Be the first voice — not ‘0 takes’ vibes.",
            ),
            3.8,
        ),
        (
            "b03.jpg",
            overlay_phone(
                screen("arenas-mobile.png"),
                kicker="Arenas → Circles next",
                title="Campus. City. Builders. Culture.",
                sub="Find your people, not just a national feed.",
            ),
            3.8,
        ),
        (
            "b04.jpg",
            text_card(
                kicker="Soft launch",
                lines=["Founding voices wanted.", "Feedback → next release."],
                accent="APK · barathx.com/get-app",
                cta="Join free → barathx.com",
            ),
            3.6,
        ),
    ]
    out = out_dir / "barathx-genz-reel-2-home-live.mp4"
    encode(slides, out, out_dir / "barathx-genz-reel-2-poster.jpg")
    slides[1][1].save(out_dir / "evening-shared.jpg", quality=92)
    slides[0][1].save(out_dir / "evening-whatsapp.jpg", quality=92)
    # Keep daily pack default name pointing at reel 1 for morning paste
    slides[2][1].save(out_dir / "barathx-daily-reel-poster.jpg", quality=92)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="2026-08-21")
    args = p.parse_args()
    out_dir = ROOT / "brand" / "social" / "daily" / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    a = reel_a(out_dir)
    b = reel_b(out_dir)
    # also alias reel 1 as daily default
    daily = out_dir / "barathx-daily-reel-20s.mp4"
    daily.write_bytes(a.read_bytes())
    print(f"wrote {a} ({a.stat().st_size})")
    print(f"wrote {b} ({b.stat().st_size})")
    print(f"alias {daily}")


if __name__ == "__main__":
    main()
