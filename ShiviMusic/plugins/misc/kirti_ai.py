# ===========================================================
# Kirti - naam se bulao, kaam ho jayega (koi AI / API / key nahi)
#
# Sab kuch bot ke apne code se chalta hai. Group me "Kirti" naam ke saath bolo:
#   "Kirti tum hi ho bajao"        -> song play
#   "Kirti play despacito"         -> song play
#   "Kirti song band kar do"       -> stop
#   "Kirti pause karo"             -> pause
#   "Kirti chalu karo"             -> resume
#   "Kirti next / skip karo"       -> skip
#   (reply karke) "Kirti isko mute kar do" / "10 min mute karo" -> mute
#   (reply karke) "Kirti isko unmute karo"                      -> unmute
#   "Kirti @username ko chup kar do" bhi chalega
#   "Kirti isko admin bana do half" / "... full" -> admin promote (half = /promote jaise,
#                                                  full = /fullpromote jaise)
#
# Rules:
#   - Music commands pe wahi admin rules jo /play /stop /skip pe hain.
#   - Mute/unmute sirf admin (Restrict right), owner ya sudo.
#   - Promote sirf owner / sudo / "Add admins" right wala admin.
#   - Admin / owner / sudo / bot mute nahi hote.
#   - Bot ko "Restrict members" admin right chahiye.
# ===========================================================

import asyncio
import re
import time

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, MessageEntityType, ParseMode
from pyrogram.types import ChatPermissions, ChatPrivileges, Message

from ShiviMusic import app
from ShiviMusic.misc import SUDOERS
from ShiviMusic.plugins.admins.pause import pause_admin
from ShiviMusic.plugins.admins.resume import resume_com
from ShiviMusic.plugins.admins.skip import skip as skip_music
from ShiviMusic.plugins.admins.stop import stop_music
from ShiviMusic.plugins.play.play import play_commnd
from config import BANNED_USERS, OWNER_ID

COOLDOWN_SEC = 3
DELETE_AFTER_SEC = 10  # mute/unmute + stop/pause/resume/skip ke text-messages itne second baad delete
PLAY_DELETE_SEC = 45  # play ka 'searching/error' message (download me time lagta hai, 10s me delete hua to play toot sakta hai)
_last_call = {}

_NAME_LATIN = re.compile(r"(?<![a-z])(kirti|kirthi|keerti|keerthi|kriti)(?![a-z])")
_NAME_DEVA = ("कीर्ति", "कीर्ती", "कीरती", "कीरति", "कृति")

_PROMOTE = (
    "promote", "admin bana", "admin kar", "admin do", "admin de", "admin banao",
    "एडमिन बना", "एडमिन कर", "एडमिन दे", "प्रमोट",
)
_FULL = ("full", "ful", "poora", "pura", "पूरा", "फुल")
_HALF = ("half", "aadha", "adha", "limited", "आधा", "हाफ")

# Check order: promote > unmute > mute > skip > stop > pause > play/resume
_UNMUTE = ("unmute", "un mute", "anmute", "mute hata", "mute khol", "bolne do", "बोलने दो", "अनम्यूट")
_MUTE = ("mute", "chup", "shant", "shaant", "चुप", "म्यूट")
_SKIP = ("skip", "next", "agla", "aglaa", "badlo", "अगला", "स्किप")
_STOP = ("band", "bandh", "stop", "end", "khatam", "rok", "बंद", "रोक", "खत्म", "स्टॉप")
_PAUSE = ("pause", "thehro", "thahro", "ruko", "ठहरो", "रुको", "पॉज")
_RESUME = ("resume", "chalu", "continue", "dobara", "phir se", "फिर से", "चालू")
_PLAY = (
    "play", "bajao", "baja", "bajana", "bajaiye", "chalao", "chala", "laga", "lagao",
    "sunao", "suna", "बजाओ", "बजा", "चलाओ", "चला", "लगाओ", "सुनाओ", "प्ले",
)
# song name se hatane wale faltu shabd
_FILLER = {
    "play", "bajao", "baja", "bajana", "bajaiye", "chalao", "chala", "laga", "lagao",
    "sunao", "suna", "kar", "karo", "kardo", "do", "de", "dena", "dijiye", "please",
    "plz", "pls", "song", "gana", "gaana", "music", "mujhe", "hume", "ek", "zara",
    "yaar", "bhai", "bro", "ji", "kirti", "kirthi", "keerti", "keerthi", "kriti",
    "बजाओ", "बजा", "चलाओ", "चला", "लगाओ", "सुनाओ", "प्ले", "कर", "करो", "दो", "दे",
    "गाना", "गाने", "सॉन्ग", "कीर्ति", "कीर्ती", "कीरती", "कीरति", "कृति",
}

