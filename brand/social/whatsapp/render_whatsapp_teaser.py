#!/usr/bin/env python3
"""
BarathX WhatsApp-group marketing teaser.

Research-backed constraints (2026):
- Vertical 9:16, ~15–30s (works in groups + Status)
- MP4 H.264, keep under ~16MB for easy share
- Burned-in captions (most people watch muted)
- One clear CTA at the end
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "brand" / "social" / "whatsapp"
SCREENS_DIR = OUT_DIR / "screens"
LOGO_PATH = ROOT / "brand" / "baratx-logo-avatar.png"

# 720p vertical — smaller file for WhatsApp groups while still sharp on phones
W, H = 720, 1280
FPS = 24
DURATION_S = 24
N_FRAMES = FPS * DURATION_S

SAFFRON = (255, 153, 51)
CREAM = (255, 248, 235)
DARK = (8, 10, 14)
GREEN = (19, 136, 8)

FONT_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_SANS_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"

# Real website / in-app page stills behind each beat
SCENE_SCREEN = {
    "hook": "bx-site-landing.png",
    "brand": "bx-site-landing.png",
    "square": "bx-site-square-raw.jpg",
    "arenas": "bx-site-arenas.jpg",
    "live": "bx-site-live.jpg",
    "promise": "bx-site-home.jpg",
    "cta": "bx-site-signup.png",
}

_SCREEN_CACHE: dict[str, Image.Image] = {}


def cover_resize(img: Image.Image, tw: int, th: int) -> Image.Image:
    """Scale+crop to fill target (object-fit: cover)."""
    img = img.convert("RGB")
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def load_screen(name: str) -> Image.Image:
    if name in _SCREEN_CACHE:
        return _SCREEN_CACHE[name]
    path = SCREENS_DIR / name
    if not path.exists():
        # Fallback solid if missing
        img = Image.new("RGB", (W, H), DARK)
    else:
        # Oversize base for Ken Burns zoom room
        img = cover_resize(Image.open(path), int(W * 1.18), int(H * 1.18))
    _SCREEN_CACHE[name] = img
    return img


def ken_burns(base: Image.Image, local: float, t: float) -> Image.Image:
    """Slow zoom + pan across website screenshot."""
    bw, bh = base.size
    zoom = 1.0 + 0.08 * local + 0.02 * math.sin(t * 0.6)
    cw, ch = int(W * zoom), int(H * zoom)
    cw = min(cw, bw)
    ch = min(ch, bh)
    # Drift
    max_x = max(bw - cw, 1)
    max_y = max(bh - ch, 1)
    x = int(max_x * (0.15 + 0.7 * local))
    y = int(max_y * (0.2 + 0.35 * math.sin(local * math.pi)))
    crop = base.crop((x, y, x + cw, y + ch)).resize((W, H), Image.Resampling.LANCZOS)
    return crop


def make_bg(t: float, kind: str, local: float = 0.0) -> Image.Image:
    """Website page screenshot background with readable dark veil."""
    screen_name = SCENE_SCREEN.get(kind, "bx-site-landing.png")
    base = load_screen(screen_name)
    frame = ken_burns(base, local, t)

    # Soften busy UI slightly so captions pop
    if kind in ("square", "arenas", "live", "promise", "cta"):
        frame = frame.filter(ImageFilter.GaussianBlur(radius=1.1))
    else:
        frame = frame.filter(ImageFilter.GaussianBlur(radius=1.6))

    frame = ImageEnhance.Brightness(frame).enhance(0.72 if kind == "hook" else 0.82)
    frame = ImageEnhance.Contrast(frame).enhance(1.08)

    # Gradient veil — keep center UI visible, darken for text
    rgba = frame.convert("RGBA")
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for y in range(H):
        # Stronger top/bottom for captions; lighter mid so page UI shows
        top = max(0, int(170 * (1 - y / (H * 0.28))))
        bot = max(0, int(190 * max(0, (y - H * 0.55) / (H * 0.45))))
        mid = 55 if kind in ("square", "arenas", "live", "home", "promise") else 85
        a = min(210, top + bot + mid)
        vd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    # Saffron edge accent
    vd.rectangle([0, 0, 6, H], fill=(*SAFFRON, 160))
    out = Image.alpha_composite(rgba, veil).convert("RGB")
    return out


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill=(255, 255, 255, 255),
    stroke=(0, 0, 0, 220),
    stroke_w: int = 4,
) -> None:
    draw.text(xy, text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)


def wrap_lines(draw, text: str, fnt, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        tw, _ = text_size(draw, trial, fnt)
        if tw <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def load_logo(size: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 210), width=3)
    return Image.alpha_composite(out, ring)


def scene_at(t: float) -> dict:
    """Timed beats for WhatsApp muted viewing."""
    beats = [
        (0.0, 3.2, "hook", "Your WhatsApp takes\ndisappear by Monday."),
        (3.2, 6.2, "brand", "BarathX\nIndia’s public square"),
        (6.2, 10.0, "square", "Square\nDrop a short take.\nGet a real reply."),
        (10.0, 14.0, "arenas", "Arenas\nPick a side.\nAgree vs Disagree."),
        (14.0, 17.5, "live", "Live\nArgue it live.\nUp to 15 voices."),
        (17.5, 20.2, "promise", "Human takes only.\nNo AI slop."),
        (20.2, 24.0, "cta", "Leave one honest take\nhttps://barathx.com"),
    ]
    for start, end, kind, copy in beats:
        if start <= t < end:
            local = (t - start) / max(end - start, 0.01)
            return {"kind": kind, "copy": copy, "local": local, "start": start, "end": end}
    kind, copy = beats[-1][2], beats[-1][3]
    return {"kind": kind, "copy": copy, "local": 1.0, "start": beats[-1][0], "end": beats[-1][1]}


def pill(draw, text, fnt, y, fill=SAFFRON):
    tw, th = text_size(draw, text, fnt)
    pad_x, pad_y = 28, 14
    x0 = (W - tw) // 2 - pad_x
    y0 = y - pad_y // 2
    x1 = (W + tw) // 2 + pad_x
    y1 = y + th + pad_y // 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=(*fill, 245))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=28, outline=(255, 255, 255, 200), width=2)
    draw_text(draw, ((W - tw) // 2, y), text, fnt, fill=(255, 255, 255, 255), stroke_w=2)
    return y1


def compose(frame_bg: Image.Image, logo: Image.Image, scene: dict, t: float) -> Image.Image:
    base = frame_bg.convert("RGBA")
    # Darken edges for text safety
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for y in range(H):
        a = 0
        if y < H * 0.12:
            a = int(140 * (1 - y / (H * 0.12)))
        if y > H * 0.78:
            a = max(a, int(160 * ((y - H * 0.78) / (H * 0.22))))
        if a:
            vd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    base = Image.alpha_composite(base, veil)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    kind = scene["kind"]
    local = scene["local"]
    fade = min(1.0, local * 4.0) if local < 0.85 else max(0.55, 1.0 - (local - 0.85) / 0.15)

    # Top brand chip — skip on product UI pages (logo already in screenshot)
    if kind not in ("hook", "square", "arenas", "live", "promise"):
        lx = (W - logo.width) // 2
        ly = 48
        layer.paste(logo, (lx, ly), logo)
        f_small = font(FONT_SANS, 28)
        brand = "BarathX"
        bw, _ = text_size(draw, brand, f_small)
        draw_text(draw, ((W - bw) // 2, ly + logo.height + 8), brand, f_small, fill=(*CREAM, 255), stroke_w=3)

    lines = scene["copy"].split("\n")
    if kind == "hook":
        f_main = font(FONT_SANS, 54)
        y = int(H * 0.38)
        for i, line in enumerate(lines):
            tw, th = text_size(draw, line, f_main)
            draw_text(draw, ((W - tw) // 2, y), line, f_main, fill=(255, 255, 255, 255), stroke_w=5)
            y += th + 14
        f_sub = font(FONT_SANS_REG, 30)
        sub = "Then the group moves on."
        sw, _ = text_size(draw, sub, f_sub)
        draw_text(draw, ((W - sw) // 2, y + 28), sub, f_sub, fill=(255, 200, 150, 255), stroke_w=3)

    elif kind == "brand":
        f_tag = font(FONT_SERIF, 48)
        y = int(H * 0.42)
        for line in lines[1:]:  # skip brand name (logo shows it)
            tw, th = text_size(draw, line, f_tag)
            draw_text(draw, ((W - tw) // 2, y), line, f_tag, fill=(255, 214, 140, 255), stroke_w=4)
            y += th + 12
        f_line = font(FONT_SANS, 36)
        wedge = "Pick a side. Argue it live."
        ww, _ = text_size(draw, wedge, f_line)
        draw_text(draw, ((W - ww) // 2, y + 36), wedge, f_line, fill=(255, 255, 255, 255), stroke_w=4)

    elif kind in ("square", "arenas", "live"):
        # Bottom caption plate — leave most of the website UI visible above
        title, *rest = lines
        plate_h = 210
        plate_top = H - plate_h - 52
        draw.rounded_rectangle(
            [24, plate_top, W - 24, H - 44],
            radius=24,
            fill=(8, 10, 14, 210),
        )
        draw.rounded_rectangle(
            [24, plate_top, W - 24, H - 44],
            radius=24,
            outline=(*SAFFRON, 200),
            width=2,
        )
        f_title = font(FONT_SANS, 48)
        tw, th = text_size(draw, title, f_title)
        y = plate_top + 22
        draw_text(draw, ((W - tw) // 2, y), title, f_title, fill=(*SAFFRON, 255), stroke_w=3)
        y += th + 10
        f_body = font(FONT_SANS, 32)
        for line in rest:
            bw, bh = text_size(draw, line, f_body)
            draw_text(draw, ((W - bw) // 2, y), line, f_body, fill=(*CREAM, 255), stroke_w=3)
            y += bh + 8
        chips = {
            "square": ["For you", "Following", "Real replies"],
            "arenas": ["Sports", "Politics", "Startups"],
            "live": ["Debate", "Audio", "15 seats"],
        }[kind]
        f_chip = font(FONT_SANS, 22)
        chip_y = y + 8
        gap = 10
        widths = [text_size(draw, c, f_chip)[0] + 28 for c in chips]
        total = sum(widths) + gap * (len(chips) - 1)
        x = (W - total) // 2
        for c, cw in zip(chips, widths):
            draw.rounded_rectangle([x, chip_y, x + cw, chip_y + 36], radius=18, fill=(255, 255, 255, 24))
            draw.rounded_rectangle([x, chip_y, x + cw, chip_y + 36], radius=18, outline=(*SAFFRON, 180), width=2)
            ctw, cth = text_size(draw, c, f_chip)
            draw_text(
                draw,
                (x + (cw - ctw) // 2, chip_y + (36 - cth) // 2),
                c,
                f_chip,
                fill=(255, 255, 255, 255),
                stroke_w=2,
            )
            x += cw + gap

    elif kind == "promise":
        f_main = font(FONT_SANS, 48)
        y = int(H * 0.40)
        for line in lines:
            tw, th = text_size(draw, line, f_main)
            draw_text(draw, ((W - tw) // 2, y), line, f_main, fill=(255, 220, 120, 255), stroke_w=5)
            y += th + 18
        f_sub = font(FONT_SANS_REG, 30)
        sub = "Arguments that stay on the record."
        sw, _ = text_size(draw, sub, f_sub)
        draw_text(draw, ((W - sw) // 2, y + 24), sub, f_sub, fill=(*CREAM, 230), stroke_w=3)

    elif kind == "cta":
        f_cta = font(FONT_SANS, 42)
        line1 = "Leave one honest take"
        tw, th = text_size(draw, line1, f_cta)
        y = int(H * 0.40)
        draw_text(draw, ((W - tw) // 2, y), line1, f_cta, fill=(255, 255, 255, 255), stroke_w=4)
        f_url = font(FONT_SANS, 36)
        url = "https://barathx.com"
        pill(draw, url, f_url, y + th + 36)
        f_soon = font(FONT_SANS, 28)
        soon = "Browser soft launch · Apps coming soon"
        sw, _ = text_size(draw, soon, f_soon)
        draw_text(draw, ((W - sw) // 2, y + th + 120), soon, f_soon, fill=(*CREAM, 240), stroke_w=3)
        f_found = font(FONT_SANS_REG, 24)
        found = "100 Founding spots — earned by real debate"
        fw, _ = text_size(draw, found, f_found)
        draw_text(draw, ((W - fw) // 2, y + th + 168), found, f_found, fill=(255, 200, 140, 230), stroke_w=2)

    # Progress dots
    labels = ["hook", "brand", "square", "arenas", "live", "promise", "cta"]
    idx = labels.index(kind) if kind in labels else 0
    dot_y = H - 36
    total_w = len(labels) * 18
    dx = (W - total_w) // 2
    for i in range(len(labels)):
        r = 5
        color = (*SAFFRON, 255) if i <= idx else (255, 255, 255, 70)
        draw.ellipse([dx + i * 18, dot_y, dx + i * 18 + r * 2, dot_y + r * 2], fill=color)

    if fade < 1:
        r, g, b, a = layer.split()
        a = a.point(lambda p: int(p * fade))
        layer = Image.merge("RGBA", (r, g, b, a))

    return Image.alpha_composite(base, layer).convert("RGB")


def encode(frame_dir: Path, out_path: Path, crf: str = "23") -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frame_dir / "frame_%04d.jpg"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-profile:v",
            "main",
            "-crf",
            crf,
            "-movflags",
            "+faststart",
            "-an",
            str(out_path),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logo = load_logo(120)
    logo_big = load_logo(160)

    with tempfile.TemporaryDirectory(prefix="bx-wa-") as tmp:
        tmp_path = Path(tmp)
        print(f"Rendering {N_FRAMES} frames @ {FPS}fps (WhatsApp teaser)…")
        for i in range(N_FRAMES):
            t = i / FPS
            scene = scene_at(t)
            bg = make_bg(t, scene["kind"], scene["local"])
            use_logo = logo_big if scene["kind"] == "brand" else logo
            if scene["kind"] == "brand":
                frame = compose(bg, logo_big, scene, t)
            else:
                frame = compose(bg, use_logo, scene, t)
            frame = ImageEnhance.Contrast(frame).enhance(1.06)
            frame.save(tmp_path / f"frame_{i:04d}.jpg", quality=88, optimize=True)
            if i % 24 == 0:
                print(f"  {i}/{N_FRAMES}")

        out = OUT_DIR / "barathx-whatsapp-teaser.mp4"
        poster = OUT_DIR / "barathx-whatsapp-teaser-poster.jpg"
        print("Encoding…")
        encode(tmp_path, out, crf="22")
        # Poster from CTA beat
        mid = Image.open(tmp_path / f"frame_{int(21.2 * FPS):04d}.jpg")
        mid.save(poster, quality=90, optimize=True)

        # Square crop for groups that prefer 1:1
        square = OUT_DIR / "barathx-whatsapp-teaser-square.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(out),
                "-vf",
                "crop=720:720:0:280",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "22",
                "-movflags",
                "+faststart",
                "-an",
                str(square),
            ],
            check=True,
            capture_output=True,
        )

    for p in (out, square, poster):
        mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.relative_to(ROOT)}  ({mb:.1f} MB)")


if __name__ == "__main__":
    main()
