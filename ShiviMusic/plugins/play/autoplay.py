# ===========================================================
# 🎵 SHIVI MUSIC - AUTO PLAY SETTINGS
# ===========================================================

from pyrogram import enums, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ShiviMusic import app
from ShiviMusic.utils.database import (
    autoplay_off,
    autoplay_on,
    is_autoplay_on,
)
from config import BANNED_USERS


# ===========================================================
# 👑 ADMIN CHECK
# ===========================================================

async def _is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(
            chat_id,
            user_id,
        )

        return member.status in (
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        )

    except Exception:
        return False


# ===========================================================
# 📝 AUTO PLAY PANEL TEXT
# ===========================================================

def autoplay_text(
    message: Message,
    status: bool,
) -> str:

    chat_id = message.chat.id
    group_name = message.chat.title or "Unknown"

    status_text = (
        "🟢 ᴇɴᴀʙʟᴇ"
        if status
        else
        "🔴 ᴅɪsᴀʙʟᴇ"
    )

    return (
        "❖ **ᴀᴜᴛᴏ ᴘʟᴀʏ sᴇᴛᴛɪɴɢ ᴘᴀɴᴇʟ**\n\n"
        f"🌼 **ɪᴅ :** `{chat_id}`\n"
        f"🍂 **sᴛᴀᴛᴜs :** {status_text}\n"
        f"🏖 **ɢʀᴏᴜᴘ :** **{group_name}**\n\n"
        "▣ **ᴛᴀᴘ ᴛᴏ ᴍᴀɴᴀɢᴇ**\n"
        "**ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏᴘʟᴀʏ sᴇᴛᴛɪɴɢ.**"
    )


# ===========================================================
# 🔘 AUTO PLAY BUTTONS
# ===========================================================

def autoplay_markup(
    chat_id: int,
    status: bool,
) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🟢 ᴇɴᴀʙʟᴇ",
                    callback_data=f"autoplay_enable:{chat_id}",
                ),
                InlineKeyboardButton(
                    "🔴 ᴅɪsᴀʙʟᴇ",
                    callback_data=f"autoplay_disable:{chat_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "⌯ ᴄʟᴏsᴇ ⌯",
                    callback_data=f"autoplay_close:{chat_id}",
                )
            ],
        ]
    )


# ===========================================================
# 🎵 /AUTOPLAY COMMAND
# ===========================================================

@app.on_message(
    filters.command(["autoplay", "aplay"])
    & filters.group
    & ~BANNED_USERS
)
async def autoplay_cmd(
    client,
    message: Message,
):

    chat_id = message.chat.id

    # =======================================================
    # /autoplay on
    # /autoplay off
    # =======================================================

    if len(message.command) > 1:

        if not message.from_user:
            return

        # ---------------------------------------------------
        # ADMIN CHECK
        # ---------------------------------------------------

        if not await _is_admin(
            chat_id,
            message.from_user.id,
        ):

            return await message.reply_text(
                "❌ **sɪʀꜰ ᴀᴅᴍɪɴs ʜɪ "
                "ᴀᴜᴛᴏᴘʟᴀʏ ᴍᴀɴᴀɢᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ.**"
            )

        mode = message.command[1].lower()

        # ---------------------------------------------------
        # ENABLE
        # ---------------------------------------------------

        if mode in ("on", "enable"):

            await autoplay_on(chat_id)

            return await message.reply_text(
                "🟢 **ᴀᴜᴛᴏᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ "
                "sᴜᴄᴄᴇssғᴜʟʟʏ.**"
            )

        # ---------------------------------------------------
        # DISABLE
        # ---------------------------------------------------

        if mode in ("off", "disable"):

            await autoplay_off(chat_id)

            return await message.reply_text(
                "🔴 **ᴀᴜᴛᴏᴘʟᴀʏ ᴅɪsᴀʙʟᴇᴅ "
                "sᴜᴄᴄᴇssғᴜʟʟʏ.**"
            )

        # ---------------------------------------------------
        # WRONG COMMAND
        # ---------------------------------------------------

        return await message.reply_text(
            "❖ **ᴜsᴀɢᴇ**\n\n"
            "➤ `/autoplay` — **ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs**\n"
            "➤ `/autoplay on` — **ᴇɴᴀʙʟᴇ**\n"
            "➤ `/autoplay off` — **ᴅɪsᴀʙʟᴇ**"
        )

    # =======================================================
    # OPEN AUTO PLAY PANEL
    # =======================================================

    status = await is_autoplay_on(chat_id)

    await message.reply_text(
        autoplay_text(
            message,
            status,
        ),
        reply_markup=autoplay_markup(
            chat_id,
            status,
        ),
    )


