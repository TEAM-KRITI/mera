# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️

# 📩 DM for permission : @TheSigmaCoder
# =======================================================


from ShiviMusic import app
from ShiviMusic.utils.database import get_assistant

from pyrogram import Client, filters, enums
from pyrogram.types import (
    ChatMemberUpdated,
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, BOT_TOKEN, BOT_NAME, SUPPORT_CHANNEL
from ShiviMusic.utils.welcome_card import create_welcome_card

import html
import json
import aiohttp

import asyncio
import random
import os
from logging import getLogger

LOGGER = getLogger(__name__)

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["Shivi_DB"]
welcomedb = db["welcome_toggle_system"]


async def get_welcome(chat_id: int):
    # Default: welcome OFF. Jab tak admin /welcome se "єηᴧʙʟє" na kare, welcome nahi bhejna.
    data = await welcomedb.find_one({"chat_id": chat_id})
    if not data:
        return False
    return data.get("welcome", False)


async def enable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True
    )


async def disable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True
    )


class temp:
    MELCOW = {}


# =======================================================
# ʙʟυє ʙυᴛᴛᴏη (ʙᴏᴛ ᴧᴘɪ ꜱє ꜱєηᴅ - ʟɪʙʀᴧʀʏ ᴘᴧʀ ηᴧʜɪ ᴅєᴘєηᴅ)
# =======================================================
# Telegram Bot API ka "style": "primary" = blue button.
# Ye pyrogram version se independent hai.

def _bot_username():
    username = getattr(app, "username", None)
    if not username:
        me = getattr(app, "me", None)
        username = getattr(me, "username", None)
    return username


def add_me_button():
    """Pyrogram fallback button (normal colour)."""
    username = _bot_username()
    if not username:
        return None
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "⊚ ᴧᴅᴅ ᴍє ᴛᴏ ʏᴏυʀ ᴄʜᴧᴛ ⊚",
            url=f"https://t.me/{username}?startgroup=true"
        )
    ]])


async def send_blue_photo(chat_id, photo_path, caption_html):
    """Photo + blue 'Add me' button, Bot API se. Message object return nahi hota,
    isliye message_id return karta hai. Fail ho to None."""
    username = _bot_username()
    if not username:
        return None

    markup = {
        "inline_keyboard": [[
            {
                "text": "⊚ ᴧᴅᴅ ᴍє ᴛᴏ ʏᴏυʀ ᴄʜᴧᴛ ⊚",
                "url": f"https://t.me/{username}?startgroup=true",
                "style": "primary",
            }
        ]]
    }

    try:
        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        form.add_field("caption", caption_html)
        form.add_field("parse_mode", "HTML")
        form.add_field("reply_markup", json.dumps(markup))
        with open(photo_path, "rb") as f:
            form.add_field(
                "photo", f.read(),
                filename="welcome.png",
                content_type="image/png"
            )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data=form
            ) as resp:
                data = await resp.json()

        if data.get("ok"):
            return data["result"]["message_id"]

        LOGGER.warning(f"Bot API sendPhoto failed: {data}")
    except Exception as e:
        LOGGER.warning(f"Bot API sendPhoto error: {e}")

    return None


def circle(pfp, size=(390, 390), brightness_factor=1.4):
    pfp = pfp.resize(size).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    pfp.putalpha(mask)
    return pfp


def welcomepic(pic, user, chatname, id, uname, brightness_factor=1.3):
    """Kirti Music welcome card (ShiviMusic/utils/welcome_card.py)."""
    os.makedirs("downloads", exist_ok=True)
    output_path = f"downloads/welcome_{id}.png"
    return create_welcome_card(
        pfp_path=pic,
        user_id=id,
        username=uname,
        chat_title=chatname,
        out_path=output_path,
        brand=BOT_NAME,
        link=SUPPORT_CHANNEL,
    )


@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(_, message: Message):

    chat = message.chat
    chat_id = chat.id

    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**» ᴏηʟʏ ᴧᴅᴍɪηꜱ ᴄᴧη ʜᴧηᴅʟє ᴡєʟᴄᴏᴍє ꜱʏꜱᴛєᴍ**")

    state = await get_welcome(chat_id)
    status = "єηᴧʙʟєᴅ" if state else "ᴅɪꜱᴧʙʟєᴅ"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("єηᴧʙʟє", callback_data=f"wlc_on_{chat_id}"),
            InlineKeyboardButton("ᴅɪꜱᴧʙʟє", callback_data=f"wlc_off_{chat_id}")
        ]
    ])

    await message.reply_text(
        f"» ᴄυʀʀєηᴛʟʏ ᴡєʟᴄᴏᴍє ꜱᴛᴧᴛυꜱ **{status}** ɪη **{chat.title}**",
        reply_markup=btn
    )


