# ============================================================
# 🎙 Voice Chat card (PNG) - screenshot jaisa dark-blue card
#   circle photo + "Voice Chat" + green dot "N participants"
# ============================================================
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
FONT_CANDIDATES = [
    os.path.join(ASSETS, "default.ttf"),
    os.path.join(ASSETS, "font.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size: int):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _gradient(w: int, h: int) -> Image.Image:
    top, bottom = (26, 54, 93), (10, 18, 36)
    base = Image.new("RGB", (w, h), top)
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return base


def _circle(photo_path, size: int) -> Image.Image:
    try:
        img = Image.open(photo_path).convert("RGB")
    except Exception:
        img = Image.open(os.path.join(ASSETS, "upic.png")).convert("RGB")
    s = min(img.size)
    img = img.crop(
        ((img.width - s) // 2, (img.height - s) // 2,
         (img.width + s) // 2, (img.height + s) // 2)
    ).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def make_vc_card(photo_path=None, participants: int = 0,
                 out_path: str = "cache/vc_card.png") -> str:
    W, H = 900, 506
    bg = _gradient(W, H).convert("RGBA")

    d = ImageDraw.Draw(bg)
    cx, cy, r = W // 2, 190, 100

    # dark ring behind photo
    d.ellipse((cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12), fill=(12, 20, 38, 255))
    bg.paste(_circle(photo_path, r * 2), (cx - r, cy - r), _circle(photo_path, r * 2))

    d = ImageDraw.Draw(bg)
    title_font = _font(48)
    d.text((cx, 355), "Voice Chat", font=title_font, fill=(255, 255, 255), anchor="mm")

    label = f"{participants} participant" + ("" if participants == 1 else "s")
    sub_font = _font(30)
    tw = d.textlength(label, font=sub_font)
    total = 22 + 14 + tw
    sx = cx - total / 2
    d.ellipse((sx, 415, sx + 22, 437), fill=(46, 204, 113))
    d.text((sx + 36, 426), label, font=sub_font, fill=(150, 175, 215), anchor="lm")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    bg.convert("RGB").save(out_path, "PNG")
    return out_path
