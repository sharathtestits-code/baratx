#!/usr/bin/env python3
"""
Render BarathX daily cross-post stills (WhatsApp + X + LinkedIn).

Layouts rotate by product feature + optional India trend hook.
1080×1080 JPGs. Use --approve for finals (no MOCKUP ribbon).
"""

from __future__ import annotations

import argparse
import glob
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from features import Feature, feature_by_key, feature_for_date

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / "brand" / "social" / "whatsapp" / "screens" / "live-2026-08-19"
LOGO = ROOT / "brand" / "baratx-logo-avatar.png"
DAILY = Path(__file__).resolve().parent

W = H = 1080
DARK = (10, 10, 14)
WHITE = (255, 255, 255)
CREAM = (255, 248, 235)
SAFFRON = (255, 103, 31)
MUTED = (150, 150, 160)
SLATE = (28, 30, 38)
TEAL = (46, 196, 182)

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

SCREEN_FILES = {
    "square": "square-mobile.png",
    "arenas": "arenas-mobile.png",
    "live": "live-mobile.png",
    "explore": "explore-mobile.png",
    "home": "home-mobile.png",
    "rewards": "rewards-mobile.png",
    "landing": "landing-mobile.png",
    "search": "search-mobile.png",
    "signup": "signup-mobile.png",
    "get_app": "get-app-mobile.png",
    "login_phone": "login-mobile.png",
    "soft_launch_phone": "soft-launch-phone-mobile.png",
}


def fnt(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def canvas(accent: tuple[int, int, int] = SAFFRON) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    for i, y in enumerate(range(0, H, 8)):
        shade = 12 + (i % 3)
        d.line([(0, y), (W, y)], fill=(shade, shade, shade + 2), width=1)
    d.rectangle([0, 0, 14, H], fill=accent)
    return img, d


def stamp(base: Image.Image, d: ImageDraw.ImageDraw, *, pill: str) -> None:
    logo = Image.open(LOGO).convert("RGBA").resize((52, 52), Image.Resampling.LANCZOS)
    mask = Image.new("L", (52, 52), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 51, 51], fill=255)
    circ = Image.new("RGBA", (52, 52), (0, 0, 0, 0))
    circ.paste(logo, (0, 0), mask)
    base.paste(circ, (36, 32), circ)
    d.text((102, 42), "BarathX", font=fnt(28), fill=CREAM)
    bb = d.textbbox((0, 0), pill, font=fnt(18))
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = W - 36 - tw - 24
    d.rounded_rectangle([x0, 36, x0 + tw + 24, 36 + th + 14], radius=16, fill=SAFFRON)
    d.text((x0 + 12, 43), pill, font=fnt(18), fill=DARK)


def cta(d: ImageDraw.ImageDraw, text: str) -> None:
    d.rectangle([0, H - 64, W, H], fill=SAFFRON)
    d.text((36, H - 46), text, font=fnt(24), fill=DARK)


def approval_ribbon(base: Image.Image) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon([(W - 260, 0), (W, 0), (W, 260)], fill=(255, 103, 31, 230))
    tmp = Image.new("RGBA", (220, 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 4), "MOCKUP · APPROVE", font=fnt(18), fill=DARK)
    rotated = tmp.rotate(-45, expand=True, fillcolor=(0, 0, 0, 0))
    overlay.paste(rotated, (W - 210, 8), rotated)
    composed = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    base.paste(composed, (0, 0))


def phone(screen_key: str, height: int = 520) -> Image.Image:
    name = SCREEN_FILES.get(screen_key, "square-mobile.png")
    path = LIVE / name
    if not path.exists():
        path = LIVE / "square-mobile.png"
    ui = Image.open(path).convert("RGBA")
    scale = height / ui.height
    nw, nh = int(ui.width * scale), int(ui.height * scale)
    ui = ui.resize((nw, nh), Image.Resampling.LANCZOS)
    pad = 12
    frame = Image.new("RGBA", (nw + pad * 2, nh + pad * 2), (28, 28, 34, 255))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=36, outline=SAFFRON, width=3)
    frame.paste(ui, (pad, pad), ui)
    return frame


