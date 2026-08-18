#!/usr/bin/env python3
"""Visual BarathX collab PPTX + one-pager PDF (real product screens)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pptx import Presentation
from pptx.util import Emu, Inches
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

ROOT = Path(__file__).resolve().parents[4]  # /workspace
OUT_DIR = Path(__file__).resolve().parent
SLIDES_DIR = OUT_DIR / "_slide_assets"
PPTX_OUT = OUT_DIR / "BarathX-Creator-Collab-Brief.pptx"
PDF_OUT = OUT_DIR / "BarathX-One-Pager.pdf"

W, H = 1920, 1080
NAVY = (11, 31, 58)
INK = (18, 22, 28)
ORANGE = (255, 107, 43)
SOFT = (232, 184, 138)
WHITE = (255, 255, 255)
MUTED = (170, 178, 188)
CREAM = (247, 244, 239)
DARK = (12, 14, 18)

SCREENS = {
    "landing": ROOT / "brand/carousel/screens/m01-landing.png",
    "feed": ROOT / "brand/carousel/screens/m03-feed.png",
    "reply": ROOT / "brand/carousel/screens/m04-post-detail.png",
    "profile": ROOT / "brand/carousel/screens/m06-profile.png",
    "desktop_landing": ROOT / "brand/carousel/screens/01-landing.png",
    "desktop_feed": ROOT / "brand/carousel/screens/03-feed.png",
    "home_mock": ROOT / "brand/product/home-v1/home-mockup-mobile.png",
    "live1": ROOT / "brand/ig/carousel/live-product/slide-01.jpg",
    "live3": ROOT / "brand/ig/carousel/live-product/slide-03.jpg",
    "hiw2": ROOT / "brand/ig/carousel/how-it-works/slide-02.jpg",
}


def clean_reply_screen() -> Path:
    """Strip email-confirm banner from post-detail for outreach visuals."""
    src = Image.open(SCREENS["reply"]).convert("RGBA")
    w, h = src.size
    # banner sits in top ~118px on current capture
    cropped = src.crop((0, 118, w, h))
    out = SLIDES_DIR / "reply-clean.png"
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    cropped.save(out)
    return out


def font(size, bold=False):
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    )
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ] + candidates
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def round_resize(im: Image.Image, size, radius=48):
    im = im.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def phone(screen_path: Path, height=820, radius=56, bezel=14):
    src = Image.open(screen_path).convert("RGBA")
    # crop to phone-ish if very tall
    w0, h0 = src.size
    target_ratio = 9 / 19.5
    if w0 / h0 > target_ratio + 0.05:
        # desktop-ish: center crop tall
        new_w = int(h0 * target_ratio)
        left = (w0 - new_w) // 2
        src = src.crop((left, 0, left + new_w, h0))
        w0, h0 = src.size
    ph = height
    pw = int(ph * (w0 / h0))
    screen = round_resize(src, (pw - 2 * bezel, ph - 2 * bezel), radius=radius - 8)
    frame = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    # soft shadow
    shadow = Image.new("RGBA", (pw + 30, ph + 30), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((15, 18, pw + 15, ph + 18), radius + 4, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    draw.rounded_rectangle((0, 0, pw - 1, ph - 1), radius, fill=(28, 30, 36, 255))
    frame.paste(screen, (bezel, bezel), screen)
    # notch
    nw, nh = int(pw * 0.28), 18
    draw.rounded_rectangle(((pw - nw) // 2, 10, (pw + nw) // 2, 10 + nh), 10, fill=(12, 12, 14, 255))
    return frame, shadow


def paste_phone(base, screen_path, xy, height=820):
    frame, shadow = phone(screen_path, height=height)
    sx, sy = xy
    base.alpha_composite(shadow, (sx - 15, sy - 12))
    base.alpha_composite(frame, (sx, sy))
    return frame.size


def gradient_bg(color_a=DARK, color_b=NAVY):
    img = Image.new("RGBA", (W, H), color_a + (255,))
    draw = ImageDraw.Draw(img)
    # soft orange glow top-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((1100, -400, 2200, 700), fill=ORANGE + (38,))
    gd.ellipse((-300, 600, 700, 1600), fill=(20, 60, 110, 50))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img, glow)
    return img


def text(draw, s, xy, size=48, bold=True, fill=WHITE, anchor=None):
    draw.text(xy, s, font=font(size, bold=bold), fill=fill, anchor=anchor)


def slide_title():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "BarathX", (120, 280), 84)
    text(d, "India’s public square", (120, 390), 36, bold=False, fill=ORANGE)
    text(d, "Built by Indians · for Indians · owned by Indians", (120, 460), 22, bold=False, fill=SOFT)
    text(d, "Creator collab brief", (120, 560), 28, bold=False, fill=MUTED)
    text(d, "barathx.com  ·  @getbarathx", (120, 980), 20, bold=False, fill=MUTED)
    # prefer framed mock if available else raw landing
    mock = SCREENS["home_mock"]
    if mock.exists():
        phone_im = Image.open(mock).convert("RGBA")
        w0, h0 = phone_im.size
        phone_im = phone_im.crop((0, 0, w0, int(h0 * 0.88)))
        target_h = 860
        target_w = int(phone_im.width * (target_h / phone_im.height))
        phone_im = phone_im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        x = min(1180, W - target_w - 60)
        img.alpha_composite(phone_im, (x, 110))
    else:
        paste_phone(img, SCREENS["landing"], (1280, 120), height=860)
    return img


def slide_problem():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "The problem", (120, 160), 28, bold=False, fill=ORANGE)
    text(d, "Hot takes die\nin WhatsApp.", (120, 260), 72)
    text(d, "Reels want your thumb —\nnot your opinion.", (120, 520), 32, bold=False, fill=MUTED)
    paste_phone(img, SCREENS["feed"], (1180, 110), height=880)
    return img


def slide_product():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "The product", (120, 70), 28, bold=False, fill=ORANGE)
    text(d, "Drop a take. Pick a side.\nGet real replies.", (120, 120), 48)
    text(d, "Human takes only. No AI slop.", (120, 280), 24, bold=False, fill=MUTED)
    reply = clean_reply_screen()
    hs = 780
    gap = 40
    phones = [SCREENS["landing"], SCREENS["feed"], reply]
    f, _ = phone(phones[0], height=hs)
    total_w = f.width * 3 + gap * 2
    x0 = (W - total_w) // 2
    y0 = 340
    labels = ["Sign in", "Square feed", "Real replies"]
    for i, p in enumerate(phones):
        size = paste_phone(img, p, (x0 + i * (f.width + gap), y0), height=hs)
        text(
            d,
            labels[i],
            (x0 + i * (f.width + gap) + size[0] // 2, y0 + size[1] + 28),
            20,
            bold=False,
            fill=MUTED,
            anchor="mm",
        )
    return img


def slide_live():
    """Widescreen product moment using polished live creative + desktop screen."""
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "Square · Arenas · Live", (120, 80), 28, bold=False, fill=ORANGE)
    text(d, "India’s public square — live.", (120, 140), 52)

    # left: how-it-works square creative
    left = Image.open(SCREENS["hiw2"]).convert("RGBA")
    left = round_resize(left, (760, 760), radius=36)
    img.alpha_composite(left, (120, 240))

    # right: arenas live creative
    right = Image.open(SCREENS["live3"]).convert("RGBA")
    right = round_resize(right, (760, 760), radius=36)
    img.alpha_composite(right, (1040, 240))
    return img


def slide_india():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "Why this matters", (120, 200), 28, bold=False, fill=ORANGE)
    text(d, "Built by Indians.\nFor Indians.\nOwned by Indians.", (120, 280), 64)
    text(
        d,
        "A home for honest public conversation —\nnot another feed to scroll past.",
        (120, 620),
        26,
        bold=False,
        fill=MUTED,
    )
    paste_phone(img, SCREENS["profile"], (1280, 120), height=860)
    return img


def slide_ask():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    text(d, "The ask", (120, 180), 28, bold=False, fill=ORANGE)
    text(d, "1 Reel + 1 Story.\nYour creative.", (120, 260), 60)
    text(
        d,
        "We send the exclusive link + short brief.\nYou tell us how partnerships work on your side.",
        (120, 480),
        26,
        bold=False,
        fill=MUTED,
    )
    # CTA pill
    pill = Image.new("RGBA", (520, 72), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((0, 0, 519, 71), 36, fill=ORANGE)
    img.alpha_composite(pill, (120, 640))
    text(d, "→  barathx.com", (160, 655), 28, fill=WHITE)
    text(d, "@getbarathx", (120, 760), 24, bold=False, fill=SOFT)
    paste_phone(img, SCREENS["landing"], (1280, 120), height=860)
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
    """One visual A4 page: phones + tiny copy."""
    # compose a tall visual then place in PDF
    pw, ph = 1240, 1754  # ~A4 @150dpi
    canvas_img = Image.new("RGBA", (pw, ph), DARK + (255,))
    glow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((600, -200, 1400, 500), fill=ORANGE + (40,))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    canvas_img = Image.alpha_composite(canvas_img, glow)
    d = ImageDraw.Draw(canvas_img)

    def t(s, xy, size, bold=True, fill=WHITE):
        d.text(xy, s, font=font(size, bold=bold), fill=fill)

    t("BarathX", (70, 70), 54)
    t("India’s public square", (70, 140), 26, bold=False, fill=ORANGE)
    t("Built by Indians · for Indians · owned by Indians", (70, 185), 18, bold=False, fill=SOFT)

    # three phones row
    reply = clean_reply_screen()
    phones = [SCREENS["landing"], SCREENS["feed"], reply]
    f, _ = phone(phones[0], height=780, bezel=12, radius=48)
    gap = 28
    total = f.width * 3 + gap * 2
    x0 = (pw - total) // 2
    y0 = 260
    for i, p in enumerate(phones):
        fr, sh = phone(p, height=780, bezel=12, radius=48)
        canvas_img.alpha_composite(sh, (x0 + i * (f.width + gap) - 12, y0 - 8))
        canvas_img.alpha_composite(fr, (x0 + i * (f.width + gap), y0))

    y = y0 + f.height + 70
    t("Drop a take. Pick a side. Get real replies.", (70, y), 28)
    t("Human takes only. Soft launch live.", (70, y + 50), 20, bold=False, fill=MUTED)

    # CTA bar
    bar = Image.new("RGBA", (pw - 140, 70), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle((0, 0, pw - 141, 69), 35, fill=ORANGE)
    canvas_img.alpha_composite(bar, (70, y + 120))
    t("→  barathx.com   ·   @getbarathx", (100, y + 138), 24)

    t("Creator / media intro  ·  reply with how you partner", (70, ph - 80), 16, bold=False, fill=MUTED)

    rgb = canvas_img.convert("RGB")
    tmp = SLIDES_DIR / "one-pager.png"
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    rgb.save(tmp, "PNG", optimize=True)

    c = pdfcanvas.Canvas(str(PDF_OUT), pagesize=A4)
    page_w, page_h = A4
    c.drawImage(ImageReader(tmp), 0, 0, width=page_w, height=page_h, preserveAspectRatio=False, mask="auto")
    c.showPage()
    c.save()
    print(f"Wrote {PDF_OUT}")


def main():
    builders = [
        ("01-title", slide_title),
        ("02-problem", slide_problem),
        ("03-product", slide_product),
        ("04-live", slide_live),
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
