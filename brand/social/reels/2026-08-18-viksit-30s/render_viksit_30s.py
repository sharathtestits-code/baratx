#!/usr/bin/env python3
"""
BarathX ~30s vertical reel:
  1) Blocked-post beat (stylized — not a real PM deepfake)
  2) Viksit Bharat beat
  3) Product beats not overused in prior reels: Explore, Human-first, Soft launch

If you later drop a licensed PM news clip, splice it over frames 0–8s.
"""

from __future__ import annotations

import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
LIVE = ROOT / "brand/social/whatsapp/screens/live-2026-08-16"
LOGO = ROOT / "brand/baratx-logo-avatar.png"
OUT_DIR = ROOT / "brand/social/reels/2026-08-18-viksit-30s"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
GREEN = (19, 136, 8)
MUTED = (150, 150, 160)
RED = (220, 50, 50)
SLATE = (28, 30, 38)

bold = (
    glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
    or glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
)[0]
reg = (
    glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
    or glob.glob("/usr/share/fonts/**/LiberationSans-Regular.ttf", recursive=True)
    or [bold]
)[0]


def fnt(size: int, b: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(bold if b else reg, size)


def base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 8)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    d.rectangle([0, 0, W, 12], fill=SAFFRON)
    d.rectangle([0, 12, W, 16], fill=WHITE)
    d.rectangle([0, 16, W, 20], fill=GREEN)
    return img, d


def stamp(img: Image.Image, d: ImageDraw.ImageDraw, pill: str) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
    mask = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 63, 63], fill=255)
    circ = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    layer = img.convert("RGBA")
    layer.paste(circ, (40, 40), circ)
    d2 = ImageDraw.Draw(layer)
    d2.text((120, 52), "BarathX", font=fnt(36), fill=CREAM)
    bb = d2.textbbox((0, 0), pill, font=fnt(20))
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = W - 40 - tw - 28
    d2.rounded_rectangle([x0, 48, x0 + tw + 28, 48 + th + 16], radius=18, fill=SAFFRON)
    d2.text((x0 + 14, 56), pill, font=fnt(20), fill=DARK)
    img.paste(layer.convert("RGB"))


def footer(d: ImageDraw.ImageDraw, text: str) -> None:
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((40, H - 72), text, font=fnt(32), fill=DARK)


def phone(path: Path, height: int = 1100) -> Image.Image:
    ui = Image.open(path).convert("RGBA")
    scale = height / ui.height
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 14
    frame = Image.new("RGBA", (nw + pad * 2, nh + pad * 2), (28, 28, 34, 255))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=48, outline=SAFFRON, width=4)
    frame.paste(ui, (pad, pad), ui)
    return frame


def slide_blocked() -> Image.Image:
    img, d = base()
    stamp(img, d, "01 / 06")
    d = ImageDraw.Draw(img)
    d.text((48, 160), "ON OTHER APPS", font=fnt(26), fill=RED)
    d.text((48, 220), "A take goes up.", font=fnt(56), fill=WHITE)
    d.text((48, 300), "Then it vanishes.", font=fnt(56), fill=SAFFRON)

    # Fake feed card + blocked stamp (metaphor — not real PM footage)
    d.rounded_rectangle([80, 420, W - 80, 980], radius=28, fill=SLATE)
    d.ellipse([110, 460, 170, 520], fill=SAFFRON)
    d.text((190, 470), "Public figure · India", font=fnt(28), fill=CREAM)
    d.text((110, 560), "Building Viksit Bharat needs", font=fnt(34), fill=WHITE)
    d.text((110, 620), "honest debate — not silence.", font=fnt(34), fill=WHITE)
    d.text((110, 720), "2.4K likes · 890 replies", font=fnt(24, False), fill=MUTED)

    # BLOCKED overlay
    d.rounded_rectangle([180, 820, W - 180, 920], radius=20, fill=RED)
    d.text((260, 848), "⚠  POST BLOCKED / REMOVED", font=fnt(32), fill=WHITE)

    d.text((48, 1040), "If the feed can bury a take…", font=fnt(30, False), fill=MUTED)
    d.text((48, 1100), "where does India argue?", font=fnt(36), fill=CREAM)
    footer(d, "India needs a public square →")
    return img


def slide_viksit() -> Image.Image:
    img, d = base()
    stamp(img, d, "02 / 06")
    d = ImageDraw.Draw(img)
    d.text((48, 200), "NEXT SECOND", font=fnt(26), fill=SAFFRON)
    d.text((48, 280), "Viksit Bharat", font=fnt(72), fill=WHITE)
    d.text((48, 380), "is the ambition.", font=fnt(48), fill=SAFFRON)
    d.text((48, 500), "A developed India still needs", font=fnt(32, False), fill=MUTED)
    d.text((48, 560), "a place for human argument —", font=fnt(32, False), fill=MUTED)
    d.text((48, 620), "on the record.", font=fnt(36), fill=CREAM)

    chips = ["No vanished threads", "Sides you pick", "Human takes first"]
    y = 760
    for c in chips:
        d.rounded_rectangle([48, y, W - 48, y + 90], radius=18, fill=SLATE)
        d.text((80, y + 26), f"→  {c}", font=fnt(32), fill=CREAM)
        y += 110

    footer(d, "That’s why we built BarathX")
    return img