_DUR = re.compile(
    r"(\d+)\s*(min|mins|minute|minutes|mint|मिनट|ghant|ghante|ghanta|hour|hours|hr|hrs|घंटा|घंटे|din|day|days|दिन)"
)


def _has_name(text: str) -> bool:
    if _NAME_LATIN.search(text):
        return True
    return any(n in text for n in _NAME_DEVA)


def _has(text: str, words) -> bool:
    for w in words:
        if w.isascii():
            # shuruaat match ho (friend, send jaise galat match na hon)
            tail = r"(?![a-z])" if len(w) <= 3 else ""
            if re.search(r"(?<![a-z])" + re.escape(w) + tail, text):
                return True
        elif w in text:
            return True
    return False


def _parse_minutes(text: str) -> int:
    """'10 min' / '2 ghante' / '1 din' -> minutes. Kuch nahi mila to 0 (permanent)."""
    m = _DUR.search(text)
    if not m:
        return 0
    n, unit = int(m.group(1)), m.group(2)
    if unit.startswith(("min", "मिनट")):
        return n
    if unit.startswith(("ghant", "hour", "hr", "घंट")):
        return n * 60
    return n * 1440


def _song_query(text: str, extra=()) -> str:
    """Original message se naam / play-words hatao, jo bacha wahi song ka naam."""
    if re.search(r"https?://\S+", text):
        return re.search(r"https?://\S+", text).group(0)
    words = re.sub(r"[^\w\s\u0900-\u097F'-]", " ", text).split()
    kept = [w for w in words if w.lower() not in _FILLER and w.lower() not in extra]
    return " ".join(kept).strip()[:150]


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
async def _delete_later(msg: Message, sec: int = DELETE_AFTER_SEC):
    await asyncio.sleep(sec)
    try:
        await msg.delete()
    except Exception:
        pass


def _autodelete(message: Message, sec: int = DELETE_AFTER_SEC):
    """Existing music handlers jo message.reply_text() se text bhejte hain, wo sec baad delete.
    (Now-playing card reply_photo / send_photo se jata hai, wo delete nahi hota.)"""
    orig = message.reply_text

    async def wrapped(*args, **kwargs):
        sent = await orig(*args, **kwargs)
        try:
            asyncio.create_task(_delete_later(sent, sec))
        except Exception:
            pass
        return sent

    message.reply_text = wrapped


async def _reply_temp(message: Message, text: str, **kw):
    """Normal message bhejo (reply-quote nahi), DELETE_AFTER_SEC second baad delete."""
    sent = await app.send_message(message.chat.id, text, **kw)
    asyncio.create_task(_delete_later(sent))
    return sent


async def _can_restrict(chat_id: int, user_id: int) -> bool:
    if user_id in SUDOERS or user_id == OWNER_ID:
        return True
    try:
        m = await app.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    if m.status == ChatMemberStatus.OWNER:
        return True
    return bool(
        m.status == ChatMemberStatus.ADMINISTRATOR
        and m.privileges
        and m.privileges.can_restrict_members
    )


async def _can_promote(chat_id: int, user_id: int) -> bool:
    if user_id in SUDOERS or user_id == OWNER_ID:
        return True
    try:
        m = await app.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    if m.status == ChatMemberStatus.OWNER:
        return True
    return bool(
        m.status == ChatMemberStatus.ADMINISTRATOR
        and m.privileges
        and m.privileges.can_promote_members
    )


async def _find_target(message: Message):
    """@username / text-mention / reply / numeric id se target user nikalo."""
    text = message.text or ""
    for ent in message.entities or []:
        if ent.type == MessageEntityType.TEXT_MENTION and ent.user:
            return ent.user
        if ent.type == MessageEntityType.MENTION:
            uname = text[ent.offset : ent.offset + ent.length]
            try:
                return await app.get_users(uname)
            except Exception:
                return None

    um = re.search(r"@([A-Za-z0-9_]{4,32})", text)
    if um:
        try:
            return await app.get_users(um.group(0))
        except Exception:
            return None

    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    m = re.search(r"\b(\d{6,12})\b", text)
    if m:
        try:
            return await app.get_users(int(m.group(1)))
        except Exception:
            return None
    return None


