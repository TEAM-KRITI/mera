# ===========================================================
# ❤️ FAVOURITES + 📂 PLAYLISTS  (user-wise)
#
# Commands
#   /fav  (/favs /favourites)       -> favourites panel
#   /addfav [song name | link]      -> favourite me add (bina naam ke = abhi baj raha gaana)
#   /playfav [shuffle]              -> saare favourites VC me bajao (group)
#
#   /playlist (/playlists)          -> apni playlists ka panel
#   /newplaylist <name>             -> nayi playlist
#   /addplaylist <name> [| song]    -> playlist me gaana add (bina song ke = abhi baj raha)
#   /delplaylist <name>             -> playlist delete
#   /playplaylist <name> [shuffle]  -> playlist VC me bajao (group)
#
#   /plhelp (/playlisthelp /favhelp /phelp)  -> help (ya /playlist help)
#
# Now-playing message ke buttons: ❤️ Fav / 📂 Playlist / ❓ Help (popup)
# ===========================================================

import html
import math
import random
import re
import traceback

from pyrogram import StopPropagation, enums, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton as Btn
from pyrogram.types import InlineKeyboardMarkup as Markup

import config
from ShiviMusic import YouTube, app
from ShiviMusic.misc import SUDOERS, db
try:
    from ShiviMusic.utils.autoplay import remember_played
except Exception:  # autoplay module na ho to bhi plugin chale
    def remember_played(chat_id, vidid):
        return None
from ShiviMusic.utils.database import (
    MAX_FAVS,
    MAX_PLAYLIST_SONGS,
    MAX_PLAYLISTS,
    add_fav,
    add_to_user_playlist,
    clear_favs,
    create_user_playlist,
    delete_user_playlist,
    find_user_playlist_by_name,
    get_favs,
    get_lang,
    get_playtype,
    get_user_playlist,
    get_user_playlists,
    is_maintenance,
    remove_fav,
    remove_from_user_playlist,
)
from ShiviMusic.utils.formatters import time_to_seconds
from ShiviMusic.utils.inline.play import stream_markup
from ShiviMusic.utils.logger import track_logs
from ShiviMusic.utils.playlist_help import HELP_COMMANDS, HELP_NOW_ALERT, HELP_ROW, help_panel
try:
    from ShiviMusic.utils.recommend import short_title
except Exception:  # recommend.py na ho to local fallback
    def short_title(title, limit: int = 26) -> str:
        title = " ".join(str(title or "").split())
        return title if len(title) <= limit else title[: max(limit - 1, 1)].rstrip() + "…"
from ShiviMusic.utils.stream.stream import stream
from config import BANNED_USERS, adminlist
from strings import get_string

HTML = enums.ParseMode.HTML
PAGE = 8
VIDID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
CLOSE_ROW = [Btn("• ᴄʟᴏsᴇ •", callback_data="close")]


# ===========================================================
# HELPERS
# ===========================================================

def _esc(text) -> str:
    return html.escape(str(text or ""))


async def _strings(chat_id: int):
    try:
        return get_string(await get_lang(chat_id))
    except Exception:
        return get_string("en")


def _current_song(chat_id: int):
    """Is chat me abhi jo YouTube gaana baj raha hai (db queue ka pehla item)."""
    queue = db.get(chat_id)
    if not queue:
        return None
    track = queue[0]
    vidid = str(track.get("vidid") or "")
    if not VIDID_RE.fullmatch(vidid):  # telegram / soundcloud / index stream
        return None
    return {"vidid": vidid, "title": track.get("title"), "dur": track.get("dur")}


async def _resolve(query: str) -> dict:
    """Naam ya YouTube link -> song dict."""
    q = query.strip()
    if "list=" in q and "watch?v=" not in q and "youtu.be" not in q:
        raise ValueError("playlist link")
    details, vidid = await YouTube.track(q)
    return {
        "vidid": vidid,
        "title": details["title"],
        "dur": details["duration_min"],
    }


def _pages(total: int) -> int:
    return max(1, math.ceil(total / PAGE))


def _clamp(page: int, total: int) -> int:
    return min(max(page, 0), _pages(total) - 1)


def _song_lines(songs, page: int) -> str:
    start = page * PAGE
    return "\n".join(
        f"<b>{start + i}.</b> {_esc(s['title'][:55])} <code>{_esc(s['dur'])}</code>"
        for i, s in enumerate(songs[start : start + PAGE], 1)
    )


