# -----------------------------------------------
# 🔸 CharviMusic Project
# 🔹 Developed & Maintained by: Charvi Bots
# 📅 Copyright © 2022 – All Rights Reserved
# -----------------------------------------------

from pyrogram import filters, enums
from ShiviMusic import app

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ShiviMusic.utils.nightmodedb import (
    nightdb,
    nightmode_on,
    nightmode_off,
    get_nightchats,
)


PHOTO_URL = "https://yukiapi.site/file/pABl4iKv"


# =======================================================
# ᴄʜᴀᴛ ᴘєʀᴍɪꜱꜱɪᴏɴꜱ
# =======================================================

CLOSE_CHAT = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_change_info=False,
    can_add_web_page_previews=False,
    can_pin_messages=False,
    can_invite_users=False
)

OPEN_CHAT = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_change_info=True,
    can_add_web_page_previews=True,
    can_pin_messages=True,
    can_invite_users=True
)


# =======================================================
# ʙᴜᴛᴛᴏɴ ꜱᴛʏʟє (ɢʀєєɴ / ʙʟᴜє)
# =======================================================
# Kurigram ke naye version me ButtonStyle enum hota hai.
# Alag-alag versions me naam alag ho sakte hain, isliye
# kai naam try kiye jaate hain. Support na ho to normal
# button dikhega, error nahi aayega.

_BS = getattr(enums, "ButtonStyle", None)


def _pick_style(*names):
    if _BS is None:
        return None
    for name in names:
        value = getattr(_BS, name, None)
        if value is not None:
            return value
    return None


GREEN = _pick_style("SUCCESS", "GREEN", "POSITIVE")
BLUE = _pick_style("PRIMARY", "BLUE", "DEFAULT")

if _BS is None:
    print("[nightmode] enums.ButtonStyle NOT found - install latest kurigram")
else:
    print(f"[nightmode] ButtonStyle members: {[m.name for m in _BS]}")
    print(f"[nightmode] GREEN={GREEN} BLUE={BLUE}")


def _btn(text, cb, style=None):
    if style is not None:
        try:
            return InlineKeyboardButton(text, callback_data=cb, style=style)
        except TypeError as e:
            print(f"[nightmode] style not supported by this version: {e}")
    return InlineKeyboardButton(text, callback_data=cb)


# =======================================================
# ɴɪɢʜᴛᴍᴏᴅє ʙᴜᴛᴛᴏɴꜱ
# =======================================================

buttons = InlineKeyboardMarkup(
    [
        [
            _btn("๏ єɴᴀʙʟє ๏", "add_night", GREEN),
            _btn("๏ ᴅɪꜱᴀʙʟє ๏", "rm_night", BLUE),
        ]
    ]
)


# =======================================================
# ᴀᴅᴅ ʙᴏᴛ ʙᴜᴛᴛᴏɴ
# =======================================================

def night_msg_buttons():
    username = getattr(app, "username", None)

    if not username:
        me = getattr(app, "me", None)
        username = getattr(me, "username", None)

    if not username:
        return None

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ᴀᴅᴅ ᴍє ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"https://t.me/{username}?startgroup=true"
                )
            ]
        ]
    )


# =======================================================
# ꜱᴇɴᴅ ʜєʟᴘєʀ (ᴘʜᴏᴛᴏ ꜰᴀɪʟ ʜᴏ ᴛᴏ ᴛєxᴛ ʙʜєᴊᴏ)
# =======================================================

