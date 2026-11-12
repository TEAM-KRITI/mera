# ===========================================================
# 🖼 NOW PLAYING THUMBNAIL — blurred song-image background
#
# Design: song ki image poore background me BLUR hoti hai, left me
# rounded album art, right me title + channel, progress bar,
# brand pill (KIRTI BOTS), controls, volume bar.
#
# Use:
#   from ShiviMusic.utils.thumbnails import get_thumb
#   thumb = await get_thumb(videoid)
#
# 🔤 TITLE FONT: song title ke liye wahi font file lagao jo tumhare
# purane thumbnail (Duvidha wala) me use hota hai. File ko
#   ShiviMusic/assets/title_font.ttf
# naam se rakh do -> title usi font me aayega.
# ===========================================================

import asyncio
import colorsys
import glob
import io
import os
import random
import traceback

import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
BLUR_RADIUS = 38  # zyada = aur blur
BRAND = "KIRTI BOTS"  # pill me dikhne wala naam

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")


def _a(name):
    return os.path.join(_ASSETS, name)


# Song title font (pehli mili hui file use hoti hai)
_TITLE_FONTS = [
    _a("title_font.ttf"),
    _a("font.ttf"),
    _a("font2.ttf"),
    _a("font3.ttf"),
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
# Baaki text (channel, time, brand)
_UI_FONTS = [
    _a("font2.ttf"),
    _a("font.ttf"),
    "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _load(cands, size):
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)  # Pillow>=10.1 (FreeType)
    except Exception:
        return ImageFont.load_default()


def _cover_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    iw, ih = img.size
    sc = max(w / iw, h / ih)
    img = img.resize((int(iw * sc) + 1, int(ih * sc) + 1), Image.LANCZOS)
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))


def _blurred_background(cover: Image.Image) -> Image.Image:
    bg = _cover_crop(cover, W, H).filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(bg, dark, 0.45)  # dark overlay -> white text clear


def _rounded(img: Image.Image, radius: int) -> Image.Image:
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    img.putalpha(mask)
    return img


def _fit_text(draw, text: str, font, max_w: int) -> str:
    text = str(text or "")
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


def _random_accent():
    """Har baar naya bright color: (accent, title_color, pill_text_color)."""
    h = random.random()
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, random.uniform(0.6, 0.9), 1.0)]
    # title ke liye thoda halka (readable on dark bg)
    tr, tg, tb = [int(x * 255) for x in colorsys.hsv_to_rgb(h, random.uniform(0.35, 0.55), 1.0)]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    pill_txt = (20, 20, 20, 255) if lum > 140 else (255, 255, 255, 255)
    return (r, g, b, 255), (tr, tg, tb, 255), pill_txt


