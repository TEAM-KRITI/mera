# ===========================================================
# 🎧 RECOMMENDATIONS — queue khatam hone par "tap below to play
# next track" wala message (Previous + 5 songs + Random AI track)
#
# ✅ Country filter: sirf usi country ke songs (utils/region.py)
# ✅ "More" button: unlimited songs (pool khatam ho to naye Mix se refill)
# ✅ FIX: same song ke duplicates (lyrics/slowed/cover) nahi aate
# ===========================================================

import asyncio
import collections
import itertools
import os
import random
import re
import time

import aiohttp
from PIL import Image, ImageDraw, ImageFont
from pyrogram import enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from py_yt import VideosSearch

from ShiviMusic.utils.autoplay import (
    _extract_candidates,
    _extract_mix_candidates,
    _fetch_mix_sync,
    _history,
)
from ShiviMusic.utils.region import (
    filter_by_region,
    get_seed_region,
    region_label,
)

_NOISE = re.compile(
    r"\((.*?)\)|\[(.*?)\]|\b(?:official|video|audio|lyrical|lyrics|full song|"
    r"hd|4k|music video)\b|\bfeat\.?.*$",
    re.I,
)


def short_title(title: str, limit: int = 30) -> str:
    t = _NOISE.sub("", title or "")
    t = re.sub(r"\s*[|\-–—].*$", lambda m: m.group(0) if len(t) <= limit else "", t)
    t = re.sub(r"\s+", " ", t).strip(" -|")
    t = t or (title or "")
    return (t[: limit - 1] + "…") if len(t) > limit else t


# ---------------------------------------------------------
# 🔁 Duplicate-song detection (title tokens based)
# ---------------------------------------------------------
_VERSION_WORDS = re.compile(
    r"\b(?:official|video|audio|lyrical|lyrics|lyric|full|song|songs|hd|4k|music|"
    r"remix|slowed|reverb|lofi|cover|version|reprise|unplugged|acoustic|live|"
    r"new|latest|feat|ft|featuring|the|and|with|from|movie|film|ost|mashup|"
    r"8d|bass|boosted|sped|up|nightcore|status|hindi|english)\b",
    re.I,
)


def _tokens(title: str) -> frozenset:
    """Title ke 'asli' words (remix/lyrics jaise version words hata kar)."""
    raw = (title or "").lower()
    t = re.sub(r"[\(\[\{].*?[\)\]\}]", " ", raw)
    t = _VERSION_WORDS.sub(" ", t)
    words = {w for w in re.findall(r"\w+", t) if len(w) > 1}
    if not words:
        words = {w for w in re.findall(r"\w+", raw) if len(w) > 1}
    return frozenset(words)


def _same(a: frozenset, b: frozenset) -> bool:
    if not a or not b:
        return False
    return len(a & b) / min(len(a), len(b)) >= 0.75


def _unique_songs(cands: list, refs=()) -> list:
    """Same song ke duplicates hatao (refs = jaise songs nahi chahiye)."""
    kept, seen_ids = [], set()
    kept_tok = [t for t in refs if t]
    for c in cands:
        if c["vidid"] in seen_ids:
            continue
        tk = _tokens(c["title"])
        if any(_same(tk, k) for k in kept_tok):
            continue
        seen_ids.add(c["vidid"])
        kept.append(c)
        kept_tok.append(tk)
    return kept


def _similar_queries(seed_title: str) -> list:
    clean = short_title(seed_title or "", 60)
    qs = [clean]
    for p in re.split(r"\s+[-–—]\s+|\s*\|\s*", clean)[:2]:
        if p.strip():
            qs.append(f"{p.strip()} songs")  # artist/movie ke aur songs
    qs.append(f"{clean} similar songs")
    out = []
    for q in qs:
        if q and q not in out:
            out.append(q)
    return out


async def _search_fallback(seed_vidid: str, seed_title: str, n: int) -> list:
    """yt_dlp Mix fail ho to varied searches se recommendations."""
    try:
        if not seed_title:
            res = await VideosSearch(
                f"https://www.youtube.com/watch?v={seed_vidid}", limit=1
            ).next()
            items = res.get("result", []) if isinstance(res, dict) else []
            seed_title = items[0]["title"] if items else ""
    except Exception as e:
        print(f"[RECOMMEND SEARCH ERROR] {type(e).__name__}: {e}")
        return []
    if not seed_title:
        return []
    cands = await _search_many(_similar_queries(seed_title), None)
    return [c for c in cands if c["vidid"] != seed_vidid][:n]


