# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# Unauthorized forking, importing, or using this code
# without giving proper credit will result in legal action ⚠️
#
# 📩 DM for permission : @TheSigmaCoder
# =======================================================

import time
import random
import asyncio

from pyrogram import enums, filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from py_yt import VideosSearch

import config

from ShiviMusic import app
from ShiviMusic.misc import _boot_
from ShiviMusic.plugins.sudo.sudoers import sudoers_list
from ShiviMusic.utils.database import (
    get_served_chats,
    get_served_users,
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from ShiviMusic.utils.decorators.language import LanguageStart
from ShiviMusic.utils.formatters import get_readable_time
from ShiviMusic.utils.inline import (
    help_pannel,
    private_panel,
    start_panel,
    support_info_panel,
)
from config import BANNED_USERS
from strings import get_string


shivi_PIC = [
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
]


# Telegram message effects (private chat): 👍 5107584321108051014 | ❤️ 5159385139981059251
# 🔥 5104841245755180586 | 🎉 5046509860389126442 | 👎 5104858069142078462
START_EFFECT_ID = 5107584321108051014

REACTIONS = ["👍", "🔥", "❤️", "🥰", "🎉", "😍", "🤩"]


async def react_on(msg):
    """Bot ke apne start message par reaction lagao."""
    emoji = random.choice(REACTIONS)
    try:
        # big=True -> poori screen par reaction ka animation (burst) chalta hai
        await msg.react(emoji, big=True)
    except TypeError:
        try:
            await msg.react(emoji)
        except Exception:
            pass
    except Exception:
        pass


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    try:
        await message.delete()
    except:
        pass

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name[0:4] == "help":
            keyboard = help_pannel(_)

            return await message.reply_photo(
                random.choice(shivi_PIC),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        if name[0:3] == "sud":
            await sudoers_list(
                client=client,
                message=message,
                _=_,
            )

            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"✦ {message.from_user.mention} "
                        f"ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ "
                        f"<b>𝐒꯭ᴜ꯭ᴅ꯭ᴏ꯭ʟ꯭ɪ꯭s꯭ᴛ</b>.\n\n"

                        f"<b>✦ 𝐔꯭s꯭ᴇ꯭ʀ ꯭༭꯭ 𝐈꯭𝐃 ➠</b> "
                        f"<code>{message.from_user.id}</code>\n"

                        f"<b>✦ 𝐔꯭s꯭ᴇ꯭ʀ꯭ɴ꯭ᴀ꯭ᴍ꯭ᴇ ➠</b> "
                        f"@{message.from_user.username}"
                    ),
                )

            return

        if name[0:3] == "inf":
            m = await message.reply_text("🔎")

            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query, limit=1)

            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title,
                duration,
                views,
                published,
                channellink,
                channel,
                app.mention,
            )

            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_["S_B_8"],
                            url=link,
                            style=enums.ButtonStyle.PRIMARY,
                        ),
                        InlineKeyboardButton(
                            text=_["S_B_9"],
                            url=config.SUPPORT_CHAT,
                            style=enums.ButtonStyle.SUCCESS,
                        ),
                    ],
                ]
            )

            await m.delete()

            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )

            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"✦ {message.from_user.mention} "
                        f"ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ "
                        f"<b>𝐓꯭ʀ꯭ᴀ꯭ᴄ꯭ᴋ ꯭༭꯭ 𝐈꯭ɴ꯭ғ꯭ᴏ꯭ʀ꯭ᴍ꯭ᴀ꯭ᴛ꯭ɪ꯭ᴏ꯭ɴ</b>.\n\n"

                        f"✦ <b>𝐔꯭s꯭ᴇ꯭ʀ ꯭༭꯭ 𝐈꯭𝐃 ➠</b> "
                        f"<code>{message.from_user.id}</code>\n"

                        f"✦ <b>𝐔꯭s꯭ᴇ꯭ʀ꯭ɴ꯭ᴀ꯭ᴍ꯭ᴇ ➠</b> "
                        f"@{message.from_user.username}"
                    ),
                )

    else:
        out = private_panel(_)

        photo_args = dict(
            photo=random.choice(shivi_PIC),
            has_spoiler=True,
            caption=_["start_2"].format(
                message.from_user.mention,
                app.mention,
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )
        try:
            # message effect = poori screen par 👍 ka animation (sirf private chat me)
            await message.reply_photo(**photo_args, effect_id=START_EFFECT_ID)
        except Exception as e:
            print(f"[start] effect failed ({type(e).__name__}: {e}), normal bhej raha hu")
            sent = await message.reply_photo(**photo_args)
            await react_on(sent)

        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"{message.from_user.mention} "
                    f"ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"

                    f"<b>ᴜsᴇʀ ɪᴅ :</b> "
                    f"<code>{message.from_user.id}</code>\n"

                    f"<b>ᴜsᴇʀɴᴀᴍᴇ :</b> "
                    f"@{message.from_user.username}"
                ),
            )


