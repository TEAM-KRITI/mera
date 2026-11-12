from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums
import config


class BUTTONS(object):

    ABUTTON = [
        [
            InlineKeyboardButton(
                "꯭˹ ꯭𝐒꯭ᴜ꯭ᴘ꯭ᴘ꯭ᴏ꯭ʀ꯭ᴛ ꯭˼",
                url="https://t.me/kirti_bots_support"
            ),
            InlineKeyboardButton(
                "꯭˹ ꯭𝐔꯭ᴘ꯭ᴅ꯭ᴀ꯭ᴛ꯭ᴇ꯭s ꯭˼",
                url="https://t.me/kirti_bots"
            )
        ],
        [
            InlineKeyboardButton(
                "꯭˹ ❍𝐎꯭ᴡ꯭ɴ꯭ᴇ꯭ʀ ꯭˼",
                user_id=config.OWNER_ID
            ),
            InlineKeyboardButton(
                "꯭˹ ꯭𝐁꯭ᴀ꯭ᴄ꯭ᴋ ꯭˼",
                callback_data="settingsback_helper"
            )
        ]
    ]


    INFO_BUTTON = [
        [
            InlineKeyboardButton(
                "꯭˹ ꯭𝐑꯭ᴇ꯭ᴘ꯭ᴏ ꯭˼",
                callback_data="gib_source"
            ),
            InlineKeyboardButton(
                "꯭˹ ꯭𝐘꯭ᴛ-𝐀꯭ᴘ꯭ɪ ꯭˼",
                callback_data="bot_info_data"
            ),
            InlineKeyboardButton(
                "꯭˹ ꯭𝐋꯭ᴀ꯭ɴ꯭ɢ꯭ᴜ꯭ᴀ꯭ɢ꯭ᴇ ꯭˼",
                callback_data="LG"
            )
        ],
        [
            InlineKeyboardButton(
                "꯭˹ ꯭𝐏꯭ʀ꯭ɪ꯭ᴠ꯭ᴀ꯭ᴄ꯭ʏ ꯭˼",
                url="https://files.catbox.moe/u21pts.jpg"
            ),
            InlineKeyboardButton(
                "꯭⌯ ꯭𝐁꯭ᴀ꯭ᴄ꯭ᴋ ꯭⌯",
                callback_data="settingsback_helper"
            )
        ]
    ]


    INFO_NEW = [
        [
            InlineKeyboardButton(
                "꯭⌯ ꯭𝐁꯭ᴀ꯭ᴄ꯭ᴋ ꯭⌯",
                callback_data="settings_back_helper"
            )
        ]
    ]
