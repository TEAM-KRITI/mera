# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

import inspect
import random
from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import app

# Check if the installed pyrogram/fork natively accepts these args
_PARAMS = inspect.signature(InlineKeyboardButton.__init__).parameters
_SUPPORTS_STYLE = "style" in _PARAMS

# primary = blue, success = green, danger = red
_COLORS = ["primary", "success", "danger"]


def _btn(text: str, style: str = None, **kwargs) -> InlineKeyboardButton:
    """Create an InlineKeyboardButton with colour support.

    style can be: "primary", "success", "danger" or "random".
    """
    if style == "random":
        style = random.choice(_COLORS)

    if style and _SUPPORTS_STYLE:
        return InlineKeyboardButton(text=text, style=style, **kwargs)

    btn = InlineKeyboardButton(text=text, **kwargs)
    if style:
        try:
            setattr(btn, "style", style)
        except Exception:
            pass
    return btn


def help_pannel(_, START: Union[bool, int] = None):
    first = [
        _btn(
            text=_["CLOSE_BUTTON"],
            callback_data="close",
            style="random",
        )
    ]
    second = [
        _btn(
            text=_["BACK_BUTTON"],
            callback_data="settingsback_helper",
            style="random",
        ),
    ]

    mark = second if START else first

    upl = InlineKeyboardMarkup(
        [
            [
                _btn(
                    text=_["H_B_25"],
                    callback_data="help_callback hb1",
                    style="random",
                ),
                _btn(
                    text=_["H_B_26"],
                    callback_data="help_callback hb2",
                    style="random",
                ),
                _btn(
                    text=_["H_B_28"],
                    callback_data="help_callback hb3",
                    style="random",
                ),
            ],
            [
                _btn(
                    text=_["H_B_27"],
                    callback_data="help_callback hb4",
                    style="random",
                ),
                _btn(
                    text=_["H_B_31"],
                    callback_data="help_callback hb5",
                    style="random",
                ),
                _btn(
                    text=_["H_B_29"],
                    callback_data="help_callback hb6",
                    style="random",
                ),
            ],
            [
                _btn(
                    text=_["H_B_33"],
                    callback_data="help_callback hb7",
                    style="random",
                ),
                _btn(
                    text=_["H_B_30"],
                    callback_data="help_callback hb8",
                    style="random",
                ),
                _btn(
                    text=_["H_B_32"],
                    callback_data="help_callback hb9",
                    style="random",
                ),
            ],
            [
                _btn(
                    text="• ᴀᴜᴛᴏ-ᴘʟᴀʏ •",
                    callback_data="help_callback hb10",
                    style="random",
                ),
                _btn(
                    text="• ᴛʜᴜᴍʙ •",
                    callback_data="help_callback hb12",
                    style="random",
                ),
                _btn(
                    text="• ᴘʟᴀʏ-ɪɴғᴏ •",
                    callback_data="help_callback hb11",
                    style="random",
                ),
            ],
            mark,
        ]
    )
    return upl


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                _btn(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                    style="random",
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            _btn(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style="random",
            ),
        ],
    ]
    return buttons


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
