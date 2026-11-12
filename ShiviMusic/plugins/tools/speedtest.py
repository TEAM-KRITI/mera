# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

import asyncio

import speedtest
from pyrogram import filters
from pyrogram.types import Message

from ShiviMusic import app
from ShiviMusic.misc import SUDOERS
from ShiviMusic.utils.decorators.language import language


def testspeed(m, _):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit_text(_["server_12"])
        test.download()
        m = m.edit_text(_["server_13"])
        test.upload()
        test.results.share()
        result = test.results.dict()
        m = m.edit_text(_["server_14"])
    except Exception as e:
        return m.edit_text(f"<code>{e}</code>")
    return result


@app.on_message(filters.command(["speedtest", "spt"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]) & SUDOERS)
@language 
async def speedtest_function(client, message: Message, _):
    m = await message.reply_text(_["server_11"])
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m, _)
    output = _["server_15"].format(
        result["client"]["isp"],
        result["client"]["country"],
        result["server"]["name"],
        result["server"]["country"],
        result["server"]["cc"],
        result["server"]["sponsor"],
        result["server"]["latency"],
        result["ping"],
    )
    msg = await message.reply_photo(photo=result["share"], caption=output)
    await m.delete()

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
