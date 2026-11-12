from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ShiviMusic import app
from config import BOT_USERNAME

start_txt = """**
<u>❃ ᴡєʟᴄσϻє ᴛᴏ ᴛєᴧϻ ᴋʀɪʀɪ ʀєᴘσs ❃</u>
 
✼ ʀєᴘᴏ ɪs ηᴏᴡ ᴘʀɪᴠᴧᴛє ᴅᴜᴅє 😌
 
❉  ʏᴏᴜ ᴄᴧη мʏ ᴜsє ᴘᴜʙʟɪᴄ ʀєᴘσs !!  

✼ || [˹ᴋɪʀᴛɪ ꭙ ʙᴏᴛѕ˼ 💞](https://t.me/annu_support) ||
 
❊ ʀᴜη 24x7 ʟᴧɢ ϝʀєє ᴡɪᴛʜσᴜᴛ sᴛσᴘ**
"""


@app.on_message(filters.command("repo"))
async def repo_command(_, msg):
    buttons = [
        [
            InlineKeyboardButton("✙ ᴧᴅᴅ ϻє вᴧʙʏ ✙", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("• ʜєʟᴘ •", url="https://t.me/annu_support"),
            InlineKeyboardButton("• 𝛅ᴜᴘᴘσʀᴛ •", url="https://t.me/annu_support"),
        ],
        [
            InlineKeyboardButton("• ϻᴧɪη ʙσᴛ •", url="https://t.me/Kirshnamusicbot?startgroup=true"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await msg.reply_photo(
        photo="https://files.catbox.moe/kbi6t5.jpg",
        caption=start_txt,
        reply_markup=reply_markup,
    )
