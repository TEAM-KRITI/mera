import re

from pyrogram import filters
from pyrogram.types import Message

from ShiviMusic import app
from ShiviMusic.plugins.misc.guest import ADD_ME_PROMO_TEXT, _add_me_markup

# ==========================================
# MEMBER-CHAT USERNAME MENTION
# ==========================================
# Guest Mode (guest.py) only fires in chats the bot is NOT a member
# of — groups it has never joined, or a stranger's private DM.
#
# Once the bot IS a member of a chat (added to a group/channel), all
# further @mentions there arrive as normal messages instead, so Guest
# Mode goes silent for that chat. This handler covers exactly that
# gap: plain-text @username mentions in chats where the bot is
# already present, so the promo works everywhere without any gaps.

_MENTION_PATTERN = re.compile(
    r"(?<![\w])@" + re.escape(app.username) + r"(?![\w])",
    flags=re.IGNORECASE,
)


@app.on_message(filters.text & ~filters.bot & ~filters.via_bot, group=7)
async def member_chat_username_mention(client, message: Message):
    text = message.text or ""
    if not _MENTION_PATTERN.search(text):
        return

    try:
        await message.reply_text(
            ADD_ME_PROMO_TEXT,
            reply_markup=_add_me_markup(),
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Member-chat mention reply error: {e}")
