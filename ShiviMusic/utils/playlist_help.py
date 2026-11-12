# ===========================================================
# ❓ PLAYLIST / FAVOURITES HELP  (helper)
#
# Sirf help ka text + buttons yahan hain, taaki favourites.py chhota rahe.
#
#   help_panel(section)  -> (text, InlineKeyboardMarkup)
#       section: "main" | "pl" | "fav" | "play"
#   HELP_CB              -> callback prefix ("PlHelp")
#   HELP_ROW             -> panels me lagane wala ❓ Help button row
#   HELP_COMMANDS        -> help command names (favourites.py me use hote hain)
# ===========================================================

import html

from pyrogram.types import InlineKeyboardButton as Btn
from pyrogram.types import InlineKeyboardMarkup as Markup

from ShiviMusic.utils.database import (
    MAX_FAVS,
    MAX_PLAYLIST_NAME,
    MAX_PLAYLIST_SONGS,
    MAX_PLAYLISTS,
)

HELP_CB = "PlHelp"
HELP_COMMANDS = ["plhelp", "playlisthelp", "favhelp", "phelp"]

# Now-playing message ke ❓ button ka popup (Telegram alert limit ~200 chars)
HELP_NOW_ALERT = (
    "📂 /playlist /newplaylist /addplaylist /delplaylist /playplaylist\n"
    "❤️ /fav /addfav /playfav\n"
    "❓ Poori help: /plhelp"
)

HELP_ROW = [Btn("❓ ʜᴇʟᴘ", callback_data=f"{HELP_CB} main")]
_CLOSE_ROW = [Btn("• ᴄʟᴏsᴇ •", callback_data="close")]

SECTIONS = ("main", "pl", "fav", "play")


def _code(text: str) -> str:
    return f"<code>{html.escape(text)}</code>"


def _main_text() -> str:
    return (
        "<b>❓ ᴘʟᴀʏʟɪsᴛ & ꜰᴀᴠᴏᴜʀɪᴛᴇs ʜᴇʟᴘ</b>\n\n"
        "<blockquote>"
        "📂 <b>Playlist</b> — apne naam se gaano ki list banao\n"
        "❤️ <b>Favourites</b> — pasandida gaane ek jagah\n"
        "▶ <b>Play</b> — VC me bajao (group me)"
        "</blockquote>\n"
        f"<b>Limits:</b> {MAX_FAVS} favourites • {MAX_PLAYLISTS} playlists • "
        f"{MAX_PLAYLIST_SONGS} gaane/playlist\n\n"
        "👇 Neeche se section chuno."
    )


def _pl_text() -> str:
    return (
        "<b>📂 ᴘʟᴀʏʟɪsᴛ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "<blockquote>"
        f"{_code('/playlist')} — apni saari playlists ka panel\n"
        f"{_code('/newplaylist name')} — nayi playlist banao "
        f"(naam max {MAX_PLAYLIST_NAME} letters)\n"
        f"{_code('/addplaylist name | song')} — playlist me gaana add\n"
        f"{_code('/addplaylist name')} — abhi baj raha gaana add\n"
        f"{_code('/delplaylist name')} — playlist delete"
        "</blockquote>\n"
        "<b>Example:</b>\n"
        f"{_code('/newplaylist Gym Mix')}\n"
        f"{_code('/addplaylist Gym Mix | kar har maidan fateh')}"
    )


def _fav_text() -> str:
    return (
        "<b>❤️ ꜰᴀᴠᴏᴜʀɪᴛᴇ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "<blockquote>"
        f"{_code('/fav')} — favourites ka panel\n"
        f"{_code('/addfav song name')} — naam ya link se add\n"
        f"{_code('/addfav')} — abhi baj raha gaana add\n"
        "❤️ button — now-playing message se seedha add"
        "</blockquote>\n"
        "Panel me ▶ se gaana bajao, 🗑 se hatao, 🧹 se sab clear karo."
    )


def _play_text() -> str:
    return (
        "<b>▶ ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "<blockquote>"
        f"{_code('/playfav')} — saare favourites bajao\n"
        f"{_code('/playfav shuffle')} — shuffle karke\n"
        f"{_code('/playplaylist name')} — playlist bajao\n"
        f"{_code('/playplaylist name shuffle')} — shuffle karke"
        "</blockquote>\n"
        "⚠️ Ye commands <b>group</b> me chalte hain (VC me bajane ke liye). "
        "Private chat me sirf panel/list dekh sakte ho.\n"
        "Panel ka ▶ ᴘʟᴀʏ ᴀʟʟ / 🔀 sʜᴜꜰꜰʟᴇ button bhi use kar sakte ho."
    )


_TEXTS = {
    "main": _main_text,
    "pl": _pl_text,
    "fav": _fav_text,
    "play": _play_text,
}


def help_panel(section: str = "main"):
    """Help ka (text, markup). Galat section aaye to main dikhata hai."""
    if section not in _TEXTS:
        section = "main"
    text = _TEXTS[section]()
    rows = [
        [
            Btn("📂 ᴘʟᴀʏʟɪsᴛ", callback_data=f"{HELP_CB} pl"),
            Btn("❤️ ꜰᴀᴠ", callback_data=f"{HELP_CB} fav"),
            Btn("▶ ᴘʟᴀʏ", callback_data=f"{HELP_CB} play"),
        ]
    ]
    if section != "main":
        rows.append([Btn("⬅ ʙᴀᴄᴋ", callback_data=f"{HELP_CB} main")])
    rows.append(_CLOSE_ROW)
    return text, Markup(rows)
