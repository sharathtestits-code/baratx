#!/usr/bin/env python3
"""BarathX Part 2 — Arenas · 25.0s · 9:16

Script: WhatsApp-group hook → pick a side → real opinions → not a group chat.
Layout: ~35% avatar panel (HeyGen drop-in zone) + ~65% live Arenas UI.
"""

from __future__ import annotations

import glob
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[5]  # …/PART-02-arenas → workspace
OUT_DIR = (
    ROOT
    / "brand"
    / "social"
    / "instagram"
    / "demo-series"
    / "PART-02-arenas"
)
SCREENS = OUT_DIR / "screens"
DAILY = ROOT / "brand" / "social" / "daily" / "2026-08-28"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"
DOWNLOADS = Path("/opt/cursor/artifacts/downloads")
SHOTS = Path("/opt/cursor/artifacts/screenshots")

W, H = 1080, 1920
FPS = 30
DARK = (10, 10, 14)
PANEL = (16, 16, 22)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 153, 51)
MUTED = (155, 158, 170)
GREEN = (34, 160, 90)

# Exact 25.0s
# beat: kind, duration, cover, avatar_line, screen, ui_kicker
BEATS = [
    ("hook", 3.0, "WHY ARGUE IN A\nWHATSAPP GROUP? 👀", "Why argue in a WhatsApp group when you can actually pick a side?", "01-arenas-list.png", ""),
    ("split", 4.0, "PICK YOUR BATTLE.", "On BarathX, find a topic and pick your side.", "13-topics-row.png", "Arenas"),
    ("split", 4.0, "YOUR TAKE. YOUR SIDE.", "Agree. Disagree. Or… it depends.", "15-agree-disagree-depends.png", "Pick a side"),
    ("ui_focus", 6.0, "REAL PEOPLE.\nREAL OPINIONS.", "Then see what real people actually think.", "17-conversation.png", "Conversation"),
    ("split", 4.0, "NOT ANOTHER\nGROUP CHAT.", "It's not another group chat.\nIt's a public conversation.", "01-arenas-list.png", "Arenas"),
    ("end", 4.0, "", "", "", ""),
]
# 3+4+4+6+4+4 = 25.0


def _fonts() -> tuple[str, str]:
    bold = (
        glob.glob("/usr/share/fonts/**/*Inter*Bold*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
    )
    regular = (
        glob.glob("/usr/share/fonts/**/*Inter-Regular*.ttf", recursive=True)
        or glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True)
        or bold
    )
    if not bold:
        raise SystemExit("No Bold TTF")
    return bold[0], regular[0]


FONT_B, FONT_R = _fonts()


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def paste_logo(base: Image.Image, size: int, xy: tuple[int, int]) -> None:
    if not LOGO.exists():
        return
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    circ = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, xy, circ)


def wrap(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.replace("\n", " \n ").split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if w == "\n":
            if cur:
                lines.append(cur)
            cur = ""
            continue
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


def cover_fit(im: Image.Image, tw: int, th: int) -> Image.Image:
    im = im.convert("RGB")
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = max((nh - th) // 2 - 40, 0)  # bias up for UI chrome
    return im.crop((left, top, left + tw, top + th))


def draw_avatar_panel(
    base: Image.Image,
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    line: str,
    show_brand: bool,
) -> None:
    """HeyGen drop-in zone (~35%). Usable now with burn-in dialogue."""
    d = ImageDraw.Draw(base)
    d.rectangle([x, y, x + w, y + h], fill=PANEL)
    d.line([x + w - 1, y, x + w - 1, y + h], fill=(40, 40, 48), width=2)

    # Avatar circle placeholder
    cx, cy, r = x + w // 2, y + int(h * 0.28), 92
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(28, 28, 36), outline=SAFFRON, width=4)
    if show_brand:
        paste_logo(base, 120, (cx - 60, cy - 60))
    else:
        d.text((cx - 28, cy - 18), "YOU", font=fnt(28), fill=MUTED)

    d.text((x + 24, cy + r + 24), "HeyGen avatar zone", font=fnt(18, False), fill=(90, 92, 105))
    # Spoken line
    ty = cy + r + 60
    for ln in wrap(d, line, fnt(28), w - 48)[:6]:
        d.text((x + 24, ty), ln, font=fnt(28), fill=CREAM)
        ty += 36


def draw_cover_banner(base: Image.Image, text: str, y: int = 48) -> None:
    if not text:
        return
    d = ImageDraw.Draw(base)
    lines = text.split("\n")
    # dark veil behind cover text
    band_h = 40 + 58 * len(lines)
    overlay = Image.new("RGBA", (W, band_h + 20), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 0, W, band_h + 20], fill=(8, 8, 12, 200))
    base.paste(overlay, (0, y - 16), overlay)
    yy = y
    for ln in lines:
        font = fnt(46)
        tw = d.textlength(ln, font=font)
        d.text(((W - tw) / 2, yy), ln, font=font, fill=WHITE)
        yy += 58


