# Kirti Music - welcome card renderer
# Template: ShiviMusic/assets/kirti_welcome_tpl.png (pfp wali jagah transparent hai)

import colorsys
import os
import random
import re

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
TEMPLATE = os.path.join(ASSETS, "kirti_welcome_tpl.webp")
FONT_MED = os.path.join(ASSETS, "Poppins-Medium.ttf")
FONT_BOLD = os.path.join(ASSETS, "Poppins-Bold.ttf")

# pfp circle (template ke hisaab se)
PFP_CENTER = (423.5, 435.5)
PFP_RADIUS = 181

def _ensure_assets():
    """Assets folder me file na ho (sirf .py upload hui ho) to embedded data se bana do."""
    global ASSETS, TEMPLATE, FONT_MED, FONT_BOLD
    import base64
    from ShiviMusic.utils import welcome_assets_data as d

    wanted = [
        ("TEMPLATE", TEMPLATE, d.TPL_WEBP),
        ("FONT_MED", FONT_MED, d.FONT_MED),
        ("FONT_BOLD", FONT_BOLD, d.FONT_BOLD),
    ]
    for var, path, data in wanted:
        if os.path.isfile(path):
            continue
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(base64.b64decode(data))
        except Exception:
            alt = os.path.join("downloads", "welcome_assets", os.path.basename(path))
            os.makedirs(os.path.dirname(alt), exist_ok=True)
            with open(alt, "wb") as f:
                f.write(base64.b64decode(data))
            globals()[var] = alt


TEXT_DARK = (28, 24, 58)
TEXT_SOFT = (128, 122, 165)


_last_shift = [0]


def _pick_shift():
    """Har baar naya hue shift (pichhli baar se alag, kam se kam 40 degree door)."""
    while True:
        deg = random.randint(25, 335)
        diff = min(abs(deg - _last_shift[0]), 360 - abs(deg - _last_shift[0]))
        if diff >= 40:
            _last_shift[0] = deg
            return deg


def _shift_image(img, deg):
    alpha = img.getchannel("A")
    h, s, v = img.convert("RGB").convert("HSV").split()
    off = int(deg / 360 * 256)
    h = h.point(lambda x: (x + off) % 256)
    out = Image.merge("HSV", (h, s, v)).convert("RGB").convert("RGBA")
    out.putalpha(alpha)
    return out


def _shift_color(rgb, deg):
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in rgb])
    h = (h + deg / 360) % 1
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _clean_text(text, fallback):
    """Poppins sirf Latin support karta hai, baaki characters hata do."""
    text = re.sub(r"[^ -ɏ‐-‧]", "", text or "").strip()
    return text or fallback


def _spaced_width(draw, text, font, spacing):
    return sum(draw.textlength(c, font=font) + spacing for c in text) - spacing


def _draw_spaced(draw, xy, text, font, fill, spacing):
    x, y = xy
    for c in text:
        draw.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += draw.textlength(c, font=font) + spacing


def _fit(draw, text, path, size, max_w, min_size=34):
    font = _font(path, size)
    while draw.textlength(text, font=font) > max_w and size > min_size:
        size -= 2
        font = _font(path, size)
    if draw.textlength(text, font=font) > max_w:
        while len(text) > 1 and draw.textlength(text + "…", font=font) > max_w:
            text = text[:-1]
        text = text.rstrip() + "…"
    return text, font


def _circle_pfp(path, radius):
    d = radius * 2
    img = Image.open(path).convert("RGBA")
    s = min(img.size)
    left, top = (img.width - s) // 2, (img.height - s) // 2
    img = img.crop((left, top, left + s, top + s)).resize((d, d), Image.LANCZOS)
    ss = 4
    mask = Image.new("L", (d * ss, d * ss), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d * ss - 1, d * ss - 1), fill=255)
    img.putalpha(mask.resize((d, d), Image.LANCZOS))
    return img


def _gradient_text(canvas, xy, text, font, c1, c2):
    """Gradient (c1 -> c2) wala text, anchor = left-middle."""
    tmp = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(tmp).text(xy, text, font=font, fill=255, anchor="lm")
    bbox = tmp.getbbox()
    if not bbox:
        return
    x0, _, x1, _ = bbox
    grad = Image.new("RGBA", canvas.size)
    gd = ImageDraw.Draw(grad)
    span = max(1, x1 - x0)
    for x in range(x0, x1 + 1):
        t = (x - x0) / span
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)
        gd.line([(x, 0), (x, canvas.height)], fill=col)
    canvas.paste(grad, (0, 0), tmp)


def create_welcome_card(
    pfp_path,
    user_id,
    username,
    chat_title,
    out_path,
    brand="Kirti Music",
    link="t.me/kirti_bots",
    hue_shift=None,
):
    """Card banao aur out_path par save karo. out_path return hota hai."""
    _ensure_assets()
    tpl = Image.open(TEMPLATE).convert("RGBA")
    # har member ke liye alag colour theme
    shift = _pick_shift() if hue_shift is None else hue_shift
    tpl = _shift_image(tpl, shift)
    W, H = tpl.size

    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    try:
        pfp = _circle_pfp(pfp_path, PFP_RADIUS)
        canvas.paste(
            pfp,
            (int(PFP_CENTER[0] - PFP_RADIUS), int(PFP_CENTER[1] - PFP_RADIUS)),
            pfp,
        )
    except Exception:
        pass
    canvas.alpha_composite(tpl)
    draw = ImageDraw.Draw(canvas)

    # group ka naam (gradient)
    title = _clean_text(chat_title, brand)
    title, tfont = _fit(draw, title, FONT_BOLD, 76, 740)
    _gradient_text(canvas, (706, 413), title, tfont, _shift_color((86, 70, 232), shift), _shift_color((190, 80, 215), shift))
    draw = ImageDraw.Draw(canvas)

    # ID + username
    info_font = _font(FONT_MED, 40)
    draw.text((842, 537), str(user_id), font=info_font, fill=TEXT_DARK, anchor="lm")
    uname = f"@{username}" if username else "No Username"
    uname, ufont = _fit(draw, uname, FONT_MED, 40, 560, min_size=26)
    draw.text((842, 638), uname, font=ufont, fill=TEXT_DARK, anchor="lm")

    # branding (neeche)
    _draw_spaced(draw, (733, 739), brand.upper(), _font(FONT_BOLD, 28), TEXT_DARK, 7)
    link = re.sub(r"^https?://", "", link or "")
    _draw_spaced(draw, (733, 777), link, _font(FONT_MED, 23), TEXT_SOFT, 2.5)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    canvas.convert("RGB").save(out_path, "PNG")
    return out_path
