# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎

# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# 🔗 Source link : https://github.com/Badnam019
# 📢 Telegram channel : t.me/lll_APNA_BADNAM_BABY_lll
# =======================================================

from typing import Union
from ShiviMusic import app
from ShiviMusic.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ]
    ]
    dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
            ),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴊᴏɪɴ ɴᴏᴡ",
                url=f"https://t.me/kirti_bots"
            ),
            InlineKeyboardButton(
                text="ɢʀᴏᴜᴘ ᴄʜᴧᴛ",
                url="https://t.me/kirti_bots_support"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ",
                callback_data="close"
            )
        ],
    ]
    return buttons

# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎

# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# 🔗 Source link : https://github.com/Badnam019
# 📢 Telegram channel : t.me/lll_APNA_BADNAM_BABY_lll
# =======================================================
