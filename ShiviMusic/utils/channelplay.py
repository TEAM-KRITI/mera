# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# ===========================================================

from ShiviMusic import app
from ShiviMusic.utils.database import get_cmode


async def get_channeplayCB(_, command, CallbackQuery):
    if command == "c":
        chat_id = await get_cmode(CallbackQuery.message.chat.id)

        if chat_id is None:
            try:
                return await CallbackQuery.answer(
                    _["setting_7"],
                    show_alert=True
                )
            except Exception:
                return

        try:
            channel = (await app.get_chat(chat_id)).title
        except Exception:
            try:
                return await CallbackQuery.answer(
                    _["cplay_4"],
                    show_alert=True
                )
            except Exception:
                return

    else:
        chat_id = CallbackQuery.message.chat.id
        channel = None

    return chat_id, channel


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# ===========================================================