async def send_night_msg(chat_id, caption):

    markup = night_msg_buttons()

    try:
        await app.send_photo(
            chat_id,
            photo=PHOTO_URL,
            caption=caption,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Photo send failed in {chat_id}: {e}")

        await app.send_message(
            chat_id,
            caption,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=markup,
            disable_web_page_preview=True
        )


# =======================================================
# ɴɪɢʜᴛᴍᴏᴅє ᴄᴏᴍᴍᴀɴᴅ
# =======================================================

@app.on_message(filters.command("nightmode") & filters.group)
async def _nightmode(_, message):

    return await message.reply_photo(
        photo=PHOTO_URL,

        caption=(
            "**⚙️ ɴɪɢʜᴛᴍᴏᴅє ꜱєᴛᴛɪɴɢꜱ**\n\n"
            "**ᴜꜱє ᴛʜє ʙᴜᴛᴛᴏɴꜱ ʙєʟᴏᴡ.**"
        ),

        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=buttons
    )


# =======================================================
# ɴɪɢʜᴛᴍᴏᴅє ᴄᴀʟʟʙᴀᴄᴋ
# =======================================================

@app.on_callback_query(
    filters.regex("^(add_night|rm_night)$")
)
async def nightcb(_, query: CallbackQuery):

    data = query.data
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    check_night = await nightdb.find_one(
        {"chat_id": chat_id}
    )

    administrators = []

    async for m in app.get_chat_members(
        chat_id,
        filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m.user.id)

    if user_id not in administrators:
        return await query.answer(
            "❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱє ᴛʜɪꜱ!",
            show_alert=True
        )

    # ===================================================
    # єɴᴀʙʟє
    # ===================================================

    if data == "add_night":

        if check_night:

            await query.message.edit_caption(
                caption="**🌕 ɴɪɢʜᴛᴍᴏᴅє ɪꜱ ᴀʟʀєᴀᴅʏ ᴏɴ.**",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=buttons
            )

        else:

            await nightmode_on(chat_id)

            await query.message.edit_caption(
                caption=(
                    "**✅ ɴɪɢʜᴛᴍᴏᴅє ᴏɴ!**\n\n"
                    "**🔒 12:00 ᴀᴍ  •  🔓 06:00 ᴀᴍ [ɪꜱᴛ]**"
                ),
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=buttons
            )

    # ===================================================
    # ᴅɪꜱᴀʙʟє
    # ===================================================

    elif data == "rm_night":

        if check_night:

            await nightmode_off(chat_id)

            await query.message.edit_caption(
                caption="**❌ ɴɪɢʜᴛᴍᴏᴅє ᴏꜰꜰ!**",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=buttons
            )

        else:

            await query.message.edit_caption(
                caption="**🌑 ɴɪɢʜᴛᴍᴏᴅє ɪꜱ ᴀʟʀєᴀᴅʏ ᴏꜰꜰ.**",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=buttons
            )

    await query.answer()


# =======================================================
# ɢᴏᴏᴅ ɴɪɢʜᴛ
# =======================================================

async def start_nightmode():

    schats = await get_nightchats()

    for chat in schats:

        chat_id = int(chat["chat_id"])

        # Pehle group lock karo, message fail ho tab bhi lock ho jaye
        try:
            await app.set_chat_permissions(chat_id, CLOSE_CHAT)
        except Exception as e:
            print(f"Unable to close group {chat_id}: {e}")

        try:
            group = await app.get_chat(chat_id)
            group_name = group.title or "ᴜɴᴋɴᴏᴡɴ ɢʀᴏᴜᴘ"

            caption = (
                "**━━━━━━━━━━━━━━━━━━━━**\n"
                "**🌌  ɢᴏᴏᴅ ɴɪɢʜᴛ єᴠєʀʏᴏɴє!  🌌**\n"
                "**━━━━━━━━━━━━━━━━━━━━**\n\n"

                "**🔒 ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴡ ᴄʟᴏꜱєᴅ ꜰᴏʀ ᴛʜє ɴɪɢʜᴛ.**\n"
                "**😴 ᴀʟʟ ᴍєᴍʙєʀꜱ ᴀʀє ᴍᴜᴛєᴅ ᴛɪʟʟ ᴍᴏʀɴɪɴɢ.**\n"
                "**⏰ ɢʀᴏᴜᴘ ᴡɪʟʟ ᴏᴘєɴ ᴀᴛ 06:00 ᴀᴍ [ɪꜱᴛ].**\n\n"

                "**✨ ꜱᴡєєᴛ ᴅʀєᴀᴍꜱ, ꜱʟєєᴘ ᴡєʟʟ ᴀɴᴅ ꜱєє ʏᴏᴜ ᴛᴏᴍᴏʀʀᴏᴡ!**\n\n"

                f"**👥 ɢʀᴏᴜᴘ : {group_name}**\n"
                f"**🆔 ɪᴅ : `{chat_id}`**\n\n"

                "**━━━━━━━━━━━━━━━━━━━━**\n"
                "**⚡ ᴘᴏᴡєʀєᴅ ʙʏ : "
                "[ᴋɪʀᴛɪ ᴍᴜꜱɪᴄ](https://t.me/kirti_bots)**"
            )

            await send_night_msg(chat_id, caption)

        except Exception as e:
            print(f"Unable to send night message {chat_id}: {e}")


# =======================================================
# ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ
# =======================================================

async def close_nightmode():

    schats = await get_nightchats()

    for chat in schats:

        chat_id = int(chat["chat_id"])

        # Pehle group open karo
        try:
            await app.set_chat_permissions(chat_id, OPEN_CHAT)
        except Exception as e:
            print(f"Unable to open group {chat_id}: {e}")

        try:
            group = await app.get_chat(chat_id)
            group_name = group.title or "ᴜɴᴋɴᴏᴡɴ ɢʀᴏᴜᴘ"

            caption = (
                "**━━━━━━━━━━━━━━━━━━━━**\n"
                "**🌅  ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ єᴠєʀʏᴏɴє!  🌅**\n"
                "**━━━━━━━━━━━━━━━━━━━━**\n\n"

                "**🔓 ɢʀᴏᴜᴘ ɪꜱ ɴᴏᴡ ᴏᴘєɴ ꜰᴏʀ ᴀʟʟ.**\n"
                "**💬 ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ꜱєɴᴅ ᴍєꜱꜱᴀɢєꜱ ᴀɢᴀɪɴ.**\n"
                "**🌙 ɢʀᴏᴜᴘ ᴡɪʟʟ ᴄʟᴏꜱє ᴀᴛ 12:00 ᴀᴍ [ɪꜱᴛ].**\n\n"

                "**☀️ ʜᴀᴠє ᴀ ʙєᴀᴜᴛɪꜰᴜʟ ᴀɴᴅ ᴘʀᴏᴅᴜᴄᴛɪᴠє ᴅᴀʏ!**\n\n"

                f"**👥 ɢʀᴏᴜᴘ : {group_name}**\n"
                f"**🆔 ɪᴅ : `{chat_id}`**\n\n"

                "**━━━━━━━━━━━━━━━━━━━━**\n"
                "**⚡ ᴘᴏᴡєʀєᴅ ʙʏ : "
                "[ᴋɪʀᴛɪ ᴍᴜꜱɪᴄ](https://t.me/kirti_bots)**"
            )

            await send_night_msg(chat_id, caption)

        except Exception as e:
            print(f"Unable to send morning message {chat_id}: {e}")


# =======================================================
# ꜱᴄʜєᴅᴜʟєʀ
# =======================================================

scheduler = AsyncIOScheduler(
    timezone="Asia/Kolkata"
)

# 11:59 PM
scheduler.add_job(
    start_nightmode,
    trigger="cron",
    hour=23,
    minute=59
)

# 06:01 AM
scheduler.add_job(
    close_nightmode,
    trigger="cron",
    hour=6,
    minute=1
)

try:
    scheduler.start()
except Exception as e:
    print(f"Scheduler start failed: {e}")


# =======================================================
# ©️ 2025-26 CharviMusic
# =======================================================
