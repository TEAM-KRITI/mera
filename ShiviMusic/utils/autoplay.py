# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
#
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

import asyncio
import functools
import glob
import json
import os
import random
import re
import time

import yt_dlp
from py_yt import VideosSearch

from ShiviMusic.utils.region import filter_by_region, get_seed_region

# =========================================================
# PER-CHAT PLAY HISTORY  —  12 GHANTE TAK NO-REPEAT
# Jo song/title ek baar chal gaya, wo us chat me 12 ghante tak dobara
# kabhi nahi aayega (same song ke lyrics/audio/slowed/cover versions bhi
# nahi). History file me save hoti hai, to bot restart se bhi reset nahi.
# =========================================================
_NO_REPEAT_SECS = 12 * 60 * 60
_MAX_PER_CHAT = 1500
_HIST_FILE = os.path.join("cache", "autoplay_history.json")

# chat_id -> {vidid: timestamp}  /  chat_id -> {title_key: timestamp}
_played_history: dict = {}
_played_titles: dict = {}
# chat_id -> {vidid: track dict}  (last-resort ke liye, taaki autoplay kabhi na ruke)
_played_info: dict = {}

_NOISE = re.compile(
    r"\(.*?\)|\[.*?\]|"
    r"\b(?:official|video|audio|lyrics?|lyrical|full song|hd|4k|with lyrics|"
    r"songs?|music|slowed|reverb|lofi|lo-fi|cover|remix|version|8d|sped up|"
    r"reprise|unplugged|acoustic|status)\b|"
    r"\bft\b.*|\bfeat\b.*",
    re.IGNORECASE,
)


def _title_key(title) -> str:
    """Same song ke alag-alag uploads (lyrics/official/audio) ko ek hi key do."""
    if not title:
        return ""
    t = _NOISE.sub(" ", str(title).lower())
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


@functools.lru_cache(maxsize=4096)
def _key_tokens(key: str) -> frozenset:
    return frozenset(w for w in key.split() if len(w) > 1)


# ---------------- persistence ----------------
def _save():
    try:
        os.makedirs(os.path.dirname(_HIST_FILE), exist_ok=True)
        tmp = _HIST_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"h": _played_history, "t": _played_titles, "i": _played_info}, f)
        os.replace(tmp, _HIST_FILE)
    except Exception as e:
        print(f"[AUTOPLAY HISTORY SAVE] {type(e).__name__}: {e}")


