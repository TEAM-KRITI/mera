import asyncio
import inspect
import random
import time

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from ShiviMusic import app
from ShiviMusic.core.mongo import mongodb
from ShiviMusic.utils.database import get_served_users, get_served_chats
from config import OWNER_ID

IMAGE_URL = "https://yukiapi.site/file/dDRjJyef"
INTERVAL = 24 * 60 * 60  # 24 hours

_state = mongodb.auto_broadcast_state
_lock = asyncio.Lock()

_SUPPORTS_STYLE = "style" in inspect.signature(
    InlineKeyboardButton.__init__
).parameters

# primary = blue, success = green, danger = red
_COLORS = ["primary", "success", "danger"]


def _btn(text: str, **kwargs) -> InlineKeyboardButton:
    """InlineKeyboardButton with a random colour every time."""
    style = random.choice(_COLORS)

    if _SUPPORTS_STYLE:
        return InlineKeyboardButton(text=text, style=style, **kwargs)

    btn = InlineKeyboardButton(text=text, **kwargs)
    try:
        setattr(btn, "style", style)
    except Exception:
        pass
    return btn


MESSAGES = f"""**๏ ᴛʜɪꜱ ɪꜱ <u>{app.mention}</u>

➻ ᴀ ꜰᴀꜱᴛ & ᴘᴏᴡєʀꜰᴜʟ ᴛєʟєɢʀᴀᴍ ᴍᴜꜱɪᴄ ᴘʟᴀʏєʀ ʙᴏᴛ 🎧

▸ ꜰᴀꜱᴛ • ʟᴀɢ ꜰʀєє • ɴᴏ ᴀᴅꜱ 🍃
▸ ᴘʟᴀʏʟɪꜱᴛ, ᴀᴜᴅɪᴏ, ᴠɪᴅєᴏ ᴘʟᴀʏ 🎥
▸ ᴀᴜᴛᴏᴘʟᴀʏ • ɴᴏɴ-ꜱᴛᴏᴘ ᴍᴜꜱɪᴄ 🔁

➻ ᴛᴀᴘ /start ᴛᴏ єxᴘʟᴏʀє ✨

────────────────────**"""


def get_buttons():
    return InlineKeyboardMarkup(
        [
            [
                _btn(
                    "⊚ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊚",
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ],
        ]
    )


async def _get_last_run() -> float:
    doc = await _state.find_one({"_id": "auto"})
    return doc.get("last_run", 0) if doc else 0


async def _set_last_run(ts: float):
    await _state.update_one(
        {"_id": "auto"}, {"$set": {"last_run": ts}}, upsert=True
    )


def _unique_ids(items, key):
    """Duplicate ids hata deta hai (order same rehta hai)."""
    ids = []
    for item in items:
        try:
            ids.append(int(item[key]))
        except Exception:
            continue
    return list(dict.fromkeys(ids))


async def _send(chat_id: int) -> bool:
    for _ in range(2):
        try:
            await app.send_photo(
                chat_id,
                photo=IMAGE_URL,
                has_spoiler=True,
                caption=MESSAGES,
                reply_markup=get_buttons(),
            )
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            return False
    return False


async def send_broadcast():
    users = _unique_ids(await get_served_users(), "user_id")
    chats = _unique_ids(await get_served_chats(), "chat_id")

    # Ek id dono list me ho to bhi sirf ek baar jayega
    user_set = set(users)
    chats = [c for c in chats if c not in user_set]

    users_sent = 0
    chats_sent = 0

    for user_id in users:
        if await _send(user_id):
            users_sent += 1
        await asyncio.sleep(3)

    for chat_id in chats:
        if await _send(chat_id):
            chats_sent += 1
        await asyncio.sleep(3)

    buttons = InlineKeyboardMarkup(
        [[_btn("ᴄʟᴏꜱᴇ", callback_data="close")]]
    )

    text = f"""**<u>✅ ᴀᴜᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ</u>**

**👤 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ :** `{len(users)}`
**✅ ᴜꜱᴇʀꜱ ꜱᴇɴᴛ :** `{users_sent}`

**👥 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘꜱ :** `{len(chats)}`
**✅ ɢʀᴏᴜᴘꜱ ꜱᴇɴᴛ :** `{chats_sent}`
"""

    msg = await app.send_message(OWNER_ID, text, reply_markup=buttons)

    try:
        await msg.pin()
    except Exception:
        pass


async def auto_broadcast():
    await asyncio.sleep(30)

    while True:
        try:
            async with _lock:
                last_run = await _get_last_run()
                now = time.time()

                if now - last_run >= INTERVAL:
                    # Pehle hi time save, taaki crash/restart pe dobara na jaye
                    await _set_last_run(now)
                    await send_broadcast()
        except Exception as e:
            print(e)

        # Har 60 sec me check, 24h poore hone par hi broadcast
        await asyncio.sleep(60)


# Module dobara load ho to duplicate task na bane
if not globals().get("_AUTO_BC_STARTED"):
    _AUTO_BC_STARTED = True
    asyncio.get_event_loop().create_task(auto_broadcast())
