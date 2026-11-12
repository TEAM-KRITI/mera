# ===========================================================
# 🌍 REGION / COUNTRY FILTER
# Recommendations + Autoplay me sirf usi country (aur pehle usi
# language) ke songs aayein jo abhi chal raha hai. Doosre country
# ke songs filter ho jaate hain.
#
# YouTube se country ka direct data nahi milta, isliye title +
# channel name se detect hota hai: script (Devanagari, Hangul,
# Arabic...), language keywords, aur known channels.
# ===========================================================

import re

from py_yt import VideosSearch

# ---------------------------------------------------------
# 1) SCRIPT based detection
# ---------------------------------------------------------
_SCRIPTS = {
    ("IN", "hi"): r"[\u0900-\u097F]",
    ("IN", "pa"): r"[\u0A00-\u0A7F]",
    ("IN", "gu"): r"[\u0A80-\u0AFF]",
    ("IN", "or"): r"[\u0B00-\u0B7F]",
    ("IN", "ta"): r"[\u0B80-\u0BFF]",
    ("IN", "te"): r"[\u0C00-\u0C7F]",
    ("IN", "kn"): r"[\u0C80-\u0CFF]",
    ("IN", "ml"): r"[\u0D00-\u0D7F]",
    ("BD", "bn"): r"[\u0980-\u09FF]",
    ("KR", "ko"): r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]",
    ("JP", "ja"): r"[\u3040-\u30FF]",
    ("CN", "zh"): r"[\u4E00-\u9FFF]",
    ("TH", "th"): r"[\u0E00-\u0E7F]",
    ("RU", "ru"): r"[\u0400-\u04FF]",
    ("IL", "he"): r"[\u0590-\u05FF]",
    ("GR", "el"): r"[\u0370-\u03FF]",
}
_SCRIPTS = {k: re.compile(v) for k, v in _SCRIPTS.items()}

_ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F]")
_URDU_ONLY = re.compile(r"[\u0679\u0688\u0691\u06BA\u06D2\u06BE\u06D3]")
_PERSIAN = re.compile(r"[\u067E\u0686\u0698\u06AF\u06A9\u06CC]")
_ARABIC_ONLY = re.compile(r"[\u0643\u064A]")


def _by_script(text: str):
    counts = {k: len(p.findall(text)) for k, p in _SCRIPTS.items()}
    if counts[("JP", "ja")]:  # kana ho to Japanese (Han bhi aa sakta hai)
        return ("JP", "ja")
    if counts[("KR", "ko")]:
        return ("KR", "ko")
    best = max(counts, key=counts.get)
    if counts[best]:
        return best
    if _ARABIC.search(text):
        if _URDU_ONLY.search(text):
            return ("PK", "ur")
        if _PERSIAN.search(text) and not _ARABIC_ONLY.search(text):
            return ("IR", "fa")
        return ("ARAB", "ar")
    return None


# ---------------------------------------------------------
# 2) KEYWORD based detection (Latin / romanized titles)
# ---------------------------------------------------------
def _rx(words):
    return re.compile(r"(?<![a-z])(?:" + "|".join(words) + r")(?![a-z])", re.I)


_LANG_KEYWORDS = [
    # (country, lang, regex)  -- specific pehle, general baad me
    ("IN", "pa", _rx(["punjabi", "jatt", "jatti", "gabru", "sidhu", "moosewala",
                      "diljit", "dosanjh", "aujla", "pind", "munde"])),
    ("IN", "hr", _rx(["haryanvi", "haryana"])),
    ("IN", "bh", _rx(["bhojpuri", "khesari", "pawan singh"])),
    ("IN", "ta", _rx(["tamil", "kollywood", "thalapathy"])),
    ("IN", "te", _rx(["telugu", "tollywood"])),
    ("IN", "kn", _rx(["kannada", "sandalwood"])),
    ("IN", "ml", _rx(["malayalam", "mollywood"])),
    ("IN", "mr", _rx(["marathi"])),
    ("IN", "gu", _rx(["gujarati"])),
    ("PK", "ur", _rx(["pakistani", "urdu", "nescafe basement"])),
    ("ARAB", "ar", _rx(["arabic", "habibi", "khaleeji", "yalla"])),
    ("KR", "ko", _rx(["k-?pop", "korean", "bts", "blackpink", "newjeans",
                      "aespa", "twice", "hybe labels", "smtown"])),
    ("JP", "ja", _rx(["j-?pop", "japanese", "yoasobi", "anime"])),
    ("CN", "zh", _rx(["mandarin", "chinese", "c-?pop"])),
    ("LATAM", "es", _rx(["reggaeton", "bachata", "cumbia", "corridos",
                         "oficial", "letra", "spanish", "latino",
                         "bad bunny", "shakira", "maluma"])),
    ("ID", "id", _rx(["lagu", "indonesia", "dangdut", "malaysia"])),
    ("TR", "tr", _rx(["turkish", "t\u00fcrk\u00e7e", "turkce"])),
    ("IN", "hi", _rx([
        "bollywood", "hindi", "tum", "tera", "teri", "tere", "mera", "meri",
        "mere", "dil", "pyar", "pyaar", "ishq", "ishaq", "mohabbat", "judai",
        "zindagi", "kabhi", "sanam", "humsafar", "tujhe", "mujhe", "tujhse",
        "aankhon", "baarish", "barish", "dard", "yaadein", "dilbar", "jaan",
        "kesariya", "bekhayali", "chaand", "arijit", "jubin", "neha kakkar",
        "shreya ghoshal", "sonu nigam", "kumar sanu", "badshah", "honey singh",
        "darshan raval", "b praak", "tulsi kumar", "lata mangeshkar",
        "kishore kumar", "mohammed rafi", "atif aslam",
    ])),
]

