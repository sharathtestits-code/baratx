#!/usr/bin/env python3
"""Generate BarathX Independence Day video — waving Tiranga + brand overlay.

Instagram Reel / Stories layout follows the platform safe-zone template:
  • Top ~280px reserved (username / audio UI)
  • Bottom ~380px reserved (captions / buttons / home bar)
  • All brand + CTA copy stays inside the middle safe band
Square feed cut is composed separately (not a blind center-crop).
"""

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
REEL_W, REEL_H = 1080, 1920
SQ_W, SQ_H = 1080, 1080
FPS = 24
DURATION_S = 12
N_FRAMES = FPS * DURATION_S

# IG Reel UI chrome (approx) — keep hero copy inside this band
REEL_SAFE_TOP = 340
REEL_SAFE_BOTTOM = 1480  # 1920 - 440

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
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=max(3, int(r * 0.06)))
    hub = max(3, int(r * 0.12))
    draw.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], fill=NAVY)
    for i in range(24):
        ang = (i / 24.0) * 2 * math.pi - math.pi / 2
        x2 = cx + int((r - 2) * math.cos(ang))
        y2 = cy + int((r - 2) * math.sin(ang))
        draw.line([(cx, cy), (x2, y2)], fill=NAVY, width=max(2, int(r * 0.035)))
    for i in range(24):
        ang = (i / 24.0) * 2 * math.pi - math.pi / 2
        dx = cx + int(r * 0.88 * math.cos(ang))
        dy = cy + int(r * 0.88 * math.sin(ang))
        rr = max(2, int(r * 0.045))
        draw.ellipse([dx - rr, dy - rr, dx + rr, dy + rr], fill=NAVY)


def make_flag_base(w: int, h: int) -> Image.Image:
    """Static Tiranga filling the frame."""
    img = Image.new("RGB", (w, h), DARK)
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / h
        r = int(255 * (1 - t * 0.35))
        g = int(180 * (1 - t * 0.5) + 40 * t)
        b = int(80 + 40 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    band = h // 3
    draw.rectangle([0, 0, w, band], fill=SAFFRON)
    draw.rectangle([0, band, w, band * 2], fill=WHITE)
    draw.rectangle([0, band * 2, w, h], fill=GREEN)

    cx, cy = w // 2, band + band // 2
    chakra_r = min(band * 0.38, w * 0.14)
    draw_chakra(draw, cx, cy, chakra_r)

    noise = np.random.randint(0, 18, (h, w, 3), dtype=np.int16)
    arr = np.asarray(img, dtype=np.int16)
    arr = np.clip(arr + noise - 9, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def wave_flag(base: Image.Image, t: float) -> Image.Image:
    """Horizontal cloth wave + gentle vertical ripple."""
    arr = np.asarray(base)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]

    fly = (xx / max(w - 1, 1)) ** 1.15
    dx = (14.0 * fly * np.sin(2 * math.pi * (yy / 95.0) - t * 2.2)).astype(np.float32)
    dx += (7.0 * fly * np.sin(2 * math.pi * (yy / 42.0) + t * 3.1)).astype(np.float32)
    dy = (6.0 * fly * np.sin(2 * math.pi * (xx / 120.0) + t * 1.7)).astype(np.float32)

    xs = np.clip((xx + dx).astype(np.int32), 0, w - 1)
    ys = np.clip((yy + dy).astype(np.int32), 0, h - 1)
    waved = arr[ys, xs]

    shade = 0.88 + 0.12 * np.sin(2 * math.pi * (yy / 70.0) - t * 2.2 + xx / 180.0)
    shade = shade[..., None]
    out = np.clip(waved.astype(np.float32) * shade, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")


def load_logo(size: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 220), width=5)
    return Image.alpha_composite(out, ring)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_text_bold(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int] = (8, 10, 14, 220),
    stroke_w: int = 4,
) -> None:
    x, y = xy
    if stroke_w > 0:
        draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
    else:
        draw.text((x, y), text, font=fnt, fill=fill)


def apply_veil(frame: Image.Image, w: int, h: int) -> Image.Image:
    """Darken edges so cream/gold copy stays readable on Tiranga."""
    veil = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(veil)
    for y in range(h):
        top = max(0, int(160 * (1 - y / max(h * 0.22, 1))))
        mid = 0
        if h * 0.28 <= y <= h * 0.72:
            mid = int(100 + 30 * math.sin(math.pi * (y - h * 0.28) / max(h * 0.44, 1)))
        bot = max(0, int(180 * max(0, (y - h * 0.62) / max(h * 0.38, 1))))
        a = min(210, top + mid + bot + 45)
        vdraw.line([(0, y), (w, y)], fill=(8, 10, 14, a))
    return Image.alpha_composite(frame, veil)