def frame_split(
    *,
    screen: Path,
    cover: str,
    avatar_line: str,
    ui_kicker: str,
    show_brand: bool,
    avatar_ratio: float = 0.35,
) -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 10], fill=SAFFRON)

    left_w = int(W * avatar_ratio)
    right_w = W - left_w
    top = 130
    bottom_bar = 110
    panel_h = H - top - bottom_bar

    draw_avatar_panel(base, x=0, y=top, w=left_w, h=panel_h, line=avatar_line, show_brand=show_brand)

    ui = cover_fit(Image.open(screen), right_w - 24, panel_h - 24)
    # phone frame
    fx, fy = left_w + 12, top + 12
    d.rounded_rectangle([fx - 4, fy - 4, fx + ui.width + 4, fy + ui.height + 4], radius=28, outline=SAFFRON, width=3)
    base.paste(ui, (fx, fy))

    if ui_kicker:
        d.text((left_w + 24, top - 36), ui_kicker.upper(), font=fnt(22), fill=SAFFRON)

    draw_cover_banner(base, cover, y=36)

    # bottom caption bar
    d.rectangle([0, H - bottom_bar, W, H], fill=SAFFRON)
    d.text((36, H - 72), "BarathX · India’s public square", font=fnt(30), fill=DARK)
    return base


def frame_ui_focus(*, screen: Path, cover: str, avatar_line: str) -> Image.Image:
    """Avatar shrinks — UI dominates (~15% strip + big UI)."""
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 10], fill=SAFFRON)
    draw_cover_banner(base, cover, y=40)

    # small avatar chip
    paste_logo(base, 72, (36, 200))
    for i, ln in enumerate(wrap(d, avatar_line, fnt(26, False), 900)[:2]):
        d.text((128, 210 + i * 34), ln, font=fnt(26, False), fill=MUTED)

    ui = cover_fit(Image.open(screen), 720, 1180)
    fx = (W - ui.width) // 2
    fy = 300
    d.rounded_rectangle([fx - 6, fy - 6, fx + ui.width + 6, fy + ui.height + 6], radius=36, outline=SAFFRON, width=4)
    base.paste(ui, (fx, fy))

    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((36, H - 72), "Real people. Real opinions.", font=fnt(30), fill=DARK)
    return base


def frame_hook(*, screen: Path, cover: str, avatar_line: str) -> Image.Image:
    """First 3s: no BarathX logo wordmark — question first, Arenas UI already visible."""
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    left_w = int(W * 0.38)
    top = 160
    panel_h = H - top - 110

    # avatar zone WITHOUT brand logo
    draw_avatar_panel(base, x=0, y=top, w=left_w, h=panel_h, line=avatar_line, show_brand=False)

    ui = cover_fit(Image.open(screen), W - left_w - 24, panel_h - 24)
    fx, fy = left_w + 12, top + 12
    d.rounded_rectangle([fx - 4, fy - 4, fx + ui.width + 4, fy + ui.height + 4], radius=28, outline=(60, 60, 70), width=3)
    base.paste(ui, (fx, fy))

    draw_cover_banner(base, cover, y=48)
    d.rectangle([0, H - 110, W, H], fill=(28, 28, 34))
    d.text((36, H - 72), "Pick a side. Jump in.", font=fnt(30), fill=CREAM)
    return base


