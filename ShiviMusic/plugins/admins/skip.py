# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ===========================================================

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config

from ShiviMusic import YouTube, app
from ShiviMusic.core.call import Shivi
from ShiviMusic.utils.recommend import send_recommendations
from ShiviMusic.misc import db
from ShiviMusic.utils.database import (
    get_loop,
    is_autoplay_on,
)
from ShiviMusic.utils.decorators import AdminRightsCheck
from ShiviMusic.utils.inline import (
    close_markup,
    stream_markup,
)
from ShiviMusic.utils.stream.autoclear import auto_clean
from ShiviMusic.utils.thumbnails import get_thumb
from config import BANNED_USERS


# ===========================================================
# HELPER
# ===========================================================

async def ensure_queue(chat_id: int):
    """
    Make sure db[chat_id] exists and contains a queue list.
    """

    if chat_id not in db:
        db[chat_id] = []

    if not isinstance(db[chat_id], list):
        db[chat_id] = []

    return db[chat_id]


# ===========================================================
# SAFE MESSAGE
# ===========================================================

async def stop_empty_stream(message: Message, chat_id: int, _):
    """
    Stop stream safely when queue becomes empty.
    """

    try:
        await message.reply_text(
            text=_["admin_6"].format(
                message.from_user.mention,
                message.chat.title,
            ),
            reply_markup=close_markup(_),
        )
    except Exception:
        pass

    try:
        await Shivi.stop_stream(chat_id)
    except Exception:
        pass


# ===========================================================
# SAVE CURRENT STREAM MESSAGE
# ===========================================================

def save_current_stream(chat_id: int, run, markup_type: str):
    """
    Safely save the currently playing message.

    Prevents:
        IndexError: list index out of range
    """

    if chat_id not in db:
        db[chat_id] = []

    if not isinstance(db[chat_id], list):
        db[chat_id] = []

    if not db[chat_id]:
        return False

    db[chat_id][0]["mystic"] = run
    db[chat_id][0]["markup"] = markup_type

    return True


# ===========================================================
# SKIP COMMAND
# ===========================================================