def compose_thumb(cover: Image.Image, title: str, artist: str, duration: str, path: str):
    cover = cover.convert("RGB")
    accent, title_col, pill_txt_col = _random_accent()
    canvas = _blurred_background(cover).convert("RGBA")

    # ---- album art (left, rounded) ----
    S = 500
    ax, ay = 80, 110
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (ax, ay + 16, ax + S, ay + S + 16), 44, fill=(0, 0, 0, 150)
    )
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(26)))
    canvas.alpha_composite(_rounded(_cover_crop(cover, S, S), 44), (ax, ay))

    # ---- underline: album art ke neeche color wali line (har baar alag color) ----
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        (ax + 20, ay + S + 20, ax + S - 20, ay + S + 30), 5, fill=accent[:3] + (200,)
    )
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(canvas).rounded_rectangle(
        (ax + 20, ay + S + 20, ax + S - 20, ay + S + 28), 4, fill=accent
    )

    # ---- translucent overlay layer (buttons, tracks) ----
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    o = ImageDraw.Draw(ov)
    white = (255, 255, 255, 255)
    soft = (255, 255, 255, 90)

    # star + more buttons
    for cx in (1110, 1160):
        o.ellipse((cx - 20, 145, cx + 20, 185), fill=(255, 255, 255, 80))
    # star outline
    import math

    sx, sy, R, r = 1110, 165, 10, 4.2
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    o.line(pts + [pts[0]], fill=white, width=2)
    for dy in (-8, 0, 8):  # 3 dots
        o.ellipse((1160 - 2.5, 165 + dy - 2.5, 1160 + 2.5, 165 + dy + 2.5), fill=white)

    # progress bar
    tx0, tx1, by = 640, 1200, 304
    o.rounded_rectangle((tx0, by - 4, tx1, by + 4), 4, fill=(255, 255, 255, 85))
    kx = tx0 + int((tx1 - tx0) * 0.25)
    o.rounded_rectangle((tx0, by - 4, kx, by + 4), 4, fill=white)
    o.ellipse((kx - 8, by - 8, kx + 8, by + 8), fill=white)

    # brand pill
    f_ui = _load(_UI_FONTS, 20)
    pill_txt = BRAND.upper()
    pw = int(ImageDraw.Draw(ov).textlength(pill_txt, font=f_ui)) + 34
    pcx, pcy = 920, 336
    o.rounded_rectangle((pcx - pw // 2, pcy - 16, pcx + pw // 2, pcy + 16), 16, fill=accent)
    o.text((pcx, pcy), pill_txt, font=f_ui, fill=pill_txt_col, anchor="mm")

    # controls: prev | pause | next
    my = 480
    px = 785
    o.rectangle((px - 27, my - 23, px - 22, my + 23), fill=white)
    o.polygon([(px - 18, my), (px + 2, my - 23), (px + 2, my + 23)], fill=white)
    o.polygon([(px + 2, my), (px + 28, my - 23), (px + 28, my + 23)], fill=white)
    o.rounded_rectangle((903, my - 23, 914, my + 23), 3, fill=white)
    o.rounded_rectangle((927, my - 23, 938, my + 23), 3, fill=white)
    nx = 1055
    o.polygon([(nx - 28, my - 23), (nx - 28, my + 23), (nx - 2, my)], fill=white)
    o.polygon([(nx - 2, my - 23), (nx - 2, my + 23), (nx + 18, my)], fill=white)
    o.rectangle((nx + 22, my - 23, nx + 27, my + 23), fill=white)

    # volume row
    vy = 560
    o.polygon([(721, vy - 5), (729, vy - 5), (738, vy - 13), (738, vy + 13), (729, vy + 5), (721, vy + 5)], fill=white)
    o.arc((734, vy - 9, 748, vy + 9), -55, 55, fill=white, width=2)
    o.arc((734, vy - 15, 756, vy + 15), -55, 55, fill=white, width=2)
    o.rounded_rectangle((765, vy - 4, 1120, vy + 4), 4, fill=white)

    # chat/lyrics bubble + queue list icons
    bx, byy = 881, 608
    o.rounded_rectangle((bx, byy, bx + 30, byy + 24), 5, outline=white, width=3)
    o.polygon([(bx + 8, byy + 24), (bx + 8, byy + 34), (bx + 18, byy + 24)], fill=white)
    o.rectangle((bx + 10, byy + 7, bx + 13, byy + 17), fill=white)
    o.rectangle((bx + 17, byy + 7, bx + 20, byy + 17), fill=white)
    lx = 960
    for i, ly in enumerate((612, 622, 632)):
        o.ellipse((lx, ly - 3, lx + 6, ly + 3), fill=white)
        o.rounded_rectangle((lx + 14, ly - 2, lx + 38, ly + 2), 2, fill=white)

    canvas.alpha_composite(ov)
    d = ImageDraw.Draw(canvas)

    # ---- text ----
    f_title = _load(_TITLE_FONTS, 56)
    d.text((640, 168), _fit_text(d, title, f_title, 420), font=f_title, fill=title_col, anchor="lm")
    f_artist = _load(_UI_FONTS, 30)
    d.text((640, 221), _fit_text(d, artist or "Unknown", f_artist, 540), font=f_artist,
           fill=(205, 205, 205, 255), anchor="lm")

    f_t = _load(_UI_FONTS, 17)
    d.text((tx0, 336), "0:00", font=f_t, fill=white, anchor="lm")
    d.text((tx1, 337), "-" + (duration or "0:00"), font=f_t, fill=white, anchor="rm")

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    canvas.convert("RGB").save(path, "JPEG", quality=92)
    return path


async def _download(session, vidid: str):
    for q in ("maxresdefault", "sddefault", "hqdefault", "mqdefault"):
        try:
            async with session.get(
                f"https://i.ytimg.com/vi/{vidid}/{q}.jpg",
                timeout=aiohttp.ClientTimeout(total=8),
            ) as r:
                if r.status == 200:
                    img = Image.open(io.BytesIO(await r.read())).convert("RGB")
                    if img.width > 200:
                        return img
        except Exception:
            continue
    return None


async def _meta(session, videoid: str):
    """(title, artist, duration) -- jo library mile usse; sab fail ho to oEmbed."""
    url = f"https://www.youtube.com/watch?v={videoid}"
    # 1) py_yt
    try:
        from py_yt import VideosSearch

        r = (await VideosSearch(url, limit=1).next())["result"][0]
        return r.get("title"), (r.get("channel") or {}).get("name"), r.get("duration")
    except Exception:
        pass
    # 2) youtubesearchpython (async)
    try:
        from youtubesearchpython.__future__ import VideosSearch

        r = (await VideosSearch(url, limit=1).next())["result"][0]
        return r.get("title"), (r.get("channel") or {}).get("name"), r.get("duration")
    except Exception:
        pass
    # 3) youtubesearchpython (sync)
    try:
        from youtubesearchpython import VideosSearch

        res = await asyncio.get_running_loop().run_in_executor(
            None, lambda: VideosSearch(url, limit=1).result()
        )
        r = res["result"][0]
        return r.get("title"), (r.get("channel") or {}).get("name"), r.get("duration")
    except Exception:
        pass
    # 4) YouTube oEmbed (kisi library ki zarurat nahi)
    try:
        async with session.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            timeout=aiohttp.ClientTimeout(total=8),
        ) as r:
            if r.status == 200:
                j = await r.json()
                return j.get("title"), j.get("author_name"), None
    except Exception:
        pass
    return None, None, None


async def get_thumb(videoid, *args, title=None, artist=None, duration=None, **kwargs):
    """Blur-background now-playing thumbnail banata hai. Fail => YouTube thumb URL.

    Purane code ke saare call styles chalte hain: get_thumb(vidid),
    get_thumb(vidid, user_id), get_thumb(vidid, a, b, c ...) -- extra args ignore.
    """
    videoid = str(videoid)
    title = title if isinstance(title, str) else None
    artist = artist if isinstance(artist, str) else None
    duration = duration if isinstance(duration, str) else None
    fallback = f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg"

    # har baar naya color chahiye isliye cache reuse nahi karte; purani files hata do
    os.makedirs("cache", exist_ok=True)
    for old in glob.glob(f"cache/{videoid}_np_*.jpg"):
        try:
            os.remove(old)
        except Exception:
            pass
    path = f"cache/{videoid}_np_{random.randint(1000, 9999)}.jpg"
    try:
        async with aiohttp.ClientSession() as session:
            if not (title and artist and duration):
                t, a, dur = await _meta(session, videoid)
                title, artist, duration = title or t, artist or a, duration or dur
            cover = await _download(session, videoid)
        if cover is None:
            print(f"[THUMB] cover download fail for {videoid}")
            return fallback
        await asyncio.get_running_loop().run_in_executor(
            None,
            compose_thumb,
            cover,
            title or "Unknown Title",
            artist or "YouTube",
            duration or "0:00",
            path,
        )
        return path
    except Exception:
        print("[THUMB] FAIL -> fallback image. Error:")
        traceback.print_exc()
        return fallback


gen_thumb = get_thumb  # purane naam se bhi chale