# Dikhaye gaye tracks ki exact details (vidid -> dict). Button dabane par yahi
# use hoti hai, search nahi -> jo title dikha wahi song chalta hai.
_TRACK_CACHE: dict = {}
_DUR_OK = re.compile(r"^\d+(:\d{2}){1,2}$")


def _cache(cands: list) -> list:
    for c in cands:
        _TRACK_CACHE[c["vidid"]] = c
    while len(_TRACK_CACHE) > 1500:
        _TRACK_CACHE.pop(next(iter(_TRACK_CACHE)))
    return cands


def get_cached_track(vidid: str):
    c = _TRACK_CACHE.get(vidid)
    if c and _DUR_OK.match(str(c.get("duration_min", ""))):
        return {
            "title": c["title"],
            "link": c.get("link") or f"https://www.youtube.com/watch?v={vidid}",
            "vidid": vidid,
            "duration_min": c["duration_min"],
            "thumb": c.get("thumb") or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg",
        }
    return None


_MIX_BAD_UNTIL = 0.0  # Mix fail/timeout ho to kuch der skip (bot-check me atakna nahi)


async def _mix_candidates(seed_vidid: str) -> list:
    global _MIX_BAD_UNTIL
    if time.time() < _MIX_BAD_UNTIL:
        return []
    loop = asyncio.get_event_loop()
    try:
        entries = await asyncio.wait_for(
            loop.run_in_executor(None, _fetch_mix_sync, seed_vidid, 50), 15
        )
    except Exception as e:
        print(f"[RECOMMEND] Mix fail/timeout ({type(e).__name__}: {e}) -> 10 min search mode")
        _MIX_BAD_UNTIL = time.time() + 600
        return []
    cands = _extract_mix_candidates(entries, 0, skip_history=True)
    return [c for c in cands if c["vidid"] != seed_vidid]


async def _fetch_pool(seed_vidid: str, seed_title: str, region) -> list:
    """Seed ka Mix (+ search fallback), country filter + duplicate filter."""
    refs = [_tokens(seed_title)] if seed_title else []
    cands = filter_by_region(await _mix_candidates(seed_vidid), region)
    cands = _unique_songs(cands, refs)

    if len(cands) < REC_COUNT:
        extra = await _search_fallback(seed_vidid, seed_title, 25)
        cands = _unique_songs(cands + filter_by_region(extra, region), refs)
    return _cache(cands)


async def _search_many(queries: list, region) -> list:
    """Kai searches ek saath (title/channel based), merge + country filter.
    region=None => filter nahi lagta."""

    async def _one(q):
        try:
            res = await asyncio.wait_for(VideosSearch(q, limit=20).next(), 12)
            items = res.get("result", []) if isinstance(res, dict) else []
            return _extract_candidates(items, 0, skip_history=True)
        except Exception as e:
            print(f"[RECOMMEND SEARCH] '{q[:30]}' fail: {type(e).__name__}: {e}")
            return []

    lists = await asyncio.gather(*[_one(q) for q in queries if q])
    merged, seen = [], set()
    for group in itertools.zip_longest(*lists):  # round-robin: variety
        for c in group:
            if c and c["vidid"] not in seen:
                seen.add(c["vidid"])
                merged.append(c)
    return _cache(filter_by_region(merged, region) if region else merged)


# ---------------------------------------------------------
# Per-chat state: queue (agle tracks), shown (dikha chuke), region
# ---------------------------------------------------------
_STATE: dict = {}
_SHOWN_LIMIT = 300
REC_COUNT = 5  # ek baar me kitne songs dikhane hain
_REGION_KEEP_SECS = 30 * 60  # itni der tak purana country filter carry hota hai


def _new_state() -> dict:
    return {"seed": None, "region": (None, None), "queue": [], "shown": [],
            "last": [], "meta": {}, "title": None, "ts": 0}


def _st(chat_id: int) -> dict:
    return _STATE.setdefault(chat_id, _new_state())


def _refill_queries(st: dict, seed_title: str) -> list:
    """Pool khatam hone par naye searches: seed title, dikhaye gaye songs ke
    titles aur sabse common channels (same artist ke aur songs)."""
    meta = st["meta"]
    shown = [v for v in st["shown"] if v in meta]
    qs = _similar_queries(seed_title or st["title"])
    for v in random.sample(shown, min(3, len(shown))):
        qs.append(meta[v]["title"])
    chans = [m["channel"] for m in meta.values() if m.get("channel")]
    for ch, _ in collections.Counter(chans).most_common(2):
        qs.append(ch)
    out = []
    for q in qs:
        if q and q not in out:
            out.append(q)
    return out[:8]