@app.on_message(
    filters.command(
        ["skip", "cskip", "next", "cnext"]
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):

    # =======================================================
    # MAKE SURE QUEUE EXISTS
    # =======================================================

    check = await ensure_queue(chat_id)

    # =======================================================
    # NO QUEUE
    # =======================================================

    if not check:

        await stop_empty_stream(
            message,
            chat_id,
            _,
        )

        return

    # =======================================================
    # SKIP WITH NUMBER
    # =======================================================

    if len(message.command) >= 2:

        loop = await get_loop(chat_id)

        if loop != 0:
            return await message.reply_text(
                _["admin_8"]
            )

        state = message.text.split(
            None,
            1,
        )[1].strip()

        if not state.isnumeric():

            return await message.reply_text(
                _["admin_9"]
            )

        state = int(state)

        count = len(check)

        # ---------------------------------------------------
        # There must be a current song + requested queue
        # ---------------------------------------------------

        if count <= 2:

            return await message.reply_text(
                _["admin_10"]
            )

        available = count - 1

        if not 1 <= state <= available:

            return await message.reply_text(
                _["admin_11"].format(
                    available
                )
            )

        # ---------------------------------------------------
        # Remove requested number of songs
        # ---------------------------------------------------

        for _index in range(state):

            if not check:
                break

            popped = None

            try:
                popped = check.pop(0)
            except Exception:
                break

            if popped:

                try:
                    await auto_clean(popped)
                except Exception:
                    pass

        # ---------------------------------------------------
        # Queue completely empty
        # ---------------------------------------------------

        if not check:

            started = False

            # -----------------------------------------------
            # AUTOPLAY
            # -----------------------------------------------

            if popped and await is_autoplay_on(chat_id):

                try:

                    started = await Shivi.autoplay_start(
                        chat_id,
                        popped.get(
                            "chat_id",
                            chat_id,
                        ),
                        popped.get(
                            "title"
                        ),
                        popped.get(
                            "vidid"
                        ),
                    )

                except Exception:
                    started = False

            if started:
                return

            if popped:
                await send_recommendations(
                    app, popped.get("chat_id", chat_id), popped
                )

            await stop_empty_stream(
                message,
                chat_id,
                _,
            )

            return

    # =======================================================
    # NORMAL SKIP
    # =======================================================

    else:

        popped = None

        try:

            # -----------------------------------------------
            # Safety check
            # -----------------------------------------------

            if not check:
                await stop_empty_stream(
                    message,
                    chat_id,
                    _,
                )
                return

            # -----------------------------------------------
            # Remove current song
            # -----------------------------------------------

            popped = check.pop(0)

            if popped:

                try:
                    await auto_clean(popped)
                except Exception:
                    pass

        except Exception:

            await stop_empty_stream(
                message,
                chat_id,
                _,
            )

            return

        # ---------------------------------------------------
        # Queue empty after skip
        # ---------------------------------------------------

        if not check:

            started = False

            # -----------------------------------------------
            # AUTOPLAY
            # -----------------------------------------------

            if popped and await is_autoplay_on(chat_id):

                try:

                    started = await Shivi.autoplay_start(
                        chat_id,
                        popped.get(
                            "chat_id",
                            chat_id,
                        ),
                        popped.get(
                            "title"
                        ),
                        popped.get(
                            "vidid"
                        ),
                    )

                except Exception:
                    started = False

            if started:
                return

            if popped:
                await send_recommendations(
                    app, popped.get("chat_id", chat_id), popped
                )

            await stop_empty_stream(
                message,
                chat_id,
                _,
            )

            return

    # =======================================================
    # FINAL SAFETY CHECK
    # =======================================================

    if not check:

        await stop_empty_stream(
            message,
            chat_id,
            _,
        )

        return

    # =======================================================
    # GET NEXT QUEUED SONG
    # =======================================================

    try:

        current = check[0]

        queued = current["file"]
        title = (
            current["title"]
            or "Unknown"
        ).title()

        user = current.get(
            "by",
            "Unknown",
        )

        streamtype = current.get(
            "streamtype",
            "audio",
        )

        videoid = current.get(
            "vidid"
        )

    except Exception:

        await stop_empty_stream(
            message,
            chat_id,
            _,
        )

        return

    # =======================================================
    # STREAM TYPE
    # =======================================================

    status = (
        True
        if str(streamtype) == "video"
        else None
    )

    # =======================================================
    # CURRENT SONG STATE
    # =======================================================

    try:

        db[chat_id][0]["played"] = 0

        exis = db[chat_id][0].get(
            "old_dur"
        )

        if exis:

            db[chat_id][0]["dur"] = exis

            db[chat_id][0]["seconds"] = (
                db[chat_id][0].get(
                    "old_second",
                    0,
                )
            )

            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0

    except Exception:
        pass

    # =======================================================
    # LIVE STREAM
    # =======================================================

    if queued and "live_" in queued:

        try:

            n, link = await YouTube.video(
                videoid,
                True,
            )

        except Exception:

            return await message.reply_text(
                _["admin_7"].format(title)
            )

        if n == 0:

            return await message.reply_text(
                _["admin_7"].format(title)
            )

        try:

            image = await YouTube.thumbnail(
                videoid,
                True,
            )

        except Exception:

            image = None

        try:

            await Shivi.skip_stream(
                chat_id,
                link,
                video=status,
                image=image,
            )

        except Exception:

            return await message.reply_text(
                _["call_6"]
            )

        button = stream_markup(
            _,
            chat_id,
        )

        try:

            img = await get_thumb(
                videoid,
                user_name=user,
            )

        except Exception:

            img = config.STREAM_IMG_URL

        try:

            run = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    current.get("dur", "Unknown"),
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            save_current_stream(
                chat_id,
                run,
                "tg",
            )

        except Exception:
            pass

    # =======================================================
    # VIDEO DOWNLOAD
    # =======================================================

    elif queued and "vid_" in queued:

        mystic = await message.reply_text(
            _["call_7"]
        )

        try:

            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )

        except Exception:

            try:
                await mystic.edit_text(
                    _["call_6"]
                )
            except Exception:
                pass

            return

        try:

            image = await YouTube.thumbnail(
                videoid,
                True,
            )

        except Exception:

            image = None

        try:

            await Shivi.skip_stream(
                chat_id,
                file_path,
                video=status,
                image=image,
            )

        except Exception:

            try:
                await mystic.edit_text(
                    _["call_6"]
                )
            except Exception:
                pass

            return

        button = stream_markup(
            _,
            chat_id,
        )

        try:

            img = await get_thumb(
                videoid,
                user_name=user,
            )

        except Exception:

            img = config.STREAM_IMG_URL

        try:

            run = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    current.get("dur", "Unknown"),
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            save_current_stream(
                chat_id,
                run,
                "stream",
            )

        except Exception:
            pass

        try:
            await mystic.delete()
        except Exception:
            pass

    # =======================================================
    # TELEGRAM INDEX
    # =======================================================

    elif queued and "index_" in queued:

        try:

            await Shivi.skip_stream(
                chat_id,
                videoid,
                video=status,
            )

        except Exception:

            return await message.reply_text(
                _["call_6"]
            )

        button = stream_markup(
            _,
            chat_id,
        )

        try:

            run = await message.reply_photo(
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(
                    user
                ),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            save_current_stream(
                chat_id,
                run,
                "tg",
            )

        except Exception:
            pass

    # =======================================================
    # OTHER STREAM TYPES
    # =======================================================

    else:

        # ---------------------------------------------------
        # IMAGE
        # ---------------------------------------------------

        if videoid in (
            "telegram",
            "soundcloud",
        ):

            image = None

        else:

            try:

                image = await YouTube.thumbnail(
                    videoid,
                    True,
                )

            except Exception:

                image = None

        # ---------------------------------------------------
        # START STREAM
        # ---------------------------------------------------

        try:

            await Shivi.skip_stream(
                chat_id,
                queued,
                video=status,
                image=image,
            )

        except Exception:

            return await message.reply_text(
                _["call_6"]
            )

        button = stream_markup(
            _,
            chat_id,
        )

        # ===================================================
        # TELEGRAM
        # ===================================================

        if videoid == "telegram":

            try:

                run = await message.reply_photo(
                    photo=(
                        config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        config.SUPPORT_CHAT,
                        title[:23],
                        current.get("dur", "Unknown"),
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                save_current_stream(
                    chat_id,
                    run,
                    "tg",
                )

            except Exception:
                pass

        # ===================================================
        # SOUNDCLOUD
        # ===================================================

        elif videoid == "soundcloud":

            try:

                run = await message.reply_photo(
                    photo=(
                        config.SOUNDCLOUD_IMG_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        config.SUPPORT_CHAT,
                        title[:23],
                        current.get("dur", "Unknown"),
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                save_current_stream(
                    chat_id,
                    run,
                    "tg",
                )

            except Exception:
                pass

        # ===================================================
        # YOUTUBE / OTHER
        # ===================================================

        else:

            try:

                img = await get_thumb(
                    videoid,
                    user_name=user,
                )

            except Exception:

                img = config.STREAM_IMG_URL

            try:

                run = await message.reply_photo(
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        current.get("dur", "Unknown"),
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                save_current_stream(
                    chat_id,
                    run,
                    "stream",
                )

            except Exception:
                pass


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder)
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
