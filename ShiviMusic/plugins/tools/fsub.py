from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions,
    ChatMemberUpdated,
)
from pymongo import MongoClient
from ShiviMusic import app
import asyncio
from ShiviMusic.misc import SUDOERS
from config import MONGO_DB_URI
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserNotParticipant,
    MessageDeleteForbidden,
    MessageIdInvalid,
)

# ── DB ──────────────────────────────────────────────────────────────────────
fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

# ── Anti-spam store: tracks last warning per (chat_id, user_id) ──────────────
# { (chat_id, user_id): { "msg": Message, "task": asyncio.Task } }
_last_warn: dict = {}


# ── Safely delete a message (ignore errors) ──────────────────────────────────
async def _safe_delete(msg: Message):
    try:
        await msg.delete()
    except (MessageDeleteForbidden, MessageIdInvalid, Exception):
        pass


# ── Simple delayed delete (for non-warning bot replies) ──────────────────────
async def _delete_after(msg: Message, delay: int = 30):
    await asyncio.sleep(delay)
    await _safe_delete(msg)


# ── Send warning — replaces previous warning for same user ───────────────────
async def _send_warn(chat_id: int, user_id: int, send_fn):
    """
    send_fn: async callable → returns sent Message
    Behaviour:
      - If user already has a pending warning → cancel its timer, delete it
      - Send new warning
      - Start fresh 30s auto-delete timer
    """
    key = (chat_id, user_id)

    # Kill old warning
    if key in _last_warn:
        old = _last_warn.pop(key)
        old["task"].cancel()
        asyncio.create_task(_safe_delete(old["msg"]))

    # Send new warning
    new_msg = await send_fn()

    # Auto-delete after 30s and clean up store
    async def _auto():
        await asyncio.sleep(30)
        await _safe_delete(new_msg)
        _last_warn.pop(key, None)

    task = asyncio.create_task(_auto())
    _last_warn[key] = {"msg": new_msg, "task": task}


# ── /fsub command ────────────────────────────────────────────────────────────
@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return

    is_admin = member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    if not (is_admin or user_id in SUDOERS):
        sent = await message.reply_text(
            "⚠️ **ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴏʀ sᴜᴅᴏᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**"
        )
        asyncio.create_task(_delete_after(sent, 30))
        return

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        sent = await message.reply_text(
            "✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**"
        )
        asyncio.create_task(_delete_after(sent, 30))
        return

    if len(message.command) != 2:
        sent = await message.reply_text(
            "ℹ️ **ᴜsᴀɢᴇ:**\n"
            "`/fsub <channel username or id>` — sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ\n"
            "`/fsub off` — ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ"
        )
        asyncio.create_task(_delete_after(sent, 30))
        return

    channel_input = message.command[1]
    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_username = channel_info.username or None

        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True,
        )

        link = f"https://t.me/{channel_username}" if channel_username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ"
        sent = await message.reply_text(
            f"🎉 **ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛ!**\n\n"
            f"ᴄʜᴀɴɴᴇʟ: [{channel_info.title}]({link})\n"
            f"ᴜsᴇʀs ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ʙᴇғᴏʀᴇ sᴇɴᴅɪɴɢ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.",
            disable_web_page_preview=True,
        )
        asyncio.create_task(_delete_after(sent, 30))

    except Exception:
        sent = await message.reply_text(
            "🚫 **ғᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.**\n"
            "ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴅᴇᴅ ᴀs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ."
        )
        asyncio.create_task(_delete_after(sent, 30))


# ── User joins group → check channel membership ──────────────────────────────
@app.on_chat_member_updated()
async def on_user_join(client: Client, update: ChatMemberUpdated):
    chat_id = update.chat.id
    new = update.new_chat_member
    old = update.old_chat_member
    if new is None:
        return

    user_joined = (
        new.status == ChatMemberStatus.MEMBER
        and (old is None or old.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED])
    )
    if not user_joined:
        return

    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data.get("channel_username")
    channel_url = f"https://t.me/{channel_username}" if channel_username else None

    user = update.from_user
    if user is None:
        return
    user_id = user.id

    try:
        await app.get_chat_member(channel_id, user_id)
        return  # already in channel

    except UserNotParticipant:
        try:
            await client.restrict_chat_member(
                chat_id, user_id,
                permissions=ChatPermissions(can_send_messages=False),
            )
        except Exception:
            pass

        if not channel_url:
            try:
                channel_url = await app.export_chat_invite_link(channel_id)
            except Exception:
                channel_url = "https://t.me"

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=channel_url)]]
        )

        async def _send():
            return await client.send_message(
                chat_id,
                f"👋 **ʜᴇʟʟᴏ {user.mention}!**\n\n"
                f"🔒 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ **ᴍᴜᴛᴇᴅ** ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ ʏᴇᴛ.\n\n"
                f"✅ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ʙᴇʟᴏᴡ ᴀɴᴅ ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴜɴᴍᴜᴛᴇᴅ.\n\n"
                f"⏳ _ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ 30 sᴇᴄᴏɴᴅs._",
                reply_markup=markup,
                disable_web_page_preview=True,
            )

        await _send_warn(chat_id, user_id, _send)

    except Exception as e:
        print(f"[ForceSub] Error on join check: {e}")