# ===========================================================
# 🟢 ENABLE / 🔴 DISABLE CALLBACK
# ===========================================================

@app.on_callback_query(
    filters.regex(
        r"^autoplay_(enable|disable):(-?\d+)$"
    )
    & ~BANNED_USERS
)
async def autoplay_toggle_callback(
    client,
    query: CallbackQuery,
):

    action = query.matches[0].group(1)
    chat_id = int(query.matches[0].group(2))

    # =======================================================
    # MESSAGE CHECK
    # =======================================================

    if not query.message:

        return await query.answer(
            "❌ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ.",
            show_alert=True,
        )

    # =======================================================
    # CHAT CHECK
    # =======================================================

    if query.message.chat.id != chat_id:

        return await query.answer(
            "❌ ᴛʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.",
            show_alert=True,
        )

    # =======================================================
    # ADMIN CHECK
    # =======================================================

    if not await _is_admin(
        chat_id,
        query.from_user.id,
    ):

        return await query.answer(
            "❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ "
            "ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏᴘʟᴀʏ.",
            show_alert=True,
        )

    # =======================================================
    # ENABLE
    # =======================================================

    if action == "enable":

        await autoplay_on(chat_id)

        status = True

        await query.answer(
            "🟢 ᴀᴜᴛᴏᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ",
            show_alert=False,
        )

    # =======================================================
    # DISABLE
    # =======================================================

    else:

        await autoplay_off(chat_id)

        status = False

        await query.answer(
            "🔴 ᴀᴜᴛᴏᴘʟᴀʏ ᴅɪsᴀʙʟᴇᴅ",
            show_alert=False,
        )

    # =======================================================
    # UPDATE PANEL
    # =======================================================

    try:

        await query.message.edit_text(
            autoplay_text(
                query.message,
                status,
            ),
            reply_markup=autoplay_markup(
                chat_id,
                status,
            ),
        )

    except Exception:
        pass


# ===========================================================
# ❌ CLOSE CALLBACK
# ===========================================================

@app.on_callback_query(
    filters.regex(
        r"^autoplay_close:(-?\d+)$"
    )
    & ~BANNED_USERS
)
async def autoplay_close_callback(
    client,
    query: CallbackQuery,
):

    chat_id = int(
        query.matches[0].group(1)
    )

    # =======================================================
    # MESSAGE CHECK
    # =======================================================

    if not query.message:
        return

    # =======================================================
    # CHAT CHECK
    # =======================================================

    if query.message.chat.id != chat_id:

        return await query.answer(
            "❌ ᴛʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.",
            show_alert=True,
        )

    # =======================================================
    # CLOSE PANEL
    # =======================================================

    try:

        await query.message.delete()

        await query.answer(
            "⌯ ᴘᴀɴᴇʟ ᴄʟᴏsᴇᴅ ⌯",
            show_alert=False,
        )

    except Exception:

        await query.answer(
            "❌ ɪ ᴄᴀɴ'ᴛ ᴄʟᴏsᴇ ᴛʜɪs ᴘᴀɴᴇʟ.",
            show_alert=True,
        )


# ===========================================================
# ©️ 2025-26 SHIVI MUSIC
# ===========================================================
