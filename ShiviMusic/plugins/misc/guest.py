from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from ShiviMusic import app

# Native coloured button (blue). Purana pyrogram/kurigram ho to
# automatic plain button use hoga -> bot crash nahi hoga.
try:
    from pyrogram.enums import ButtonStyle

    _BLUE = ButtonStyle.PRIMARY
except Exception:
    _BLUE = None


# ==========================================================
# ɢᴜєꜱᴛ ᴍєꜱꜱᴀɢє
# ==========================================================

ADD_ME_PROMO_TEXT = (
    "❖ <a href=\"https://t.me/{username}\">˹{name}˼ ♪</a> — "
    "<b>ʏᴏᴜʀ ᴘʀєᴍɪᴜᴍ ᴍᴜꜱɪᴄ ꜱᴛʀєᴀᴍєʀ ʙᴏᴛ 🍂</b>\n\n"

    "<blockquote>"
    "<b>▸ ꜰᴀꜱᴛ  • ʟᴀɢ  ꜰʀєє  • ɴᴏ  ᴀᴅꜱ 🍂</b>\n"
    "<b>▸ ᴀᴜᴛᴏ-ᴘʟᴀʏ  • ᴀᴜᴅɪᴏ  • ᴠɪᴅєᴏ 🎥</b>"
    "</blockquote>\n\n"

    "<b>◼️ ᴀᴅᴅ</b> "
    "<a href=\"https://t.me/{username}\">˹{name}˼ ♪</a> "
    "<b>ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ  & єɴᴊᴏʏ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ꜱᴏɴɢ ❄️</b>"
)


# ==========================================================
# ʙᴜᴛᴛᴏɴꜱ
# ==========================================================

def _add_me_button(username: str) -> InlineKeyboardButton:
    text = "✙ ᴀᴅᴅ ᴍє ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✙"
    url = f"https://t.me/{username}?startgroup=true"

    if _BLUE is not None:
        try:
            return InlineKeyboardButton(text=text, url=url, style=_BLUE)
        except TypeError:  # style support nahi -> plain button
            pass
    return InlineKeyboardButton(text=text, url=url)


def _add_me_markup(username: str):
    return InlineKeyboardMarkup([[_add_me_button(username)]])


# ==========================================================
# ɢᴜєꜱᴛ ᴍᴏᴅє
# ==========================================================

@app.on_guest_message()
async def guest_username_mention(_, message: Message):

    guest_query_id = getattr(
        message,
        "guest_query_id",
        None,
    )

    if not guest_query_id:
        return

    try:

        me = await app.get_me()

        # Full bot name
        name = me.first_name or "Music Bot"

        if me.last_name:
            name = f"{name} {me.last_name}"

        # Bot username
        username = me.username

        if not username:
            return

        promo_text = ADD_ME_PROMO_TEXT.format(
            name=name,
            username=username,
        )

        keyboard = _add_me_markup(username)

        result = InlineQueryResultArticle(
            title="❖ ᴍᴜꜱɪᴄ ʙᴏᴛ ♪",
            description=f"@{username} • ᴀᴅᴅ ᴍє ༭ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🎶",
            thumb_url="https://files.catbox.moe/qv2ob4.jpg",

            input_message_content=InputTextMessageContent(
                message_text=promo_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            ),

            reply_markup=keyboard,
        )

        await app.answer_guest_query(
            guest_query_id,
            result=result,
        )

    except Exception as e:

        print(
            f"Guest Mode Error: {type(e).__name__}: {e}"
        )