async def get_more_recommendations(
    chat_id: int, seed_vidid: str, n: int = REC_COUNT, seed_title: str = None
) -> list:
    """
    "More" button: agle n tracks (same country). Pool khatam ho jaye to naye
    searches/Mix se refill hota hai -> unlimited songs.
    """
    st = _st(chat_id)
    if st["seed"] != seed_vidid:  # state lost (restart) ya naya seed
        keep_title = seed_title or st["title"]
        st.clear()
        st.update(_new_state())
        st.update(seed=seed_vidid, title=keep_title)
        st["region"] = await get_seed_region(seed_vidid, seed_title)

    title = seed_title or st["title"]
    blocked = set(st["shown"]) | set(_history(chat_id)) | {seed_vidid}

    def _add(pool):
        queued = {c["vidid"] for c in st["queue"]}
        refs = [_tokens(title)] if title else []
        refs += [_tokens(st["meta"][v]["title"]) for v in st["shown"] if v in st["meta"]]
        refs += [_tokens(c["title"]) for c in st["queue"]]
        for c in _unique_songs(pool, refs):
            if c["vidid"] in blocked or c["vidid"] in queued:
                continue
            st["queue"].append(c)
            st["meta"][c["vidid"]] = {"title": c["title"], "channel": c.get("channel", "")}
            queued.add(c["vidid"])

    async def _refill():
        if len(st["queue"]) < n:
            _add(await _fetch_pool(seed_vidid, title, st["region"]))
        if len(st["queue"]) < n:
            _add(await _search_many(_refill_queries(st, title), st["region"]))

    await _refill()

    if not st["queue"]:
        # Sab kuch dikha chuke -> naya round (sirf abhi wale 5 hatao)
        print("[RECOMMEND] pool khatam -> naya round")
        st["shown"] = list(st["last"])
        blocked = {seed_vidid} | set(st["last"])
        await _refill()

    items, st["queue"] = st["queue"][:n], st["queue"][n:]
    st["last"] = [c["vidid"] for c in items]
    st["shown"] = (st["shown"] + st["last"])[-_SHOWN_LIMIT:]
    st["ts"] = time.time()
    print(f"[RECOMMEND] more -> {len(items)} tracks, queue left {len(st['queue'])}")
    return items


async def fetch_recommendations(
    seed_vidid: str, n: int = REC_COUNT, seed_title: str = None, chat_id: int = None
) -> list:
    if not seed_vidid:
        return []
    region = await get_seed_region(seed_vidid, seed_title)

    if chat_id is None:
        return (await _fetch_pool(seed_vidid, seed_title, region))[:n]

    st = _st(chat_id)
    old_region, old_ts = st["region"], st["ts"]
    # Naye song ka country pata na chale to pichhla country filter rakho
    # (taaki chain me doosre country ke songs na ghus jaayein)
    if not region[0] and old_region[0] and time.time() - old_ts < _REGION_KEEP_SECS:
        region = old_region
    st.clear()
    st.update(_new_state())
    st.update(seed=seed_vidid, region=region, title=seed_title)
    return await get_more_recommendations(chat_id, seed_vidid, n, seed_title)


def recommend_text(prev_title: str, region=None) -> str:
    label = region_label(region)
    region_line = f"\n<b>🌍 ʀᴇɢɪᴏɴ :</b> <code>{label}</code>" if label else ""
    return (
        "<b>❖ ǫᴜᴇᴜᴇ ᴇɴᴅᴇᴅ</b>\n"
        "<blockquote>"
        f"<b>👑 ᴘʀᴇᴠɪᴏᴜs :</b> <code>{(prev_title or '—')[:40]}…</code>"
        f"{region_line}\n"
        "<b>💡 ᴛᴀᴘ ʙᴇʟᴏᴡ ᴛᴏ ᴘʟᴀʏ ɴᴇxᴛ ᴛʀᴀᴄᴋ</b>"
        "</blockquote>"
    )


# ---------------------------------------------------------
# 🎨 Native Telegram coloured buttons (blue = PRIMARY, red = DANGER)
# Lisa bot jaisa: saare buttons blue, sirf close red.
# Agar pyrogram/kurigram purana hai (ButtonStyle nahi) to automatic
# emoji-square wala purana look use hoga -> bot crash nahi hoga.
#   Fix: pip install -U kurigram   (ya jo fork use kar rahe ho)
# ---------------------------------------------------------
try:
    from pyrogram.enums import ButtonStyle

    _BLUE = ButtonStyle.PRIMARY
    _RED = ButtonStyle.DANGER
    _HAS_STYLE = True
