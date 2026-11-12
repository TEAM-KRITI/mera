# ===========================================================
# 🖼 THUMBNAIL SETTINGS  (/thumb)  - per chat enable / disable
# ===========================================================

from pyrogram import enums, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import BANNED_USERS
from ShiviMusic import app
from ShiviMusic.utils.database import is_thumb_on, thumb_off, thumb_on


async def _is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in (
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        )
    except Exception:
        return False


def _text(chat, status: bool) -> str:
    st = "🟢 ᴇɴᴀʙʟᴇᴅ" if status else "🔴 ᴅɪsᴀʙʟᴇᴅ"
    return (
        "❖ **ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛᴛɪɴɢs**\n\n"
        f"🌼 **ɪᴅ :** `{chat.id}`\n"
        f"🍂 **sᴛᴀᴛᴜs :** {st}\n"
        f"🏖 **ɢʀᴏᴜᴘ :** **{chat.title or 'Unknown'}**\n\n"
        "▣ **ᴇɴᴀʙʟᴇ** : sᴛʀᴇᴀᴍ ᴡɪᴛʜ sᴏɴɢ ᴛʜᴜᴍʙɴᴀɪʟs.\n"
        "▣ **ᴅɪsᴀʙʟᴇ** : sᴛʀᴇᴀᴍ ᴡɪᴛʜᴏᴜᴛ sᴏɴɢ ᴛʜᴜᴍʙɴᴀɪʟs."
    )


def _markup(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🟢 ᴇɴᴀʙʟᴇ", callback_data=f"thumb_enable:{chat_id}"),
                InlineKeyboardButton("🔴 ᴅɪsᴀʙʟᴇ", callback_data=f"thumb_disable:{chat_id}"),
            ],
            [InlineKeyboardButton("⌯ ᴄʟᴏsᴇ ⌯", callback_data=f"thumb_close:{chat_id}")],
        ]
    )


@app.on_message(filters.command(["thumb", "thumbnail"]) & ~BANNED_USERS)
async def thumb_cmd(client, message: Message):
    chat_id = message.chat.id

    # private chat me /thumb ka matlab nahi -> chup rehne ki jagah batao
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "❖ **ᴛʜᴜᴍʙɴᴀɪʟ sᴇᴛᴛɪɴɢs sɪʀғ ɢʀᴏᴜᴘ ᴍᴇ ʜɪ ᴋᴀᴀᴍ ᴋᴀʀᴛᴇ ʜᴀɪɴ.**\n"
            "➤ ʙᴏᴛ ᴋᴏ ɢʀᴏᴜᴘ ᴍᴇ ᴀᴅᴅ ᴋᴀʀᴋᴇ `/thumb` ʏᴀ `/thumb on` / `/thumb off` ᴜsᴇ ᴋᴀʀᴏ."
        )

    # anonymous admin (group ke naam se message) ko bhi allow karo
    anon_admin = bool(message.sender_chat and message.sender_chat.id == chat_id)

    if len(message.command) > 1:
        if not anon_admin and (not message.from_user or not await _is_admin(chat_id, message.from_user.id)):
            return await message.reply_text("❌ **sɪʀғ ᴀᴅᴍɪɴs ʜɪ ᴛʜᴜᴍʙɴᴀɪʟ ᴍᴀɴᴀɢᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ.**")
        mode = message.command[1].lower()
        if mode in ("on", "enable"):
            await thumb_on(chat_id)
            return await message.reply_text("🟢 **ᴛʜᴜᴍʙɴᴀɪʟ ᴇɴᴀʙʟᴇᴅ.**")
        if mode in ("off", "disable"):
            await thumb_off(chat_id)
            return await message.reply_text("🔴 **ᴛʜᴜᴍʙɴᴀɪʟ ᴅɪsᴀʙʟᴇᴅ.**")
        return await message.reply_text(
            "❖ **ᴜsᴀɢᴇ**\n\n➤ `/thumb` — **ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs**\n"
            "➤ `/thumb on` — **ᴇɴᴀʙʟᴇ**\n➤ `/thumb off` — **ᴅɪsᴀʙʟᴇ**"
        )

    status = await is_thumb_on(chat_id)
    await message.reply_text(_text(message.chat, status), reply_markup=_markup(chat_id))


@app.on_callback_query(filters.regex(r"^thumb_(enable|disable|close):(-?\d+)$") & ~BANNED_USERS)
async def thumb_cb(client, query: CallbackQuery):
    action = query.matches[0].group(1)
    chat_id = int(query.matches[0].group(2))

    if not query.message or query.message.chat.id != chat_id:
        return await query.answer("❌ ᴛʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.", show_alert=True)

    if not await _is_admin(chat_id, query.from_user.id):
        return await query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜᴜᴍʙɴᴀɪʟ.", show_alert=True)

    if action == "close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action == "enable":
        await thumb_on(chat_id)
        await query.answer("🟢 ᴛʜᴜᴍʙɴᴀɪʟ ᴇɴᴀʙʟᴇᴅ")
    else:
        await thumb_off(chat_id)
        await query.answer("🔴 ᴛʜᴜᴍʙɴᴀɪʟ ᴅɪsᴀʙʟᴇᴅ")

    try:
        await query.message.edit_text(
            _text(query.message.chat, action == "enable"), reply_markup=_markup(chat_id)
        )
    except MessageNotModified:
        pass