async def _is_protected(chat_id: int, user) -> bool:
    if user.is_bot or user.id in SUDOERS or user.id == OWNER_ID:
        return True
    try:
        m = await app.get_chat_member(chat_id, user.id)
        return m.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except Exception:
        return False


async def _do_mute(message: Message, minutes: int, mute: bool):
    chat_id = message.chat.id
    if not await _can_restrict(chat_id, message.from_user.id):
        return await _reply_temp(message, "❌ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ sɪʀғ ᴀᴅᴍɪɴ (ʀᴇsᴛʀɪᴄᴛ ʀɪɢʜᴛ ᴡᴀʟᴇ) ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ.")

    target = await _find_target(message)
    if not target:
        return await _reply_temp(
            message,
            "ᴋɪsᴋᴏ? @ᴜsᴇʀɴᴀᴍᴇ ᴛᴀɢ ᴋᴀʀᴏ (ʏᴀ ʀᴇᴘʟʏ ᴋᴀʀᴏ)."
        )

    if mute and await _is_protected(chat_id, target):
        return await _reply_temp(message, "😅 ᴀᴅᴍɪɴ / ᴏᴡɴᴇʀ / ʙᴏᴛ ᴋᴏ ᴍᴜᴛᴇ ɴᴀʜɪ ᴋɪʏᴀ ᴊᴀ sᴀᴋᴛᴀ.")

    try:
        if mute:
            secs = minutes * 60
            until = int(time.time()) + secs if secs else 0
            await app.restrict_chat_member(
                chat_id, target.id, ChatPermissions(), until_date=until
            )
            dur = f" ({secs // 60} ᴍɪɴ)" if secs and secs < 3600 else (
                f" ({secs // 3600} ʜᴏᴜʀ)" if secs and secs < 86400 else (
                    f" ({secs // 86400} ᴅᴀʏ)" if secs else ""
                )
            )
            await _reply_temp(
                message,
                f"🔇 {target.mention} ᴋᴏ ᴍᴜᴛᴇ ᴋᴀʀ ᴅɪʏᴀ{dur}.", parse_mode=ParseMode.HTML
            )
        else:
            chat = await app.get_chat(chat_id)
            perms = chat.permissions or ChatPermissions(
                can_send_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
            )
            await app.restrict_chat_member(chat_id, target.id, perms)
            await _reply_temp(
                message,
                f"🔊 {target.mention} ᴋᴏ ᴜɴᴍᴜᴛᴇ ᴋᴀʀ ᴅɪʏᴀ.", parse_mode=ParseMode.HTML
            )
    except Exception as e:
        await _reply_temp(
            message,
            "❌ ɴᴀʜɪ ʜᴏ sᴀᴋᴀ. ʙᴏᴛ ᴋᴏ <b>Restrict members</b> ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴄʜᴀʜɪʏᴇ.\n"
            f"<code>{type(e).__name__}</code>",
            parse_mode=ParseMode.HTML,
        )