def slide_product(screen: str, kicker: str, title: str, sub: str, pill: str, cta: str) -> Image.Image:
    img, d = base()
    stamp(img, d, pill)
    d = ImageDraw.Draw(img)
    d.text((48, 150), kicker.upper(), font=fnt(24), fill=SAFFRON)
    d.text((48, 200), title, font=fnt(52), fill=WHITE)
    d.text((48, 280), sub, font=fnt(28, False), fill=MUTED)
    ph = phone(LIVE / screen, 1180)
    layer = img.convert("RGBA")
    layer.paste(ph, ((W - ph.width) // 2, 360), ph)
    d2 = ImageDraw.Draw(layer)
    footer(d2, cta)
    return layer.convert("RGB")


def slide_cta() -> Image.Image:
    img, d = base()
    stamp(img, d, "06 / 06")
    d = ImageDraw.Draw(img)
    d.text((48, 520), "Your move.", font=fnt(72), fill=WHITE)
    d.text((48, 640), "Leave one honest take", font=fnt(40), fill=SAFFRON)
    d.text((48, 720), "on India’s public square.", font=fnt(40), fill=CREAM)
    d.text((48, 860), "Soft launch open · browser now", font=fnt(28, False), fill=MUTED)
    d.text((48, 920), "Human first. No AI slop.", font=fnt(28, False), fill=MUTED)
    footer(d, "Join free → barathx.com")
    return img


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="bx-viksit-"))
    # ~30s total
    slides = [
        ("01-blocked.jpg", slide_blocked(), 5.0),
        ("02-viksit.jpg", slide_viksit(), 5.0),
        (
            "03-explore.jpg",
            slide_product(
                "explore-mobile.png",
                "New beat · Explore",
                "People or topics.",
                "Not a buried dump — find @user or India now.",
                "03 / 06",
                "Explore → barathx.com",
            ),
            5.5,
        ),
        (
            "04-human.jpg",
            slide_product(
                "home-mobile.png",
                "New beat · Human-first",
                "AI drafts sink.",
                "Real takes rise. No AI slop in the square.",
                "04 / 06",
                "Human takes only → barathx.com",
            ),
            5.5,
        ),
        (
            "05-square.jpg",
            slide_product(
                "square-mobile.png",
                "On the record",
                "Drop a take.",
                "Square · Arenas · Live — argue it live.",
                "05 / 06",
                "Open Square → barathx.com",
            ),
            5.0,
        ),
        ("06-cta.jpg", slide_cta(), 4.0),
    ]
    # 5+5+5.5+5.5+5+4 = 30.0s

    lines = []
    for name, im, dur in slides:
        path = tmp / name
        im.save(path, quality=92)
        lines.append(f"file '{path}'\n")
        lines.append(f"duration {dur}\n")
    lines.append(f"file '{tmp / slides[-1][0]}'\n")
    list_path = tmp / "list.txt"
    list_path.write_text("".join(lines), encoding="utf-8")

    out = OUT_DIR / "barathx-viksit-bharat-30s.mp4"
    cmd = [
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
        "-t",
        "30",
        str(out),
    ]
    subprocess.check_call(cmd)
    slides[0][1].save(OUT_DIR / "poster.jpg", quality=92)
    (OUT_DIR / "CAPTION.md").write_text(
        """# Viksit Bharat · 30s reel

**File:** `barathx-viksit-bharat-30s.mp4` (9:16 · ~30s)

## Beats
1. Blocked / removed take (stylized — not a deepfake PM clip)
2. Viksit Bharat → India needs a public square
3. Explore (people + topics) — underused in prior reels
4. Human-first / no AI slop — underused
5. Square on the record
6. CTA → barathx.com

## Note
If you have a **licensed** news clip of a blocked post + PM saying “Viksit Bharat”, drop the file in this folder and ask to splice it over seconds 0–8.

## Caption
```
Other apps can bury a take in a second.
Viksit Bharat still needs a place to argue — on the record.

BarathX = India’s public square.
Explore · Human-first · Square · Arenas · Live.
No AI slop.

→ https://barathx.com

IG https://www.instagram.com/getbaratx/
WA https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o
X https://x.com/getbaratx

#BarathX #ViksitBharat #India #PublicSquare #NoAISlop
```
""",
        encoding="utf-8",
    )
    print("wrote", out, out.stat().st_size)


if __name__ == "__main__":
    main()
