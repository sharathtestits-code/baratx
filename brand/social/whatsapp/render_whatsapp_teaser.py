#!/usr/bin/env python3
"""
BarathX WhatsApp / Instagram marketing teaser.

Same story beats as the original WA teaser, laid out for the Instagram Reel
safe-zone template so the logo and bottom captions are not clipped by IG UI.
Also works in WhatsApp Status / Channel (9:16 MP4).
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "brand" / "social" / "whatsapp"
SCREENS_DIR = OUT_DIR / "screens"
LOGO_PATH = ROOT / "brand" / "baratx-logo-avatar.png"

# Instagram Reel / Stories + WhatsApp Status
W, H = 1080, 1920
SQ_W, SQ_H = 1080, 1080
FPS = 24
DURATION_S = 24
N_FRAMES = FPS * DURATION_S

# IG Reel chrome — keep logo + captions inside this band
SAFE_TOP = 320
SAFE_BOTTOM = 1480  # 1920 - 440

SAFFRON = (255, 153, 51)
CREAM = (255, 248, 235)
DARK = (8, 10, 14)
GREEN = (19, 136, 8)

FONT_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_SANS_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"

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
    img = img.convert("RGB")
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def load_screen(name: str, tw: int, th: int) -> Image.Image:
    key = f"{name}:{tw}x{th}"
    if key in _SCREEN_CACHE:
        return _SCREEN_CACHE[key]
    path = SCREENS_DIR / name
    if not path.exists():
        img = Image.new("RGB", (tw, th), DARK)
    else:
        img = cover_resize(Image.open(path), int(tw * 1.18), int(th * 1.18))
    _SCREEN_CACHE[key] = img
    return img


def ken_burns(base: Image.Image, local: float, t: float, tw: int, th: int) -> Image.Image:
    bw, bh = base.size
    zoom = 1.0 + 0.08 * local + 0.02 * math.sin(t * 0.6)
    cw, ch = int(tw * zoom), int(th * zoom)
    cw = min(cw, bw)
    ch = min(ch, bh)
    max_x = max(bw - cw, 1)
    max_y = max(bh - ch, 1)
    x = int(max_x * (0.15 + 0.7 * local))
    y = int(max_y * (0.2 + 0.35 * math.sin(local * math.pi)))
    return base.crop((x, y, x + cw, y + ch)).resize((tw, th), Image.Resampling.LANCZOS)


def make_bg(t: float, kind: str, local: float, tw: int, th: int) -> Image.Image:
    screen_name = SCENE_SCREEN.get(kind, "bx-site-landing.png")
    base = load_screen(screen_name, tw, th)
    frame = ken_burns(base, local, t, tw, th)

    if kind in ("square", "arenas", "live", "promise", "cta"):
        frame = frame.filter(ImageFilter.GaussianBlur(radius=1.2))
    else:
        frame = frame.filter(ImageFilter.GaussianBlur(radius=1.8))

    frame = ImageEnhance.Brightness(frame).enhance(0.70 if kind == "hook" else 0.80)
    frame = ImageEnhance.Contrast(frame).enhance(1.08)

    rgba = frame.convert("RGBA")
    veil = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for y in range(th):
        top = max(0, int(180 * (1 - y / (th * 0.28))))
        bot = max(0, int(200 * max(0, (y - th * 0.55) / (th * 0.45))))
        mid = 60 if kind in ("square", "arenas", "live", "promise") else 90
        a = min(215, top + bot + mid)
        vd.line([(0, y), (tw, y)], fill=(8, 10, 14, a))
    vd.rectangle([0, 0, 8, th], fill=(*SAFFRON, 160))
    return Image.alpha_composite(rgba, veil).convert("RGB")


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


def load_logo(size: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 220), width=4)
    return Image.alpha_composite(out, ring)


def scene_at(t: float) -> dict:
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


def pill(draw, text, fnt, y, tw_frame: int, fill=SAFFRON):
    tw, th = text_size(draw, text, fnt)
    pad_x, pad_y = 40, 18
    x0 = (tw_frame - tw) // 2 - pad_x
    y0 = y
    x1 = (tw_frame + tw) // 2 + pad_x
    y1 = y + th + pad_y
    draw.rounded_rectangle([x0, y0, x1, y1], radius=34, fill=(*fill, 245))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=34, outline=(255, 255, 255, 220), width=3)
    draw_text(draw, ((tw_frame - tw) // 2, y + pad_y // 2), text, fnt, fill=(255, 255, 255, 255), stroke_w=2)
    return y1


def draw_progress(draw, kind: str, tw: int, y: int) -> None:
    labels = ["hook", "brand", "square", "arenas", "live", "promise", "cta"]
    idx = labels.index(kind) if kind in labels else 0
    step = 22
    total_w = len(labels) * step
    dx = (tw - total_w) // 2
    for i in range(len(labels)):
        r = 6
        color = (*SAFFRON, 255) if i <= idx else (255, 255, 255, 70)
        draw.ellipse([dx + i * step, y, dx + i * step + r * 2, y + r * 2], fill=color)


def compose(
    frame_bg: Image.Image,
    logo: Image.Image,
    scene: dict,
    *,
    tw: int,
    th: int,
    safe_top: int,
    safe_bottom: int,
) -> Image.Image:
    base = frame_bg.convert("RGBA")
    veil = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for y in range(th):
        a = 0
        if y < safe_top:
            a = int(120 * (1 - y / max(safe_top, 1)))
        if y > safe_bottom:
            a = max(a, int(140 * ((y - safe_bottom) / max(th - safe_bottom, 1))))
        if a:
            vd.line([(0, y), (tw, y)], fill=(8, 10, 14, a))
    base = Image.alpha_composite(base, veil)

    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    kind = scene["kind"]
    local = scene["local"]
    fade = min(1.0, local * 4.0) if local < 0.85 else max(0.55, 1.0 - (local - 0.85) / 0.15)

    # Scale fonts for reel vs square
    scale = 1.0 if th >= 1600 else 0.86
    f_hook = font(FONT_SANS, int(72 * scale))
    f_hook_sub = font(FONT_SANS_REG, int(34 * scale))
    f_brand_name = font(FONT_SANS, int(42 * scale))
    f_tag = font(FONT_SERIF, int(58 * scale))
    f_wedge = font(FONT_SANS, int(40 * scale))
    f_title = font(FONT_SANS, int(56 * scale))
    f_body = font(FONT_SANS, int(36 * scale))
    f_chip = font(FONT_SANS, int(26 * scale))
    f_promise = font(FONT_SANS, int(56 * scale))
    f_promise_sub = font(FONT_SANS_REG, int(34 * scale))
    f_cta = font(FONT_SANS, int(48 * scale))
    f_url = font(FONT_SANS, int(40 * scale))
    f_soon = font(FONT_SANS, int(30 * scale))
    f_found = font(FONT_SANS_REG, int(26 * scale))

    # Brand mark — always inside safe_top (never under IG username chrome)
    show_logo = kind in ("brand", "cta", "hook", "promise")
    y = safe_top + 12
    if show_logo:
        lx = (tw - logo.width) // 2
        layer.paste(logo, (lx, y), logo)
        y += logo.height + 14
        brand = "BarathX"
        bw, bh = text_size(draw, brand, f_brand_name)
        draw_text(draw, ((tw - bw) // 2, y), brand, f_brand_name, fill=(*CREAM, 255), stroke_w=4)
        y += bh + 28
    else:
        # Product UI scenes: small corner mark so brand is never cut, UI stays visible
        mini = logo.resize((72, 72), Image.Resampling.LANCZOS)
        layer.paste(mini, (tw - mini.width - 36, safe_top + 8), mini)

    lines = scene["copy"].split("\n")

    if kind == "hook":
        # Center copy in safe band under logo
        heights = [text_size(draw, ln, f_hook)[1] for ln in lines]
        sub = "Then the group moves on."
        sub_h = text_size(draw, sub, f_hook_sub)[1]
        block_h = sum(heights) + 14 * max(len(lines) - 1, 0) + 28 + sub_h
        y = max(y, safe_top + max(0, (safe_bottom - safe_top - block_h) // 2))
        for line in lines:
            tw_, th_ = text_size(draw, line, f_hook)
            draw_text(draw, ((tw - tw_) // 2, y), line, f_hook, fill=(255, 255, 255, 255), stroke_w=6)
            y += th_ + 14
        sw, sh = text_size(draw, sub, f_hook_sub)
        draw_text(draw, ((tw - sw) // 2, y + 16), sub, f_hook_sub, fill=(255, 200, 150, 255), stroke_w=4)

    elif kind == "brand":
        tag = lines[1] if len(lines) > 1 else "India’s public square"
        tw_, th_ = text_size(draw, tag, f_tag)
        y = max(y, safe_top + int((safe_bottom - safe_top) * 0.38))
        draw_text(draw, ((tw - tw_) // 2, y), tag, f_tag, fill=(255, 214, 140, 255), stroke_w=5)
        y += th_ + 28
        wedge = "Pick a side. Argue it live."
        ww, _ = text_size(draw, wedge, f_wedge)
        draw_text(draw, ((tw - ww) // 2, y), wedge, f_wedge, fill=(255, 255, 255, 255), stroke_w=5)

    elif kind in ("square", "arenas", "live"):
        # Caption plate docked just above SAFE_BOTTOM (never under IG captions)
        title, *rest = lines
        plate_pad = 28
        title_h = text_size(draw, title, f_title)[1]
        body_h = sum(text_size(draw, ln, f_body)[1] + 10 for ln in rest)
        chips_h = 48
        plate_h = plate_pad + title_h + 12 + body_h + chips_h + plate_pad
        plate_bottom = safe_bottom - 24
        plate_top = plate_bottom - plate_h
        draw.rounded_rectangle(
            [36, plate_top, tw - 36, plate_bottom],
            radius=28,
            fill=(8, 10, 14, 220),
        )
        draw.rounded_rectangle(
            [36, plate_top, tw - 36, plate_bottom],
            radius=28,
            outline=(*SAFFRON, 210),
            width=3,
        )
        py = plate_top + plate_pad
        tw_, th_ = text_size(draw, title, f_title)
        draw_text(draw, ((tw - tw_) // 2, py), title, f_title, fill=(*SAFFRON, 255), stroke_w=4)
        py += th_ + 12
        for line in rest:
            bw, bh = text_size(draw, line, f_body)
            draw_text(draw, ((tw - bw) // 2, py), line, f_body, fill=(*CREAM, 255), stroke_w=3)
            py += bh + 10
        chips = {
            "square": ["For you", "Following", "Real replies"],
            "arenas": ["Sports", "Politics", "Startups"],
            "live": ["Debate", "Audio", "15 seats"],
        }[kind]
        gap = 12
        widths = [text_size(draw, c, f_chip)[0] + 32 for c in chips]
        total = sum(widths) + gap * (len(chips) - 1)
        x = (tw - total) // 2
        chip_y = py + 4
        for c, cw in zip(chips, widths):
            draw.rounded_rectangle([x, chip_y, x + cw, chip_y + 40], radius=20, fill=(255, 255, 255, 28))
            draw.rounded_rectangle([x, chip_y, x + cw, chip_y + 40], radius=20, outline=(*SAFFRON, 180), width=2)
            ctw, cth = text_size(draw, c, f_chip)
            draw_text(
                draw,
                (x + (cw - ctw) // 2, chip_y + (40 - cth) // 2),
                c,
                f_chip,
                fill=(255, 255, 255, 255),
                stroke_w=2,
            )
            x += cw + gap

    elif kind == "promise":
        block_h = 0
        for line in lines:
            block_h += text_size(draw, line, f_promise)[1] + 18
        sub = "Arguments that stay on the record."
        block_h += 24 + text_size(draw, sub, f_promise_sub)[1]
        y = max(y, safe_top + (safe_bottom - safe_top - block_h) // 2)
        for line in lines:
            tw_, th_ = text_size(draw, line, f_promise)
            draw_text(draw, ((tw - tw_) // 2, y), line, f_promise, fill=(255, 220, 120, 255), stroke_w=6)
            y += th_ + 18
        sw, _ = text_size(draw, sub, f_promise_sub)
        draw_text(draw, ((tw - sw) // 2, y + 16), sub, f_promise_sub, fill=(*CREAM, 230), stroke_w=3)

    elif kind == "cta":
        line1 = "Leave one honest take"
        tw1, th1 = text_size(draw, line1, f_cta)
        soon = "Browser soft launch · Apps coming soon"
        found = "100 Founding spots — earned by real debate"
        soon_h = text_size(draw, soon, f_soon)[1]
        found_h = text_size(draw, found, f_found)[1]
        url_h = text_size(draw, "https://barathx.com", f_url)[1] + 18
        block_h = th1 + 28 + url_h + 20 + soon_h + 14 + found_h
        y = max(y, safe_top + (safe_bottom - safe_top - block_h) // 2)
        draw_text(draw, ((tw - tw1) // 2, y), line1, f_cta, fill=(255, 255, 255, 255), stroke_w=5)
        y = pill(draw, "https://barathx.com", f_url, y + th1 + 28, tw)
        y += 20
        sw, sh = text_size(draw, soon, f_soon)
        draw_text(draw, ((tw - sw) // 2, y), soon, f_soon, fill=(*CREAM, 245), stroke_w=4)
        y += sh + 14
        fw, _ = text_size(draw, found, f_found)
        draw_text(draw, ((tw - fw) // 2, y), found, f_found, fill=(255, 200, 140, 235), stroke_w=3)

    # Progress dots inside safe band (above IG caption chrome)
    draw_progress(draw, kind, tw, safe_bottom - 28)

    if fade < 1:
        r, g, b, a = layer.split()
        a = a.point(lambda p: int(p * fade))
        layer = Image.merge("RGBA", (r, g, b, a))

    return Image.alpha_composite(base, layer).convert("RGB")


def encode(frame_dir: Path, out_path: Path, pattern: str, crf: str = "22") -> None:
    subprocess.run(
        [
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
    logo = load_logo(156)
    logo_sq = load_logo(132)

    with tempfile.TemporaryDirectory(prefix="bx-wa-") as tmp:
        tmp_path = Path(tmp)
        print(f"Rendering {N_FRAMES} IG-reel + square frames @ {FPS}fps…")
        for i in range(N_FRAMES):
            t = i / FPS
            scene = scene_at(t)

            bg = make_bg(t, scene["kind"], scene["local"], W, H)
            frame = compose(
                bg,
                logo,
                scene,
                tw=W,
                th=H,
                safe_top=SAFE_TOP,
                safe_bottom=SAFE_BOTTOM,
            )
            frame = ImageEnhance.Contrast(frame).enhance(1.05)
            frame.save(tmp_path / f"reel_{i:04d}.jpg", quality=88, optimize=True)

            bg_sq = make_bg(t, scene["kind"], scene["local"], SQ_W, SQ_H)
            sq = compose(
                bg_sq,
                logo_sq,
                scene,
                tw=SQ_W,
                th=SQ_H,
                safe_top=48,
                safe_bottom=SQ_H - 64,
            )
            sq = ImageEnhance.Contrast(sq).enhance(1.05)
            sq.save(tmp_path / f"sq_{i:04d}.jpg", quality=88, optimize=True)

            if i % 24 == 0:
                print(f"  {i}/{N_FRAMES}")

        out = OUT_DIR / "barathx-whatsapp-teaser.mp4"
        square = OUT_DIR / "barathx-whatsapp-teaser-square.mp4"
        poster = OUT_DIR / "barathx-whatsapp-teaser-poster.jpg"
        print("Encoding reel…")
        encode(tmp_path, out, "reel_%04d.jpg", crf="21")
        print("Encoding square…")
        encode(tmp_path, square, "sq_%04d.jpg", crf="21")

        mid = Image.open(tmp_path / f"reel_{int(21.2 * FPS):04d}.jpg")
        mid.save(poster, quality=90, optimize=True)

        # Safe-zone audit still (tmp only)
        audit = Image.open(tmp_path / f"reel_{int(8 * FPS):04d}.jpg").copy()
        ad = ImageDraw.Draw(audit)
        ad.rectangle([0, 0, W - 1, SAFE_TOP], outline=(255, 0, 80), width=4)
        ad.rectangle([0, SAFE_BOTTOM, W - 1, H - 1], outline=(255, 0, 80), width=4)
        audit_path = Path(tempfile.gettempdir()) / "bx-wa-teaser-safezone.jpg"
        audit.save(audit_path, quality=85)
        print(f"Safe-zone audit: {audit_path}")

    for p in (out, square, poster):
        mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.relative_to(ROOT)}  ({mb:.1f} MB)")


if __name__ == "__main__":
    main()
