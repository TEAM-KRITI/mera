# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

import random

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.errors import RPCError, ChatAdminRequired

from config import LOGGER_ID as LOG_GROUP_ID
from ShiviMusic import app


photo = [
    "https://n.uguu.se/COCvZVmH.jpg",
    "https://n.uguu.se/sUnCjERi.jpg",
    "https://h.uguu.se/UFespaut.jpg",
    "https://n.uguu.se/JQCcgtmE.jpg",
    "https://d.uguu.se/SDjTEpEk.jpg",
    "https://n.uguu.se/FzOLVSlF.jpg",
    "https://n.uguu.se/QnLMTcYx.jpg",
    "https://d.uguu.se/aOQGWHbN.jpg",
]

BTN_TEXT = "#𝗚𝗥𝗢𝗨𝗣 #𝗟𝗜𝗡𝗞"

# Random colour: (ButtonStyle name, fallback emoji)
BUTTON_COLORS = [
    ("PRIMARY", "🔵"),   # blue
    ("SUCCESS", "🟢"),   # green
    ("DANGER", "🔴"),    # red
]


def make_button(url: str) -> InlineKeyboardButton:
    """Random colour wala button. Same ek hi button, sirf colour random."""
    style_name, emoji = random.choice(BUTTON_COLORS)
    try:
        from pyrogram.enums import ButtonStyle

        return InlineKeyboardButton(
            BTN_TEXT,
            url=url,
            style=getattr(ButtonStyle, style_name),
        )
    except Exception:
        # Agar library colour style support nahi karti to emoji se colour
        return InlineKeyboardButton(f"{emoji} {BTN_TEXT}", url=url)


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message: Message):

    try:
        # Get bot information safely
        me = await app.get_me()

        # Check whether our bot was added
        if not any(member.id == me.id for member in message.new_chat_members):
            return

        chat = message.chat

        # Get member count safely
        try:
            count = await app.get_chat_members_count(chat.id)
        except RPCError:
            count = "Unknown"

        # Get invite link.
        # This requires admin permission.
        link = None

        try:
            link = await app.export_chat_invite_link(chat.id)
        except ChatAdminRequired:
            # Bot is not admin, so don't crash the handler.
            link = None
        except RPCError:
            link = None

        # Chat username
        username = (
            f"@{chat.username}"
            if chat.username
            else "Private Group"
        )

        # Added by
        added_by = (
            message.from_user.mention
            if message.from_user
            else "Unknown User"
        )

        # Link text
        if link:
            chat_link = f"[ᴄʟɪᴄᴋ]({link})"
        elif chat.username:
            public_link = f"https://t.me/{chat.username}"
            chat_link = f"[ᴄʟɪᴄᴋ]({public_link})"
        else:
            chat_link = "Not Available"

        msg = (
            f"#𝗕𝗢𝗧_𝗔𝗗𝗗𝗘𝗗_𝗡𝗘𝗪_𝗚𝗥𝗢𝗨𝗣\n\n"
            f"⦿───────────────────⦿\n\n"
            f"◎ ᴄʜᴀᴛ ɴᴀᴍᴇ ▸ {chat.title or 'Unknown'}\n"
            f"◎ ᴄʜᴀᴛ ɪᴅ ▸ {chat.id}\n"
            f"◎ ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ▸ {username}\n"
            f"◎ ᴄʜᴀᴛ ʟɪɴᴋ ▸ {chat_link}\n"
            f"◎ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ▸ {count}\n"
            f"◎ ᴀᴅᴅᴇᴅ ʙʏ ▸ {added_by}\n"
            f"⦿───────────────────⦿"
        )

        buttons = []

        if link:
            buttons.append([make_button(link)])
        elif chat.username:
            buttons.append([make_button(f"https://t.me/{chat.username}")])

        await app.send_photo(
            LOG_GROUP_ID,
            photo=random.choice(photo),
            caption=msg,
            reply_markup=(
                InlineKeyboardMarkup(buttons)
                if buttons
                else None
            ),
        )

    except Exception as e:
        print(f"chatlog join_watcher error: {e}")


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):

    try:
        me = await app.get_me()

        # Check whether our bot left
        if not message.left_chat_member:
            return

        if message.left_chat_member.id != me.id:
            return

        remove_by = (
            message.from_user.mention
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )

        title = message.chat.title or "Unknown"

        username = (
            f"@{message.chat.username}"
            if message.chat.username
            else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ"
        )

        chat_id = message.chat.id

        left = (
            f"✫ <b><u>#𝗟𝗘𝗙𝗧_𝗚𝗥𝗢𝗨𝗣</u></b> ✫\n\n"
            f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\n"
            f"ᴄʜᴀᴛ ɪᴅ : {chat_id}\n\n"
            f"ᴄʜᴀᴛ : {username}\n\n"
            f"ʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}\n\n"
            f"ʙᴏᴛ : @{me.username or 'Unknown'}"
        )

        await app.send_photo(
            LOG_GROUP_ID,
            photo=random.choice(photo),
            caption=left,
        )

    except Exception as e:
        print(f"chatlog left handler error: {e}")
