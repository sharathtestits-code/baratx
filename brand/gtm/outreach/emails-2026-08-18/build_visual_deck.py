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
    t(d, "BarathX", (110, 220), 92)
    t(d, "India’s public square", (110, 335), 34, display=False, fill=SAFFRON, medium=True)
    t(d, "Built by Indians · for Indians · owned by Indians", (110, 400), 22, display=False, fill=SOFT)
    t(
        d,
        "Exactly what India needs from social —\nreal discourse, not another foreign feed.",
        (110, 470),
        26,
        display=False,
        fill=MUTED,
    )
    t(d, "barathx.com  ·  @getbarathx", (110, 980), 20, display=False, fill=MUTED)
    paste_phone(img, SCREENS["m_landing"], (1280, 90), height=900)
    return img


def slide_problem():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "The problem", (110, 140), 24, display=False, fill=SAFFRON, medium=True)
    t(d, "Hot takes die\nin WhatsApp.", (110, 210), 64)
    t(
        d,
        "Youth hours go to foreign apps.\nReels want your thumb — not your opinion.\nIndia needs its own square for real discourse.",
        (110, 450),
        26,
        display=False,
        fill=MUTED,
    )
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
    t(d, "Built for India", (110, 150), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Exactly what you’re\nlooking for —\nspecially for India.", (110, 210), 44)
    t(d, "Built by Indians.\nFor Indians.\nOwned by Indians.", (110, 480), 36)
    t(
        d,
        "Not a US clone with India skin.\nA public square for sided debate — made here.",
        (110, 680),
        22,
        display=False,
        fill=MUTED,
    )
    paste_panel(img, SCREENS["d_landing"], (980, 160, 860, 760), radius=22)
    return img


def slide_human():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Human first", (110, 140), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "No AI slop.\nOnly real humans.", (110, 200), 58)
    bullets = [
        "Human takes only — AI drafts flagged & demoted",
        "Real replies rise. Bot / paste-AI sinks.",
        "Agree / Disagree — sided talk, not scroll theater",
        "Live rooms: human voices only",
    ]
    y = 420
    for line in bullets:
        t(d, "→  " + line, (110, y), 24, display=False, fill=MUTED)
        y += 58
    paste_phone(img, SCREENS["m_landing"], (1280, 100), height=880)
    return img


def slide_safety():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Safety we ship", (110, 100), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Safe square.\nNot an afterthought.", (110, 160), 52)
    left = [
        "No adult / sexual content (posts, DMs, Live)",
        "We do not encourage adult content — blocked by design",
        "Report → review · spam & harassment paths",
        "Community guidelines in-product",
    ]
    right = [
        "India DPDP — consent, export, delete",
        "Passwords hashed · private email/phone",
        "OTP / Google rate limits · session kill",
        "Country-based blocks next (abuse / adult traffic)",
    ]
    y = 380
    for line in left:
        t(d, "•  " + line, (110, y), 22, display=False, fill=MUTED)
        y += 52
    y = 380
    for line in right:
        t(d, "•  " + line, (1000, y), 22, display=False, fill=MUTED)
        y += 52
    t(d, "Soft launch — we treat trust as product.", (110, 980), 20, display=False, fill=SOFT)
    return img


def slide_no_monetization():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Incentives", (110, 140), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Not an ads feed.\nNot selling your mood.", (110, 200), 52)
    bullets = [
        "Built for discourse — not engagement farming",
        "No ads marketplace on the square (by design)",
        "No pay-to-post / cash-for-signup growth games",
        "Status earned by real debate, not installs",
        "Foreign algorithms don’t own this product",
    ]
    y = 420
    for line in bullets:
        t(d, "→  " + line, (110, y), 24, display=False, fill=MUTED)
        y += 58
    paste_panel(img, SCREENS["ui_square"], (1180, 200, 660, 700), radius=22)
    return img


def slide_ask():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    t(d, "Next step", (110, 170), 22, display=False, fill=SAFFRON, medium=True)
    t(d, "Try the square.\nTell us what breaks.", (110, 230), 52)
    t(
        d,
        "Soft launch live at barathx.com\n2 minutes: pick a side · leave one take.\nHappy to take 10 minutes if this is useful.",
        (110, 450),
        24,
        display=False,
        fill=MUTED,
    )
    pill = Image.new("RGBA", (480, 70), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, 479, 69), 35, fill=SAFFRON)
    img.alpha_composite(pill, (110, 640))
    t(d, "→  barathx.com", (145, 655), 26, fill=(13, 13, 18))
    t(d, "@getbarathx  ·  hello@barathx.com", (110, 750), 22, display=False, fill=SOFT)
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

    tt("BarathX", (64, 50), 48)
    tt("India’s public square", (64, 112), 22, display=False, fill=SAFFRON, medium=True)
    tt("Exactly what India needs from social — built here, owned here.", (64, 152), 15, display=False, fill=SOFT)
    tt("Built by Indians · for Indians · owned by Indians", (64, 182), 14, display=False, fill=MUTED)

    phones = [SCREENS["m_landing"], SCREENS["m_login"], SCREENS["m_signup"]]
    f, _ = phone(phones[0], height=780, bezel=11, radius=46)
    gap = 24
    total = f.width * 3 + gap * 2
    x0 = (pw - total) // 2
    y0 = 250
    for i, p in enumerate(phones):
        fr, sh = phone(p, height=780, bezel=11, radius=46)
        canvas_img.alpha_composite(sh, (x0 + i * (f.width + gap) - 14, y0 - 10))
        canvas_img.alpha_composite(fr, (x0 + i * (f.width + gap), y0))

    y = y0 + f.height + 40
    tt("Drop a take. Pick a side. Get real replies.", (64, y), 24)
    # feature chips
    chips = [
        "No AI slop — humans only",
        "No adult content · safe square",
        "Not an ads feed",
        "Indian-built & owned",
    ]
    cy = y + 50
    x = 64
    for chip in chips:
        fnt = font_body(15, medium=True)
        tw = fnt.getlength(chip) if hasattr(fnt, "getlength") else len(chip) * 8
        bw = int(tw + 28)
        chip_img = Image.new("RGBA", (bw, 36), (0, 0, 0, 0))
        ImageDraw.Draw(chip_img).rounded_rectangle((0, 0, bw - 1, 35), 18, fill=SURFACE, outline=SAFFRON + (120,))
        canvas_img.alpha_composite(chip_img, (x, cy))
        tt(chip, (x + 14, cy + 8), 15, display=False, fill=SOFT, medium=True)
        x += bw + 12
        if x > pw - 200:
            x = 64
            cy += 44

    bar = Image.new("RGBA", (pw - 128, 64), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rounded_rectangle((0, 0, pw - 129, 63), 32, fill=SAFFRON)
    canvas_img.alpha_composite(bar, (64, ph - 160))
    tt("→  barathx.com   ·   @getbarathx", (90, ph - 142), 20, fill=(13, 13, 18))
    tt("Human discourse · soft launch live", (64, ph - 70), 14, display=False, fill=MUTED)

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
        ("05-human", slide_human),
        ("06-safety", slide_safety),
        ("07-no-ads", slide_no_monetization),
        ("08-india", slide_india),
        ("09-ask", slide_ask),
    ]
    paths = []
    for name, fn in builders:
        print(f"render {name}…")
        paths.append(save_slide(fn(), name))
    build_pptx(paths)
    build_pdf()


if __name__ == "__main__":
    main()
