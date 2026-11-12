# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from pyrogram import filters
from pyrogram.types import Message

from ShiviMusic import app
from ShiviMusic.misc import SUDOERS
from ShiviMusic.utils.database import blacklist_chat, blacklisted_chats, whitelist_chat
from ShiviMusic.utils.decorators.language import language
from config import BANNED_USERS


@app.on_message(filters.command(["blchat", "blacklistchat"]) & SUDOERS)
@language
async def blacklist_chat_func(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_1"])
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text(_["black_2"])
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        await message.reply_text(_["black_3"])
    else:
        await message.reply_text(_["black_9"])
    try:
        await app.leave_chat(chat_id)
    except:
        pass


@app.on_message(
    filters.command(["whitelistchat", "unblacklistchat", "unblchat"]) & SUDOERS
)
@language
async def white_funciton(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_4"])
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text(_["black_5"])
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(_["black_6"])
    await message.reply_text(_["black_9"])


@app.on_message(filters.command(["blchats", "blacklistedchats"]) & ~BANNED_USERS)
@language
async def all_chats(client, message: Message, _):
    text = _["black_7"]
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except:
            title = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        j = 1
        text += f"{count}. {title}[<code>{chat_id}</code>]\n"
    if j == 0:
        await message.reply_text(_["black_8"].format(app.mention))
    else:
        await message.reply_text(text)

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
