# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from unidecode import unidecode

from ShiviMusic import app
from ShiviMusic.misc import SUDOERS
from ShiviMusic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)


# ===========================================================
# JOIN LINK
# ===========================================================

async def generate_join_link(chat_id: int):
    """
    Generate an invite link for a chat.
    """
    return await app.export_chat_invite_link(chat_id)


# ===========================================================
# ORDINAL
# ===========================================================

def ordinal(n: int):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd",
        }.get(n % 10, "th")

    return f"{n}{suffix}"


# ===========================================================
# ACTIVE VOICE CHATS
# ===========================================================

@app.on_message(
    filters.command(
        ["activevc", "activevoice"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & SUDOERS
)
async def activevc(_, message: Message):

    mystic = await message.reply_text(
        "» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ʟɪsᴛ..."
    )

    served_chats = await get_active_chats()

    text = ""
    j = 0
    buttons = []

    for chat_id in served_chats:

        try:
            chat_info = await app.get_chat(chat_id)

            title = chat_info.title or "Unknown Chat"

            invite_link = await generate_join_link(chat_id)

        except Exception:
            try:
                await remove_active_chat(chat_id)
            except Exception:
                pass

            continue

        try:
            display_title = unidecode(title).upper()

            if chat_info.username:
                text += (
                    f"<b>{j + 1}.</b> "
                    f'<a href="https://t.me/{chat_info.username}">'
                    f"{display_title}"
                    f"</a> "
                    f"[<code>{chat_id}</code>]\n"
                )
            else:
                text += (
                    f"<b>{j + 1}.</b> "
                    f"{display_title} "
                    f"[<code>{chat_id}</code>]\n"
                )

            button_text = (
                f"๏ ᴊᴏɪɴ {ordinal(j + 1)} ɢʀᴏᴜᴘ ๏"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        url=invite_link,
                    )
                ]
            )

            j += 1

        except Exception:
            continue

    # -------------------------------------------------------
    # NO ACTIVE VOICE CHATS
    # -------------------------------------------------------

    if not text:

        await mystic.edit_text(
            f"» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ᴏɴ {app.mention}."
        )

        return

    # -------------------------------------------------------
    # ACTIVE VOICE CHAT LIST
    # -------------------------------------------------------

    await mystic.edit_text(
        f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs :</b>\n\n"
        f"{text}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ===========================================================
# ACTIVE VIDEO CHATS
# ===========================================================

@app.on_message(
    filters.command(
        ["activev", "activevideo"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & SUDOERS
)
async def activevi_(_, message: Message):

    mystic = await message.reply_text(
        "» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs ʟɪsᴛ..."
    )

    served_chats = await get_active_video_chats()

    text = ""
    j = 0
    buttons = []

    for chat_id in served_chats:

        try:
            chat_info = await app.get_chat(chat_id)

            title = chat_info.title or "Unknown Chat"

            invite_link = await generate_join_link(chat_id)

        except Exception:
            try:
                await remove_active_video_chat(chat_id)
            except Exception:
                pass

            continue

        try:
            display_title = unidecode(title).upper()

            if chat_info.username:
                text += (
                    f"<b>{j + 1}.</b> "
                    f'<a href="https://t.me/{chat_info.username}">'
                    f"{display_title}"
                    f"</a> "
                    f"[<code>{chat_id}</code>]\n"
                )
            else:
                text += (
                    f"<b>{j + 1}.</b> "
                    f"{display_title} "
                    f"[<code>{chat_id}</code>]\n"
                )

            button_text = (
                f"๏ ᴊᴏɪɴ {ordinal(j + 1)} ɢʀᴏᴜᴘ ๏"
            )

            buttons.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        url=invite_link,
                    )
                ]
            )

            j += 1

        except Exception:
            continue

    # -------------------------------------------------------
    # NO ACTIVE VIDEO CHATS
    # -------------------------------------------------------

    if not text:

        await mystic.edit_text(
            f"» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs ᴏɴ {app.mention}."
        )

        return

    # -------------------------------------------------------
    # ACTIVE VIDEO CHAT LIST
    # -------------------------------------------------------

    await mystic.edit_text(
        f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs :</b>\n\n"
        f"{text}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ===========================================================
# ACTIVE CHAT COUNT
# ===========================================================

@app.on_message(
    filters.command(["ac"])
    & SUDOERS
)
async def start(client: Client, message: Message):

    ac_audio = len(await get_active_chats())
    ac_video = len(await get_active_video_chats())

    await message.reply_text(
        f"✫ <b><u>ᴀᴄᴛɪᴠᴇ ᴄʜᴀᴛs ɪɴғᴏ</u></b> :\n\n"
        f"ᴠᴏɪᴄᴇ : {ac_audio}\n"
        f"ᴠɪᴅᴇᴏ : {ac_video}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✯ ᴄʟᴏsᴇ ✯",
                        callback_data="close",
                    )
                ]
            ]
        ),
    )


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder)
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