def _nav_row(cb_prefix: str, page: int, pages: int):
    if pages <= 1:
        return None
    row = []
    if page > 0:
        row.append(Btn("⬅", callback_data=f"{cb_prefix}|{page - 1}"))
    row.append(Btn(f"{page + 1}/{pages}", callback_data="FavN 0"))
    if page < pages - 1:
        row.append(Btn("➡", callback_data=f"{cb_prefix}|{page + 1}"))
    return row


HELP_FAV = (
    "<b>💡 ᴛɪᴘ:</b> ɢᴀᴀɴᴀ ʙᴀᴊᴛᴇ ᴡᴀǫᴛ ❤️ ᴅᴀʙᴀᴏ ʏᴀ "
    "<code>/addfav song name</code> ʟɪᴋʜᴏ."
)
HELP_PL = (
    "<b>💡 ᴛɪᴘ:</b> <code>/newplaylist name</code> sᴇ ʙᴀɴᴀᴏ, "
    "<code>/addplaylist name | song</code> sᴇ ɢᴀᴀɴᴇ ᴅᴀʟᴏ."
)


# ===========================================================
# PANELS
# ===========================================================

def fav_panel(uid: int, songs: list, page: int = 0):
    page = _clamp(page, len(songs))
    text = f"<b>❤️ ʏᴏᴜʀ ꜰᴀᴠᴏᴜʀɪᴛᴇs</b> <code>({len(songs)}/{MAX_FAVS})</code>\n\n"
    if not songs:
        text += f"<blockquote>ᴀʙʜɪ ᴋᴏɪ ꜰᴀᴠᴏᴜʀɪᴛᴇ ɴᴀʜɪ.</blockquote>\n{HELP_FAV}"
        return text, Markup([HELP_ROW, CLOSE_ROW])

    text += f"<blockquote expandable>{_song_lines(songs, page)}</blockquote>"
    rows = []
    for s in songs[page * PAGE : (page + 1) * PAGE]:
        rows.append(
            [
                Btn(f"▶ {short_title(s['title'], 26)}", callback_data=f"FavP {uid}|{s['vidid']}"),
                Btn("🗑", callback_data=f"FavD {uid}|{s['vidid']}|{page}"),
            ]
        )
    nav = _nav_row(f"FavL {uid}", page, _pages(len(songs)))
    if nav:
        rows.append(nav)
    rows.append(
        [
            Btn("▶ ᴘʟᴀʏ ᴀʟʟ", callback_data=f"FavA {uid}|0"),
            Btn("🔀 sʜᴜꜰꜰʟᴇ", callback_data=f"FavA {uid}|1"),
            Btn("🧹 ᴄʟᴇᴀʀ", callback_data=f"FavC {uid}"),
        ]
    )
    rows.append(HELP_ROW)
    rows.append(CLOSE_ROW)
    return text, Markup(rows)


def playlists_panel(uid: int, pls: list):
    text = f"<b>📂 ʏᴏᴜʀ ᴘʟᴀʏʟɪsᴛs</b> <code>({len(pls)}/{MAX_PLAYLISTS})</code>\n\n"
    if not pls:
        text += f"<blockquote>ᴀʙʜɪ ᴋᴏɪ ᴘʟᴀʏʟɪsᴛ ɴᴀʜɪ.</blockquote>\n{HELP_PL}"
        return text, Markup([HELP_ROW, CLOSE_ROW])
    text += "<blockquote>" + "\n".join(
        f"<b>{i}.</b> {_esc(p['name'])} <code>({len(p['songs'])})</code>"
        for i, p in enumerate(pls, 1)
    ) + "</blockquote>\n" + HELP_PL
    rows = [
        [Btn(f"📂 {p['name'][:24]} ({len(p['songs'])})", callback_data=f"PlO {uid}|{p['id']}|0")]
        for p in pls
    ]
    rows.append(HELP_ROW)
    rows.append(CLOSE_ROW)
    return text, Markup(rows)