@app.on_callback_query(filters.regex("wlc_"))
async def welcome_toggle(_, query):

    data = query.data.split("_")
    action = data[1]
    chat_id = int(data[2])

    member = await app.get_chat_member(chat_id, query.from_user.id)
    if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await query.answer("ʏᴏυ ᴧʀє ηᴏᴛ ᴧᴅᴍɪη ʙᴧʙʏ 🥺", show_alert=True)

    if action == "on":
        await enable_welcome(chat_id)
        new_status = "єηᴧʙʟєᴅ"
    else:
        await disable_welcome(chat_id)
        new_status = "ᴅɪꜱᴧʙʟєᴅ"

    chat = await app.get_chat(chat_id)

    await query.message.edit_text(
        f"» ᴡєʟᴄᴏᴍє ᴍєꜱꜱᴧɢє **{new_status}** ɪη **{chat.title}** ʙʏ :- **{query.from_user.mention}**"
    )

    await query.answer()


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):

    chat_id = member.chat.id
    is_enabled = await get_welcome(chat_id)
    if not is_enabled:
        return

    user = member.new_chat_member.user if member.new_chat_member else None
    if not user:
        return

    if member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != "kicked":

        try:
            pic = await app.download_media(
                user.photo.big_file_id, file_name=f"pp{user.id}.png"
            )
        except:
            pic = "ShiviMusic/assets/upic.png"

        old = temp.MELCOW.get(f"welcome-{chat_id}")
        if old:
            try:
                await old.delete()
            except:
                pass

        welcomeimg = welcomepic(
            pic,
            user.first_name,
            member.chat.title,
            user.id,
            user.username
        )

        # Group ke total members
        try:
            members_count = await app.get_chat_members_count(chat_id)
        except Exception:
            members_count = " η/ᴧ"

        username = f"@{user.username}" if user.username else "η/ᴧ"

        caption_html = (
            f"<b>⏤͟͟͞͞★ ʜєʟʟᴏ ᴅєᴧʀ, ᴡєʟᴄᴏᴍє ᴛᴏ : {html.escape(member.chat.title or '')}</b>\n\n"
            "<b>🌸 ʀᴧᴅʜє ᴊᴧʏ ꜱʜʀєє ᴋʀɪꜱʜηᴧ 🌸</b>\n\n"
            "<blockquote expandable>"
            "<u><b>❖ υꜱєʀ ꜱʜᴏʀᴛ ɪηꜰᴏ</b></u>\n\n"
            f"<b>➻ ηᴧᴍє »</b> <a href=\"tg://user?id={user.id}\">{html.escape(user.first_name or 'User')}</a>\n"
            f"<b>➻ υꜱєʀ ɪᴅ »</b> <code>{user.id}</code>\n"
            f"<b>➻ υꜱєʀηᴧᴍє »</b> {html.escape(username)}\n"
            f"<b>➻ ᴛᴏᴛᴧʟ ᴍєᴍʙєʀꜱ »</b> <code>{members_count}</code>\n\n"
            "<b>➻ ᴘʟєᴧꜱє ʀєᴧᴅ ᴛʜє ɢʀᴏυᴘ ʀυʟєꜱ ᴧηᴅ ʙє ʀєꜱᴘєᴄᴛꜰυʟ ᴛᴏ єᴠєʀʏᴏηє 🤝\n"
            "➻ ʜᴧᴠє ꜰυη, ꜱʜᴧʀє ᴍυꜱɪᴄ ᴧηᴅ ᴍᴧᴋє ηєᴡ ꜰʀɪєηᴅꜱ 🎧\n"
            "➻ ᴛʜᴧηᴋꜱ ꜰᴏʀ ᴊᴏɪηɪηɢ υꜱ ⚡️~!</b>"
            "</blockquote>\n"
            "<b>🙏 ʀᴧᴅʜє ʀᴧᴅʜє 🙏\n"
            "❅─────✧❅✦❅✧─────❅</b>"
        )

        # Pehle blue button wala Bot API message try karo
        msg = None
        msg_id = await send_blue_photo(chat_id, welcomeimg, caption_html)

        if msg_id is None:
            # Fallback: normal pyrogram message
            msg = await app.send_photo(
                chat_id,
                photo=welcomeimg,
                caption=caption_html,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=add_me_button()
            )
            msg_id = msg.id

        class _Msg:
            async def delete(self_inner):
                await app.delete_messages(chat_id, msg_id)

        msg = _Msg()

        async def delete_welcome():
            await asyncio.sleep(120)
            try:
                await msg.delete()
                if f"welcome-{chat_id}" in temp.MELCOW:
                    del temp.MELCOW[f"welcome-{chat_id}"]
            except:
                pass

        asyncio.create_task(delete_welcome())
        temp.MELCOW[f"welcome-{chat_id}"] = msg


# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎

# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Sonali-MusicV2
# 📢 Telegram channel : t.me/Purvi_Bots
# =======================================================
