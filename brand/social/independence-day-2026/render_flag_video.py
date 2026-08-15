#!/usr/bin/env python3
"""Generate BarathX Independence Day video — waving Tiranga + brand overlay."""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "brand" / "social" / "independence-day-2026"
LOGO_PATH = ROOT / "brand" / "baratx-logo-avatar.png"

# Instagram Reel / Stories
W, H = 1080, 1920
FPS = 24
DURATION_S = 12
N_FRAMES = FPS * DURATION_S

SAFFRON = (255, 153, 51)
WHITE = (255, 255, 255)
GREEN = (19, 136, 8)
NAVY = (0, 0, 128)
DARK = (8, 10, 14)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


FONT_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_SANS_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"


def draw_chakra(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: float) -> None:
    # Outer ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=max(3, int(r * 0.06)))
    # Inner hub
    hub = max(3, int(r * 0.12))
    draw.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], fill=NAVY)
    # 24 spokes
    for i in range(24):
        ang = (i / 24.0) * 2 * math.pi - math.pi / 2
        x2 = cx + int((r - 2) * math.cos(ang))
        y2 = cy + int((r - 2) * math.sin(ang))
        draw.line([(cx, cy), (x2, y2)], fill=NAVY, width=max(2, int(r * 0.035)))
    # Small dots on rim
    for i in range(24):
        ang = (i / 24.0) * 2 * math.pi - math.pi / 2
        dx = cx + int(r * 0.88 * math.cos(ang))
        dy = cy + int(r * 0.88 * math.sin(ang))
        rr = max(2, int(r * 0.045))
        draw.ellipse([dx - rr, dy - rr, dx + rr, dy + rr], fill=NAVY)


