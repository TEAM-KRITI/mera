# ===========================================================
# 🎧 Recommendation buttons ke callbacks (RecPlay / RecRand)
# ===========================================================

import asyncio
import random
import traceback

from pyrogram import StopPropagation, filters

import config
from ShiviMusic import YouTube, app
from ShiviMusic.utils.autoplay import fetch_autoplay_track, remember_played
from ShiviMusic.utils.database import get_lang
from ShiviMusic.utils.formatters import time_to_seconds
from ShiviMusic.utils.logger import track_logs
from ShiviMusic.utils.recommend import (
    _st,
    edit_recommend_message,
    fetch_recommendations,
    get_cached_track,
    get_more_recommendations,
    recommend_markup,
    recommend_text,
)
from ShiviMusic.utils.stream.stream import stream
from config import BANNED_USERS
from strings import get_string


async def _strings(chat_id: int):
    try:
        return get_string(await get_lang(chat_id))
    except Exception:
        return get_string("en")


async def _play_vidid(CallbackQuery, vidid: str, source: str = "Recommend"):
    msg = CallbackQuery.message
    chat_id = msg.chat.id
    user = CallbackQuery.from_user
    _ = await _strings(chat_id)

    try:
        await CallbackQuery.answer("🎧 ʟᴏᴀᴅɪɴɢ...")
    except Exception:
        pass

    mystic = await app.send_message(chat_id, _["play_1"])
    try:
        details = get_cached_track(vidid)  # exact wahi song jo button par dikha
        if details is None:
            details, _track_id = await YouTube.track(vidid, True)
        if details.get("vidid") != vidid:
            raise ValueError(f"vidid mismatch {details.get('vidid')} != {vidid}")
    except Exception as e:
        print(f"[RECOMMEND PLAY] track() fail: {type(e).__name__}: {e}")
        return await mystic.edit_text(_["play_3"])

    dur = details.get("duration_min")
    if dur and time_to_seconds(dur) > config.DURATION_LIMIT:
        return await mystic.edit_text(
            _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
        )

    try:
        await stream(
            _,
            mystic,
            user.id,
            details,
            chat_id,
            user.mention,
            chat_id,
            None,
            streamtype="youtube",
        )
    except Exception as e:
        traceback.print_exc()
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        return await mystic.edit_text(err)

    remember_played(chat_id, vidid)
    await track_logs(chat_id, details["title"], vidid, source, user)
    try:
        await mystic.delete()
    except Exception:
        pass
    try:
        await msg.delete()  # recommendation message sirf success par hatao
    except Exception:
        pass


# group=-1 => ye handler pehle chalta hai, aur StopPropagation se
# purane unanchored regex handlers ("close", "LG" ...) beech me nahi aate.

@app.on_callback_query(filters.regex(r"^RecPlay ") & ~BANNED_USERS, group=-1)
async def rec_play(client, CallbackQuery):
    try:
        vidid = CallbackQuery.data.split(None, 1)[1].strip()
        await _play_vidid(CallbackQuery, vidid)
    except Exception:
        traceback.print_exc()
    raise StopPropagation


_MORE_LOCKS: dict = {}


@app.on_callback_query(filters.regex(r"^RecMore ") & ~BANNED_USERS, group=-1)
async def rec_more(client, CallbackQuery):
    """🔄 More — same country ke naye songs, unlimited."""
    msg = CallbackQuery.message
    try:
        seed = CallbackQuery.data.split(None, 1)[1].strip()
        chat_id = msg.chat.id
        lock = _MORE_LOCKS.setdefault(chat_id, asyncio.Lock())
        if lock.locked():
            return await CallbackQuery.answer("⏳ ʟᴏᴀᴅɪɴɢ ʜᴏ ʀᴀʜᴀ ʜᴀɪ, ʀᴜᴋᴏ...")
        async with lock:
            print(f"[RECOMMEND MORE] pressed chat={chat_id} seed={seed}")
            try:
                await CallbackQuery.answer("🔄 ʟᴏᴀᴅɪɴɢ ᴍᴏʀᴇ...")
            except Exception:
                pass
            old_markup = msg.reply_markup
            try:
                old_text = (
                    msg.caption.html if msg.photo and msg.caption
                    else (msg.text.html if msg.text else None)
                )
            except Exception:
                old_text = None
            try:  # turant visible feedback
                await edit_recommend_message(
                    msg, "<b>🔄 ʟᴏᴀᴅɪɴɢ ᴍᴏʀᴇ sᴏɴɢs...</b>", old_markup
                )
            except Exception:
                pass

            tracks = await get_more_recommendations(chat_id, seed)
            st = _st(chat_id)
            try:
                if tracks:
                    await edit_recommend_message(
                        msg,
                        recommend_text(st.get("title"), st.get("region")),
                        recommend_markup(tracks, seed),
                        tracks,
                    )
                else:
                    await edit_recommend_message(
                        msg,
                        (old_text or recommend_text(st.get("title"), st.get("region")))
                        + "\n\n<b>❌ ᴀᴜʀ ᴛʀᴀᴄᴋ ɴᴀʜɪ ᴍɪʟᴇ, ᴅᴏʙᴀʀᴀ ᴛʀʏ ᴋᴀʀᴏ</b>",
                        old_markup,
                    )
            except Exception as e:
                print(f"[RECOMMEND MORE] edit fail: {type(e).__name__}: {e}")
    except Exception:
        traceback.print_exc()
    raise StopPropagation


@app.on_callback_query(filters.regex(r"^RecRand ") & ~BANNED_USERS, group=-1)
async def rec_random(client, CallbackQuery):
    try:
        seed = CallbackQuery.data.split(None, 1)[1].strip()
        track = None
        try:
            track = await fetch_autoplay_track(CallbackQuery.message.chat.id, "", seed)
        except Exception as e:
            print(f"[RECOMMEND RAND] autoplay fetch fail: {e}")
        if not track:  # fallback: cache / search / last good list
            recs = await fetch_recommendations(seed)
            track = random.choice(recs) if recs else None
        if not track:
            await CallbackQuery.answer("❌ ᴛʀᴀᴄᴋ ɴᴀʜɪ ᴍɪʟᴀ", show_alert=True)
        else:
            await _play_vidid(CallbackQuery, track["vidid"], "Recommend (Random AI Track)")
    except Exception:
        traceback.print_exc()
    raise StopPropagation