_TURKISH_CHARS = re.compile(r"[\u011f\u015f\u0131\u0130]")

_IN_CHANNELS = _rx([
    "t-?series", "zee music", "sony music india", "saregama", "tips official",
    "tips music", "speed records", "lahari", "aditya music", "times music",
    "eros now", "yrf", "yash raj", "white hill", "desi melodies", "muzik247",
    "think music", "gaana", "jiosaavn", "venus", "shemaroo", "goldmines",
    "panchhi", "pen music", "saregama hum bhojpuri", "t series",
])
_KR_CHANNELS = _rx(["hybe labels", "smtown", "jyp entertainment", "mnet", "1thek"])

_ENG_WORDS = _rx(["the", "and", "you", "your", "my", "with", "for", "this",
                  "that", "from", "are", "was", "is", "it", "of", "i"])


def _by_keywords(title: str, channel: str):
    text = f"{title} {channel}".lower()
    for country, lang, rx in _LANG_KEYWORDS:
        if rx.search(text):
            return (country, lang)
    if _TURKISH_CHARS.search(text):
        return ("TR", "tr")
    if _IN_CHANNELS.search(channel.lower()):
        return ("IN", "hi")
    if _KR_CHANNELS.search(channel.lower()):
        return ("KR", "ko")
    # English title: 2+ English function words aur koi doosra marker nahi
    if len(_ENG_WORDS.findall(title.lower())) >= 2:
        return ("WEST", "en")
    return None


def detect_region(title: str, channel: str = ""):
    """(country, lang) return karta hai, ya (None, None) agar pata na chale."""
    title = title or ""
    channel = channel or ""
    r = _by_script(f"{title} {channel}") or _by_keywords(title, channel)
    return r or (None, None)


# ---------------------------------------------------------
# 3) FILTER
# ---------------------------------------------------------
def region_rank(seed, cand):
    """0 = same language, 1 = same country, 2 = unknown, None = doosra country."""
    sc, sl = seed
    cc, cl = cand
    if not sc:
        return 1  # seed ka region pata nahi -> filter off
    if not cc:
        return 2
    if cc != sc:
        return None
    return 0 if cl == sl else 1


def filter_by_region(cands, seed_region):
    """Doosre country ke tracks hata deta hai; same language pehle, phir same
    country, phir unknown. Har candidate me 'rank' key add hoti hai."""
    if not seed_region or not seed_region[0]:
        return list(cands)
    ranked = []
    for i, c in enumerate(cands):
        r = region_rank(seed_region, detect_region(c.get("title"), c.get("channel")))
        if r is None:
            continue
        c["rank"] = r
        ranked.append((r, i, c))
    ranked.sort(key=lambda x: (x[0], x[1]))
    return [c for _, _, c in ranked]


# ---------------------------------------------------------
# 4) SEED region (cache + optional channel lookup)
# ---------------------------------------------------------
_SEED_CACHE: dict = {}


async def get_seed_region(vidid: str = None, title: str = None):
    if vidid and vidid in _SEED_CACHE:
        return _SEED_CACHE[vidid]

    region = detect_region(title or "")
    if not region[0] and vidid:
        # title se pata nahi chala -> channel name se koshish karo
        try:
            res = await VideosSearch(
                f"https://www.youtube.com/watch?v={vidid}", limit=1
            ).next()
            items = res.get("result", []) if isinstance(res, dict) else []
            if items:
                ch = items[0].get("channel") or {}
                channel = ch.get("name", "") if isinstance(ch, dict) else str(ch)
                region = detect_region(title or items[0].get("title", ""), channel)
        except Exception as e:
            print(f"[REGION] seed lookup fail: {type(e).__name__}: {e}")

    if vidid:
        if len(_SEED_CACHE) > 500:
            _SEED_CACHE.pop(next(iter(_SEED_CACHE)))
        _SEED_CACHE[vidid] = region
    return region


_FLAGS = {
    "IN": "🇮🇳 India", "PK": "🇵🇰 Pakistan", "BD": "🇧🇩 Bangladesh",
    "KR": "🇰🇷 Korea", "JP": "🇯🇵 Japan", "CN": "🇨🇳 China", "TH": "🇹🇭 Thailand",
    "RU": "🇷🇺 Russia", "IL": "🇮🇱 Israel", "GR": "🇬🇷 Greece", "IR": "🇮🇷 Iran",
    "ARAB": "🌍 Arab", "LATAM": "🌎 Latin", "ID": "🇮🇩 Indonesia/Malaysia",
    "TR": "🇹🇷 Turkey", "WEST": "🌐 English/Western",
}


def region_label(region) -> str:
    if not region or not region[0]:
        return ""
    return _FLAGS.get(region[0], region[0])