def playlist_panel(uid: int, pl: dict, page: int = 0):
    songs = pl["songs"]
    page = _clamp(page, len(songs))
    text = (
        f"<b>📂 {_esc(pl['name'])}</b> "
        f"<code>({len(songs)}/{MAX_PLAYLIST_SONGS})</code>\n\n"
    )
    if songs:
        text += f"<blockquote expandable>{_song_lines(songs, page)}</blockquote>"
    else:
        text += (
            "<blockquote>ᴘʟᴀʏʟɪsᴛ ᴋʜᴀʟɪ ʜᴀɪ.</blockquote>\n"
            f"<code>/addplaylist {_esc(pl['name'])} | song name</code>"
        )
    rows = []
    for s in songs[page * PAGE : (page + 1) * PAGE]:
        rows.append(
            [
                Btn(f"▶ {short_title(s['title'], 26)}", callback_data=f"PlP {uid}|{pl['id']}|{s['vidid']}"),
                Btn("❌", callback_data=f"PlR {uid}|{pl['id']}|{s['vidid']}|{page}"),
            ]
        )
    nav = _nav_row(f"PlO {uid}|{pl['id']}", page, _pages(len(songs)))
    if nav:
        rows.append(nav)
    if songs:
        rows.append(
            [
                Btn("▶ ᴘʟᴀʏ ᴀʟʟ", callback_data=f"PlA {uid}|{pl['id']}|0"),
                Btn("🔀 sʜᴜꜰꜰʟᴇ", callback_data=f"PlA {uid}|{pl['id']}|1"),
            ]
        )
    rows.append(
        [
            Btn("🗑 ᴅᴇʟᴇᴛᴇ", callback_data=f"PlX {uid}|{pl['id']}"),
            Btn("⬅ ʙᴀᴄᴋ", callback_data=f"PlL {uid}"),
        ]
    )
    return text, Markup(rows)


# ===========================================================
# PLAYING
# ===========================================================

async def _can_play(chat_id: int, user_id: int):
    """None = ok, warna error text."""
    if user_id in SUDOERS:
        return None
    if await is_maintenance() is False:
        return "🛠 Bot maintenance me hai."
    if await get_playtype(chat_id) != "Everyone":
        admins = adminlist.get(chat_id)
        if not admins:
            return "❌ Pehle /reload karo (admin list refresh)."
        if user_id not in admins:
            return "❌ Is group me sirf admins gaana play kar sakte hain."
    return None


async def _start_stream(chat_id: int, user, songs: list, source: str):
    _ = await _strings(chat_id)
    songs = songs[: config.PLAYLIST_FETCH_LIMIT]
    mystic = await app.send_message(chat_id, _["play_1"])
    try:
        if len(songs) == 1:
            s = songs[0]
            try:
                if time_to_seconds(s["dur"]) > config.DURATION_LIMIT:
                    return await mystic.edit_text(
                        _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                    )
            except Exception:
                pass
            details = {
                "link": f"https://www.youtube.com/watch?v={s['vidid']}",
                "vidid": s["vidid"],
                "title": s["title"],
                "duration_min": s["dur"],
                "thumb": f"https://i.ytimg.com/vi/{s['vidid']}/hqdefault.jpg",
            }
            await stream(
                _, mystic, user.id, details, chat_id, user.mention, chat_id, None,
                streamtype="youtube",
            )
            try:
                remember_played(chat_id, s["vidid"])
                await track_logs(chat_id, s["title"], s["vidid"], source, user)
            except Exception:
                pass
        else:
            await stream(
                _, mystic, user.id, [s["vidid"] for s in songs], chat_id,
                user.mention, chat_id, None, streamtype="playlist",
            )
    except Exception as e:
        traceback.print_exc()
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        return await mystic.edit_text(err)
    try:
        await mystic.delete()
    except Exception:
        pass


async def _play_from_callback(q, songs: list, source: str):
    if q.message.chat.type == enums.ChatType.PRIVATE:
        return await q.answer(
            "🎧 Gaana bajane ke liye ye panel kisi group me kholo (/fav ya /playlist).",
            show_alert=True,
        )
    if not songs:
        return await q.answer("❌ Koi gaana nahi mila.", show_alert=True)
    err = await _can_play(q.message.chat.id, q.from_user.id)
    if err:
        return await q.answer(err, show_alert=True)
    await q.answer("🎧 ʟᴏᴀᴅɪɴɢ...")
    await _start_stream(q.message.chat.id, q.from_user, songs, source)