def make_flag_base(w: int, h: int) -> Image.Image:
    """Static Tiranga filling the frame (pole on left, cloth fills rest)."""
    img = Image.new("RGB", (w, h), DARK)
    draw = ImageDraw.Draw(img)

    # Soft sky wash behind flag
    for y in range(h):
        t = y / h
        r = int(255 * (1 - t * 0.35))
        g = int(180 * (1 - t * 0.5) + 40 * t)
        b = int(80 + 40 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Flag cloth region (full-bleed patriotic field)
    band = h // 3
    draw.rectangle([0, 0, w, band], fill=SAFFRON)
    draw.rectangle([0, band, w, band * 2], fill=WHITE)
    draw.rectangle([0, band * 2, w, h], fill=GREEN)

    # Ashoka Chakra centered on white band
    cx, cy = w // 2, band + band // 2
    chakra_r = min(band * 0.38, w * 0.14)
    draw_chakra(draw, cx, cy, chakra_r)

    # Subtle fabric grain
    noise = np.random.randint(0, 18, (h, w, 3), dtype=np.int16)
    arr = np.asarray(img, dtype=np.int16)
    arr = np.clip(arr + noise - 9, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def wave_flag(base: Image.Image, t: float) -> Image.Image:
    """Horizontal cloth wave + gentle vertical ripple."""
    arr = np.asarray(base)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    # Primary wind wave (stronger toward fly end)
    fly = (xx / max(w - 1, 1)) ** 1.15
    dx = (14.0 * fly * np.sin(2 * math.pi * (yy / 95.0) - t * 2.2)).astype(np.float32)
    dx += (7.0 * fly * np.sin(2 * math.pi * (yy / 42.0) + t * 3.1)).astype(np.float32)
    dy = (6.0 * fly * np.sin(2 * math.pi * (xx / 120.0) + t * 1.7)).astype(np.float32)

    xs = np.clip((xx + dx).astype(np.int32), 0, w - 1)
    ys = np.clip((yy + dy).astype(np.int32), 0, h - 1)
    waved = arr[ys, xs]

    # Soft shading bands so the cloth feels dimensional
    shade = 0.88 + 0.12 * np.sin(2 * math.pi * (yy / 70.0) - t * 2.2 + xx / 180.0)
    shade = shade[..., None]
    out = np.clip(waved.astype(np.float32) * shade, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")


def load_logo(size: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    # Punch to circle so square PNG corners don't show on the flag.
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    # Soft ring so it separates from saffron band
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 210), width=4)
    return Image.alpha_composite(out, ring)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def compose_overlay(base: Image.Image, logo: Image.Image, progress: float) -> Image.Image:
    """Brand + Independence Day copy over darkened waving flag."""
    frame = base.convert("RGBA")

    # Dark vignette so text reads
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(veil)
    # Top/bottom gradient bars
    for y in range(H):
        top = max(0, int(160 * (1 - y / (H * 0.28))))
        bot = max(0, int(180 * max(0, (y - H * 0.62) / (H * 0.38))))
        a = min(200, top + bot + 55)
        vdraw.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    frame = Image.alpha_composite(frame, veil)

    # Fade-in for title block
    alpha = int(255 * min(1.0, max(0.0, (progress - 0.04) / 0.18)))
    title_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(title_layer)

    # Logo
    lx = (W - logo.width) // 2
    ly = int(H * 0.18)
    title_layer.paste(logo, (lx, ly), logo)

    # Wordmark
    f_brand = font(FONT_SANS, 92)
    brand = "BarathX"
    tw, th = text_size(draw, brand, f_brand)
    bx = (W - tw) // 2
    by = ly + logo.height + 28
    # Soft shadow
    draw.text((bx + 3, by + 3), brand, font=f_brand, fill=(0, 0, 0, 160))
    draw.text((bx, by), brand, font=f_brand, fill=(255, 255, 255, 255))

    # Wish
    f_wish = font(FONT_SERIF, 64)
    wish = "Happy Independence Day"
    ww, wh = text_size(draw, wish, f_wish)
    wx = (W - ww) // 2
    wy = by + th + 48
    draw.text((wx + 2, wy + 2), wish, font=f_wish, fill=(0, 0, 0, 140))
    draw.text((wx, wy), wish, font=f_wish, fill=(255, 214, 140, 255))

    # Date line with saffron / green rules
    f_date = font(FONT_SANS_REG, 36)
    date = "15 August 2026"
    dw, dh = text_size(draw, date, f_date)
    dx = (W - dw) // 2
    dy = wy + wh + 28
    rule_y = dy + dh // 2
    gap = 28
    draw.line([(dx - 160, rule_y), (dx - gap, rule_y)], fill=(*SAFFRON, 255), width=3)
    draw.line([(dx + dw + gap, rule_y), (dx + dw + 160, rule_y)], fill=(*GREEN, 255), width=3)
    draw.text((dx, dy), date, font=f_date, fill=(255, 255, 255, 230))

    # Tagline
    f_tag = font(FONT_SANS_REG, 40)
    tag = "India’s public square."
    tgw, _ = text_size(draw, tag, f_tag)
    ty = dy + dh + 36
    draw.text(((W - tgw) // 2, ty), tag, font=f_tag, fill=(255, 255, 255, 220))

    # CTA block near bottom
    f_cta = font(FONT_SANS, 42)
    cta = "Leave one honest take"
    cw, ch = text_size(draw, cta, f_cta)
    cy = int(H * 0.78)
    draw.text(((W - cw) // 2 + 2, cy + 2), cta, font=f_cta, fill=(0, 0, 0, 140))
    draw.text(((W - cw) // 2, cy), cta, font=f_cta, fill=(255, 255, 255, 255))

    f_url = font(FONT_SANS, 48)
    url = "barathx.com"
    uw, uh = text_size(draw, url, f_url)
    uy = cy + ch + 22
    # Pill behind URL
    pad_x, pad_y = 36, 16
    pill = [
        (W - uw) // 2 - pad_x,
        uy - pad_y // 2,
        (W + uw) // 2 + pad_x,
        uy + uh + pad_y // 2,
    ]
    draw.rounded_rectangle(pill, radius=28, fill=(255, 153, 51, 230))
    draw.text(((W - uw) // 2, uy), url, font=f_url, fill=(255, 255, 255, 255))

    f_soon = font(FONT_SANS_REG, 28)
    soon = "Browser soft launch · Apps coming soon"
    sw, _ = text_size(draw, soon, f_soon)
    draw.text(((W - sw) // 2, uy + uh + 28), soon, font=f_soon, fill=(255, 255, 255, 190))

    if alpha < 255:
        # Apply overall alpha to title layer
        r, g, b, a = title_layer.split()
        a = a.point(lambda p: int(p * alpha / 255))
        title_layer = Image.merge("RGBA", (r, g, b, a))

    out = Image.alpha_composite(frame, title_layer)
    return out.convert("RGB")


def encode_mp4(frame_dir: Path, out_path: Path) -> None:
    cmd = [
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
        "high",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def make_square_variant(portrait: Path, square_out: Path) -> None:
    """Center-crop portrait reel to 1080×1080 for feed posts."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(portrait),
        "-vf",
        "crop=1080:1080:0:420",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(square_out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building flag base…")
    base = make_flag_base(W, H)
    logo = load_logo(220)

    with tempfile.TemporaryDirectory(prefix="bx-indep-") as tmp:
        tmp_path = Path(tmp)
        print(f"Rendering {N_FRAMES} frames @ {FPS}fps…")
        for i in range(N_FRAMES):
            t = i / FPS
            progress = i / max(N_FRAMES - 1, 1)
            waved = wave_flag(base, t)
            # Slight blur on fabric for motion softness
            if i % 2 == 0:
                waved = waved.filter(ImageFilter.GaussianBlur(radius=0.4))
            frame = compose_overlay(waved, logo, progress)
            # Mild contrast punch
            frame = ImageEnhance.Contrast(frame).enhance(1.05)
            frame.save(tmp_path / f"frame_{i:04d}.jpg", quality=92, optimize=True)
            if i % 24 == 0:
                print(f"  {i}/{N_FRAMES}")

        reel = OUT_DIR / "barathx-independence-day-flag-reel.mp4"
        square = OUT_DIR / "barathx-independence-day-flag-square.mp4"
        print("Encoding reel…")
        encode_mp4(tmp_path, reel)
        print("Encoding square crop…")
        make_square_variant(reel, square)

        # Still poster from mid frame
        poster = Image.open(tmp_path / f"frame_{N_FRAMES // 2:04d}.jpg")
        poster_path = OUT_DIR / "barathx-independence-day-flag-poster.jpg"
        poster.save(poster_path, quality=92, optimize=True)

    print("Wrote:")
    for p in (reel, square, poster_path):
        mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.relative_to(ROOT)}  ({mb:.1f} MB)")


if __name__ == "__main__":
    main()
