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
import importlib
import platform
import random

import pyrogram
from pyrogram import idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ShiviMusic import LOGGER, app, userbot
from ShiviMusic.core.call import Shivi
from ShiviMusic.misc import sudo
from ShiviMusic.plugins import ALL_MODULES
from ShiviMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


# Random colour: (ButtonStyle name, fallback emoji)
BUTTON_COLORS = [
    ("PRIMARY", "🔵"),   # blue
    ("SUCCESS", "🟢"),   # green
    ("DANGER", "🔴"),    # red
]


def make_button(text: str, url: str) -> InlineKeyboardButton:
    """Random colour wala button (sirf colour random, text same)."""
    style_name, emoji = random.choice(BUTTON_COLORS)
    try:
        from pyrogram.enums import ButtonStyle

        return InlineKeyboardButton(
            text,
            url=url,
            style=getattr(ButtonStyle, style_name),
        )
    except Exception:
        # Agar library colour style support nahi karti to emoji se colour
        return InlineKeyboardButton(f"{emoji} {text}", url=url)


async def send_startup_message():
    caption = (
        "❖ <b>ʙᴏᴛ ꜱᴛᴀʀᴛєᴅ ꜱᴜᴄᴄєꜱꜱꜰᴜʟʟʏ</b> ✅\n\n"
        f"• <b>ʙᴏᴛ :-</b> {app.mention}\n"
        f"• <b>ᴘʟᴜɢɪɴꜱ :-</b> {len(ALL_MODULES)} ʟᴏᴀᴅєᴅ\n"
        f"• <b>ᴘʏʀᴏɢʀᴀᴍ :-</b> <code>{pyrogram.__version__}</code>\n"
        f"• <b>ᴘʏᴛʜᴏɴ :-</b> <code>{platform.python_version()}</code>\n\n"
        f"» <b>ᴘᴏᴡєʀєᴅ ʙʏ :-</b> <a href='{config.SUPPORT_CHANNEL}'>ᴋɪʀᴛɪ-ʙᴏᴛꜱ</a>"
    )
    markup = InlineKeyboardMarkup(
        [
            [
                make_button(
                    "➕ ᴀᴅᴅ ᴍє ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
                    f"https://t.me/{app.username}?startgroup=true",
                )
            ]
        ]
    )
    try:
        await app.send_photo(
            chat_id=config.LOGGER_ID,
            photo=config.START_IMG_URL,
            caption=caption,
            reply_markup=markup,
        )
    except Exception as e:
        LOGGER("ShiviMusic").error(f"Startup photo failed: {e}")
        try:
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=caption,
                reply_markup=markup,
                disable_web_page_preview=True,
            )
        except Exception as e2:
            LOGGER("ShiviMusic").error(f"Startup message failed: {e2}")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ꜱᴛʀɪɴɢ ꜱєꜱꜱɪᴏɴ ɴᴏᴛ ꜰɪʟʟєᴅ 🙃, ᴘʟєᴀꜱє ꜰɪʟʟ ᴀ ᴘʏʀᴏɢʀᴀᴍ ꜱєꜱꜱɪᴏɴ...🙂")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ShiviMusic.plugins" + all_module)
    LOGGER("ShiviMusic.plugins").info("ᴀʟʟ ᴘʟᴜɢɪɴꜱ ʟᴏᴀᴅєᴅ ꜱᴜᴄᴄєꜱꜱꜰᴜʟʟʏ....🥳..")
    await userbot.start()
    await Shivi.start()
    try:
        await Shivi.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ShiviMusic").error(
            "ᴘʟᴢ ꜱᴛᴀʀᴛ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴєʟ ᴠᴏɪᴄєᴄʜᴀᴛ... 😒\n\nᴍᴜꜱɪᴄ ʙᴏᴛ ꜱᴛᴏᴘ........🤕"
        )
        exit()
    except:
        pass
    await Shivi.decorators()
    await send_startup_message()
    LOGGER("ShiviMusic").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎ ᴍᴀᴅє ʙʏ ᴋɪʀᴛɪ ʙᴏᴛꜱ ☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ShiviMusic").info("ꜱᴛᴏᴘ ᴍᴜꜱɪᴄ ʙᴏᴛ...🥹")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