async def _play_from_command(message, songs: list, source: str):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("🎧 Ye command group me use karo (VC me bajane ke liye).")
    err = await _can_play(message.chat.id, message.from_user.id)
    if err:
        return await message.reply_text(err)
    await _start_stream(message.chat.id, message.from_user, songs, source)


# ===========================================================
# COMMANDS
# ===========================================================

def _arg(message) -> str:
    parts = (message.text or "").split(None, 1)
    return parts[1].strip() if len(parts) > 1 else ""


def _add_result_text(status: str, title: str, where: str) -> str:
    t = _esc(title[:60])
    return {
        "added": f"✅ <b>{t}</b> — {where} me add ho gaya.",
        "exists": f"ℹ️ <b>{t}</b> pehle se {where} me hai.",
        "full": f"❌ {where} full hai. Pehle kuch hata do.",
        "missing": "❌ Playlist nahi mili.",
    }[status]


@app.on_message(filters.command(HELP_COMMANDS) & ~BANNED_USERS)
async def playlist_help_cmd(client, message):
    text, mk = help_panel("main")
    await message.reply_text(text, reply_markup=mk, parse_mode=HTML)


@app.on_message(filters.command(["fav", "favs", "favourites", "favorites"]) & ~BANNED_USERS)
async def fav_cmd(client, message):
    if not message.from_user:
        return
    songs = await get_favs(message.from_user.id)
    text, mk = fav_panel(message.from_user.id, songs)
    await message.reply_text(text, reply_markup=mk, parse_mode=HTML)


@app.on_message(filters.command(["addfav", "addfavourite", "addfavorite"]) & ~BANNED_USERS)
async def addfav_cmd(client, message):
    if not message.from_user:
        return
    query = _arg(message)
    if not query:
        song = _current_song(message.chat.id)
        if not song:
            return await message.reply_text(
                "ℹ️ Usage: <code>/addfav song name</code> ya link.\n"
                "Ya gaana bajte waqt bina naam ke <code>/addfav</code> likho.",
                parse_mode=HTML,
            )
        status = await add_fav(message.from_user.id, song)
        return await message.reply_text(
            _add_result_text(status, song["title"], "favourites"), parse_mode=HTML
        )
    mystic = await message.reply_text("🔎 ᴅʜᴜɴᴅ ʀᴀʜᴀ ʜᴏᴏɴ...")
    try:
        song = await _resolve(query)
    except Exception:
        return await mystic.edit_text("❌ Gaana nahi mila. Naam ya YouTube link check karo.")
    status = await add_fav(message.from_user.id, song)
    await mystic.edit_text(_add_result_text(status, song["title"], "favourites"), parse_mode=HTML)


@app.on_message(filters.command(["playfav", "favplay"]) & ~BANNED_USERS)
async def playfav_cmd(client, message):
    if not message.from_user:
        return
    songs = await get_favs(message.from_user.id)
    if not songs:
        return await message.reply_text("❌ Tumhare favourites khali hain. /addfav se gaane add karo.")
    if "shuffle" in _arg(message).lower():
        random.shuffle(songs)
    await _play_from_command(message, songs, "Favourites")


@app.on_message(filters.command(["playlist", "playlists", "myplaylist"]) & ~BANNED_USERS)
async def playlist_cmd(client, message):
    if not message.from_user:
        return
    if _arg(message).lower() == "help":
        text, mk = help_panel("pl")
        return await message.reply_text(text, reply_markup=mk, parse_mode=HTML)
    pls = await get_user_playlists(message.from_user.id)
    text, mk = playlists_panel(message.from_user.id, pls)
    await message.reply_text(text, reply_markup=mk, parse_mode=HTML)


@app.on_message(filters.command(["newplaylist", "createplaylist"]) & ~BANNED_USERS)
async def newplaylist_cmd(client, message):
    if not message.from_user:
        return
    name = _arg(message)
    if not name:
        return await message.reply_text(
            "ℹ️ Usage: <code>/newplaylist My Gym Mix</code>", parse_mode=HTML
        )
    status, pl = await create_user_playlist(message.from_user.id, name)
    if status == "ok":
        return await message.reply_text(
            f"✅ Playlist <b>{_esc(pl['name'])}</b> ban gayi.\n"
            f"Gaane add karo: <code>/addplaylist {_esc(pl['name'])} | song name</code>",
            parse_mode=HTML,
        )
    await message.reply_text(
        {
            "exists": "ℹ️ Is naam ki playlist pehle se hai.",
            "full": f"❌ Max {MAX_PLAYLISTS} playlists ban sakti hain.",
            "invalid": "❌ Playlist ka naam likho.",
        }[status]
    )