def frame_end() -> Image.Image:
    base = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, W, 14], fill=SAFFRON)
    paste_logo(base, 140, ((W - 140) // 2, 280))
    d.text((W // 2 - 150, 460), "BarathX", font=fnt(56), fill=WHITE)
    d.text((W // 2 - 240, 540), "India’s public square", font=fnt(32), fill=SAFFRON)

    d.text((80, 680), "PART 2 — ARENAS  ✓", font=fnt(40), fill=CREAM)
    d.text((80, 760), "NEXT → YOU", font=fnt(52), fill=SAFFRON)
    d.text((80, 850), "Put your name behind your take.", font=fnt(30, False), fill=MUTED)
    d.text((80, 980), "Follow @getbaratx", font=fnt(40), fill=WHITE)

    d.rectangle([0, H - 110, W, H], fill=SAFFRON)
    d.text((36, H - 72), "barathx.com", font=fnt(32), fill=DARK)
    return base


def jpg_clip(img: Image.Image, path: Path, duration: float) -> Path:
    img.save(path, quality=93)
    out = path.with_suffix(".mp4")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(path),
            "-t", f"{duration:.3f}", "-r", str(FPS),
            "-vf", f"scale={W}:{H},format=yuv420p",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def concat(clips: list[Path], out: Path, tmp: Path) -> None:
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)

    total = sum(b[1] for b in BEATS)
    if abs(total - 25.0) > 0.01:
        raise SystemExit(f"Beats must sum to 25s, got {total}")

    with tempfile.TemporaryDirectory(prefix="bx-p2-") as td:
        tmp = Path(td)
        clips: list[Path] = []
        for i, (kind, dur, cover, line, screen, kicker) in enumerate(BEATS):
            if kind == "end":
                img = frame_end()
            else:
                path = SCREENS / screen
                if not path.exists():
                    raise SystemExit(f"Missing screen {path}")
                if kind == "hook":
                    img = frame_hook(screen=path, cover=cover, avatar_line=line)
                elif kind == "ui_focus":
                    img = frame_ui_focus(screen=path, cover=cover, avatar_line=line)
                else:
                    img = frame_split(
                        screen=path,
                        cover=cover,
                        avatar_line=line,
                        ui_kicker=kicker,
                        show_brand=True,
                    )
            clips.append(jpg_clip(img, tmp / f"{i:02d}.jpg", dur))

        out = OUT_DIR / "barathx-PART2-arenas-25s.mp4"
        concat(clips, out, tmp)
        poster = OUT_DIR / "barathx-PART2-arenas-25s-poster.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", "1.0", "-i", str(out), "-frames:v", "1", "-q:v", "2", str(poster)],
            check=True,
            capture_output=True,
        )

        for folder in (DAILY, OUT_DIR):
            (folder / "barathx-PART2-arenas-25s.mp4").write_bytes(out.read_bytes()) if folder != OUT_DIR else None
        (DAILY / "barathx-PART2-arenas-25s.mp4").write_bytes(out.read_bytes())
        (DAILY / "barathx-PART2-arenas-25s-poster.jpg").write_bytes(poster.read_bytes())
        (DOWNLOADS / "BarathX-Part2-Arenas-25s.mp4").write_bytes(out.read_bytes())
        (DOWNLOADS / "barathx-PART2-arenas-25s-LATEST.mp4").write_bytes(out.read_bytes())
        (SHOTS / "barathx-part2-arenas-poster.jpg").write_bytes(poster.read_bytes())

        dur = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(out)],
            text=True,
        ).strip()
        print(f"Wrote {out} ({dur}s)")
        print(f"Download: {DOWNLOADS / 'BarathX-Part2-Arenas-25s.mp4'}")


if __name__ == "__main__":
    main()