# ── Per-message check ─────────────────────────────────────────────────────────
async def check_forcesub(client: Client, message: Message) -> bool:
    chat_id = message.chat.id

    if message.from_user is None:
        return True

    user_id = message.from_user.id

    if user_id in SUDOERS:
        return True

    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return True

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data.get("channel_username")

    try:
        await app.get_chat_member(channel_id, user_id)

        # User is now in channel — unmute if restricted
        try:
            chat_member = await client.get_chat_member(chat_id, user_id)
            if not chat_member.permissions or not chat_member.permissions.can_send_messages:
                await client.restrict_chat_member(
                    chat_id, user_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    ),
                )
        except Exception:
            pass

        # User joined channel → clear their pending warning immediately
        key = (chat_id, user_id)
        if key in _last_warn:
            old = _last_warn.pop(key)
            old["task"].cancel()
            asyncio.create_task(_safe_delete(old["msg"]))

        return True

    except UserNotParticipant:
        # Delete the user's message
        try:
            await message.delete()
        except Exception:
            pass

        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
        else:
            try:
                channel_url = await app.export_chat_invite_link(channel_id)
            except Exception:
                channel_url = "https://t.me"

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=channel_url)]]
        )
        mention = message.from_user.mention

        # Capture for closure
        _channel_url = channel_url
        _markup = markup

        async def _send():
            return await client.send_message(
                chat_id,
                f"🔒 **{mention}**, ʏᴏᴜ ᴄᴀɴɴᴏᴛ sᴇɴᴅ ᴍᴇssᴀɢᴇs ʜᴇʀᴇ!\n\n"
                f"👉 ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({_channel_url}) ғɪʀsᴛ ᴛᴏ ɢᴀɪɴ ᴀᴄᴄᴇss.\n\n"
                f"⏳ _ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ 30 sᴇᴄᴏɴᴅs._",
                reply_markup=_markup,
                disable_web_page_preview=True,
            )

        await _send_warn(chat_id, user_id, _send)
        return False

    except ChatAdminRequired:
        forcesub_collection.delete_one({"chat_id": chat_id})
        sent = await client.send_message(
            chat_id,
            "⚠️ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅɪsᴀʙʟᴇᴅ.**\n"
            "ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ."
        )
        asyncio.create_task(_delete_after(sent, 30))
        return True

    except Exception as e:
        print(f"[ForceSub] check_forcesub error: {e}")
        return True


# ── Group message handler ─────────────────────────────────────────────────────
@app.on_message(filters.group, group=30)
async def enforce_forcesub(client: Client, message: Message):
    await check_forcesub(client, message)


# ── Close button callback ─────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("ᴄʟᴏsᴇᴅ!")
    await callback_query.message.delete()


# ── Help metadata ─────────────────────────────────────────────────────────────
__MODULE__ = "ғsᴜʙ"
__HELP__ = """
**ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ**

`/fsub <channel username or id>` — sᴇᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴀs ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.
`/fsub off` — ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.

• ᴜsᴇʀs ᴡʜᴏ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴡɪʟʟ ʙᴇ ᴍᴜᴛᴇᴅ.
• ᴡᴀʀɴɪɴɢ ᴍᴇssᴀɢᴇs ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ 30 sᴇᴄᴏɴᴅs.
• sᴘᴀᴍ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ: ᴏɴʟʏ 1 ᴡᴀʀɴɪɴɢ ᴘᴇʀ ᴜsᴇʀ ᴀᴛ ᴀ ᴛɪᴍᴇ — ᴏʟᴅ ᴏɴᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡʜᴇɴ ɴᴇᴡ ᴀʀʀɪᴠᴇs.
"""