@app.on_message(filters.command(["addplaylist", "addtoplaylist"]) & ~BANNED_USERS)
async def addplaylist_cmd(client, message):
    if not message.from_user:
        return
    raw = _arg(message)
    if not raw:
        return await message.reply_text(
            "ℹ️ Usage: <code>/addplaylist name | song name</code>\n"
            "Ya abhi baj rahe gaane ke liye: <code>/addplaylist name</code>",
            parse_mode=HTML,
        )
    name, _sep, query = raw.partition("|")
    pl = await find_user_playlist_by_name(message.from_user.id, name)
    if not pl:
        return await message.reply_text(
            "❌ Is naam ki playlist nahi mili. /playlist se dekho ya /newplaylist se banao."
        )
    query = query.strip()
    if query:
        mystic = await message.reply_text("🔎 ᴅʜᴜɴᴅ ʀᴀʜᴀ ʜᴏᴏɴ...")
        try:
            song = await _resolve(query)
        except Exception:
            return await mystic.edit_text("❌ Gaana nahi mila. Naam ya YouTube link check karo.")
        reply = mystic.edit_text
    else:
        song = _current_song(message.chat.id)
        if not song:
            return await message.reply_text(
                "ℹ️ Abhi koi gaana nahi baj raha. <code>/addplaylist name | song name</code> use karo.",
                parse_mode=HTML,
            )
        reply = message.reply_text
    status = await add_to_user_playlist(message.from_user.id, pl["id"], song)
    await reply(_add_result_text(status, song["title"], f"“{_esc(pl['name'])}”"), parse_mode=HTML)


@app.on_message(filters.command(["delplaylist", "deleteplaylist"]) & ~BANNED_USERS)
async def delplaylist_cmd(client, message):
    if not message.from_user:
        return
    name = _arg(message)
    pl = await find_user_playlist_by_name(message.from_user.id, name) if name else None
    if not pl:
        return await message.reply_text(
            "ℹ️ Usage: <code>/delplaylist name</code> (naam /playlist me dekho)", parse_mode=HTML
        )
    await delete_user_playlist(message.from_user.id, pl["id"])
    await message.reply_text(f"🗑 Playlist <b>{_esc(pl['name'])}</b> delete ho gayi.", parse_mode=HTML)


@app.on_message(filters.command(["playplaylist", "plplay"]) & ~BANNED_USERS)
async def playplaylist_cmd(client, message):
    if not message.from_user:
        return
    raw = _arg(message)
    shuffle = raw.lower().endswith("shuffle")
    if shuffle:
        raw = raw[: -len("shuffle")].strip()
    pl = await find_user_playlist_by_name(message.from_user.id, raw) if raw else None
    if not pl:
        return await message.reply_text(
            "ℹ️ Usage: <code>/playplaylist name [shuffle]</code>", parse_mode=HTML
        )
    songs = pl["songs"][:]
    if not songs:
        return await message.reply_text("❌ Ye playlist khali hai.")
    if shuffle:
        random.shuffle(songs)
    await _play_from_command(message, songs, f"Playlist ({pl['name']})")


# ===========================================================
# CALLBACKS
# ===========================================================

async def _edit(q, text, mk):
    try:
        await q.edit_message_text(
            text, reply_markup=mk, parse_mode=HTML, disable_web_page_preview=True
        )
    except MessageNotModified:
        pass


async def _show_fav(q, uid, page=0):
    text, mk = fav_panel(uid, await get_favs(uid), page)
    await _edit(q, text, mk)


async def _show_playlists(q, uid):
    text, mk = playlists_panel(uid, await get_user_playlists(uid))
    await _edit(q, text, mk)


async def _show_playlist(q, uid, pid, page=0):
    pl = await get_user_playlist(uid, pid)
    if not pl:
        await q.answer("❌ Playlist nahi mili.", show_alert=True)
        return await _show_playlists(q, uid)
    text, mk = playlist_panel(uid, pl, page)
    await _edit(q, text, mk)


# ---- favourites ----

async def cb_noop(q, a):
    await q.answer()


