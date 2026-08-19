#!/usr/bin/env python3
"""
20-second follow-up reel: Why India needs BarathX.

Append after the "built for someone else" deck (slides 01–04) or any screen
recording. Uses latest product screens (live barathx.com + mobile demo frames).

Outputs:
  brand/social/why-india-needs/barathx-why-india-needs-20s.mp4   (1080×1080 — matches slide deck)
  brand/social/why-india-needs/barathx-why-india-needs-20s-reel.mp4 (1080×1920 — IG Reels)
  brand/social/why-india-needs/barathx-why-india-needs-poster.jpg

Usage:
  /tmp/pilvenv/bin/python brand/social/why-india-needs/render_why_india_needs.py
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent
SCREENS = OUT_DIR / "screens"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"

W, H = 1080, 1080
FPS = 24
DURATION_S = 20
N_FRAMES = FPS * DURATION_S

SAFFRON = (255, 103, 31)
SAFFRON_SOFT = (255, 153, 51)
CREAM = (255, 248, 235)
DARK = (8, 10, 14)
INK = (18, 20, 28)
WHITE = (255, 255, 255)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# Latest screens — refresh with capture_screens.sh when UI changes
SCREEN_FILES = {
    "landing-live": "landing-live.png",
    "square": "square.jpg",
    "arenas": "arenas.jpg",
    "live": "live.jpg",
    "home": "home-returning.png",
    "signup": "signup.png",
}

BEATS = [
    (0.0, 2.6, "title", "Why India needs BarathX", "India's public square — live now", "landing-live"),
    (2.6, 5.0, "product", "Not another Reels feed", "Short takes. Real replies.", "landing-live"),
    (5.0, 7.4, "product", "Square", "One question. Your take.", "square"),
    (7.4, 9.8, "product", "Arenas", "Pick a side. Jump in.", "arenas"),
    (9.8, 12.2, "product", "Live", "Argue it now — up to 15 voices.", "live"),
    (12.2, 14.6, "product", "Built for India", "Sports · Politics · Startups · News", "home"),
    (14.6, 17.0, "promise", "Human takes only", "No AI slop.", "landing-live"),
    (17.0, 20.0, "cta", "Join free today", "barathx.com", "signup"),
]


def fnt(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    img = img.convert("RGB")
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def load_screen(key: str) -> Image.Image:
    name = SCREEN_FILES[key]
    path = SCREENS / name
    if not path.exists():
        raise FileNotFoundError(f"Missing screen: {path}")
    return Image.open(path).convert("RGB")


def gradient_bg(kind: str, t: float) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    if kind in ("title", "promise"):
        # Warm cream → saffron (matches slides 01–04)
        for y in range(H):
            p = y / H
            r = int(255 * (1 - p * 0.08) + SAFFRON_SOFT[0] * p * 0.35)
            g = int(248 * (1 - p * 0.12) + SAFFRON_SOFT[1] * p * 0.28)
            b = int(235 * (1 - p * 0.15) + SAFFRON_SOFT[2] * p * 0.15)
            draw.line([(0, y), (W, y)], fill=(r, g, b))
    elif kind == "cta":
        for y in range(H):
            p = y / H
            r = int(INK[0] + SAFFRON[0] * p * 0.55)
            g = int(INK[1] + SAFFRON[1] * p * 0.35)
            b = int(INK[2] + SAFFRON[2] * p * 0.15)
            draw.line([(0, y), (W, y)], fill=(r, g, b))
    else:
        for y in range(H):
            p = y / H
            shade = int(10 + 18 * p)
            draw.line([(0, y), (W, y)], fill=(shade, shade, shade + 4))
    # subtle grain pulse
    pulse = 0.03 * math.sin(t * 2.5)
    if pulse > 0:
        overlay = Image.new("RGB", (W, H), SAFFRON)
        img = Image.blend(img, overlay, pulse)
    return img


def phone_frame(screen: Image.Image, *, zoom: float = 1.0, y_offset: int = 0) -> Image.Image:
    """Render product screen inside an iPhone-style frame."""
    pw, ph = 430, 880
    inner = cover(screen, pw - 24, ph - 120)
    inner = inner.resize((pw - 24, ph - 120), Image.Resampling.LANCZOS)

    frame = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    body = Image.new("RGBA", (pw, ph), (22, 22, 26, 255))
    draw = ImageDraw.Draw(body)
    draw.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=48, fill=(18, 18, 22, 255))
    draw.rounded_rectangle([8, 8, pw - 9, ph - 9], radius=42, outline=(60, 60, 68, 255), width=3)
    # notch
    draw.rounded_rectangle([pw // 2 - 54, 16, pw // 2 + 54, 44], radius=16, fill=(8, 8, 10, 255))
    frame.paste(body, (0, 0), body)
    frame.paste(inner, (12, 72))

    if zoom != 1.0:
        nw, nh = int(pw * zoom), int(ph * zoom)
        frame = frame.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fx, fy = (W - frame.width) // 2, (H - frame.height) // 2 + y_offset
    canvas.paste(frame, (fx, fy), frame)
    return canvas


def ken_burns(screen: Image.Image, local: float) -> Image.Image:
    base = cover(screen, int(W * 1.15), int(H * 1.15))
    bw, bh = base.size
    zoom = 1.0 + 0.06 * local
    cw, ch = int(W * zoom), int(H * zoom)
    cw, ch = min(cw, bw), min(ch, bh)
    x = int((bw - cw) * (0.12 + 0.5 * local))
    y = int((bh - ch) * 0.18)
    crop = base.crop((x, y, x + cw, y + ch)).resize((W, H), Image.Resampling.LANCZOS)
    dark = ImageEnhance.Brightness(crop).enhance(0.55)
    return dark


def draw_stroked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, ...],
    stroke: tuple[int, ...] = DARK,
    stroke_w: int = 4,
) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)


def compose_frame(beat: dict, t: float) -> Image.Image:
    kind = beat["kind"]
    local = beat["local"]
    fade_in = min(1.0, local * 5.0)
    fade_out = min(1.0, (1.0 - local) * 5.0) if local > 0.82 else 1.0
    alpha = fade_in * fade_out

    if kind == "title":
        bg = gradient_bg("title", t)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        # small slide number echo
        d.text((36, 28), "05", font=fnt(FONT_REG, 22), fill=(120, 120, 130, 180))
        headline = beat["headline"]
        sub = beat["sub"]
        fh = fnt(FONT_SERIF, 62)
        fs = fnt(FONT_REG, 34)
        hw, hh = text_size(d, headline, fh)
        draw_stroked(d, ((W - hw) // 2, 120), headline, fh, (*INK, 255), stroke=(*CREAM, 200), stroke_w=2)
        sw, _ = text_size(d, sub, fs)
        draw_stroked(d, ((W - sw) // 2, 120 + hh + 20), sub, fs, (*SAFFRON, 255), stroke_w=2)
        phone = phone_frame(load_screen(beat["screen"]), zoom=0.92, y_offset=80)
        bg = Image.alpha_composite(bg.convert("RGBA"), layer)
        bg = Image.alpha_composite(bg, phone)
        out = bg.convert("RGB")

    elif kind == "promise":
        bg = gradient_bg("promise", t)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        lines = beat["headline"], beat["sub"]
        y = 180
        for i, line in enumerate(lines):
            font = fnt(FONT_BOLD, 56 if i == 0 else 40)
            color = SAFFRON if i == 0 else INK
            tw, th = text_size(d, line, font)
            draw_stroked(d, ((W - tw) // 2, y), line, font, (*color, 255), stroke=(*CREAM, 180), stroke_w=3)
            y += th + 16
        phone = phone_frame(load_screen(beat["screen"]), zoom=0.78, y_offset=120)
        bg = Image.alpha_composite(bg.convert("RGBA"), layer)
        bg = Image.alpha_composite(bg, phone)
        out = bg.convert("RGB")

    elif kind == "cta":
        bg = gradient_bg("cta", t)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        logo = Image.open(LOGO).convert("RGBA").resize((120, 120), Image.Resampling.LANCZOS)
        mask = Image.new("L", (120, 120), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 119, 119], fill=255)
        circ = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        circ.paste(logo, (0, 0), mask)
        layer.paste(circ, ((W - 120) // 2, 140), circ)
        brand = "BarathX"
        fb = fnt(FONT_BOLD, 44)
        bw, _ = text_size(d, brand, fb)
        draw_stroked(d, ((W - bw) // 2, 280), brand, fb, (*WHITE, 255), stroke_w=2)
        fh = fnt(FONT_BOLD, 58)
        headline = beat["headline"]
        hw, hh = text_size(d, headline, fh)
        draw_stroked(d, ((W - hw) // 2, 360), headline, fh, (*WHITE, 255), stroke_w=4)
        url = beat["sub"]
        fu = fnt(FONT_BOLD, 46)
        uw, uh = text_size(d, url, fu)
        px, py = (W - uw) // 2 - 32, 360 + hh + 40
        d.rounded_rectangle([px, py, px + uw + 64, py + uh + 32], radius=36, fill=(*WHITE, 255))
        d.text((px + 32, py + 14), url, font=fu, fill=(*SAFFRON, 255))
        found = "100 Founding spots — earned by real debate"
        ff = fnt(FONT_REG, 28)
        fw, _ = text_size(d, found, ff)
        draw_stroked(d, ((W - fw) // 2, py + uh + 52), found, ff, (*CREAM, 240), stroke_w=2)
        tag = "India's public square · Phone OTP or email"
        ft = fnt(FONT_REG, 26)
        tw, _ = text_size(d, tag, ft)
        draw_stroked(d, ((W - tw) // 2, py + uh + 100), tag, ft, (*CREAM, 220), stroke_w=2)
        phone = phone_frame(load_screen(beat["screen"]), zoom=0.62, y_offset=200)
        bg = Image.alpha_composite(bg.convert("RGBA"), layer)
        bg = Image.alpha_composite(bg, phone)
        out = bg.convert("RGB")

    else:  # product
        screen = load_screen(beat["screen"])
        bg = ken_burns(screen, local)
        bg = bg.convert("RGBA")
        veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vd = ImageDraw.Draw(veil)
        for y in range(H):
            top = max(0, int(150 * (1 - y / (H * 0.35))))
            bot = max(0, int(180 * max(0, (y - H * 0.55) / (H * 0.45))))
            a = min(220, top + bot + 70)
            vd.line([(0, y), (W, y)], fill=(*DARK, a))
        bg = Image.alpha_composite(bg, veil)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        # top headline plate
        title = beat["headline"]
        sub = beat["sub"]
        ft = fnt(FONT_BOLD, 54)
        fs = fnt(FONT_REG, 30)
        tw, th = text_size(d, title, ft)
        draw_stroked(d, (48, 56), title, ft, (*SAFFRON, 255), stroke_w=3)
        draw_stroked(d, (48, 56 + th + 8), sub, fs, (*CREAM, 255), stroke_w=2)
        # phone centered lower
        phone = phone_frame(screen, zoom=0.88, y_offset=40)
        bg = Image.alpha_composite(bg, layer)
        bg = Image.alpha_composite(bg, phone)
        # progress dots
        idx = next(i for i, b in enumerate(BEATS) if b[2] == kind and b[3] == beat["headline"])
        dot_y = H - 40
        n = len(BEATS)
        total_w = n * 16
        dx = (W - total_w) // 2
        for i in range(n):
            color = (*SAFFRON, 255) if i <= idx else (255, 255, 255, 80)
            d2 = ImageDraw.Draw(bg)
            d2.ellipse([dx + i * 16, dot_y, dx + i * 16 + 10, dot_y + 10], fill=color)
        out = bg.convert("RGB")

    if alpha < 1.0:
        black = Image.new("RGB", (W, H), DARK)
        out = Image.blend(black, out, alpha)
    out = ImageEnhance.Contrast(out).enhance(1.04)
    return out


def scene_at(t: float) -> dict:
    for start, end, kind, headline, sub, screen in BEATS:
        if start <= t < end:
            local = (t - start) / max(end - start, 0.001)
            return {
                "kind": kind,
                "headline": headline,
                "sub": sub,
                "screen": screen,
                "local": local,
                "start": start,
                "end": end,
            }
    _, _, kind, headline, sub, screen = BEATS[-1]
    return {"kind": kind, "headline": headline, "sub": sub, "screen": screen, "local": 1.0}


def encode(frames: Path, out: Path, *, size: tuple[int, int] | None = None) -> None:
    inp = frames / "frame_%04d.jpg"
    vf = []
    if size and size != (W, H):
        vf.append(f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease,pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2:black")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(inp),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-profile:v", "main",
        "-crf", "20",
        "-movflags", "+faststart",
        "-an",
    ]
    if vf:
        cmd.extend(["-vf", ",".join(vf)])
    cmd.append(str(out))
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENS.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="bx-why-india-") as tmp:
        tmp_path = Path(tmp)
        print(f"Rendering {N_FRAMES} frames @ {FPS}fps ({DURATION_S}s)…")
        for i in range(N_FRAMES):
            t = i / FPS
            beat = scene_at(t)
            frame = compose_frame(beat, t)
            frame.save(tmp_path / f"frame_{i:04d}.jpg", quality=92, optimize=True)
            if i % 48 == 0:
                print(f"  {i}/{N_FRAMES}")

        square = OUT_DIR / "barathx-why-india-needs-20s.mp4"
        reel = OUT_DIR / "barathx-why-india-needs-20s-reel.mp4"
        poster = OUT_DIR / "barathx-why-india-needs-poster.jpg"
        print("Encoding square (1080×1080)…")
        encode(tmp_path, square)
        print("Encoding reel (1080×1920)…")
        encode(tmp_path, reel, size=(1080, 1920))
        Image.open(tmp_path / f"frame_{N_FRAMES - 1:04d}.jpg").save(poster, quality=90, optimize=True)

    for p in (square, reel, poster):
        mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.name}  ({mb:.2f} MB)")


if __name__ == "__main__":
    main()