# ======================================================
# 🆘 SUPPORT INFO  (Support button → info + Support/Updates + Back)
# ======================================================

SUPPORT_INFO_TEXT = (
    "✨ <b><a href='{chat}'>{bot}</a> sᴜᴘᴘᴏʀᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>\n\n"
    "❏ ɪғ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ɪssᴜᴇs, ʙᴜɢs ᴏʀ ɴᴇᴇᴅ ʜᴇʟᴘ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ, "
    "ᴊᴏɪɴ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.\n\n"
    "📢 ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ ᴛᴏ ɢᴇᴛ ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇs ᴀɴᴅ ɴᴇᴡs.\n\n"
    "❖ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ"
)


@app.on_callback_query(filters.regex("^support_info$") & ~BANNED_USERS)
async def support_info_cb(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    _ = get_string(await get_lang(CallbackQuery.message.chat.id))

    await CallbackQuery.edit_message_caption(
        caption=SUPPORT_INFO_TEXT.format(
            chat=config.SUPPORT_CHAT, bot=app.mention
        ),
        reply_markup=InlineKeyboardMarkup(support_info_panel(_)),
    )


@app.on_callback_query(filters.regex("^back_to_start$") & ~BANNED_USERS)
async def back_to_start_cb(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    _ = get_string(await get_lang(CallbackQuery.message.chat.id))

    await CallbackQuery.edit_message_caption(
        caption=_["start_2"].format(
            CallbackQuery.from_user.mention, app.mention
        ),
        reply_markup=InlineKeyboardMarkup(private_panel(_)),
    )


# ======================================================
# 📩 JOIN REQUEST → PRIVATE WELCOME
# ======================================================

@app.on_chat_join_request()
async def join_request_welcome(
    client,
    request: ChatJoinRequest,
):
    user = request.from_user

    if not user:
        return

    try:
        language = await get_lang(request.chat.id)
        _ = get_string(language)

        user_chat_id = (
            getattr(request, "user_chat_id", None)
            or user.id
        )

        group_title = request.chat.title or "this group"

        caption = (
    f"<b>❏ ˹ᴡᴇʟᴄᴏᴍᴇ, {user.mention} 🇮🇳˼</b>\n\n"
    f"˹ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ "
    f"<b>{group_title}</b> ʜᴀs ʙᴇᴇɴ ʀᴇᴄᴇɪᴠᴇᴅ˼ ✅\n\n"
    f"˹ᴇηᴊσʏ ᴜηʟɪмɪᴛ𝛆ᴅ мᴜsɪᴄ ᴧηᴅ ᴠɪʙ𝛆s˼ 🎧\n\n"
    f"❏ ʜɪɢʜ ǫᴜᴀʟɪᴛʏ мᴜsɪᴄ 🎶\n"
    f"❏ ғᴀsᴛ & sмᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ ♡\n"
    f"❏ sᴛᴀʙʟᴇ мᴜsɪᴄ ᴇxᴘᴇʀɪᴇɴᴄᴇ ✨\n\n"
    f"˹ᴜsᴇ /start ᴛᴏ ʙᴇɢɪɴ˼"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=_["S_B_14"],
                        callback_data="abot_cb",
                        style=enums.ButtonStyle.PRIMARY,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=_["S_B_6"],
                        url=config.SUPPORT_CHANNEL,
                        style=enums.ButtonStyle.SUCCESS,
                    ),
                    InlineKeyboardButton(
                        text=_["S_B_9"],
                        url=config.SUPPORT_CHAT,
                        style=enums.ButtonStyle.SUCCESS,
                    ),
                ],
            ]
        )

        await app.send_photo(
            chat_id=user_chat_id,
            photo=random.choice(shivi_PIC),
            has_spoiler=True,
            caption=caption,
            reply_markup=keyboard,
        )

    except Exception as ex:
        print(f"[JOIN REQUEST] {ex}")


@app.on_message(
    filters.command(["start"])
    & filters.group
    & ~BANNED_USERS
)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)

    uptime = int(time.time() - _boot_)

    sent = await message.reply_photo(
        random.choice(shivi_PIC),
        has_spoiler=True,
        caption=_["start_1"].format(
            app.mention,
            get_readable_time(uptime),
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await react_on(sent)

    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:

                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(
                        message.chat.id
                    )

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )

                    return await app.leave_chat(
                        message.chat.id
                    )

                out = start_panel(_)

                await message.reply_text(
                    text=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await add_served_chat(
                    message.chat.id
                )

                await message.stop_propagation()

        except Exception as ex:
            print(ex)


# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Purvi-V3
# 📢 Telegram channel : t.me/Purvi_Bots
# ======================================================
