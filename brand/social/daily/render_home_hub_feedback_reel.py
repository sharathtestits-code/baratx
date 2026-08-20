#!/usr/bin/env python3
"""~22s 9:16 reel: Home hub UI + why BarathX + feedback to 1000 users."""

from __future__ import annotations

import argparse
import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-19"
HUB = ROOT / "brand" / "product" / "home-hub-v2"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1920
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)
GREEN = (34, 139, 90)


def _font_paths() -> tuple[str, str]:
    bold = (
        glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
    )
    regular = (
        glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/LiberationSans-Regular.ttf", recursive=True)
        or bold
    )
    if not bold:
        raise SystemExit("No usable Bold TTF found under /usr/share/fonts")
    return bold[0], regular[0]


FONT_B, FONT_R = _font_paths()


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def _paste_logo(base: Image.Image, size: int, xy: tuple[int, int]) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, xy, circ)


def _footer(d: ImageDraw.ImageDraw, label: str) -> None:
    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((48, H - 72), label, font=fnt(34), fill=DARK)


def _wrap(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
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


def title_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    _paste_logo(base, 140, ((W - 140) // 2, 380))
    d.text((W // 2 - 150, 560), "BarathX", font=fnt(64), fill=WHITE)
    d.text((90, 680), "India’s public square", font=fnt(40), fill=SAFFRON)
    d.text((90, 780), "New Home hub", font=fnt(52), fill=CREAM)
    d.text((90, 880), "Overview · Tagged · Following · My posts", font=fnt(28, False), fill=MUTED)
    d.text((90, 1000), "Built with early users in mind.", font=fnt(32, False), fill=MUTED)
    _footer(d, "Soft launch → barathx.com/get-app")
    return base


def why_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    _paste_logo(base, 72, (48, 48))
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)
    d.text((48, 180), "WHY BARATHX", font=fnt(26), fill=SAFFRON)
    lines = [
        "A place for India to talk",
        "in public — human takes,",
        "real sides, no AI slop.",
    ]
    y = 280
    for line in lines:
        d.text((48, y), line, font=fnt(48), fill=WHITE)
        y += 78
    d.text((48, 560), "Square. Arenas. Live.", font=fnt(36), fill=SAFFRON)
    d.text((48, 660), "Your voice stays on the record.", font=fnt(32, False), fill=MUTED)
    _footer(d, "Join free → barathx.com")
    return base


def frame_ui(path: Path, *, kicker: str, title: str, sub: str = "") -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 14], fill=SAFFRON)
    _paste_logo(base, 72, (48, 48))
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)
    d.text((48, 150), kicker.upper(), font=fnt(26), fill=SAFFRON)
    d.text((48, 200), title[:34], font=fnt(48), fill=WHITE)
    if sub:
        d.text((48, 270), sub[:52], font=fnt(26, False), fill=MUTED)

    ui = Image.open(path).convert("RGB")
    max_h, max_w = 1180, 700
    scale = min(max_w / ui.width, max_h / ui.height)
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 14
    frame_w, frame_h = nw + pad * 2, nh + pad * 2
    frame = Image.new("RGB", (frame_w, frame_h), (28, 28, 34))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame_w - 1, frame_h - 1], radius=48, outline=SAFFRON, width=4)
    frame.paste(ui, (pad, pad))
    base.paste(frame, ((W - frame_w) // 2, 340 if sub else 320))
    _footer(d, "Join free → barathx.com")
    return base


def feedback_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    _paste_logo(base, 72, (48, 48))
    d.text((140, 62), "BarathX", font=fnt(40), fill=CREAM)
    d.text((48, 180), "SOFT LAUNCH", font=fnt(26), fill=SAFFRON)
    d.text((48, 250), "We’re here for", font=fnt(44), fill=WHITE)
    d.text((48, 320), "your feedback.", font=fnt(52), fill=CREAM)

    bullets = [
        ("Up to 1,000 early users", "Tell us what breaks / what helps"),
        ("We ship changes fast", "Your notes → next release"),
        ("Home hub is one example", "Tabs from real early use"),
    ]
    y = 460
    for title, detail in bullets:
        d.ellipse([48, y + 10, 68, y + 30], fill=GREEN)
        d.text((90, y), title, font=fnt(34), fill=WHITE)
        d.text((90, y + 48), detail, font=fnt(26, False), fill=MUTED)
        y += 130

    _footer(d, "Feedback → next release")
    return base


def cta_card() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 18], fill=SAFFRON)
    d.text((80, 560), "Your move.", font=fnt(72), fill=WHITE)
    for i, line in enumerate(
        _wrap(d, "Join soft launch. Leave one honest take. Tell us what to fix.", fnt(36, False), 900)
    ):
        d.text((80, 700 + i * 52), line, font=fnt(36, False), fill=MUTED)
    d.text((80, 920), "Feedback → next release", font=fnt(40), fill=SAFFRON)
    d.text((80, 1020), "Up to 1,000 early voices.", font=fnt(32, False), fill=MUTED)
    _footer(d, "Open barathx.com/get-app")
    return base


def build_reel(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="bx-home-hub-reel-"))

    overview = HUB / "home-hub-mobile-overview-mockup.png"
    tagged = HUB / "home-hub-mobile-tagged-tab-mockup.png"
    live_home = LIVE / "home-mobile.png"
    if not overview.exists():
        overview = live_home
    if not tagged.exists():
        tagged = live_home

    slides = [
        ("00-title.jpg", title_card(), 3.0),
        ("01-why.jpg", why_card(), 3.2),
        (
            "02-overview.jpg",
            frame_ui(
                overview,
                kicker="New · Home hub",
                title="Overview stays calm",
                sub="2–3 previews · See all → full tab",
            ),
            3.4,
        ),
        (
            "03-tagged.jpg",
            frame_ui(
                tagged,
                kicker="Tagged · Following · Mine",
                title="Inbox, not noise",
                sub="Mentions get their own tab",
            ),
            3.2,
        ),
        ("04-feedback.jpg", feedback_card(), 4.2),
        ("05-cta.jpg", cta_card(), 3.0),
    ]

    concat_lines: list[str] = []
    for name, img, dur in slides:
        path = tmp / name
        img.save(path, quality=92)
        concat_lines.append(f"file '{path}'\n")
        concat_lines.append(f"duration {dur}\n")
    concat_lines.append(f"file '{tmp / slides[-1][0]}'\n")
    list_path = tmp / "list.txt"
    list_path.write_text("".join(concat_lines), encoding="utf-8")

    out_mp4 = out_dir / "barathx-daily-reel-20s.mp4"
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
        str(out_mp4),
    ]
    subprocess.check_call(cmd)
    slides[2][1].save(out_dir / "barathx-daily-reel-poster.jpg", quality=92)
    # Still frames for morning/evening packs
    slides[2][1].save(out_dir / "morning-shared.jpg", quality=92)
    slides[3][1].save(out_dir / "morning-linkedin.jpg", quality=92)
    slides[4][1].save(out_dir / "evening-shared.jpg", quality=92)
    slides[1][1].save(out_dir / "evening-whatsapp.jpg", quality=92)
    return out_mp4


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default="2026-08-20")
    args = p.parse_args()
    out_dir = ROOT / "brand" / "social" / "daily" / args.date
    out = build_reel(out_dir)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    print(f"poster {out_dir / 'barathx-daily-reel-poster.jpg'}")


if __name__ == "__main__":
    main()