async def _do_promote(message: Message, full):
    chat_id = message.chat.id
    if not await _can_promote(chat_id, message.from_user.id):
        return await _reply_temp(message, "❌ ᴘʀᴏᴍᴏᴛᴇ sɪʀғ ᴏᴡɴᴇʀ ʏᴀ \"ᴀᴅᴅ ᴀᴅᴍɪɴs\" ʀɪɢʜᴛ ᴡᴀʟᴇ ᴀᴅᴍɪɴ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ.")

    target = await _find_target(message)
    if not target:
        return await _reply_temp(message, "ᴋɪsᴋᴏ? @ᴜsᴇʀɴᴀᴍᴇ ᴛᴀɢ ᴋᴀʀᴏ (ʏᴀ ʀᴇᴘʟʏ ᴋᴀʀᴏ).")
    if full is None:
        return await _reply_temp(
            message,
            f"{target.mention} ᴋᴏ <b>full</b> ʏᴀ <b>half</b> ᴀᴅᴍɪɴ? "
            "ᴊᴀɪsᴇ: <i>Kirti isko admin bana do full</i>",
            parse_mode=ParseMode.HTML,
        )

    try:
        member = await app.get_chat_member(chat_id, target.id)
        if member.status == ChatMemberStatus.OWNER:
            return await _reply_temp(message, "😅 ᴏᴡɴᴇʀ ᴘᴇ ᴋᴀᴍ ɴᴀʜɪ ᴋᴀʀ sᴀᴋᴛᴇ.")
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return await _reply_temp(message, "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ.")
    except Exception:
        pass

    if full:
        privs = ChatPrivileges(
            can_manage_chat=True,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=True,
            is_anonymous=False,
            can_manage_video_chats=True,
        )
    else:
        privs = ChatPrivileges(
            can_change_info=False,
            can_delete_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_restrict_members=False,
            can_promote_members=False,
            can_manage_chat=True,
            can_manage_video_chats=True,
            is_anonymous=False,
        )
    try:
        await app.promote_chat_member(chat_id, target.id, privileges=privs)
        kind = "ꜰᴜʟʟ" if full else "ʜᴀʟꜰ"
        await _reply_temp(
            message,
            f"👑 {target.mention} ᴋᴏ {kind} ᴀᴅᴍɪɴ ʙᴀɴᴀ ᴅɪʏᴀ.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await _reply_temp(
            message,
            "❌ ɴᴀʜɪ ʜᴏ sᴀᴋᴀ. ʙᴏᴛ ᴋᴏ <b>Add new admins</b> ᴀᴅᴍɪɴ ʀɪɢʜᴛ ᴄʜᴀʜɪʏᴇ.\n"
            f"<code>{type(e).__name__}</code>",
            parse_mode=ParseMode.HTML,
        )


# ---------------------------------------------------------------
# Main listener
# ---------------------------------------------------------------
async def _run_play(client, message: Message, query: str):
    _autodelete(message, PLAY_DELETE_SEC)
    # play handler message.text / message.command se query padhta hai
    message.text = f"/play {query}".strip()
    message.command = ["play"] + query.split()
    await play_commnd(client, message)


@app.on_message(
    filters.text
    & filters.group
    & ~filters.via_bot
    & ~filters.regex(r"^[/!.]")  # normal commands ko mat chhedo
    & ~BANNED_USERS,
    group=7,
)
async def kirti_cmd(client, message: Message):
    if not message.from_user:
        return
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return

    raw = (message.text or "").strip()
    text = raw.lower()
    if len(raw) > 200 or not _has_name(text):
        return

    now = time.time()
    if now - _last_call.get(message.from_user.id, 0) < COOLDOWN_SEC:
        return
    _last_call[message.from_user.id] = now

    if _has(text, _PROMOTE):
        if _has(text, _HALF):
            full = False
        elif _has(text, _FULL):
            full = True
        else:
            full = None  # bataya nahi to pooch lo, guess nahi karna
        return await _do_promote(message, full)
    if _has(text, _UNMUTE):
        return await _do_mute(message, 0, mute=False)
    if _has(text, _MUTE):
        return await _do_mute(message, _parse_minutes(text), mute=True)

    handlers = (
        (_SKIP, skip_music, "skip"),
        (_STOP, stop_music, "stop"),
        (_PAUSE, pause_admin, "pause"),
    )
    for words, handler, name in handlers:
        if _has(text, words):
            message.command = [name]  # existing handlers message.command[0] padhte hain
            _autodelete(message)
            return await handler(client, message)

    # play / resume
    has_play = _has(text, _PLAY)
    has_resume = _has(text, _RESUME)
    if has_resume:
        # "chalu karo", "phir se chalao" - song ka naam nahi hai to resume
        left = _song_query(
            raw, extra={"resume", "chalu", "continue", "dobara", "phir", "se", "चालू", "फिर", "से"}
        )
        if not left:
            message.command = ["resume"]
            _autodelete(message)
            return await resume_com(client, message)
    if not has_play:
        return  # sirf naam liya / baat ki - kuch nahi karna
    query = _song_query(raw)
    if query:
        return await _run_play(client, message, query)
    if _has(text, ("chalao", "chala", "चलाओ", "चला")):
        message.command = ["resume"]  # "Kirti chalao" = ruka hua gana chalao
        _autodelete(message)
        return await resume_com(client, message)
    return await _run_play(client, message, "")
