# ===========================================================
# Auto Assistant Leave
# Jab bot kisi group/channel se remove (kick/ban/left) ho jaye,
# to assistant ID bhi us chat se khud leave ho jayegi.
# ===========================================================

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import ChatMemberUpdated, Message

import config
from ShiviMusic import app
from ShiviMusic.core.call import Shivi
from ShiviMusic.logging import LOGGER
from ShiviMusic.utils.database import (
    _get_valid_assistants,
    assdb,
    assistantdict,
    get_client,
)

# Same chat ke liye dobara trigger na ho (dono handlers ek saath fire ho sakte hain)
_processing = set()

_REMOVED = (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)


async def _assistants_for_chat(chat_id: int):
    """Is chat me jo assistant use ho raha tha uska number (bina naya assign kiye)."""
    number = assistantdict.get(chat_id)

    if number is None:
        doc = await assdb.find_one({"chat_id": chat_id})
        if doc:
            number = doc.get("assistant")

    try:
        number = int(number)
    except (TypeError, ValueError):
        number = None

    valid = await _get_valid_assistants()

    if number in valid:
        return [number]

    # Mapping nahi mili to sab started assistants try karo
    return valid


async def assistant_leave_chat(chat_id: int):
    if chat_id in _processing:
        return
    if chat_id == config.LOGGER_ID:
        return

    _processing.add(chat_id)

    try:
        # 1) Stream/queue/VC band karo
        try:
            await Shivi.stop_stream_force(chat_id)
        except Exception:
            pass

        # 2) Assistant ko chat se leave karao
        for number in await _assistants_for_chat(chat_id):
            client = await get_client(number)
            if client is None:
                continue

            try:
                await client.leave_chat(chat_id)
                LOGGER(__name__).info(
                    f"Assistant {number} left chat {chat_id} (bot removed)"
                )
            except FloodWait as e:
                await asyncio.sleep(int(e.value))
                try:
                    await client.leave_chat(chat_id)
                except Exception:
                    pass
            except Exception:
                # Assistant us chat me tha hi nahi / pehle se leave kar chuka
                pass

        # 3) Purana assistant mapping hata do (dobara add hone par fresh assign hoga)
        assistantdict.pop(chat_id, None)
        try:
            await assdb.delete_one({"chat_id": chat_id})
        except Exception:
            pass

    finally:
        _processing.discard(chat_id)


# Handler 1: bot ka status change (kick / ban / left) - group channels me bhi kaam karta hai
@app.on_chat_member_updated(group=7)
async def bot_removed_update(_, update: ChatMemberUpdated):
    try:
        if update.chat.type not in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
            ChatType.CHANNEL,
        ):
            return

        old = update.old_chat_member
        new = update.new_chat_member

        # Sirf bot ka apna status
        member = new or old
        if not member or not member.user or member.user.id != app.me.id:
            return

        # Bot pehle chat me tha aur ab nahi hai
        was_in = old is not None and old.status not in _REMOVED
        now_out = new is None or new.status in _REMOVED

        if was_in and now_out:
            await assistant_leave_chat(update.chat.id)

    except Exception as e:
        LOGGER(__name__).warning(f"assistant_leave (member update) error: {e}")


# Handler 2: fallback - "bot left" service message
@app.on_message(filters.left_chat_member, group=7)
async def bot_removed_message(_, message: Message):
    try:
        left = message.left_chat_member
        if not left or left.id != app.me.id:
            return

        await assistant_leave_chat(message.chat.id)

    except Exception as e:
        LOGGER(__name__).warning(f"assistant_leave (message) error: {e}")