except Exception:
    _BLUE = _RED = None
    _HAS_STYLE = False

def _btn(text: str, data: str, style=None) -> InlineKeyboardButton:
    if _HAS_STYLE and style is not None:
        try:
            return InlineKeyboardButton(text, callback_data=data, style=style)
        except TypeError:  # style param support nahi -> plain button
            pass
    return InlineKeyboardButton(text, callback_data=data)


def recommend_markup(tracks: list, seed_vidid: str) -> InlineKeyboardMarkup:
    btns = [
        _btn(
            f"{i}. {short_title(t['title'], 16)}",
            f"RecPlay {t['vidid']}",
            _BLUE,
        )
        for i, t in enumerate(tracks, 1)
    ]
    rows = [btns[i : i + 2] for i in range(0, len(btns), 2)]  # 2 per row
    rows.append([_btn("ᴍᴏʀᴇ ʟɪᴋᴇ ᴛʜɪs", f"RecMore {seed_vidid}", _BLUE)])
    rows.append([_btn("ᴘʟᴀʏ ʀᴀɴᴅᴏᴍ ᴀɪ ᴛʀᴀᴄᴋ", f"RecRand {seed_vidid}", _BLUE)])
    rows.append([_btn("ᴄʟᴏsᴇ", "close", _RED)])  # red close, full width
    return InlineKeyboardMarkup(rows)


# ===========================================================
# 🖼 COLLAGE — recommended songs ki photos (numbered 1, 2, 3 ...)
# Button numbers = photo numbers. Titles buttons/caption me hain
# (image par text nahi => Hindi/emoji fonts ka koi issue nahi).
# ===========================================================

_GAP = 10


def _cover_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    iw, ih = img.size
    sc = max(w / iw, h / ih)
    img = img.resize((int(iw * sc) + 1, int(ih * sc) + 1), Image.LANCZOS)
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))


async def _download_thumb(session, track: dict):
    vidid = track.get("vidid")
    urls = [
        track.get("thumb"),
        f"https://i.ytimg.com/vi/{vidid}/mqdefault.jpg",
        f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg",
    ]
    for url in filter(None, urls):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status != 200:
                    continue
                import io

                return Image.open(io.BytesIO(await r.read())).convert("RGB")
        except Exception:
            continue
    return None


def _compose_collage(images: list, path: str):
    n = len(images)
    cols = 5 if n > 6 else min(3, n)
    _TILE_W = 300 if n > 6 else 420
    _TILE_H = _TILE_W * 9 // 16
    rows = (n + cols - 1) // cols
    W = cols * _TILE_W + (cols + 1) * _GAP
    H = rows * _TILE_H + (rows + 1) * _GAP
    canvas = Image.new("RGB", (W, H), (18, 18, 24))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__), "..", "assets", "font.ttf"), 28
        )
    except Exception:
        font = ImageFont.load_default()

    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = _GAP + c * (_TILE_W + _GAP)
        y = _GAP + r * (_TILE_H + _GAP)
        if img is None:
            tile = Image.new("RGB", (_TILE_W, _TILE_H), (40, 40, 52))
        else:
            tile = _cover_crop(img, _TILE_W, _TILE_H)
        canvas.paste(tile, (x, y))
        # number badge (top-left)
        cx, cy, rad = x + 32, y + 32, 22
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(255, 20, 147))
        draw.text((cx, cy), str(i + 1), font=font, fill=(255, 255, 255), anchor="mm")
    canvas.save(path, "JPEG", quality=88)


async def build_collage(tracks: list, key):
    """Tracks ki thumbnails ka numbered collage banata hai. Fail => None."""
    try:
        if not tracks:
            return None
        async with aiohttp.ClientSession() as session:
            images = await asyncio.gather(
                *[_download_thumb(session, t) for t in tracks]
            )
        if not any(images):
            return None
        os.makedirs("cache", exist_ok=True)
        path = f"cache/rec_{key}_{int(time.time() * 1000)}.jpg"
        await asyncio.get_running_loop().run_in_executor(
            None, _compose_collage, list(images), path
        )
        return path
    except Exception as e:
        print(f"[RECOMMEND COLLAGE] fail: {type(e).__name__}: {e}")
        return None