def _load():
    try:
        with open(_HIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cutoff = time.time() - _NO_REPEAT_SECS
        for name, store in (("h", _played_history), ("t", _played_titles)):
            for chat, items in (data.get(name) or {}).items():
                items = {k: v for k, v in items.items() if v >= cutoff}
                if items:
                    store[int(chat)] = items
        for chat, items in (data.get("i") or {}).items():
            hist = _played_history.get(int(chat), {})
            items = {k: v for k, v in items.items() if k in hist}
            if items:
                _played_info[int(chat)] = items
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[AUTOPLAY HISTORY LOAD] {type(e).__name__}: {e}")


_load()


def _prune(store: dict, chat_id: int) -> dict:
    """12 ghante se purani entries hatao, chat ka dict return karo."""
    d = store.get(chat_id)
    if not d:
        return {}
    cutoff = time.time() - _NO_REPEAT_SECS
    old = [k for k, ts in d.items() if ts < cutoff]
    for k in old:
        del d[k]
        if store is _played_history:
            _played_info.get(chat_id, {}).pop(k, None)
    return d


def _put(store: dict, chat_id: int, key: str):
    d = store.setdefault(chat_id, {})
    d.pop(key, None)  # re-insert => latest position
    d[key] = time.time()
    while len(d) > _MAX_PER_CHAT:
        d.pop(next(iter(d)))


def remember_played(chat_id: int, vidid: str, title: str = None, track: dict = None):
    if vidid:
        _put(_played_history, chat_id, vidid)
        if track:
            info = _played_info.setdefault(chat_id, {})
            info[vidid] = track
            while len(info) > _MAX_PER_CHAT:
                info.pop(next(iter(info)))
    key = _title_key(title)
    if key:
        _put(_played_titles, chat_id, key)
    _save()


def _history(chat_id: int) -> list:
    """Pichhle 12 ghante me bajaye gaye vidids."""
    return list(_prune(_played_history, chat_id).keys())


def _titles(chat_id: int) -> list:
    return list(_prune(_played_titles, chat_id).keys())


def clear_history(chat_id: int):
    """
    Compatible rakha (purane imports na tootein). Ab history jaldi reset
    nahi hoti: sirf 12 ghante se purani entries hatati hai.
    """
    _prune(_played_history, chat_id)
    _prune(_played_titles, chat_id)
    _save()


def _title_seen(chat_id: int, key: str) -> bool:
    seen = _prune(_played_titles, chat_id)
    if not seen:
        return False
    if key in seen:
        return True
    tk = _key_tokens(key)
    if len(tk) < 2:
        return False
    for k in seen:
        kt = _key_tokens(k)
        if len(kt) >= 2 and len(tk & kt) / min(len(tk), len(kt)) >= 0.75:
            return True
    return False


def _is_played(chat_id: int, vidid: str, title: str, seed_vidid: str, skip_history: bool) -> bool:
    if seed_vidid and vidid == seed_vidid:
        return True  # abhi bajne wala/bajaya hua gaana kabhi nahi
    if skip_history:
        return False
    if vidid in _prune(_played_history, chat_id):
        return True
    key = _title_key(title)
    return bool(key) and _title_seen(chat_id, key)


def _extract_candidates(results, chat_id: int, skip_history: bool, seed_vidid: str = None):
    candidates = []
    for video in results:
        vidid = video.get("id")
        title = video.get("title")
        link = video.get("link")
        duration = video.get("duration")
        if not (vidid and title and link and duration):
            continue
        if _is_played(chat_id, vidid, title, seed_vidid, skip_history):
            continue
        thumbs = video.get("thumbnails") or []
        thumb = thumbs[0].get("url", "").split("?")[0] if thumbs else None
        ch = video.get("channel") or {}
        channel = ch.get("name", "") if isinstance(ch, dict) else str(ch)
        candidates.append(
            {
                "vidid": vidid,
                "title": title,
                "channel": channel,
                "link": link,
                "duration_min": duration,
                "thumb": thumb,
            }
        )
    return candidates


# =========================================================
# ASHOK-STYLE: YouTube Mix playlist ("RD" + videoID)
# Genuinely YouTube's own "related songs" algorithm — much
# better variety than a plain title-text search, which often
# just returns covers/remixes of the same song.
# =========================================================

def _cookie_file():
    folder = os.path.join(os.getcwd(), "ShiviMusic", "assets")
    txt_files = glob.glob(os.path.join(folder, "*.txt"))
    if not txt_files:
        return None
    return random.choice(txt_files)


def _fetch_mix_sync(video_id: str, limit: int = 20) -> list:
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": limit,
        "no_warnings": True,
    }
    cookiefile = _cookie_file()
    if cookiefile:
        ydl_opts["cookiefile"] = cookiefile
    url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return (info or {}).get("entries") or []


def _extract_mix_candidates(entries, chat_id: int, skip_history: bool, seed_vidid: str = None):
    candidates = []
    for e in entries or []:
        if not e:
            continue
        vidid = e.get("id")
        title = e.get("title")
        if not (vidid and title):
            continue
        if _is_played(chat_id, vidid, title, seed_vidid, skip_history):
            continue
        duration = e.get("duration")
        if isinstance(duration, (int, float)):
            m, s = divmod(int(duration), 60)
            duration_min = f"{m}:{s:02d}"
        else:
            duration_min = str(duration) if duration else "Live"
        candidates.append(
            {
                "vidid": vidid,
                "title": title,
                "channel": e.get("channel") or e.get("uploader") or "",
                "link": f"https://www.youtube.com/watch?v={vidid}",
                "duration_min": duration_min,
                "thumb": e.get("thumbnail")
                or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg",
            }
        )
    return candidates