def _wrap(d: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = (text or "").split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textbbox((0, 0), trial, font=font)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def render_still(
    *,
    feature: Feature,
    trend: str,
    slot: str,
    channel: str,
    for_approval: bool,
) -> Image.Image:
    """channel: shared | linkedin | whatsapp. slot: morning | evening."""
    pill = f"{'AM' if slot == 'morning' else 'PM'} · {feature.name.upper()[:10]}"
    trend_line = (trend or "India is talking").strip()
    if len(trend_line) > 72:
        trend_line = trend_line[:69] + "…"

    tpl = feature.template
    if channel == "linkedin":
        tpl = "linkedin_board"
    elif channel == "whatsapp" and slot == "evening":
        tpl = "whatsapp_trio"

    if tpl == "phone_right":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 110), trend_line.upper()[:40], font=fnt(20), fill=SAFFRON)
        d.text((36, 150), feature.name, font=fnt(54), fill=WHITE)
        for i, line in enumerate(_wrap(d, feature.one_liner, fnt(28, False), 520)[:3]):
            d.text((36, 230 + i * 40), line, font=fnt(28, bold=False), fill=MUTED)
        y = 360
        for b in feature.bullets[:3]:
            d.ellipse([44, y + 8, 60, y + 24], fill=SAFFRON)
            d.text((76, y), b, font=fnt(26), fill=CREAM)
            y += 48
        ph = phone(feature.screen, 500)
        ph = ph.resize((int(ph.width * 0.9), int(ph.height * 0.9)), Image.Resampling.LANCZOS)
        layer = base.convert("RGBA")
        layer.paste(ph, (W - ph.width - 18, 380), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Join free → barathx.com")
        out = layer.convert("RGB")

    elif tpl == "split_cards":
        base, d = canvas(TEAL)
        stamp(base, d, pill=pill)
        d.text((36, 110), "TRENDING · INDIA", font=fnt(20), fill=SAFFRON)
        for i, line in enumerate(_wrap(d, trend_line, fnt(40), W - 72)[:2]):
            d.text((36, 150 + i * 52), line, font=fnt(40), fill=WHITE)
        d.text((36, 280), f"Feature · {feature.name}", font=fnt(24), fill=SAFFRON)
        d.rounded_rectangle([36, 340, W // 2 - 16, 720], radius=20, fill=SLATE)
        d.rounded_rectangle([W // 2 + 8, 340, W - 36, 720], radius=20, fill=SLATE)
        d.text((56, 380), "Agree", font=fnt(36), fill=TEAL)
        d.text((W // 2 + 28, 380), "Disagree", font=fnt(36), fill=SAFFRON)
        d.text((56, 460), feature.one_liner[:48], font=fnt(22, False), fill=MUTED)
        d.text((W // 2 + 28, 460), "Pick a side. On the record.", font=fnt(22, False), fill=MUTED)
        ph = phone(feature.screen, 280)
        layer = base.convert("RGBA")
        layer.paste(ph, ((W - ph.width) // 2, 760), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Open Arenas → barathx.com")
        out = layer.convert("RGB")

    elif tpl == "phone_center":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 110), trend_line.upper()[:42], font=fnt(20), fill=SAFFRON)
        d.text((36, 155), "Argue it live.", font=fnt(52), fill=WHITE)
        d.text((36, 225), feature.one_liner[:56], font=fnt(26, False), fill=MUTED)
        ph = phone(feature.screen, 560)
        layer = base.convert("RGBA")
        layer.paste(ph, ((W - ph.width) // 2, 300), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Enter Live → barathx.com")
        out = layer.convert("RGB")

    elif tpl == "search_focus":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 120), "EXPLORE", font=fnt(22), fill=SAFFRON)
        d.text((36, 165), "People or topics.", font=fnt(48), fill=WHITE)
        d.text((36, 235), "Not a buried dump.", font=fnt(48), fill=SAFFRON)
        d.rounded_rectangle([36, 340, W - 36, 430], radius=28, outline=SAFFRON, width=3)
        d.text((60, 368), f"Try @{trend_line.split()[0][:16].lower() if trend_line else 'username'} · or cricket", font=fnt(26, False), fill=MUTED)
        for i, b in enumerate(feature.bullets[:3]):
            d.text((48, 480 + i * 50), f"→  {b}", font=fnt(28), fill=CREAM)
        ph = phone(feature.screen, 360)
        layer = base.convert("RGBA")
        layer.paste(ph, (W - ph.width - 24, 640), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Get app → barathx.com/get-app")
        out = layer.convert("RGB")

    elif tpl == "bold_type":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 140), "FEEDS ARE FULL OF AI", font=fnt(22), fill=SAFFRON)
        d.text((36, 190), "We rank", font=fnt(64), fill=WHITE)
        d.text((36, 270), "humans first.", font=fnt(64), fill=SAFFRON)
        d.text((36, 380), trend_line, font=fnt(24, False), fill=MUTED)
        y = 460
        for b in feature.bullets:
            d.rounded_rectangle([36, y, W - 36, y + 70], radius=16, fill=SLATE)
            d.text((60, y + 18), b, font=fnt(28), fill=CREAM)
            y += 90
        cta(d, "Human takes only → barathx.com")
        out = base

    elif tpl == "founding_banner":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 130), "FOUNDING 100", font=fnt(22), fill=SAFFRON)
        d.text((36, 175), "Earned,", font=fnt(56), fill=WHITE)
        d.text((36, 250), "not bought.", font=fnt(56), fill=SAFFRON)
        for i, line in enumerate(_wrap(d, feature.one_liner, fnt(26, False), W - 72)[:4]):
            d.text((36, 350 + i * 36), line, font=fnt(26, bold=False), fill=MUTED)
        ph = phone(feature.screen, 420)
        layer = base.convert("RGBA")
        layer.paste(ph, (W - ph.width - 20, 520), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Open a debate → barathx.com")
        out = layer.convert("RGB")

    elif tpl == "launch_hero":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 140), "SOFT LAUNCH", font=fnt(22), fill=SAFFRON)
        d.text((36, 190), "Install. Phone OTP.", font=fnt(48), fill=WHITE)
        d.text((36, 255), "You’re in.", font=fnt(48), fill=SAFFRON)
        d.text((36, 340), trend_line, font=fnt(24, False), fill=MUTED)
        for i, b in enumerate(feature.bullets[:3]):
            d.text((48, 400 + i * 48), f"•  {b}", font=fnt(28), fill=CREAM)
        ph = phone(feature.screen, 400)
        layer = base.convert("RGBA")
        layer.paste(ph, ((W - ph.width) // 2, 560), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Get app → barathx.com/get-app")
        out = layer.convert("RGB")

    elif tpl == "linkedin_board":
        base, d = canvas()
        stamp(base, d, pill=f"LI · {feature.name.upper()[:8]}")
        d.text((36, 120), "BUILDING IN PUBLIC", font=fnt(20), fill=SAFFRON)
        d.text((36, 165), feature.name, font=fnt(48), fill=WHITE)
        for i, line in enumerate(_wrap(d, feature.one_liner, fnt(28, False), W - 72)[:3]):
            d.text((36, 240 + i * 38), line, font=fnt(28, bold=False), fill=MUTED)
        d.rounded_rectangle([36, 370, 560, 720], radius=22, fill=SLATE)
        d.text((56, 400), f"India hook: {trend_line[:40]}", font=fnt(20), fill=SAFFRON)
        for i, b in enumerate(feature.bullets[:4]):
            d.text((56, 450 + i * 48), f"→  {b}", font=fnt(24, False), fill=CREAM)
        ph = phone(feature.screen, 420)
        layer = base.convert("RGBA")
        layer.paste(ph, (W - ph.width - 28, 360), ph)
        d2 = ImageDraw.Draw(layer)
        cta(d2, "Get app → barathx.com/get-app")
        out = layer.convert("RGB")

    elif tpl == "whatsapp_trio":
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 120), "TONIGHT ON BARATHX", font=fnt(20), fill=SAFFRON)
        d.text((36, 165), feature.name, font=fnt(48), fill=WHITE)
        d.text((36, 235), feature.one_liner[:52], font=fnt(24, False), fill=MUTED)
        keys = [feature.screen, "square", "live"]
        xs = [40, 380, 720]
        labels = [feature.name[:8], "Square", "Live"]
        layer = base.convert("RGBA")
        for key, x, label in zip(keys, xs, labels):
            ph = phone(key, 380)
            ph = ph.resize((int(ph.width * 0.7), int(ph.height * 0.7)), Image.Resampling.LANCZOS)
            layer.paste(ph, (x, 320), ph)
        d2 = ImageDraw.Draw(layer)
        for label, x in zip(labels, xs):
            d2.text((x + 36, 860), label, font=fnt(22), fill=SAFFRON)
        cta(d2, "Open → barathx.com")
        out = layer.convert("RGB")

    else:
        base, d = canvas()
        stamp(base, d, pill=pill)
        d.text((36, 160), feature.name, font=fnt(52), fill=WHITE)
        d.text((36, 240), feature.one_liner[:60], font=fnt(28, False), fill=MUTED)
        cta(d, "barathx.com")
        out = base

    if for_approval:
        approval_ribbon(out)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="IST date YYYY-MM-DD")
    p.add_argument("--approve", action="store_true", help="Final (no MOCKUP ribbon)")
    p.add_argument("--feature", default="", help="Override feature key")
    p.add_argument("--trend", default="", help="India trend / headline hook")
    args = p.parse_args()

    d = date.fromisoformat(args.date)
    feature = feature_by_key(args.feature) or feature_for_date(d)
    trend = args.trend.strip() or "India is talking — leave a take"
    out_dir = DAILY / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    for_approval = not args.approve

    mapping = [
        ("morning-shared.jpg", "morning", "shared"),
        ("morning-linkedin.jpg", "morning", "linkedin"),
        ("evening-shared.jpg", "evening", "shared"),
        ("evening-whatsapp.jpg", "evening", "whatsapp"),
    ]
    print(f"Rendering → {out_dir} feature={feature.key} trend={trend[:50]!r} approval={for_approval}")
    for name, slot, channel in mapping:
        img = render_still(
            feature=feature,
            trend=trend,
            slot=slot,
            channel=channel,
            for_approval=for_approval,
        )
        path = out_dir / name
        img.save(path, quality=92, optimize=True)
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