def _rm(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ---------------------------------------------------------
# ⏱ Auto-delete: 1 minute tak koi song play na ho to message delete
# Delete se pehle check hota hai ki message me abhi bhi recommendation
# buttons (RecPlay/RecMore/RecRand) hain. Agar user ne song chala diya aur
# message ban gaya "now playing" card, to delete NAHI hota.
# ---------------------------------------------------------
_DEL_SECS = 60
_DEL_TASKS: dict = {}  # (chat_id, msg_id) -> asyncio.Task
_REC_PREFIXES = ("RecPlay", "RecMore", "RecRand")


def _has_rec_buttons(msg) -> bool:
    try:
        for row in msg.reply_markup.inline_keyboard:
            for b in row:
                d = b.callback_data
                if isinstance(d, bytes):
                    d = d.decode("utf-8", "ignore")
                if d and str(d).startswith(_REC_PREFIXES):
                    return True
    except Exception:
        pass
    return False


async def _auto_delete(client, chat_id: int, msg_id: int, delay: float):
    key = (chat_id, msg_id)
    try:
        await asyncio.sleep(delay)
        m = await client.get_messages(chat_id, msg_id)
        if not m or getattr(m, "empty", False):
            return  # pehle hi delete ho chuka
        if not _has_rec_buttons(m):
            return  # song chal gaya / message badal gaya
        await m.delete()
        print(f"[RECOMMEND] {int(delay)}s me play nahi hua -> message deleted (chat={chat_id})")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"[RECOMMEND AUTODEL] {type(e).__name__}: {e}")
    finally:
        if _DEL_TASKS.get(key) is asyncio.current_task():
            _DEL_TASKS.pop(key, None)


def cancel_auto_delete(chat_id: int, msg_id: int):
    """Optional: handler se call kar sakte ho (RecPlay dabne par)."""
    t = _DEL_TASKS.pop((chat_id, msg_id), None)
    if t and not t.done():
        t.cancel()


def schedule_auto_delete(client, chat_id: int, msg_id: int, delay: float = _DEL_SECS):
    """Timer (re)start karo. Purana timer cancel ho jata hai."""
    if not client or not chat_id or not msg_id:
        return
    cancel_auto_delete(chat_id, msg_id)
    _DEL_TASKS[(chat_id, msg_id)] = asyncio.create_task(
        _auto_delete(client, chat_id, msg_id, delay)
    )


async def edit_recommend_message(msg, text: str, markup, tracks: list = None):
    """Photo message ho to photo/caption edit, warna normal text edit.
    Naye tracks (More button) aane par 1 minute ka timer dobara shuru."""
    res = None
    if msg.photo:
        if tracks:
            path = await build_collage(tracks, msg.chat.id)
            if path:
                try:
                    res = await msg.edit_media(
                        InputMediaPhoto(
                            path, caption=text, parse_mode=enums.ParseMode.HTML
                        ),
                        reply_markup=markup,
                    )
                finally:
                    _rm(path)
        if res is None:
            res = await msg.edit_caption(
                text, parse_mode=enums.ParseMode.HTML, reply_markup=markup
            )
    else:
        res = await msg.edit_text(text, reply_markup=markup)

    if tracks:
        schedule_auto_delete(getattr(msg, "_client", None), msg.chat.id, msg.id)
    return res


async def send_recommendations(app, original_chat_id: int, popped: dict) -> bool:
    """Queue khatam hone par call.py / skip.py se call hota hai."""
    try:
        seed = popped.get("vidid")
        print(f"[RECOMMEND] queue ended, seed={seed}, chat={original_chat_id}")
        tracks = await fetch_recommendations(
            seed, seed_title=popped.get("title"), chat_id=original_chat_id
        )
        if not tracks:
            print("[RECOMMEND] koi track nahi mila (yt_dlp/cookies/network check karo)")
            return False
        text = recommend_text(popped.get("title"), _st(original_chat_id)["region"])
        markup = recommend_markup(tracks, seed)
        sent = False
        sent_msg = None
        path = await build_collage(tracks, original_chat_id)
        if path:
            try:
                sent_msg = await app.send_photo(
                    original_chat_id,
                    path,
                    caption=text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=markup,
                )
                sent = True
            except Exception as e:
                print(f"[RECOMMEND] send_photo fail: {type(e).__name__}: {e}")
            finally:
                _rm(path)
        if not sent:  # fallback: pehle jaisa text message
            sent_msg = await app.send_message(original_chat_id, text, reply_markup=markup)
        if sent_msg:
            schedule_auto_delete(app, original_chat_id, sent_msg.id)
        print(f"[RECOMMEND] {len(tracks)} tracks bhej diye")
        return True
    except Exception as e:
        print(f"[RECOMMEND ERROR] {type(e).__name__}: {e}")
        return False
