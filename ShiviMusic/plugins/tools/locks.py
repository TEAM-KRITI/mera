# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️
 
# 📩 DM for permission : @TheSigmaCoder
# =======================================================


from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from ShiviMusic import app
from ShiviMusic.core.mongo import mongodb
from pyrogram.errors import PeerIdInvalid
from config import OWNER_ID
import re
import asyncio

lockdb = mongodb.locks
warndb = mongodb.warnings
approveddb = mongodb.approvedusers

def smallcaps(text: str) -> str:
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    table = str.maketrans(normal, small)
    return text.translate(table)


async def add_approved_user(chat_id: int, user_id: int):
    await approveddb.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"approved": True}},
        upsert=True
    )

async def remove_approved_user(chat_id: int, user_id: int):
    await approveddb.delete_one({"chat_id": chat_id, "user_id": user_id})

async def is_user_approved(chat_id: int, user_id: int) -> bool:
    data = await approveddb.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(data)

async def get_all_approved(chat_id: int):
    cursor = approveddb.find({"chat_id": chat_id})
    return [doc["user_id"] async for doc in cursor]


async def get_locks(chat_id: int):
    data = await lockdb.find_one({"chat_id": chat_id})
    if not data:
        return {"admin_lock": False, "locked": []}
    return data

async def set_lock(chat_id: int, lock_type: str, status: bool):
    data = await get_locks(chat_id)
    locked = data.get("locked", [])
    if status and lock_type not in locked:
        locked.append(lock_type)
    elif not status and lock_type in locked:
        locked.remove(lock_type)
    await lockdb.update_one({"chat_id": chat_id}, {"$set": {"locked": locked}}, upsert=True)

async def set_adminlock(chat_id: int, status: bool):
    await lockdb.update_one({"chat_id": chat_id}, {"$set": {"admin_lock": status}}, upsert=True)

async def unlock_all(chat_id: int):
    await lockdb.update_one({"chat_id": chat_id}, {"$set": {"locked": [], "admin_lock": False}}, upsert=True)

async def get_warnings(chat_id: int, user_id: int):
    data = await warndb.find_one({"chat_id": chat_id, "user_id": user_id})
    return data.get("warns", 0) if data else 0

async def add_warning(chat_id: int, user_id: int):
    current_warns = await get_warnings(chat_id, user_id)
    new_warns = current_warns + 1
    await warndb.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"warns": new_warns}},
        upsert=True
    )
    return new_warns

