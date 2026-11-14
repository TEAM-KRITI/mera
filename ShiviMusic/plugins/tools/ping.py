# -----------------------------------------------
# 🔸 VampireMusic Project
# 🔹 Developed & Maintained by: Vampire Bots (https://github.com/TEAM-VAMPIRE-OP)
# 📅 Copyright © 2025 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by TEAM-VAMPIRE-OP
# -----------------------------------------------

import random
import time
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from ShiviMusic import app
from ShiviMusic.core.call import Shivi
from ShiviMusic.utils import bot_sys_stats
from ShiviMusic.utils.decorators.language import language
from ShiviMusic.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL

Shivi_PIC = [
    "https://n.uguu.se/COCvZVmH.jpg",
    "https://n.uguu.se/sUnCjERi.jpg",
    "https://h.uguu.se/UFespaut.jpg",
    "https://n.uguu.se/JQCcgtmE.jpg",
    "https://d.uguu.se/SDjTEpEk.jpg",
    "https://n.uguu.se/FzOLVSlF.jpg",
    "https://n.uguu.se/QnLMTcYx.jpg",
    "https://d.uguu.se/aOQGWHbN.jpg"
]

_PING_FILE_ID = None  # cached after first upload -> no re-download from uguu.se


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    global _PING_FILE_ID
    start = time.perf_counter()
    response = await message.reply_photo(
        photo=_PING_FILE_ID or random.choice(Shivi_PIC),
        caption=_["ping_1"].format(app.mention),
        parse_mode=ParseMode.HTML,
    )
    # real Telegram round-trip only (stats gathering is not counted)
    resp = round((time.perf_counter() - start) * 1000, 2)
    if not _PING_FILE_ID:
        try:
            _PING_FILE_ID = response.photo.file_id
        except Exception:
            pass
    pytgping = await Shivi.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    await response.edit_caption(
        _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        parse_mode=ParseMode.HTML,
        reply_markup=supp_markup(_),
    )
