#!/usr/bin/env python3
"""Visual BarathX collab PPTX + one-pager PDF — live midnight theme screens only."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Inches
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent
SLIDES_DIR = OUT_DIR / "_slide_assets"
LIVE = OUT_DIR / "screens-live"
FONTS = OUT_DIR / "_fonts"
PPTX_OUT = OUT_DIR / "BarathX-Creator-Collab-Brief.pptx"
PDF_OUT = OUT_DIR / "BarathX-One-Pager.pdf"

W, H = 1920, 1080

# Tri-Color Midnight (matches frontend data-theme="midnight")
BG = (13, 13, 18)  # --bg #0d0d12
SURFACE = (26, 26, 36)
SAFFRON = (255, 153, 51)  # --brand #ff9933
SAFFRON_SOFT = (255, 179, 102)
GREEN = (19, 136, 8)  # --india-green
WHITE = (255, 255, 255)
MUTED = (184, 184, 196)
SOFT = (255, 210, 160)

SCREENS = {
    "m_landing": LIVE / "m-landing.png",
    "m_login": LIVE / "m-login.png",
    "m_signup": LIVE / "m-signup.png",
    "d_landing": LIVE / "d-landing.png",
    "d_login": LIVE / "d-login.png",
    "ui_square": LIVE / "ui-square.jpg",
    "ui_arenas": LIVE / "ui-arenas.jpg",
}


def font_display(size):
    for p in [FONTS / "Syne.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def font_body(size, medium=False):
    prefer = [
        FONTS / "DMSans-Medium.ttf" if medium else FONTS / "DMSans-Regular.ttf",
        FONTS / "DMSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in prefer:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def gradient_bg():
    img = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((1050, -420, 2100, 620), fill=SAFFRON + (36,))
    gd.ellipse((-420, 520, 620, 1500), fill=(0, 0, 128, 40))
    gd.ellipse((700, 700, 1400, 1400), fill=GREEN + (18,))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    return Image.alpha_composite(img, glow)


def round_resize(im: Image.Image, size, radius=40):
    im = im.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def phone(screen_path: Path, height=820, radius=52, bezel=12):
    src = Image.open(screen_path).convert("RGBA")
    w0, h0 = src.size
    # Prefer top of tall mobile captures (hero / form)
    if h0 / w0 > 1.8:
        src = src.crop((0, 0, w0, int(w0 * 2.05)))
        w0, h0 = src.size
    ph = height
    pw = max(280, int(ph * (w0 / h0)))
    screen = round_resize(src, (pw - 2 * bezel, ph - 2 * bezel), radius=radius - 6)
    frame = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    shadow = Image.new("RGBA", (pw + 36, ph + 36), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((18, 22, pw + 18, ph + 22), radius + 4, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    draw.rounded_rectangle((0, 0, pw - 1, ph - 1), radius, fill=(20, 20, 28, 255))
    # saffron hairline
    draw.rounded_rectangle((1, 1, pw - 2, ph - 2), radius - 1, outline=SAFFRON + (70,), width=2)
    frame.paste(screen, (bezel, bezel), screen)
    nw, nh = int(pw * 0.32), 16
    draw.rounded_rectangle(((pw - nw) // 2, 9, (pw + nw) // 2, 9 + nh), 8, fill=(8, 8, 12, 255))
    return frame, shadow


def paste_phone(base, path, xy, height=820):
    frame, shadow = phone(path, height=height)
    sx, sy = xy
    base.alpha_composite(shadow, (sx - 18, sy - 14))
    base.alpha_composite(frame, (sx, sy))
    return frame.size


def paste_panel(base, path, box, radius=28):
    x, y, w, h = box
    im = round_resize(Image.open(path), (w, h), radius=radius)
    # subtle border
    border = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle((0, 0, w - 1, h - 1), radius, outline=SAFFRON + (80,), width=2)
    base.alpha_composite(im, (x, y))
    base.alpha_composite(border, (x, y))


def t(draw, s, xy, size=48, display=True, fill=WHITE, medium=False, anchor=None):
    f = font_display(size) if display else font_body(size, medium=medium)
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)


def slide_title():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "BarathX", (110, 250), 92)
    t(d, "India’s public square", (110, 365), 34, display=False, fill=SAFFRON, medium=True)
    t(d, "Built by Indians · for Indians · owned by Indians", (110, 430), 22, display=False, fill=SOFT)
    t(d, "Creator collab brief", (110, 520), 26, display=False, fill=MUTED)
    t(d, "barathx.com  ·  @getbarathx", (110, 980), 20, display=False, fill=MUTED)
    paste_phone(img, SCREENS["m_landing"], (1280, 90), height=900)
    return img


def slide_problem():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "The problem", (110, 160), 24, display=False, fill=SAFFRON, medium=True)
    t(d, "Hot takes die\nin WhatsApp.", (110, 240), 70)
    t(d, "Reels want your thumb —\nnot your opinion.", (110, 500), 30, display=False, fill=MUTED)
    paste_phone(img, SCREENS["m_login"], (1240, 100), height=880)
    return img


def slide_product():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "The product", (110, 55), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Drop a take. Pick a side.\nGet real replies.", (110, 100), 46)
    t(d, "Human takes only. No AI slop.", (110, 250), 22, display=False, fill=MUTED)
    phones = [SCREENS["m_landing"], SCREENS["m_login"], SCREENS["m_signup"]]
    labels = ["Landing", "Sign in", "Create account"]
    hs = 760
    f, _ = phone(phones[0], height=hs)
    gap = 36
    total = f.width * 3 + gap * 2
    x0 = (W - total) // 2
    y0 = 310
    for i, p in enumerate(phones):
        size = paste_phone(img, p, (x0 + i * (f.width + gap), y0), height=hs)
        t(
            d,
            labels[i],
            (x0 + i * (f.width + gap) + size[0] // 2, y0 + size[1] + 26),
            18,
            display=False,
            fill=MUTED,
            anchor="mm",
        )
    return img


def slide_square():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Square · Arenas · Live", (110, 70), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "India’s public square — live.", (110, 120), 48)
    paste_panel(img, SCREENS["ui_square"], (90, 240, 850, 760), radius=24)
    paste_panel(img, SCREENS["ui_arenas"], (980, 240, 850, 760), radius=24)
    return img


def slide_india():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Why this matters", (110, 180), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Built by Indians.\nFor Indians.\nOwned by Indians.", (110, 250), 58)
    t(
        d,
        "Midnight theme. Soft launch live.\nA square that belongs here.",
        (110, 560),
        24,
        display=False,
        fill=MUTED,
    )
    # desktop landing panel
    paste_panel(img, SCREENS["d_landing"], (980, 160, 860, 760), radius=22)
    return img


def slide_ask():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "The ask", (110, 170), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "1 Reel + 1 Story.\nYour creative.", (110, 230), 56)
    t(
        d,
        "We send the exclusive link + short brief.\nYou tell us how partnerships work on your side.",
        (110, 450),
        24,
        display=False,
        fill=MUTED,
    )
    pill = Image.new("RGBA", (480, 70), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, 479, 69), 35, fill=SAFFRON)
    img.alpha_composite(pill, (110, 600))
    t(d, "→  barathx.com", (145, 615), 26, fill=(13, 13, 18))
    t(d, "@getbarathx", (110, 710), 22, display=False, fill=SOFT)
    paste_phone(img, SCREENS["m_landing"], (1280, 100), height=880)
    return img


def save_slide(img: Image.Image, name: str) -> Path:
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    path = SLIDES_DIR / f"{name}.png"
    img.convert("RGB").save(path, "PNG", optimize=True)
    return path


def build_pptx(paths):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for p in paths:
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(str(p), 0, 0, width=prs.slide_width, height=prs.slide_height)
    prs.save(PPTX_OUT)
    print(f"Wrote {PPTX_OUT}")


def build_pdf():
    pw, ph = 1240, 1754
    canvas_img = Image.new("RGBA", (pw, ph), BG + (255,))
    glow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((500, -250, 1400, 450), fill=SAFFRON + (40,))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    canvas_img = Image.alpha_composite(canvas_img, glow)
    d = ImageDraw.Draw(canvas_img)

    def tt(s, xy, size, display=True, fill=WHITE, medium=False):
        f = font_display(size) if display else font_body(size, medium=medium)
        d.text(xy, s, font=f, fill=fill)

    tt("BarathX", (64, 60), 52)
    tt("India’s public square", (64, 128), 24, display=False, fill=SAFFRON, medium=True)
    tt("Built by Indians · for Indians · owned by Indians", (64, 172), 16, display=False, fill=SOFT)

    phones = [SCREENS["m_landing"], SCREENS["m_login"], SCREENS["m_signup"]]
    f, _ = phone(phones[0], height=820, bezel=11, radius=46)
    gap = 24
    total = f.width * 3 + gap * 2
    x0 = (pw - total) // 2
    y0 = 230
    for i, p in enumerate(phones):
        fr, sh = phone(p, height=820, bezel=11, radius=46)
        canvas_img.alpha_composite(sh, (x0 + i * (f.width + gap) - 14, y0 - 10))
        canvas_img.alpha_composite(fr, (x0 + i * (f.width + gap), y0))

    y = y0 + f.height + 55
    tt("Drop a take. Pick a side. Get real replies.", (64, y), 26)
    tt("Human takes only. Soft launch live — midnight theme.", (64, y + 46), 18, display=False, fill=MUTED)

    bar = Image.new("RGBA", (pw - 128, 68), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rounded_rectangle((0, 0, pw - 129, 67), 34, fill=SAFFRON)
    canvas_img.alpha_composite(bar, (64, y + 110))
    tt("→  barathx.com   ·   @getbarathx", (90, y + 128), 22, fill=(13, 13, 18))
    tt("Creator / media intro  ·  reply with how you partner", (64, ph - 70), 14, display=False, fill=MUTED)

    tmp = SLIDES_DIR / "one-pager.png"
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    canvas_img.convert("RGB").save(tmp, "PNG", optimize=True)
    c = pdfcanvas.Canvas(str(PDF_OUT), pagesize=A4)
    page_w, page_h = A4
    c.drawImage(ImageReader(tmp), 0, 0, width=page_w, height=page_h, preserveAspectRatio=False, mask="auto")
    c.showPage()
    c.save()
    print(f"Wrote {PDF_OUT}")


def main():
    missing = [k for k, p in SCREENS.items() if not p.exists()]
    if missing:
        raise SystemExit(f"Missing live screens: {missing}. Capture from barathx.com first.")
    builders = [
        ("01-title", slide_title),
        ("02-problem", slide_problem),
        ("03-product", slide_product),
        ("04-square", slide_square),
        ("05-india", slide_india),
        ("06-ask", slide_ask),
    ]
    paths = []
    for name, fn in builders:
        print(f"render {name}…")
        paths.append(save_slide(fn(), name))
    build_pptx(paths)
    build_pdf()


if __name__ == "__main__":
    main()
