import math
import random
from pyrogram import enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton
from ShiviMusic.utils.formatters import time_to_seconds
from ShiviMusic import app

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def track_markup(_, videoid, user_id, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=alone_style
            )
        ],
    ]
    return buttons


def _progress_bar(played_sec, duration_sec, size=12):
    ratio = (played_sec / duration_sec) if duration_sec else 0
    pos = min(size - 1, max(0, int(ratio * size)))
    return "─" * pos + "▷" + "─" * (size - 1 - pos)


def _control_rows(chat_id, style):
    return [
        InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=style),
        InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=style),
        InlineKeyboardButton(
            text="➕",
            url=f"https://t.me/{app.username}?startgroup=true",
            style=style,
        ),
        InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=style),
        InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=style),
    ]


def _fav_row(chat_id, style):
    """Now-playing message ke neeche ❤️ Favourite / 📂 Playlist buttons."""
    return [
        InlineKeyboardButton(text="❤️ ꜰᴀᴠ", callback_data=f"FavNow {chat_id}", style=style),
        InlineKeyboardButton(text="📂 ᴘʟᴀʏʟɪsᴛ", callback_data=f"PlPick {chat_id}", style=style),
    ]


def stream_markup_timer(_, chat_id, played, dur):
    style = random.choice(STYLES)
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = _progress_bar(played_sec, duration_sec)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="api_status",
                style=style,
            ),
        ],
        _control_rows(chat_id, style),
        _fav_row(chat_id, style),
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=style),
        ],
    ]
    return buttons


def stream_markup(_, chat_id):
    style = random.choice(STYLES)
    buttons = [
        _control_rows(chat_id, style),
        _fav_row(chat_id, style),
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=style),
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"ShiviPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"ShiviPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=alone_style
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    alone_style = random.choice(STYLES)

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=alone_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=alone_style
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])

    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=group_style
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=group_style
            ),
        ],
    ]
    return buttons