async def _fetch_mix_candidates(chat_id: int, seed_vidid: str, region=None) -> list:
    """
    Seed ka Mix -> country filter. Seed ka Mix khatam ho jaye (sab 12h me
    play ho chuke) to pichhle played songs ko seed bana kar naye Mix
    fetch karta hai. History kabhi reset nahi hoti.
    """
    loop = asyncio.get_event_loop()
    seeds = [seed_vidid]
    recent = [v for v in _history(chat_id) if v != seed_vidid]
    random.shuffle(recent)
    seeds += recent[:6]

    errors = 0
    for seed in seeds:
        try:
            entries = await asyncio.wait_for(
                loop.run_in_executor(None, _fetch_mix_sync, seed, 40), 20
            )
        except Exception as e:
            print(f"[AUTOPLAY MIX ERROR] {type(e).__name__}: {e}")
            errors += 1
            if errors >= 2:  # cookies/bot-check -> baar baar try mat karo
                break
            continue
        candidates = _extract_mix_candidates(entries, chat_id, False, seed_vidid)
        candidates = filter_by_region(candidates, region)
        if candidates:
            return candidates
    return []


def _pick(candidates: list) -> dict:
    # Pehle same language/country wale (rank 0/1) me se random, warna baaki
    best = [c for c in candidates if c.get("rank", 0) <= 1] or candidates
    return random.choice(best)


async def _search_candidates(chat_id: int, queries: list, seed_vidid, region) -> list:
    for q in queries:
        if not q:
            continue
        try:
            data = await asyncio.wait_for(VideosSearch(q, limit=25).next(), 12)
            results = data.get("result", []) if isinstance(data, dict) else []
        except Exception as e:
            print(f"[AUTOPLAY SEARCH ERROR] '{q[:30]}' {type(e).__name__}: {e}")
            continue
        cands = filter_by_region(
            _extract_candidates(results, chat_id, False, seed_vidid), region
        )
        if cands:
            return cands
    return []


async def _find_new(chat_id: int, seed_title: str, seed_vidid: str, region):
    """Sirf aisa track jo 12h me nahi baja. Mix -> alag-alag searches."""
    if seed_vidid:
        mix_candidates = await _fetch_mix_candidates(chat_id, seed_vidid, region)
        if mix_candidates:
            return _pick(mix_candidates)

    if not seed_title:
        return None

    clean = _title_key(seed_title) or seed_title
    queries = [seed_title, f"{clean} songs", f"{clean} similar songs"]
    words = clean.split()
    if len(words) >= 2:
        queries.append(" ".join(words[:2]) + " songs")
    past = _titles(chat_id)
    random.shuffle(past)
    queries += past[:4]  # purane gaano ke titles se naye gaane
    for x in region or ():
        if isinstance(x, str) and len(x) > 2:  # language/country naam
            queries += [f"top {x} songs", f"new {x} songs"]
    cands = await _search_candidates(chat_id, queries, seed_vidid, region)
    return _pick(cands) if cands else None


def _least_recent_track(chat_id: int, seed_vidid: str):
    """
    Aakhri raasta (taaki track change hota rahe, autoplay ruke nahi):
    12h ke andar sabse purana bajaya gaana, lekin sabse recent 25 me se nahi.
    """
    hist = list(_prune(_played_history, chat_id).keys())
    recent = set(hist[-25:])
    info = _played_info.get(chat_id, {})
    for v in hist:  # oldest first
        if v in recent or v == seed_vidid:
            continue
        if v in info:
            return info[v]
    return None


async def fetch_autoplay_track(chat_id: int, seed_title: str, seed_vidid: str = None):
    """
    Har baar NAYA track (seed se alag) return karta hai.
      1) Mix + searches, country filter ke saath, 12h me na bajaya hua
      2) Wahi, par country filter hata kar (phir bhi 12h me na bajaya hua)
      3) Last resort: sabse purana bajaya gaana (recent 25 chhod kar)
    Seed kabhi return nahi hota.
    """
    region = await get_seed_region(seed_vidid, seed_title)

    # Abhi wala seed bhi history me daal do (agar caller ne nahi dala)
    if seed_vidid:
        remember_played(chat_id, seed_vidid, seed_title)

    pick = await _find_new(chat_id, seed_title, seed_vidid, region)

    if pick is None and region and any(region):
        print(f"[AUTOPLAY] chat={chat_id}: country filter hata ke try")
        pick = await _find_new(chat_id, seed_title, seed_vidid, None)

    if pick is None:
        pick = _least_recent_track(chat_id, seed_vidid)
        if pick:
            print(f"[AUTOPLAY] chat={chat_id}: naya nahi mila -> sabse purana song")

    if pick is None:
        print(f"[AUTOPLAY] chat={chat_id}: koi track nahi mila")
        return None

    remember_played(chat_id, pick["vidid"], pick["title"], track=pick)
    return pick

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
