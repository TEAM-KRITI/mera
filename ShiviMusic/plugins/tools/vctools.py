# ============================================================
# 🎧 ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sʏsᴛᴇᴍ
# ============================================================

from pyrogram import filters, raw
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import os

from ShiviMusic import app
from ShiviMusic.utils.vc_card import make_vc_card
from ShiviMusic.utils.database import get_assistant

try:  # native coloured buttons (purana kurigram ho to plain button)
    from pyrogram.enums import ButtonStyle
    _GREEN = ButtonStyle.SUCCESS
except Exception:
    _GREEN = None


# ============================================================
# 🔘 ʙᴜᴛᴛᴏɴs
# ============================================================

async def get_buttons(client):

    me = await client.get_me()

    username = me.username

    if username:
        add_url = f"https://t.me/{username}?startgroup=true"
    else:
        add_url = "https://t.me/"

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✙ ᴧᴅᴅ ᴍᴇ ✙",
                    url=add_url,
                ),
                InlineKeyboardButton(
                    "≡ ᴄʟᴏsᴇ ≡",
                    callback_data="close_vc_message",
                ),
            ]
        ]
    )


# ============================================================
# 🟢 ᴠᴄ sᴛᴀʀᴛᴇᴅ
# ============================================================

async def _vc_join_url(client, chat):
    """Public group -> t.me/username?videochat, private -> invite link?videochat"""
    if chat.username:
        return f"https://t.me/{chat.username}?videochat"
    try:
        link = chat.invite_link or await client.export_chat_invite_link(chat.id)
        if link:
            return f"{link}?videochat"
    except Exception:
        pass
    return None


def _join_button(url):
    text = "ᴊᴏɪɴ"
    if _GREEN is not None:
        try:
            return InlineKeyboardButton(text, url=url, style=_GREEN)
        except TypeError:
            pass
    return InlineKeyboardButton("🟢 " + text, url=url)


async def _send_vc_card(client, message, participants: int = 0):
    """VC card (PNG + JOIN button) bhejta hai."""
    photo_path = None
    card_path = f"cache/vc_card_{message.chat.id}.png"

    try:
        # group ki photo (circle me), na ho to default
        try:
            if message.chat.photo:
                photo_path = await client.download_media(
                    message.chat.photo.big_file_id,
                    file_name=f"vcpp{message.chat.id}.png",
                )
        except Exception:
            photo_path = None

        make_vc_card(photo_path, participants=participants, out_path=card_path)

        join_url = await _vc_join_url(client, message.chat)

        rows = []
        if join_url:
            rows.append([_join_button(join_url)])
        rows.extend((await get_buttons(client)).inline_keyboard)

        word = "participant" if participants == 1 else "participants"
        await message.reply_photo(
            card_path,
            caption=f"Voice Chat · {participants} {word}",
            reply_markup=InlineKeyboardMarkup(rows),
        )

    finally:
        for f in (card_path, photo_path):
            try:
                if f and os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass


@app.on_message(filters.video_chat_started)
async def video_chat_started(client, message):
    try:
        await _send_vc_card(client, message, participants=0)
    except Exception as e:
        print(f"VIDEO CHAT START ERROR: {e}")


# ============================================================
# 🔢 ʟɪᴠᴇ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛs ᴄᴏᴜɴᴛ (assistant ke through)
#   None  -> VC active nahi hai
#   int   -> participants ki sankhya
#   -1    -> pata nahi chala (assistant group me nahi / error)
# ============================================================

async def _live_participants(chat_id: int):
    try:
        assistant = await get_assistant(chat_id)
        if assistant is None:
            return -1

        peer = await assistant.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerChannel):
            full = await assistant.invoke(
                raw.functions.channels.GetFullChannel(
                    channel=raw.types.InputChannel(
                        channel_id=peer.channel_id,
                        access_hash=peer.access_hash,
                    )
                )
            )
        else:
            full = await assistant.invoke(
                raw.functions.messages.GetFullChat(chat_id=peer.chat_id)
            )

        call = getattr(full.full_chat, "call", None)
        if not call:
            return None

        gc = await assistant.invoke(
            raw.functions.phone.GetGroupCall(call=call, limit=1)
        )
        return gc.call.participants_count or 0

    except Exception as e:
        print(f"VC PARTICIPANTS ERROR: {e}")
        return -1