async def cb_help_now(q, a):
    # now-playing message photo/caption wala hota hai, isliye edit nahi, popup dikhao
    await q.answer(HELP_NOW_ALERT, show_alert=True)


async def cb_help(q, a):
    text, mk = help_panel(a[0])
    await _edit(q, text, mk)
    await q.answer()


async def cb_fav_list(q, a):
    await _show_fav(q, int(a[0]), int(a[1]))
    await q.answer()


async def cb_fav_play(q, a):
    song = next((s for s in await get_favs(int(a[0])) if s["vidid"] == a[1]), None)
    if not song:
        return await q.answer("❌ Ye gaana ab list me nahi hai.", show_alert=True)
    await _play_from_callback(q, [song], "Favourites")


async def cb_fav_del(q, a):
    uid = int(a[0])
    await remove_fav(uid, a[1])
    await q.answer("🗑 Hata diya")
    await _show_fav(q, uid, int(a[2]))


async def cb_fav_all(q, a):
    songs = await get_favs(int(a[0]))
    if a[1] == "1":
        random.shuffle(songs)
    await _play_from_callback(q, songs, "Favourites")


async def cb_fav_clear(q, a):
    uid = int(a[0])
    await _edit(
        q,
        "<b>🧹 Saare favourites hata dun?</b>\nYe wapas nahi aayenge.",
        Markup(
            [[Btn("✅ ʜᴀᴀɴ", callback_data=f"FavCY {uid}"), Btn("❌ ɴᴀʜɪ", callback_data=f"FavL {uid}|0")]]
        ),
    )
    await q.answer()


async def cb_fav_clear_yes(q, a):
    uid = int(a[0])
    await clear_favs(uid)
    await q.answer("🧹 Favourites clear")
    await _show_fav(q, uid)


# ---- playlists ----

async def cb_pl_list(q, a):
    await _show_playlists(q, int(a[0]))
    await q.answer()


async def cb_pl_open(q, a):
    await _show_playlist(q, int(a[0]), a[1], int(a[2]))
    await q.answer()


async def cb_pl_play(q, a):
    pl = await get_user_playlist(int(a[0]), a[1])
    song = next((s for s in (pl or {}).get("songs", []) if s["vidid"] == a[2]), None)
    if not song:
        return await q.answer("❌ Ye gaana ab playlist me nahi hai.", show_alert=True)
    await _play_from_callback(q, [song], f"Playlist ({pl['name']})")


async def cb_pl_remove(q, a):
    uid = int(a[0])
    await remove_from_user_playlist(uid, a[1], a[2])
    await q.answer("❌ Hata diya")
    await _show_playlist(q, uid, a[1], int(a[3]))


async def cb_pl_all(q, a):
    pl = await get_user_playlist(int(a[0]), a[1])
    if not pl or not pl["songs"]:
        return await q.answer("❌ Playlist khali hai.", show_alert=True)
    songs = pl["songs"][:]
    if a[2] == "1":
        random.shuffle(songs)
    await _play_from_callback(q, songs, f"Playlist ({pl['name']})")


async def cb_pl_delete(q, a):
    uid = int(a[0])
    pl = await get_user_playlist(uid, a[1])
    if not pl:
        return await _show_playlists(q, uid)
    await _edit(
        q,
        f"<b>🗑 “{_esc(pl['name'])}” delete kar dun?</b>\nIsme {len(pl['songs'])} gaane hain.",
        Markup(
            [
                [
                    Btn("✅ ʜᴀᴀɴ", callback_data=f"PlXY {uid}|{a[1]}"),
                    Btn("❌ ɴᴀʜɪ", callback_data=f"PlO {uid}|{a[1]}|0"),
                ]
            ]
        ),
    )
    await q.answer()


async def cb_pl_delete_yes(q, a):
    uid = int(a[0])
    await delete_user_playlist(uid, a[1])
    await q.answer("🗑 Playlist delete")
    await _show_playlists(q, uid)


# ---- now-playing message ke buttons ----

async def _restore_markup(q, chat_id: int):
    _ = await _strings(chat_id)
    try:
        await q.edit_message_reply_markup(Markup(stream_markup(_, chat_id)))
    except MessageNotModified:
        pass