def compose_brand_stack(
    draw: ImageDraw.ImageDraw,
    logo: Image.Image,
    layer: Image.Image,
    *,
    w: int,
    safe_top: int,
    safe_bottom: int,
    sizes: dict[str, int],
) -> None:
    """
    Single vertical stack inside [safe_top, safe_bottom].
    Keeps logo fully visible and bottom CTA above IG chrome.
    """
    brand_size = sizes["brand"]
    wish_size = sizes["wish"]
    plate_title = sizes["plate_title"]
    plate_date = sizes["plate_date"]
    plate_tag = sizes["plate_tag"]
    cta_size = sizes["cta"]
    url_size = sizes["url"]
    soon_size = sizes["soon"]
    gap = sizes["gap"]

    f_brand = font(FONT_SANS, brand_size)
    f_wish = font(FONT_SERIF, wish_size)
    f_80 = font(FONT_SANS, plate_title)
    f_date = font(FONT_SANS, plate_date)
    f_tag = font(FONT_SANS, plate_tag)
    f_cta = font(FONT_SANS, cta_size)
    f_url = font(FONT_SANS, url_size)
    f_soon = font(FONT_SANS, soon_size)

    brand = "BarathX"
    wish = "Happy Independence Day"
    milestone = "80th Independence Day"
    date = "15 August 2026"
    tag = "India’s public square."
    cta = "Leave one honest take"
    url = "https://barathx.com"
    soon = "Browser soft launch · Apps coming soon"

    tw, th = text_size(draw, brand, f_brand)
    ww, wh = text_size(draw, wish, f_wish)
    mww, mwh = text_size(draw, milestone, f_80)
    dw, dh = text_size(draw, date, f_date)
    tgw, tgh = text_size(draw, tag, f_tag)
    cw, ch = text_size(draw, cta, f_cta)
    uw, uh = text_size(draw, url, f_url)
    sw, sh = text_size(draw, soon, f_soon)

    plate_pad_y = 20
    plate_inner = mwh + 12 + dh + 12 + tgh
    plate_h = plate_inner + plate_pad_y * 2
    pill_pad_y = 14
    pill_h = uh + pill_pad_y * 2

    # Measure total stack height, then center inside safe band
    block_h = (
        logo.height
        + gap
        + th
        + gap
        + wh
        + gap
        + plate_h
        + gap
        + ch
        + gap // 2
        + pill_h
        + gap // 2
        + sh
    )
    usable = max(safe_bottom - safe_top, block_h)
    y = safe_top + max(0, (usable - block_h) // 2)

    # Logo
    lx = (w - logo.width) // 2
    layer.paste(logo, (lx, y), logo)
    y += logo.height + gap

    # Wordmark
    draw_text_bold(draw, ((w - tw) // 2, y), brand, f_brand, (255, 255, 255, 255), stroke_w=5)
    y += th + gap

    # Wish
    draw_text_bold(
        draw,
        ((w - ww) // 2, y),
        wish,
        f_wish,
        (255, 220, 120, 255),
        stroke=(20, 12, 4, 230),
        stroke_w=5,
    )
    y += wh + gap

    # Milestone plate
    plate = [int(w * 0.08), y, int(w * 0.92), y + plate_h]
    draw.rounded_rectangle(plate, radius=26, fill=(8, 10, 14, 220))
    draw.rounded_rectangle(plate, radius=26, outline=(255, 153, 51, 210), width=3)

    py = y + plate_pad_y
    draw_text_bold(
        draw,
        ((w - mww) // 2, py),
        milestone,
        f_80,
        (255, 214, 140, 255),
        stroke=(0, 0, 0, 255),
        stroke_w=3,
    )
    py += mwh + 12

    rule_y = py + dh // 2
    dx = (w - dw) // 2
    gap_rule = 18
    draw.line([(dx - 100, rule_y), (dx - gap_rule, rule_y)], fill=(*SAFFRON, 255), width=4)
    draw.line([(dx + dw + gap_rule, rule_y), (dx + dw + 100, rule_y)], fill=(*GREEN, 255), width=4)
    draw_text_bold(
        draw,
        (dx, py),
        date,
        f_date,
        (255, 214, 140, 255),
        stroke=(0, 0, 0, 255),
        stroke_w=3,
    )
    py += dh + 12

    draw_text_bold(
        draw,
        ((w - tgw) // 2, py),
        tag,
        f_tag,
        (255, 248, 235, 255),
        stroke=(0, 0, 0, 255),
        stroke_w=3,
    )
    y += plate_h + gap

    # CTA
    draw_text_bold(draw, ((w - cw) // 2, y), cta, f_cta, (255, 255, 255, 255), stroke_w=5)
    y += ch + gap // 2

    # URL pill
    pad_x = 36
    pill = [
        (w - uw) // 2 - pad_x,
        y,
        (w + uw) // 2 + pad_x,
        y + pill_h,
    ]
    draw.rounded_rectangle(pill, radius=34, fill=(255, 153, 51, 245))
    draw.rounded_rectangle(pill, radius=34, outline=(255, 255, 255, 230), width=3)
    draw_text_bold(
        draw,
        ((w - uw) // 2, y + pill_pad_y),
        url,
        f_url,
        (255, 255, 255, 255),
        stroke=(140, 60, 10, 200),
        stroke_w=2,
    )
    y += pill_h + gap // 2

    # Soft-launch line — still above safe_bottom
    draw_text_bold(
        draw,
        ((w - sw) // 2, y),
        soon,
        f_soon,
        (255, 255, 255, 245),
        stroke_w=4,
    )


def compose_overlay(
    base: Image.Image,
    logo: Image.Image,
    progress: float,
    *,
    w: int,
    h: int,
    safe_top: int,
    safe_bottom: int,
    sizes: dict[str, int],
) -> Image.Image:
    frame = apply_veil(base.convert("RGBA"), w, h)

    alpha = int(255 * min(1.0, max(0.0, (progress - 0.04) / 0.18)))
    title_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(title_layer)
    compose_brand_stack(
        draw,
        logo,
        title_layer,
        w=w,
        safe_top=safe_top,
        safe_bottom=safe_bottom,
        sizes=sizes,
    )

    if alpha < 255:
        r, g, b, a = title_layer.split()
        a = a.point(lambda p: int(p * alpha / 255))
        title_layer = Image.merge("RGBA", (r, g, b, a))

    return Image.alpha_composite(frame, title_layer).convert("RGB")


REEL_SIZES = {
    "brand": 86,
    "wish": 56,
    "plate_title": 44,
    "plate_date": 38,
    "plate_tag": 38,
    "cta": 44,
    "url": 40,
    "soon": 30,
    "gap": 22,
}

SQUARE_SIZES = {
    "brand": 78,
    "wish": 48,
    "plate_title": 40,
    "plate_date": 34,
    "plate_tag": 34,
    "cta": 38,
    "url": 34,
    "soon": 26,
    "gap": 16,
}


def encode_mp4(frame_dir: Path, out_path: Path, pattern: str = "frame_%04d.jpg") -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(frame_dir / pattern),
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


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building flag bases…")
    base_reel = make_flag_base(REEL_W, REEL_H)
    base_sq = make_flag_base(SQ_W, SQ_H)
    logo_reel = load_logo(168)
    logo_sq = load_logo(148)

    with tempfile.TemporaryDirectory(prefix="bx-indep-") as tmp:
        tmp_path = Path(tmp)
        print(f"Rendering {N_FRAMES} reel + square frames @ {FPS}fps…")
        for i in range(N_FRAMES):
            t = i / FPS
            progress = i / max(N_FRAMES - 1, 1)

            waved_r = wave_flag(base_reel, t)
            waved_s = wave_flag(base_sq, t)
            if i % 2 == 0:
                waved_r = waved_r.filter(ImageFilter.GaussianBlur(radius=0.4))
                waved_s = waved_s.filter(ImageFilter.GaussianBlur(radius=0.35))

            reel_frame = compose_overlay(
                waved_r,
                logo_reel,
                progress,
                w=REEL_W,
                h=REEL_H,
                safe_top=REEL_SAFE_TOP,
                safe_bottom=REEL_SAFE_BOTTOM,
                sizes=REEL_SIZES,
            )
            sq_frame = compose_overlay(
                waved_s,
                logo_sq,
                progress,
                w=SQ_W,
                h=SQ_H,
                safe_top=56,
                safe_bottom=SQ_H - 56,
                sizes=SQUARE_SIZES,
            )

            reel_frame = ImageEnhance.Contrast(reel_frame).enhance(1.05)
            sq_frame = ImageEnhance.Contrast(sq_frame).enhance(1.05)
            reel_frame.save(tmp_path / f"reel_{i:04d}.jpg", quality=92, optimize=True)
            sq_frame.save(tmp_path / f"sq_{i:04d}.jpg", quality=92, optimize=True)
            if i % 24 == 0:
                print(f"  {i}/{N_FRAMES}")

        reel = OUT_DIR / "barathx-independence-day-flag-reel.mp4"
        square = OUT_DIR / "barathx-independence-day-flag-square.mp4"
        print("Encoding reel…")
        encode_mp4(tmp_path, reel, "reel_%04d.jpg")
        print("Encoding square…")
        encode_mp4(tmp_path, square, "sq_%04d.jpg")

        poster = Image.open(tmp_path / f"reel_{N_FRAMES // 2:04d}.jpg")
        poster_path = OUT_DIR / "barathx-independence-day-flag-poster.jpg"
        poster.save(poster_path, quality=92, optimize=True)

        # Local audit still with safe-zone guides (not shipped)
        audit = poster.copy()
        ad = ImageDraw.Draw(audit)
        ad.rectangle([0, 0, REEL_W - 1, REEL_SAFE_TOP], outline=(255, 0, 80), width=4)
        ad.rectangle([0, REEL_SAFE_BOTTOM, REEL_W - 1, REEL_H - 1], outline=(255, 0, 80), width=4)
        audit_path = Path(tempfile.gettempdir()) / "bx-indep-reel-safezone-audit.jpg"
        audit.save(audit_path, quality=88)
        print(f"Safe-zone audit: {audit_path}")

    print("Wrote:")
    for p in (reel, square, poster_path):
        mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.relative_to(ROOT)}  ({mb:.1f} MB)")


if __name__ == "__main__":
    main()
