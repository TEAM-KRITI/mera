# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

import inspect
import random

from pyrogram.types import InlineKeyboardButton

import config
from ShiviMusic import app

# Check if the installed pyrogram/fork natively accepts these args
_PARAMS = inspect.signature(InlineKeyboardButton.__init__).parameters
_SUPPORTS_ICON = "icon_custom_emoji_id" in _PARAMS
_SUPPORTS_STYLE = "style" in _PARAMS

# primary = blue, success = green, danger = red
_COLORS = ["primary", "success", "danger"]


def _btn(
    text: str,
    icon_custom_emoji_id: str = None,
    style: str = None,
    **kwargs,
) -> InlineKeyboardButton:
    """Create an InlineKeyboardButton with custom emoji + colour support.

    style can be: "primary", "success", "danger" or "random".
    """
    if style == "random":
        style = random.choice(_COLORS)

    extra = {}
    if icon_custom_emoji_id and _SUPPORTS_ICON:
        extra["icon_custom_emoji_id"] = str(icon_custom_emoji_id)
    if style and _SUPPORTS_STYLE:
        extra["style"] = style

    btn = InlineKeyboardButton(text=text, **extra, **kwargs)

    # Fallback for forks that don't accept these args in __init__
    if icon_custom_emoji_id and not _SUPPORTS_ICON:
        try:
            setattr(btn, "icon_custom_emoji_id", str(icon_custom_emoji_id))
        except Exception:
            pass
    if style and not _SUPPORTS_STYLE:
        try:
            setattr(btn, "style", style)
        except Exception:
            pass

    return btn


# ===========================================================
# START PANEL
# ===========================================================

def start_panel(_):

    buttons = [
        [
            _btn(
                text=f"{_['S_B_1']}",
                url=f"https://t.me/{app.username}?startgroup=true",
                icon_custom_emoji_id="6285259654977036895",
                style="random",
            ),
            _btn(
                text=f"{_['S_B_2']}",
                url=config.SUPPORT_CHAT,
                icon_custom_emoji_id="6280582160713786149",
                style="random",
            ),
        ],
    ]

    return buttons


# ===========================================================
# PRIVATE PANEL
# ===========================================================

def private_panel(_):

    buttons = [
        [
            _btn(
                text="ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ",
                url=f"https://t.me/{app.username}?startgroup=true",
                icon_custom_emoji_id="6285259654977036895",
                style="random",
            )
        ],
        [
            _btn(
                text="˹ ❍ᴡηєʀ ˼",
                user_id=config.OWNER_ID,
                icon_custom_emoji_id="6280798188978840619",
                style="random",
            ),
            _btn(
                text="˹ sυᴘᴘσʀᴛ ˼",
                callback_data="support_info",
                icon_custom_emoji_id="6278234608899204440",
                style="random",
            ),
        ],
        [
            _btn(
                text="˹ ʜєʟᴘ ᴧηᴅ ᴄσϻϻᴧηᴅs ˼",
                callback_data="settings_back_helper",
                icon_custom_emoji_id="6282902589809894216",
                style="random",
            )
        ],
    ]

    return buttons


# ===========================================================
# SUPPORT INFO PANEL (Support + Updates + Back)
# ===========================================================

def support_info_panel(_):

    buttons = [
        [
            _btn(
                text="˹ sυᴘᴘσʀᴛ ˼",
                url=config.SUPPORT_CHAT,
                icon_custom_emoji_id="6278234608899204440",
                style="random",
            ),
            _btn(
                text="˹ υᴘᴅᴧᴛєs ˼",
                url=config.SUPPORT_CHANNEL,
                icon_custom_emoji_id="6280582160713786149",
                style="random",
            ),
        ],
        [
            _btn(
                text="⌯ ʙᴧᴄᴋ ⌯",
                callback_data="back_to_start",
                style="random",
            )
        ],
    ]

    return buttons


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder)
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