async def cb_fav_now(q, a):
    song = _current_song(int(a[0]))
    if not song:
        return await q.answer("ℹ️ Abhi koi YouTube gaana nahi baj raha.", show_alert=True)
    status = await add_fav(q.from_user.id, song)
    await q.answer(
        {
            "added": "❤️ Favourites me add ho gaya!",
            "exists": "ℹ️ Ye pehle se favourites me hai.",
            "full": f"❌ Favourites full ({MAX_FAVS}).",
        }[status],
        show_alert=status != "added",
    )


async def cb_pl_pick(q, a):
    chat_id = int(a[0])
    if not _current_song(chat_id):
        return await q.answer("ℹ️ Abhi koi YouTube gaana nahi baj raha.", show_alert=True)
    pls = await get_user_playlists(q.from_user.id)
    if not pls:
        return await q.answer(
            "📂 Tumhari koi playlist nahi hai. Pehle likho: /newplaylist name",
            show_alert=True,
        )
    rows = [
        [Btn(f"📂 {p['name'][:24]} ({len(p['songs'])})", callback_data=f"PlAdd {chat_id}|{p['id']}")]
        for p in pls
    ]
    rows.append([Btn("⬅ ʙᴀᴄᴋ", callback_data=f"PlBack {chat_id}")])
    await q.edit_message_reply_markup(Markup(rows))
    await q.answer("Kis playlist me add karun?")


async def cb_pl_add(q, a):
    chat_id = int(a[0])
    song = _current_song(chat_id)
    if not song:
        await q.answer("ℹ️ Abhi koi YouTube gaana nahi baj raha.", show_alert=True)
        return await _restore_markup(q, chat_id)
    pl = await get_user_playlist(q.from_user.id, a[1])
    status = await add_to_user_playlist(q.from_user.id, a[1], song)
    name = pl["name"] if pl else "playlist"
    await q.answer(
        {
            "added": f"✅ “{name}” me add ho gaya!",
            "exists": f"ℹ️ Ye pehle se “{name}” me hai.",
            "full": f"❌ “{name}” full hai ({MAX_PLAYLIST_SONGS}).",
            "missing": "❌ Playlist nahi mili.",
        }[status],
        show_alert=status != "added",
    )
    await _restore_markup(q, chat_id)


async def cb_pl_back(q, a):
    await _restore_markup(q, int(a[0]))
    await q.answer()


# (handler, first arg user_id hai? -> sirf owner dabaye)
CALLBACKS = {
    "FavN": (cb_noop, False),
    "PlHelp": (cb_help, False),
    "PlHelpNow": (cb_help_now, False),
    "FavL": (cb_fav_list, True),
    "FavP": (cb_fav_play, True),
    "FavD": (cb_fav_del, True),
    "FavA": (cb_fav_all, True),
    "FavC": (cb_fav_clear, True),
    "FavCY": (cb_fav_clear_yes, True),
    "PlL": (cb_pl_list, True),
    "PlO": (cb_pl_open, True),
    "PlP": (cb_pl_play, True),
    "PlR": (cb_pl_remove, True),
    "PlA": (cb_pl_all, True),
    "PlX": (cb_pl_delete, True),
    "PlXY": (cb_pl_delete_yes, True),
    "FavNow": (cb_fav_now, False),
    "PlPick": (cb_pl_pick, False),
    "PlAdd": (cb_pl_add, False),
    "PlBack": (cb_pl_back, False),
}

_CB_REGEX = r"^(" + "|".join(sorted(CALLBACKS, key=len, reverse=True)) + r") "


async def _dispatch(q):
    cmd, _sep, arg = q.data.partition(" ")
    handler, owner_only = CALLBACKS[cmd]
    args = arg.split("|")
    if owner_only and int(args[0]) != q.from_user.id:
        return await q.answer(
            "❌ Ye panel tumhara nahi hai. Apna kholne ke liye /fav ya /playlist likho.",
            show_alert=True,
        )
    await handler(q, args)


# group=-1 + StopPropagation: purane unanchored regex handlers beech me na aaye
@app.on_callback_query(filters.regex(_CB_REGEX) & ~BANNED_USERS, group=-1)
async def favourites_callbacks(client, q):
    try:
        await _dispatch(q)
    except Exception:
        traceback.print_exc()
        try:
            await q.answer("❌ Kuch gadbad ho gayi, dobara try karo.", show_alert=True)
        except Exception:
            pass
    raise StopPropagation

