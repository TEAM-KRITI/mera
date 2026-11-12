# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ShiviMusic import app

@app.on_message(filters.command("privacy"))
async def privacy_command(client: Client, message: Message):
    await message.reply_photo(
          has_spoiler=True,
        photo="https://d.uguu.se/LbHGyjwp.jpg",
        caption="**➻ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴋɪʀᴛɪ ʙᴏᴛѕ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ.**\n\n**⊚ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛʜᴇɴ ꜱᴇᴇ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ 🔏**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("˹ᴘʀᴏᴍᴏ˼", url="https://t.me/Only_badnam?text=𝖧ᴇʏ%20ʙᴀʙʏ%20%20😄%20ɪ%20ᴡᴀɴᴛ%20ᴘᴀɪᴅ%20ᴘʀᴏᴍᴏᴛɪᴏɴ,%20ɢɪᴠᴇ%20ᴍᴇ%20ᴘʀɪᴄᴇ%20ʟɪsᴛ%20😙")]
            ]
        )
    )

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
