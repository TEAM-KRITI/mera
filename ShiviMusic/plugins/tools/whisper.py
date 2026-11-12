from ShiviMusic import app
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ================================
#       ADD-ME PROMO
# ================================

ADD_ME_PROMO_TEXT = (
    f"❖ ♪ — @{app.username} 𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 𝖡𝗈𝗍 🎶\n\n"
    "▸ 𝖥𝖺𝗌𝗍 • 𝖫𝖺𝗀 𝖥𝗋𝖾𝖾 • 𝖭𝗈 𝖠𝖽𝗌 🍃\n"
    "▸ 𝖠𝗎𝗍𝗈-𝖯𝗅𝖺𝗒 • 𝖠𝗎𝖽𝗂𝗈 • 𝖵𝗂𝖽𝖾𝗈 🎥\n\n"
    "➜ 𝖠𝖽𝖽 ˹ ♪ 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 & 𝖤𝗇𝗃𝗈𝗒\n"
    " 𝖧𝗂𝗀𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒 𝖲𝗈𝗇𝗀𝗌 🎶"
)


def add_me_btn():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ➕",
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ]
        ]
    )


def add_me_article():
    return InlineQueryResultArticle(
        title=f"❖ ♪ — @{app.username}",
        description="𝖸𝗈𝗎𝗋 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖬𝗎𝗌𝗂𝖼 𝖲𝗍𝗋𝖾𝖺𝗆𝖾𝗋 🎶",
        thumb_url="https://files.catbox.moe/qv2ob4.jpg",
        input_message_content=InputTextMessageContent(
            ADD_ME_PROMO_TEXT
        ),
        reply_markup=add_me_btn(),
    )


# ================================
#       INLINE HANDLER
# ================================

@app.on_inline_query()
async def bot_inline(_, inline_query):
    if not inline_query.query.strip():
        await inline_query.answer(
            [add_me_article()],
            cache_time=0,
            is_personal=True,
        )