async def clear_warnings(chat_id: int, user_id: int):
    await warndb.delete_one({"chat_id": chat_id, "user_id": user_id})

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def can_change_info(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status == ChatMemberStatus.OWNER:
            return True
        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            return member.privileges.can_change_info if member.privileges else False
        return False
    except:
        return False

async def can_restrict_members(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status == ChatMemberStatus.OWNER:
            return True
        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            return member.privileges.can_restrict_members if member.privileges else False
        return False
    except:
        return False

LOCKABLES = [
    "all", "audio", "bots", "button", "contact", "document", "egame", "forward", 
    "game", "gif", "info", "inline", "invite", "location", "media", "messages", 
    "other", "photo", "pin", "poll", "previews", "rtl", "sticker", "url", "username", "video", "voice"
]

def contains_url(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

def contains_invite_link(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r't\.me/joinchat/[a-zA-Z0-9_-]+',
        r't\.me/\+[a-zA-Z0-9_-]+',
        r'telegram\.me/joinchat/[a-zA-Z0-9_-]+',
        r'telegram\.me/\+[a-zA-Z0-9_-]+',
        r'tg://join\?invite=[a-zA-Z0-9_-]+',
        r'joinchat/[a-zA-Z0-9_-]+'
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

def contains_username(text: str) -> bool:
    if not text:
        return False
    pattern = r'@[a-zA-Z0-9_]{5,32}'
    return bool(re.search(pattern, text))

def has_username_entity(message: Message) -> bool:
    if not message.entities:
        return False
    return any(entity.type == "mention" for entity in message.entities)

def is_rtl_text(text: str) -> bool:
    if not text:
        return False
    rtl_chars = '\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF'
    return bool(re.search(f'[{rtl_chars}]', text))

def has_buttons(message: Message) -> bool:
    return bool(message.reply_markup and hasattr(message.reply_markup, 'inline_keyboard'))

def has_web_preview(message: Message) -> bool:
    return bool(message.web_page)

def get_premium_button_text(lock_type: str, is_locked: bool) -> str:
    icons = {
        "all": "🌐", "audio": "🎵", "bots": "🤖", "button": "🔘", "contact": "📞",
        "document": "📄", "egame": "🎮", "forward": "↗️", "game": "🎯", "gif": "🎭",
        "info": "ℹ️", "inline": "🔗", "invite": "📩", "location": "📍", "media": "📸",
        "messages": "💬", "other": "📦", "photo": "🖼️", "pin": "📌", "poll": "📊",
        "previews": "👁️", "rtl": "🔄", "sticker": "🎨", "url": "🌍", 
        "username": "👤", "video": "🎬", "voice": "🎙️"
    }
    icon = icons.get(lock_type, "🔒")
    status = "✅ ON" if is_locked else "❌ OFF"
    return f"{icon} {lock_type.upper()} {status}"

@app.on_message(filters.new_chat_members & filters.group, group=1)
async def handle_new_members(_, message: Message):
    try:
        data = await get_locks(message.chat.id)
        if "bots" not in data.get("locked", []):
            return
        adminlock = data.get("admin_lock", False)
        for new_member in message.new_chat_members:
            if not new_member.is_bot:
                continue
            adder = message.from_user
            if not adder:
                continue
            adder_is_admin = await is_admin(message.chat.id, adder.id)
            should_remove = False
            action_reason = ""
            if adminlock:
                should_remove = True
                action_reason = "Admin lock is ON - bots are completely locked"
            elif not adder_is_admin:
                should_remove = True
                action_reason = "Only admins can add bots when bot lock is active"
            if should_remove:
                try:
                    await app.ban_chat_member(message.chat.id, new_member.id)
                    await app.unban_chat_member(message.chat.id, new_member.id)
                    warns = await add_warning(message.chat.id, adder.id)
                    warning_msg = await app.send_message(
                        message.chat.id,
                        f"<b>🚫🤖 {smallcaps('bot addition blocked!')} 🤖🚫</b>\n\n"
                        f"👤 <b>User:</b> {adder.mention}\n"
                        f"🤖 <b>Bot:</b> {new_member.mention}\n"
                        f"⚠️ <b>Warnings:</b> {warns}/3\n"
                        f"📝 <b>Reason:</b> {action_reason}\n\n"
                        f"<i>💡 Bots are locked in this group!</i>"
                    )
                    if warns >= 3:
                        try:
                            await app.ban_chat_member(message.chat.id, adder.id)
                            ban_msg = await app.send_message(
                                message.chat.id,
                                f"<b>🔨 {smallcaps('user banned!')} 🔨</b>\n"
                                f"👤 {adder.mention} banned for repeatedly adding bots!"
                            )
                            await clear_warnings(message.chat.id, adder.id)
                            asyncio.create_task(delete_notification(ban_msg, 10))
                        except Exception as e:
                            pass
                    asyncio.create_task(delete_notification(warning_msg, 10))
                except Exception as e:
                    pass
    except Exception as e:
        pass

async def delete_notification(message: Message, delay: int):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        pass

@app.on_message(filters.command("lock") & filters.group)
async def lock_handler(_, message: Message):
    if not message.from_user:
        return
    if not await can_change_info(message.chat.id, message.from_user.id):
        return await message.reply_text(
            f"<b>🚫 {smallcaps('you need can_change_info permission to use locks!')}</b>"
        )
    if len(message.command) < 2:
        available_locks = "\n".join([f"• {lock}" for lock in LOCKABLES])
        return await message.reply_text(
            f"<b>🔒 {smallcaps('usage: /lock [type]')}</b>\n\n"
            f"<b>📋 {smallcaps('available locks:')}</b>\n{available_locks}"
        )
    lock_type = message.command[1].lower()
    if lock_type not in LOCKABLES:
        available_locks = "\n".join([f"• {lock}" for lock in LOCKABLES])
        return await message.reply_text(
            f"<b>❌ {smallcaps('invalid lock type!')}</b>\n\n"
            f"<b>📋 {smallcaps('available locks:')}</b>\n{available_locks}"
        )
    await set_lock(message.chat.id, lock_type, True)
    if lock_type == "bots":
        extra_info = f"\n<i>🤖 {smallcaps('bot additions are now blocked with auto-warn system!')}</i>"
    else:
        extra_info = ""
    await message.reply_text(
        f"<b>🔒✨ {smallcaps(lock_type + ' locked successfully!')}</b>{extra_info}"
    )

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_handler(_, message: Message):
    if not message.from_user:
        return
    if not await can_change_info(message.chat.id, message.from_user.id):
        return await message.reply_text(
            f"<b>🚫 {smallcaps('you need can_change_info permission to use locks!')}</b>"
        )
    if len(message.command) < 2:
        return await message.reply_text(f"<b>🔓 {smallcaps('usage: /unlock [type]')}</b>")
    lock_type = message.command[1].lower()
    if lock_type not in LOCKABLES:
        available_locks = "\n".join([f"• {lock}" for lock in LOCKABLES])
        return await message.reply_text(
            f"<b>❌ {smallcaps('invalid lock type!')}</b>\n\n"
            f"<b>📋 {smallcaps('available locks:')}</b>\n{available_locks}"
        )
    await set_lock(message.chat.id, lock_type, False)
    await message.reply_text(f"<b>🔓✨ {smallcaps(lock_type + ' unlocked successfully!')}</b>")

@app.on_message(filters.command("unlockall") & filters.group)
async def unlockall_handler(_, message: Message):
    if not message.from_user:
        return
    if not await can_change_info(message.chat.id, message.from_user.id):
        return await message.reply_text(
            f"<b>🚫 {smallcaps('you need can_change_info permission to use locks!')}</b>"
        )
    await unlock_all(message.chat.id)
    await message.reply_text(f"<b>🔓🌟 {smallcaps('all locks removed successfully!')}</b>")

@app.on_message(filters.command("locks") & filters.group)
async def locks_handler(_, message: Message):
    if not await can_change_info(message.chat.id, message.from_user.id):
        return await message.reply_text(
            f"<b>🚫 {smallcaps('you need can_change_info permission to use locks!')}</b>"
        )
    data = await get_locks(message.chat.id)
    locked = data.get("locked", [])
    buttons = []
    for i in range(0, len(LOCKABLES), 2):
        row = []
        for l in LOCKABLES[i:i+2]:
            is_locked = l in locked
            button_text = get_premium_button_text(l, is_locked)
            row.append(InlineKeyboardButton(button_text, callback_data=f"toggle_lock:{l}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔓🌟 UNLOCK ALL 🌟🔓", callback_data="unlock_all")])
    await message.reply_text(
        f"<b>🔒✨ {smallcaps('premium lock settings')} ✨🔒</b>\n"
        f"<i>🎯 {smallcaps('tap to toggle locks')} 🎯</i>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex("^toggle_lock"))
async def toggle_lock_callback(_, query: CallbackQuery):
    if not await can_change_info(query.message.chat.id, query.from_user.id):
        return await query.answer("🚫 You need can_change_info permission!", show_alert=True)
    lock_type = query.data.split(":")[1]
    data = await get_locks(query.message.chat.id)
    locked = data.get("locked", [])
    if lock_type in locked:
        await set_lock(query.message.chat.id, lock_type, False)
        await query.answer(f"🔓✨ {lock_type} unlocked!", show_alert=True)
    else:
        await set_lock(query.message.chat.id, lock_type, True)
        if lock_type == "bots":
            await query.answer(f"🔒✨ {lock_type} locked! Bot additions blocked!", show_alert=True)
        else:
            await query.answer(f"🔒✨ {lock_type} locked!", show_alert=True)
    data = await get_locks(query.message.chat.id)
    locked = data.get("locked", [])
    buttons = []
    for i in range(0, len(LOCKABLES), 2):
        row = []
        for l in LOCKABLES[i:i+2]:
            is_locked = l in locked
            button_text = get_premium_button_text(l, is_locked)
            row.append(InlineKeyboardButton(button_text, callback_data=f"toggle_lock:{l}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔓🌟 UNLOCK ALL 🌟🔓", callback_data="unlock_all")])
    await query.message.edit_text(
        f"<b>🔒✨ {smallcaps('premium lock settings')} ✨🔒</b>\n"
        f"<i>🎯 {smallcaps('tap to toggle locks')} 🎯</i>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_callback_query(filters.regex("^unlock_all"))
async def unlock_all_callback(_, query: CallbackQuery):
    if not await can_change_info(query.message.chat.id, query.from_user.id):
        return await query.answer("🚫 You need can_change_info permission!", show_alert=True)
    await unlock_all(query.message.chat.id)
    await query.answer("🔓🌟 All locks removed!", show_alert=True)
    buttons = []
    for i in range(0, len(LOCKABLES), 2):
        row = []
        for l in LOCKABLES[i:i+2]:
            button_text = get_premium_button_text(l, False)
            row.append(InlineKeyboardButton(button_text, callback_data=f"toggle_lock:{l}"))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔓🌟 UNLOCK ALL 🌟🔓", callback_data="unlock_all")])
    await query.message.edit_text(
        f"<b>🔒✨ {smallcaps('premium lock settings')} ✨🔒</b>\n"
        f"<i>🎯 {smallcaps('tap to toggle locks')} 🎯</i>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

@app.on_message(filters.command("lockadmin") & filters.group)
async def lockadmin_handler(_, message: Message):
    if not await can_change_info(message.chat.id, message.from_user.id):
        return await message.reply_text(
            f"<b>🚫 {smallcaps('you need can_change_info permission!')}</b>"
        )
    if len(message.command) < 2:
        return await message.reply_text(f"<b>⚙️ {smallcaps('usage: /lockadmin [on|off]')}</b>")
    arg = message.command[1].lower()
    if arg == "on":
        await set_adminlock(message.chat.id, True)
        await message.reply_text(
            f"<b>🔒👑 {smallcaps('lockadmin enabled!')}</b>\n"
            f"<i>🚫 {smallcaps('admins are also restricted now!')}</i>"
        )
    elif arg == "off":
        await set_adminlock(message.chat.id, False)
        await message.reply_text(
            f"<b>🔓👑 {smallcaps('lockadmin disabled!')}</b>\n"
            f"<i>✅ {smallcaps('admins are ignored from locks!')}</i>"
        )
    else:
        await message.reply_text(f"<b>⚙️ {smallcaps('usage: /lockadmin [on|off]')}</b>")

@app.on_message(filters.command("locktypes") & filters.group)
async def locktypes_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("<b>🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴠɪᴇᴡ ʟᴏᴄᴋ ᴛʏᴘᴇs!</b>")

    text = "<b>🔒✨ ᴀᴠᴀɪʟᴀʙʟᴇ ʟᴏᴄᴋ ᴛʏᴘᴇs ✨🔒</b>\n\n"

    descriptions = {
        "ᴀʟʟ": "<b>ʙʟᴏᴄᴋs ᴀʟʟ ᴍᴇssᴀɢᴇs</b>",
        "ᴀᴜɪᴅᴏ": "<b>ʙʟᴏᴄᴋs ᴀᴜᴅɪᴏ ꜰɪʟᴇs</b>",
        "ʙᴏᴛs": "<b>ʙʟᴏᴄᴋs ʙᴏᴛ ᴀᴅᴅɪᴛɪᴏɴs & ʀᴇᴍᴏᴠᴇs ᴛʜᴇᴍ ᴡɪᴛʜ ᴡᴀʀɴɪɴɢs</b>",
        "ʙᴜᴛᴛᴏɴ": "<b>ʙʟᴏᴄᴋs ᴍᴇssᴀɢᴇs ᴡɪᴛʜ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴs</b>",
        "ᴄᴏɴᴛᴀᴄᴛ": "<b>ʙʟᴏᴄᴋs ᴄᴏɴᴛᴀᴄᴛ sʜᴀʀɪɴɢ</b>",
        "ᴅᴏᴄᴜᴍᴇɴᴛ": "<b>ʙʟᴏᴄᴋs ᴅᴏᴄᴜᴍᴇɴᴛ ꜰɪʟᴇs</b>",
        "ᴇɢᴀᴍᴇ": "<b>ʙʟᴏᴄᴋs ᴇᴍʙᴇᴅᴅᴇᴅ ɢᴀᴍᴇs</b>",
        "ғᴏʀᴡᴀʀᴅᴇᴅ": "<b>ʙʟᴏᴄᴋs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇssᴀɢᴇs</b>",
        "ɢᴀᴍᴇ": "<b>ʙʟᴏᴄᴋs ɢᴀᴍᴇs</b>",
        "ɢɪғ": "<b>ʙʟᴏᴄᴋs ɢɪꜰ ᴀɴɪᴍᴀᴛɪᴏɴs</b>",
        "ɪɴғᴏ": "<b>ʙʟᴏᴄᴋs sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs</b>",
        "ɪɴʟɪɴᴇ": "<b>ʙʟᴏᴄᴋs ɪɴʟɪɴᴇ ʙᴏᴛ ʀᴇsᴜʟᴛs</b>",
        "ɪɴᴠɪᴛᴇ": "<b>ʙʟᴏᴄᴋs ɪɴᴠɪᴛᴇ ʟɪɴᴋs</b>",
        "ʟᴏᴄᴛᴀɪᴏɴ": "<b>ʙʟᴏᴄᴋs ʟᴏᴄᴀᴛɪᴏɴ/ᴠᴇɴᴜᴇ sʜᴀʀɪɴɢ</b>",
        "ᴍᴇᴅɪᴀ": "<b>ʙʟᴏᴄᴋs ᴀʟʟ ᴍᴇᴅɪᴀ ᴛʏᴘᴇs</b>",
        "ᴍᴇssᴀɢᴇ": "<b>ʙʟᴏᴄᴋs ᴛᴇxᴛ ᴍᴇssᴀɢᴇs</b>",
        "ᴏᴛʜᴇʀ": "<b>ʙʟᴏᴄᴋs ᴏᴛʜᴇʀ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇs</b>",
        "ᴘʜᴏᴛᴏ": "<b>ʙʟᴏᴄᴋs ᴘʜᴏᴛᴏs/ɪᴍᴀɢᴇs</b>",
        "ᴘɪɴ": "<b>ʙʟᴏᴄᴋs ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs</b>",
        "ᴘᴏʟʟ": "<b>ʙʟᴏᴄᴋs ᴘᴏʟʟs</b>",
        "ᴘʀᴇᴠɪᴡᴇs": "<b>ʙʟᴏᴄᴋs ʟɪɴᴋ ᴘʀᴇᴠɪᴇᴡs</b>",
        "ʀᴛʟ": "<b>ʙʟᴏᴄᴋs ʀᴛʟ ᴛᴇxᴛ</b>",
        "sᴛɪᴄᴋᴇʀ": "<b>ʙʟᴏᴄᴋs sᴛɪᴄᴋᴇʀs</b>",
        "ᴜʀʟ": "<b>ʙʟᴏᴄᴋs ᴜʀʟs/ʟɪɴᴋs</b>",
        "ᴜsᴇʀɴᴀᴍᴇ": "<b>ʙʟᴏᴄᴋs ᴜsᴇʀɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴs (@username)</b>",
        "ᴠɪᴅᴇᴏs": "<b>ʙʟᴏᴄᴋs ᴠɪᴅᴇᴏs</b>",
        "ᴠᴏɪᴄᴇ": "<b>ʙʟᴏᴄᴋs ᴠᴏɪᴄᴇ ᴍᴇssᴀɢᴇs</b>"
    }

    icons = {
        "all": "🌐", "audio": "🎵", "bots": "🤖", "button": "🔘",
        "contact": "📞", "document": "📄", "egame": "🎮", "forward": "↗️",
        "game": "🎯", "gif": "🎭", "info": "ℹ️", "inline": "🔗",
        "invite": "📩", "location": "📍", "media": "📸", "messages": "💬",
        "other": "📦", "photo": "🖼️", "pin": "📌", "poll": "📊",
        "previews": "👁️", "rtl": "🔄", "sticker": "🎨", "url": "🌍",
        "username": "👤", "video": "🎬", "voice": "🎙️"
    }

    for lock_type in LOCKABLES:
        desc = descriptions.get(lock_type, "<b>sᴘᴇᴄɪᴀʟ ʟᴏᴄᴋ ᴛʏᴘᴇ</b>")
        icon = icons.get(lock_type, "🔒")
        text += f"{icon} <code>{lock_type}</code> - {desc}\n"

    text += "\n<b>💡 ᴜsᴀɢᴇ :</b> <code>/lock [ᴛʏᴘᴇ]</code> ᴏʀ <code>/unlock [ᴛʏᴘᴇ]</code>"
    text += "\n<b>⚡ ǫᴜɪᴄᴋ :</b> <code>/unlockall</code> ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀʟʟ ʟᴏᴄᴋs"
    text += "\n<b>🔧 ᴘᴇʀᴍɪssɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ :</b> ᴄᴀɴ ᴄʜᴀɴɢᴇ ɪɴꜰᴏ"
    text += "\n\n<b>🤖 ʙᴏᴛ ʟᴏᴄᴋ :</b> ᴘʀᴇᴠᴇɴᴛs ʙᴏᴛ ᴀᴅᴅɪᴛɪᴏɴs ᴡɪᴛʜ ᴀᴜᴛᴏ-ᴡᴀʀɴ/ʙᴀɴ sʏsᴛᴇᴍ!"

    await message.reply_text(text)

@app.on_message(filters.command("clearwarns") & filters.group)
async def clearwarns_handler(_, message: Message):
    if not await can_restrict_members(message.chat.id, message.from_user.id):
        return await message.reply_text("<b>🚫 ʏᴏᴜ ɴᴇᴇᴅ ʀᴇsᴛʀɪᴄᴛ ᴍᴇᴍʙᴇʀs ᴘᴇʀᴍɪssɪᴏɴ!</b>")
    
    if not message.reply_to_message:
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ᴄʟᴇᴀʀ ᴛʜᴇɪʀ ᴡᴀʀɴɪɴɢs!</b>")
    
    user = message.reply_to_message.from_user
    if not user:
        return
    
    await clear_warnings(message.chat.id, user.id)
    await message.reply_text(f"<b>✅ ᴡᴀʀɴɪɴɢs ᴄʟᴇᴀʀᴇᴅ ꜰᴏʀ {user.mention}!</b>")


@app.on_message(filters.command("lockwarns") & filters.group)
async def lockwarns_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("<b>🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʜᴇᴄᴋ ʟᴏᴄᴋ ᴡᴀʀɴɪɴɢs!</b>")
    
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await app.get_users(message.command[1])
        except:
            return await message.reply_text("<b>❌ ᴜsᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ!</b>")
    else:
        return await message.reply_text("<b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>")
    
    if not user:
        return
    
    warns = await get_warnings(message.chat.id, user.id)

    await message.reply_text(
        f"<b>🤖 ʟᴏᴄᴋ ᴡᴀʀɴɪɴɢs ꜰᴏʀ {user.mention}</b>\n"
        f"<b>ᴄᴜʀʀᴇɴᴛ :</b> {warns}/3\n"
        f"<b>{'⚠️ ᴄʟᴏsᴇ ᴛᴏ ʙᴀɴ!' if warns >= 2 else '✅ sᴀꜰᴇ'}</b>\n"
        f"<i>💡 ᴛʜᴇsᴇ ᴡᴀʀɴɪɴɢs ᴀʀᴇ ꜰᴏʀ ʙᴏᴛ ᴀᴅᴅɪᴛɪᴏɴ ᴀᴛᴛᴇᴍᴘᴛs</i>"
    )

@app.on_message(filters.group, group=4)
async def lock_detector(_, message: Message):
    try:
        data = await get_locks(message.chat.id)
        locked = data.get("locked", [])
        adminlock = data.get("admin_lock", False)

        if not locked:
            return

        user_id = message.from_user.id if message.from_user else None

        if user_id == OWNER_ID:
            return

        if await is_user_approved(message.chat.id, user_id):
            return

        isadmin = await is_admin(message.chat.id, user_id) if user_id else False
        if isadmin and not adminlock:
            return

        delete = False
        reason = None
        text_content = message.text or message.caption or ""

        
        if "all" in locked:
            delete, reason = True, "all content"

        elif "messages" in locked and message.text:
            delete, reason = True, "text messages"

        elif "media" in locked and (
            message.photo or message.video or message.audio or
            message.voice or message.document or message.sticker or 
            message.animation
        ):
            delete, reason = True, "media content"

        elif "photo" in locked and message.photo:
            delete, reason = True, "photos"

        elif "video" in locked and message.video:
            delete, reason = True, "videos"

        elif "audio" in locked and message.audio:
            delete, reason = True, "audio files"

        elif "voice" in locked and message.voice:
            delete, reason = True, "voice messages"

        elif "document" in locked and message.document:
            delete, reason = True, "documents"

        elif "sticker" in locked and message.sticker:
            delete, reason = True, "stickers"

        elif "gif" in locked and message.animation:
            delete, reason = True, "GIFs"

        elif "url" in locked and contains_url(text_content):
            delete, reason = True, "URLs"

        elif "username" in locked and contains_username(text_content):
            delete, reason = True, "username mention"

        elif "invite" in locked and contains_invite_link(text_content):
            delete, reason = True, "invite link"

        elif "forward" in locked and (message.forward_from or message.forward_from_chat):
            delete, reason = True, "forwarded messages"

        elif "inline" in locked and message.via_bot:
            delete, reason = True, "inline bot result"

        elif "bots" in locked and message.via_bot:
            delete, reason = True, "bot message"

        elif "button" in locked and has_buttons(message):
            delete, reason = True, "inline buttons"

        elif "game" in locked and message.game:
            delete, reason = True, "games"

        elif "egame" in locked and message.game:
            delete, reason = True, "embedded games"

        elif "poll" in locked and message.poll:
            delete, reason = True, "polls"

        elif "location" in locked and (message.location or message.venue):
            delete, reason = True, "location"

        elif "contact" in locked and message.contact:
            delete, reason = True, "contact"

        elif "rtl" in locked and is_rtl_text(text_content):
            delete, reason = True, "RTL text"

        elif "previews" in locked and has_web_preview(message):
            delete, reason = True, "link previews"

        elif "info" in locked and message.service:
            delete, reason = True, "service messages"

        elif "pin" in locked and message.service and hasattr(message.service, "pinned_message"):
            delete, reason = True, "pinned messages"

        elif "other" in locked and not any([
            message.text, message.photo, message.video, message.audio,
            message.voice, message.document, message.sticker, message.animation
        ]):
            delete, reason = True, "other content"

        
        if delete and reason:
            try:
                await message.delete()

                if message.from_user:
                    user_mention = (
                        message.from_user.mention or
                        f"@{message.from_user.username}" or
                        message.from_user.first_name
                    )

                    notification = await app.send_message(
                        message.chat.id,
                        f"<b>🚫✨ {smallcaps(reason + ' are locked!')}</b>\n"
                        f"👤 {user_mention} {smallcaps('tried to send locked content.')}",
                    )

                    asyncio.create_task(delete_notification(notification, 5))

            except Exception:
                pass

    except Exception:
        pass


@app.on_message(filters.command("approve") & filters.group)
async def approve_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("🚫 **ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ ᴜꜱᴇʀꜱ !!**")


    if message.reply_to_message: 
        user = message.reply_to_message.from_user 
    
    elif len(message.command) > 1: 
        try: 
            user = await app.get_users(message.command[1]) 
        except: 
            return await message.reply_text("**❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ᴜꜱᴇʀ ɪᴅ !!**") 
    else: 
        return await message.reply_text("**» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇ :-** `/approve ᴜꜱᴇʀɴᴀᴍᴇ_ᴏʀ_ɪᴅ`") 
    await add_approved_user(message.chat.id, user.id) 
    await message.reply_text( 
        f"**✅ ᴀᴘᴘʀᴏᴠᴇᴅ {user.mention}**\n\n**» ɴᴏᴡ ʟᴏᴄᴋꜱ ᴡɪʟʟ ɴᴏᴛ ᴀꜰꜰᴇᴄᴛ ᴛʜᴇᴍ !!**" 
    ) 

@app.on_message(filters.command("unapprove") & filters.group)
async def unapprove_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("**🚫 ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴜꜱᴇʀꜱ !!**")

    
    if message.reply_to_message: 
        user = message.reply_to_message.from_user 
    
    elif len(message.command) > 1: 
        try: 
            user = await app.get_users(message.command[1]) 
        except: 
            return await message.reply_text("**❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ᴜꜱᴇʀ ɪᴅ !!**") 
    else: 
        return await message.reply_text("**» ʀᴇᴘʟʏ ᴏʀ ᴜꜱᴇ :-**`/unapprove ᴜꜱᴇʀɴᴀᴍᴇ_ᴏʀ_ɪᴅ`") 
    await remove_approved_user(message.chat.id, user.id) 
    await message.reply_text( 
        f"**❌ ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ {user.mention}**\n\n**» ɴᴏᴡ ʟᴏᴄᴋꜱ ᴡɪʟʟ ᴀᴘᴘʟʏ !!**" 
    ) 

@app.on_message(filters.command("approvedusers") & filters.group)
async def approved_users_handler(_, message: Message):
    try:
        users = await get_all_approved(message.chat.id)

        if not users: 
            return await message.reply_text("**» ɴᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀꜱ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**") 
        
        text = "<b>🟢 ᴀᴘᴘʀᴏᴠᴇᴅ ᴜꜱᴇʀꜱ :</b>\n\n" 
        
        for uid in users: 
            try:
                u = await app.get_users(uid)
                first_name = u.first_name or ""
                last_name = u.last_name or ""
                full_name = f"{first_name} {last_name}".strip()
                username = f"(@{u.username})" if u.username else ""
                text += f"• {full_name} [{uid}] {username}\n"
            except PeerIdInvalid:
                text += f"• ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ [{uid}]\n"
                
        await message.reply_text(text) 
        
    except Exception as e:
        await message.reply_text("**❌ ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs.**")
        print(f"Error in approved_users_handler: {e}")

@app.on_message(filters.command("allunapprove") & filters.group)
async def all_unapprove_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("**🚫 ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ !!**")

    await approveddb.delete_many({"chat_id": message.chat.id}) 
    await message.reply_text("**» ᴀʟʟ ᴜꜱᴇʀꜱ ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ !!**") 
    
# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎

# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Sonali-MusicV2
# 📢 Telegram channel : t.me/Purvi_Bots
# =======================================================
