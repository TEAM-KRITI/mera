# =======================================================
# ©️ 2025-26 All Rights Reserved by REVANGE Bots (suraj08832) 🚀
#
# This source code is under MIT License 📜
# =======================================================

from pyrogram.enums import ParseMode
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ShiviMusic import app


# =======================================================
# /ID COMMAND
# =======================================================

@app.on_message(filters.command("id"))
async def getid(client, message: Message):

    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = (
        f"**● [ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    )

    text += (
        f"**● [ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** "
        f"`{your_id}`\n"
    )

    # ---------------------------------------------------
    # USERNAME / USER ID ARGUMENT
    # ---------------------------------------------------

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user = await client.get_users(split)
            user_id = user.id

            text += (
                f"**● [ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** "
                f"`{user_id}`\n"
            )

        except Exception:
            return await message.reply_text(
                "● ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.",
                quote=True,
            )

    # ---------------------------------------------------
    # CHAT ID
    # ---------------------------------------------------

    if chat.username:
        text += (
            f"**● [ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** "
            f"`{chat.id}`\n\n"
        )
    else:
        text += (
            f"**● ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n\n"
        )

    # ---------------------------------------------------
    # REPLIED MESSAGE
    # ---------------------------------------------------

    if (
        reply
        and not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):

        text += (
            f"**● [ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** "
            f"`{reply.id}`\n"
        )

        if reply.from_user:
            text += (
                f"**● [ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:]"
                f"(tg://user?id={reply.from_user.id})** "
                f"`{reply.from_user.id}`\n\n"
            )
        else:
            text += "\n"

    # ---------------------------------------------------
    # FORWARDED CHANNEL
    # ---------------------------------------------------

    if reply and reply.forward_from_chat:

        text += (
            f"● ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, "
            f"{reply.forward_from_chat.title}, "
            f"ʜᴀs ᴀɴ ɪᴅ ᴏғ "
            f"`{reply.forward_from_chat.id}`\n\n"
        )

    # ---------------------------------------------------
    # SENDER CHAT
    # ---------------------------------------------------

    if reply and reply.sender_chat:

        text += (
            f"● ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, "
            f"ɪs `{reply.sender_chat.id}`"
        )

    # ---------------------------------------------------
    # SEND RESULT
    # ---------------------------------------------------

    await message.reply_text(
        text,
        parse_mode=ParseMode.DEFAULT,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴄʟᴏsᴇ",
                        callback_data="close",
                    )
                ]
            ]
        ),
    )


# =======================================================
# USER INFORMATION
# =======================================================

INFO_TEXT = """
<u><b>👤 ᴜꜱᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b></u>

<b>● ғɪʀsᴛ ɴᴀᴍᴇ ➠</b> {first}
<b>● ʟᴀsᴛ ɴᴀᴍᴇ ➠</b> {last}
<b>● ᴜꜱᴇʀ ɪᴅ ➠</b> <code>{id}</code>
<b>● ᴜꜱᴇʀɴᴀᴍᴇ ➠</b> @{username}
<b>● ᴍᴇɴᴛɪᴏɴ ➠</b> {mention}
<b>● ꜱᴛᴀᴛᴜꜱ ➠</b> {status}
<b>● ᴅᴄ ɪᴅ ➠</b> {dcid}
<b>● ᴘʀᴇᴍɪᴜᴍ ➠</b> {premium}
<b>● ꜱᴄᴀᴍ ➠</b> {scam}

<b>● ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➠
<a href="https://t.me/annu_updates">˹ᴋɪʀᴛɪ ʙᴏᴛѕ˼</a></b>
"""


# =======================================================
# USER STATUS
# =======================================================

async def userstatus(user_id):

    try:
        user = await app.get_users(user_id)
        status = user.status

        if status == enums.UserStatus.RECENTLY:
            return "ʀᴇᴄᴇɴᴛʟʏ"

        elif status == enums.UserStatus.LAST_WEEK:
            return "ʟᴀꜱᴛ ᴡᴇᴇᴋ"

        elif status == enums.UserStatus.LONG_AGO:
            return "ʟᴏɴɢ ᴀɢᴏ"

        elif status == enums.UserStatus.OFFLINE:
            return "ᴏꜰꜰʟɪɴᴇ"

        elif status == enums.UserStatus.ONLINE:
            return "ᴏɴʟɪɴᴇ"

        return "ᴜɴᴋɴᴏᴡɴ"

    except Exception:
        return "ᴇʀʀᴏʀ"


# =======================================================
# /INFO /USERINFO /WHOIS
# =======================================================

@app.on_message(
    filters.command(
        ["info", "information", "userinfo", "whois"],
        prefixes=["/", "!"],
    )
)
async def userinfo(_, message: Message):

    try:

        # ------------------------------------------------
        # GET USER
        # ------------------------------------------------

        if (
            not message.reply_to_message
            and len(message.command) == 2
        ):

            user_id = message.text.split(
                None,
                1,
            )[1].strip()

        elif message.reply_to_message:

            reply_user = message.reply_to_message.from_user

            if not reply_user:
                return await message.reply_text(
                    "✦ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴅᴏᴇs ɴᴏᴛ ʙᴇʟᴏɴɢ ᴛᴏ ᴀ ᴜsᴇʀ."
                )

            user_id = reply_user.id

        elif (
            not message.reply_to_message
            and len(message.command) == 1
        ):

            return await message.reply_text(
                "**✦ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ, "
                "ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴀꜰᴛᴇʀ ᴄᴏᴍᴍᴀɴᴅ.**"
            )

        else:

            user_id = message.from_user.id

        # ------------------------------------------------
        # GET USER INFORMATION
        # ------------------------------------------------

        user = await app.get_users(user_id)

        status = await userstatus(user.id)

        scam = (
            "ʏᴇs"
            if user.is_scam
            else "ɴᴏ"
        )

        premium = (
            "ʏᴇs"
            if user.is_premium
            else "ɴᴏ"
        )

        profile_url = (
            f"https://t.me/{user.username}"
            if user.username
            else f"tg://user?id={user.id}"
        )

        # ------------------------------------------------
        # USER INFO MESSAGE
        # ------------------------------------------------

        info_message = INFO_TEXT.format(
            first=user.first_name or "N/A",
            last=user.last_name or "N/A",
            id=user.id,
            username=user.username or "N/A",
            mention=user.mention,
            status=status,
            dcid=user.dc_id or "N/A",
            premium=premium,
            scam=scam,
        )

        # ------------------------------------------------
        # SEND
        # ------------------------------------------------

        await message.reply_text(
            text=info_message,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            user.first_name or "User",
                            url=profile_url,
                        )
                    ]
                ]
            ),
        )

    except Exception as e:

        await message.reply_text(
            f"**❌ ᴇʀʀᴏʀ:** `{e}`"
        )


# =======================================================
# ©️ 2025-26 All Rights Reserved by Revange 😎
#
# 🧑‍💻 Developer : t.me/dmcatelegram
# 🔗 Source link : https://github.com/hexamusic/REVANGEMUSIC
# 📢 Telegram channel : t.me/dmcatelegram
# ====================================================