# ============================================================
# 🎙 /vc  /joinvc  /vcinfo  -> VC card on demand
# ============================================================

@app.on_message(
    filters.command(["vc", "joinvc", "vcinfo"]) & filters.group
)
async def vc_command(client, message):

    try:
        count = await _live_participants(message.chat.id)

        if count is None:
            return await message.reply_text(
                "**❖ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʙʜɪ ᴀᴄᴛɪᴠᴇ ɴᴀʜɪ ʜᴀɪ.**\n\n"
                "**▶ ᴘᴇʜʟᴇ ᴠᴄ sᴛᴀʀᴛ ᴋᴀʀᴏ, ꜰɪʀ /play ᴋᴀʀᴏ 🎶**"
            )

        await _send_vc_card(
            client, message, participants=max(count, 0)
        )

    except Exception as e:
        print(f"VC COMMAND ERROR: {e}")


# ============================================================
# 🔴 ᴠᴄ ᴇɴᴅᴇᴅ
# ============================================================

@app.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message):

    try:
        chat_name = message.chat.title or "ᴛʜɪs ɢʀᴏᴜᴘ"

        duration = 0

        if message.video_chat_ended:
            duration = message.video_chat_ended.duration or 0

        days = duration // 86400
        hours = (duration % 86400) // 3600
        minutes = (duration % 3600) // 60

        if days > 0:
            duration_text = f"{days}ᴅ {hours}ʜ"

        elif hours > 0:
            duration_text = f"{hours}ʜ {minutes}ᴍ"

        elif minutes > 0:
            duration_text = f"{minutes}ᴍ"

        else:
            duration_text = f"{duration}s"

        text = (
            f"**❖ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ ɪɴ {chat_name}**\n\n"
            f"**⏰ ᴅᴜʀᴀᴛɪᴏɴ: {duration_text}**\n\n"
            f"**◆ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ Qᴜᴇᴜᴇ sᴏɴɢs 🗑**"
        )

        buttons = await get_buttons(client)

        await message.reply_text(
            text,
            reply_markup=buttons,
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(f"VIDEO CHAT END ERROR: {e}")


# ============================================================
# 👥 ᴠᴄ ᴍᴇᴍʙᴇʀs ɪɴᴠɪᴛᴇᴅ
# ============================================================

@app.on_message(filters.video_chat_members_invited)
async def video_chat_members_invited(client, message):

    try:

        if not message.from_user:
            return

        if not message.video_chat_members_invited:
            return

        users = message.video_chat_members_invited.users

        if not users:
            return

        inviter_name = message.from_user.first_name or "ᴜsᴇʀ"

        inviter = (
            f"[{inviter_name}](tg://user?id={message.from_user.id})"
        )

        invited_users = []

        for user in users:

            name = user.first_name or "ᴜsᴇʀ"

            invited_users.append(
                f"[{name}](tg://user?id={user.id})"
            )

        names = ", ".join(invited_users)

        text = (
            f"**❖ {inviter} ɪɴᴠɪᴛᴇᴅ {names} ᴏɴ ᴠᴄ ⚡**\n\n"
            f"**⏤͟͟͞͞★ ᴊᴏɪɴ ғᴀsᴛ & ᴇɴᴊᴏʏ ᴍᴜsɪᴄ 🎧**"
        )

        buttons = await get_buttons(client)

        await message.reply_text(
            text,
            reply_markup=buttons,
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(f"VIDEO CHAT INVITE ERROR: {e}")


# ============================================================
# ❌ ᴄʟᴏsᴇ
# ============================================================

@app.on_callback_query(
    filters.regex("^close_vc_message$")
)
async def close_vc_message(client, query):

    try:

        await query.answer(
            "ᴄʟᴏsᴇᴅ ✨"
        )

        await query.message.delete()

    except Exception as e:

        print(f"VC CLOSE ERROR: {e}")

        try:
            await query.answer(
                "ᴄᴀɴɴᴏᴛ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.",
                show_alert=True,
            )
        except Exception:
            pass
