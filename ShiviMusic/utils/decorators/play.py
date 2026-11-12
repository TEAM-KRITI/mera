# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import YouTube, app
from ShiviMusic.misc import SUDOERS
from ShiviMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from ShiviMusic.utils.inline import botplaylist_markup

# ---- Anonymous admin support (inline, alag file ki zarurat nahi) ----
from pyrogram.types import User as _AnonUser

_ANON_ADMIN_ID = 1087968824  # Telegram ka "GroupAnonymousBot" id


def make_anon_admin(client, message) -> bool:
    sc = getattr(message, "sender_chat", None)
    if not sc or sc.id != message.chat.id:
        return False
    # Anonymous admin ka asli naam Telegram nahi deta. Isliye song "by" me
    # admin ka custom title (author_signature) dikhao, nahi to group ka naam.
    shown_name = (
        getattr(message, "author_signature", None)
        or getattr(sc, "title", None)
        or "Anonymous Admin"
    )
    message.from_user = _AnonUser(
        id=_ANON_ADMIN_ID, is_bot=True, first_name=shown_name, client=client
    )
    message.is_anon_admin = True
    return True


def is_anon_admin(message) -> bool:
    return bool(getattr(message, "is_anon_admin", False))

from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string


links = {}


def PlayWrapper(command):
    async def wrapper(client, message):

        # ==================================================
        # LANGUAGE
        # ==================================================

        language = await get_lang(message.chat.id)
        _ = get_string(language)

        # ==================================================
        # SENDER CHAT CHECK
        # ==================================================

        if message.sender_chat and not make_anon_admin(client, message):
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʜᴏᴡ ᴛᴏ ғɪx ?",
                            callback_data="ShivimousAdmin",
                        )
                    ]
                ]
            )

            return await message.reply_text(
                _["general_3"],
                reply_markup=upl,
            )

        # ==================================================
        # MAINTENANCE
        # ==================================================

        if await is_maintenance() is False:

            if message.from_user and message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=(
                        f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                        f"ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> "
                        f"ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ."
                    ),
                    disable_web_page_preview=True,
                )

        # ==================================================
        # DELETE COMMAND
        # ==================================================

        try:
            await message.delete()
        except Exception:
            pass

        # ==================================================
        # REPLIED AUDIO
        # ==================================================

        audio_telegram = (
            (
                message.reply_to_message.audio
                or message.reply_to_message.voice
            )
            if message.reply_to_message
            else None
        )

        # ==================================================
        # REPLIED VIDEO
        # ==================================================

        video_telegram = (
            (
                message.reply_to_message.video
                or message.reply_to_message.document
            )
            if message.reply_to_message
            else None
        )

        # ==================================================
        # YOUTUBE URL
        # ==================================================

        url = await YouTube.url(message)

        # ==================================================
        # NO QUERY
        # ==================================================

        if (
            audio_telegram is None
            and video_telegram is None
            and url is None
        ):

            if len(message.command) < 2:

                if "stream" in message.command:
                    return await message.reply_text(
                        _["str_1"]
                    )

                buttons = botplaylist_markup(_)

                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # ==================================================
        # CHANNEL PLAY
        # ==================================================

        if message.command[0][0] == "c":

            chat_id = await get_cmode(message.chat.id)

            if chat_id is None:
                return await message.reply_text(
                    _["setting_7"]
                )

            try:
                chat = await app.get_chat(chat_id)

            except Exception:
                return await message.reply_text(
                    _["cplay_4"]
                )

            channel = chat.title

        else:
            chat_id = message.chat.id
            chat = message.chat
            channel = None

        # ==================================================
        # PLAY MODE
        # ==================================================

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        # ==================================================
        # ADMIN ONLY PLAY
        # ==================================================

        if playty != "Everyone":

            if (
                message.from_user
                and not is_anon_admin(message)
                and message.from_user.id not in SUDOERS
            ):

                admins = adminlist.get(message.chat.id)

                if not admins:
                    return await message.reply_text(
                        _["admin_13"]
                    )

                if message.from_user.id not in admins:
                    return await message.reply_text(
                        _["play_4"]
                    )

        # ==================================================
        # VIDEO / AUDIO
        # ==================================================

        if message.command[0][0] == "v":
            video = True

        else:

            if "-v" in message.text:
                video = True

            else:

                try:
                    video = (
                        True
                        if len(message.command) > 1
                        and message.command[0][1] == "v"
                        else None
                    )
                except Exception:
                    video = None

        # ==================================================
        # FORCE PLAY
        # ==================================================

        if message.command[0][-1] == "e":

            if not await is_active_chat(chat_id):
                return await message.reply_text(
                    _["play_16"]
                )

            fplay = True

        else:
            fplay = None

        # ==================================================
        # ASSISTANT CHECK
        # ==================================================

        if not await is_active_chat(chat_id):

            userbot = await get_assistant(chat_id)

            # --------------------------------------------------
            # IMPORTANT FIX:
            # Pyrogram Client does NOT have .id
            # --------------------------------------------------

            try:
                userbot_me = await userbot.get_me()
                userbot_id = userbot_me.id

            except Exception as e:
                return await message.reply_text(
                    _["call_3"].format(
                        app.mention,
                        type(e).__name__,
                    )
                )

            # ==================================================
            # CHECK ASSISTANT MEMBER STATUS
            # ==================================================

            try:

                get = await app.get_chat_member(
                    chat_id,
                    userbot_id,
                )

                if get.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):

                    assistant_name = (
                        userbot_me.first_name
                        or "Assistant"
                    )

                    assistant_username = (
                        userbot_me.username
                        or ""
                    )

                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention,
                            userbot_id,
                            assistant_name,
                            assistant_username,
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text=(
                                            "๏ ᴜɴʙᴀɴ "
                                            "ᴀssɪsᴛᴀɴᴛ ๏"
                                        ),
                                        callback_data=(
                                            "unban_assistant"
                                        ),
                                    )
                                ]
                            ]
                        ),
                    )

            # --------------------------------------------------
            # ASSISTANT NOT IN CHAT
            # --------------------------------------------------

            except UserNotParticipant:

                # ==============================================
                # GET INVITE LINK
                # ==============================================

                if chat_id in links:

                    invitelink = links[chat_id]

                else:

                    # ------------------------------------------
                    # PUBLIC CHAT
                    # ------------------------------------------

                    # NOTE: channel play me target chat CHANNEL hai,
                    # group nahi -> channel ka username/link use karo
                    if chat.username:

                        invitelink = (
                            chat.username
                        )

                        try:
                            await userbot.resolve_peer(
                                invitelink
                            )
                        except Exception:
                            pass

                    # ------------------------------------------
                    # PRIVATE CHAT
                    # ------------------------------------------

                    else:

                        try:

                            invitelink = (
                                await app.export_chat_invite_link(
                                    chat_id
                                )
                            )

                        except ChatAdminRequired:

                            return await message.reply_text(
                                _["call_1"]
                            )

                        except Exception as e:

                            return await message.reply_text(
                                _["call_3"].format(
                                    app.mention,
                                    type(e).__name__,
                                )
                            )

                # ==============================================
                # CONVERT OLD INVITE FORMAT
                # ==============================================

                if invitelink.startswith(
                    "https://t.me/+"
                ):

                    invitelink = invitelink.replace(
                        "https://t.me/+",
                        "https://t.me/joinchat/",
                    )

                # ==============================================
                # JOIN MESSAGE
                # ==============================================

                myu = await message.reply_text(
                    _["call_4"].format(app.mention)
                )

                try:

                    await asyncio.sleep(1)

                    await userbot.join_chat(
                        invitelink
                    )

                # ==============================================
                # JOIN REQUEST
                # ==============================================

                except InviteRequestSent:

                    try:

                        await app.approve_chat_join_request(
                            chat_id,
                            userbot_id,
                        )

                    except Exception as e:

                        return await message.reply_text(
                            _["call_3"].format(
                                app.mention,
                                type(e).__name__,
                            )
                        )

                    await asyncio.sleep(3)

                    try:
                        await myu.edit(
                            _["call_5"].format(
                                app.mention
                            )
                        )
                    except Exception:
                        pass

                # ==============================================
                # ALREADY PARTICIPANT
                # ==============================================

                except UserAlreadyParticipant:
                    pass

                # ==============================================
                # OTHER JOIN ERROR
                # ==============================================

                except Exception as e:

                    return await message.reply_text(
                        _["call_3"].format(
                            app.mention,
                            type(e).__name__,
                        )
                    )

                # ==============================================
                # SAVE LINK
                # ==============================================

                links[chat_id] = invitelink

                # ==============================================
                # RESOLVE CHAT
                # ==============================================

                try:
                    await userbot.resolve_peer(
                        chat_id
                    )
                except Exception:
                    pass

            # --------------------------------------------------
            # OTHER CHAT MEMBER ERROR
            # --------------------------------------------------

            except ChatAdminRequired:

                return await message.reply_text(
                    _["call_1"]
                )

            except Exception as e:

                return await message.reply_text(
                    _["call_3"].format(
                        app.mention,
                        type(e).__name__,
                    )
                )

        # ==================================================
        # RUN COMMAND
        # ==================================================

        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots
# ===========================================================
