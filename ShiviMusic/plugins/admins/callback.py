# ======================================================
# ©️ 2025-26 All Rights Reserved by Kirti 😎
# 🧑‍💻 Developer : t.me/lll_APNA_BADNAM_BABY_lll
# ======================================================

import asyncio
import time

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import YouTube, app
from ShiviMusic.core.call import Shivi
from ShiviMusic.misc import SUDOERS, db
from ShiviMusic.utils.database import (
    get_active_chats,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
    get_loop,
)
from ShiviMusic.utils.decorators.language import languageCB
from ShiviMusic.utils.formatters import seconds_to_min
from ShiviMusic.utils.inline import (
    close_markup,
    stream_markup,
    stream_markup_timer,
)
from ShiviMusic.utils.stream.autoclear import auto_clean
from ShiviMusic.utils.thumbnails import get_thumb

from config import (
    BANNED_USERS,
    SUPPORT_CHAT,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
    confirmer,
    votemode,
)

from strings import get_string


checker = {}
upvoters = {}

# ======================================================
# 🎧 AUTOPLAY LOCAL DATABASE
# ======================================================

AUTOPLAY_CHATS = []


async def is_autoplay_group(chat_id: int):
    return chat_id in AUTOPLAY_CHATS


async def add_autoplay_group(chat_id: int):
    if chat_id not in AUTOPLAY_CHATS:
        AUTOPLAY_CHATS.append(chat_id)


async def remove_autoplay_group(chat_id: int):
    if chat_id in AUTOPLAY_CHATS:
        AUTOPLAY_CHATS.remove(chat_id)


# ======================================================
# 🗑️ DELETE MESSAGE AFTER FEW SECONDS
# ======================================================

async def delete_after(message, seconds=5):
    await asyncio.sleep(seconds)

    try:
        await message.delete()
    except Exception:
        pass


# ======================================================
# 🎵 LIVE PROGRESS STATE
# ======================================================

_progress_state = {}


# ======================================================
# 🎛️ ADMIN CALLBACK HANDLER
# ======================================================

@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    try:
        callback_request = callback_data.split(None, 1)[1]
    except Exception:
        return await CallbackQuery.answer(
            "Invalid request.",
            show_alert=True,
        )

    try:
        command, chat = callback_request.split("|", 1)
    except Exception:
        return await CallbackQuery.answer(
            "Invalid request.",
            show_alert=True,
        )

    counter = None

    if "_" in str(chat):
        bet = chat.split("_", 1)
        chat = bet[0]
        counter = bet[1]

    try:
        chat_id = int(chat)
    except Exception:
        return await CallbackQuery.answer(
            "Invalid chat.",
            show_alert=True,
        )

    # ==================================================
    # ACTIVE CHAT CHECK
    # ==================================================

    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(
            _["general_5"],
            show_alert=True,
        )

    mention = CallbackQuery.from_user.mention

    # ==================================================
    # UPVOTE
    # ==================================================

    if command == "UpVote":

        if chat_id not in votemode:
            votemode[chat_id] = {}

        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = upvoters[chat_id].get(
            CallbackQuery.message.id
        )

        if not voters:
            upvoters[chat_id][
                CallbackQuery.message.id
            ] = []

        vote = votemode[chat_id].get(
            CallbackQuery.message.id
        )

        if vote is None:
            votemode[chat_id][
                CallbackQuery.message.id
            ] = 0

        if (
            CallbackQuery.from_user.id
            in upvoters[chat_id][CallbackQuery.message.id]
        ):

            upvoters[chat_id][
                CallbackQuery.message.id
            ].remove(
                CallbackQuery.from_user.id
            )

            votemode[chat_id][
                CallbackQuery.message.id
            ] -= 1

        else:

            upvoters[chat_id][
                CallbackQuery.message.id
            ].append(
                CallbackQuery.from_user.id
            )

            votemode[chat_id][
                CallbackQuery.message.id
            ] += 1

        upvote = await get_upvote_count(chat_id)

        get_upvotes = int(
            votemode[chat_id][
                CallbackQuery.message.id
            ]
        )

        if get_upvotes >= upvote:

            votemode[chat_id][
                CallbackQuery.message.id
            ] = upvote

            try:
                exists = confirmer[chat_id][
                    CallbackQuery.message.id
                ]

                current = db[chat_id][0]

            except Exception:

                return await CallbackQuery.edit_message_text(
                    "ғᴀɪʟᴇᴅ."
                )

            try:

                if (
                    current["vidid"] != exists["vidid"]
                    or current["file"] != exists["file"]
                ):

                    return await CallbackQuery.edit_message_text(
                        _["admin_35"]
                    )

            except Exception:

                return await CallbackQuery.edit_message_text(
                    _["admin_36"]
                )

            try:

                await CallbackQuery.edit_message_text(
                    _["admin_37"].format(upvote)
                )

            except Exception:
                pass

            command = counter
            mention = "ᴜᴘᴠᴏᴛᴇs"

        else:

            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.id]
            ):

                await CallbackQuery.answer(
                    _["admin_38"],
                    show_alert=True,
                )

            else:

                await CallbackQuery.answer(
                    _["admin_39"],
                    show_alert=True,
                )

            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"👍 {get_upvotes}",
                            callback_data=(
                                f"ADMIN  UpVote|"
                                f"{chat_id}_{counter}"
                            ),
                        )
                    ]
                ]
            )

            await CallbackQuery.answer(
                _["admin_40"],
                show_alert=True,
            )

            return await CallbackQuery.edit_message_reply_markup(
                reply_markup=upl
            )

    # ==================================================
    # ADMIN PERMISSION
    # ==================================================

    else:

        is_non_admin = await is_nonadmin_chat(
            CallbackQuery.message.chat.id
        )

        if not is_non_admin:

            if CallbackQuery.from_user.id not in SUDOERS:

                admins = adminlist.get(
                    CallbackQuery.message.chat.id
                )

                if not admins:

                    return await CallbackQuery.answer(
                        _["admin_13"],
                        show_alert=True,
                    )

                if CallbackQuery.from_user.id not in admins:

                    return await CallbackQuery.answer(
                        _["admin_14"],
                        show_alert=True,
                    )

    # ==================================================
    # PAUSE
    # ==================================================

    if command == "Pause":

        if not await is_music_playing(chat_id):

            return await CallbackQuery.answer(
                _["admin_1"],
                show_alert=True,
            )

        await CallbackQuery.answer()

        await music_off(chat_id)

        await Shivi.pause_stream(chat_id)

        await CallbackQuery.message.reply_text(
            _["admin_2"].format(mention),
            reply_markup=close_markup(_),
        )

    # ==================================================
    # RESUME
    # ==================================================

    elif command == "Resume":

        if await is_music_playing(chat_id):

            return await CallbackQuery.answer(
                _["admin_3"],
                show_alert=True,
            )

        await CallbackQuery.answer()

        await music_on(chat_id)

        await Shivi.resume_stream(chat_id)

        try:

            playing = db.get(chat_id)

            if playing and playing[0]:

                played = int(
                    playing[0].get(
                        "played",
                        0,
                    )
                )

                _progress_state[chat_id] = {
                    "played": played,
                    "time": time.monotonic(),
                }

        except Exception:
            pass

        await CallbackQuery.message.reply_text(
            _["admin_4"].format(mention),
            reply_markup=close_markup(_),
        )

    # ==================================================
    # STOP
    # ==================================================

    elif command == "Stop" or command == "End":

        await CallbackQuery.answer()

        _progress_state.pop(
            chat_id,
            None,
        )

        await Shivi.stop_stream(chat_id)

        await set_loop(
            chat_id,
            0,
        )

        await CallbackQuery.message.reply_text(
            _["admin_5"].format(mention),
            reply_markup=close_markup(_),
        )

        try:
            await CallbackQuery.message.delete()
        except Exception:
            pass

    # ==================================================
    # LOOP
    # ==================================================

    elif command == "Loop":

        loop = await get_loop(chat_id)

        if loop == 0:

            await set_loop(
                chat_id,
                3,
            )

            await CallbackQuery.answer(
                "🟢 ʟσσᴘ єηᴧʙʟєᴅ!",
                show_alert=True,
            )

            await CallbackQuery.message.reply_text(
                f"""
<blockquote>
<b>🟢 🔁 ʟσσᴘ sʏsᴛєϻ</b>

<b>ʟσσᴘ ғσʀ ᴛʜɪs ɢʀσυᴘ ɪs ησᴡ єηᴧʙʟєᴅ 🟢.</b>

└ <b>ʙʏ :</b> {mention}
</blockquote>
""",
                reply_markup=close_markup(_),
            )

        else:

            await set_loop(
                chat_id,
                0,
            )

            await CallbackQuery.answer(
                "🔴 ʟσσᴘ ᴅɪsᴧʙʟєᴅ!",
                show_alert=True,
            )

            await CallbackQuery.message.reply_text(
                f"""
<blockquote>
<b>🔴 🔁 ʟσσᴘ sʏsᴛєϻ</b>

<b>ʟσσᴘ ғσʀ ᴛʜɪs ɢʀσυᴘ ɪs ησᴡ ᴅɪsᴧʙʟєᴅ 🔴.</b>

└ <b>ʙʏ :</b> {mention}
</blockquote>
""",
                reply_markup=close_markup(_),
            )

    # ==================================================
    # AUTOPLAY
    # ==================================================

    elif command == "AutoPlay":

        if await is_autoplay_group(chat_id):

            # ------------------------------------------
            # DISABLE AUTOPLAY
            # ------------------------------------------

            await remove_autoplay_group(chat_id)

            await CallbackQuery.answer(
                "🔴 ᴧυᴛσᴘʟᴧʏ ᴅɪsᴧʙʟєᴅ!",
                show_alert=True,
            )

            msg = await CallbackQuery.message.reply_text(
                f"""
<blockquote>
<b>🔴 🎧 ᴧυᴛσᴘʟᴧʏ sʏsᴛєϻ</b>

<b>ᴧυᴛσᴘʟᴧʏ ғσʀ ᴛʜɪs ɢʀσυᴘ ɪs ησᴡ ᴅɪsᴧʙʟєᴅ 🔴.</b>

└ <b>ʙʏ :</b> {mention}
</blockquote>
""",
                reply_markup=close_markup(_),
            )

            asyncio.create_task(
                delete_after(
                    msg,
                    5,
                )
            )

        else:

            # ------------------------------------------
            # ENABLE AUTOPLAY
            # ------------------------------------------

            await add_autoplay_group(chat_id)

            await CallbackQuery.answer(
                "🟢 ᴧυᴛσᴘʟᴧʏ єηᴧʙʟєᴅ!",
                show_alert=True,
            )

            msg = await CallbackQuery.message.reply_text(
                f"""
<blockquote>
<b>🟢 🎧 ᴧυᴛσᴘʟᴧʏ sʏsᴛєϻ</b>

<b>ᴧυᴛσᴘʟᴧʏ ғσʀ ᴛʜɪs ɢʀσυᴘ ɪs ησᴡ єηᴧʙʟєᴅ 🟢.</b>

└ <b>ʙʏ :</b> {mention}
</blockquote>
""",
                reply_markup=close_markup(_),
            )

            asyncio.create_task(
                delete_after(
                    msg,
                    5,
                )
            )

    # ==================================================
    # SKIP / REPLAY
    # ==================================================

    elif command == "Skip" or command == "Replay":

        check = db.get(chat_id)

        if not check:

            return await CallbackQuery.answer(
                "Nothing is playing.",
                show_alert=True,
            )

        if command == "Skip":

            txt = (
                "➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🎄\n"
                "│ \n"
                f"└ʙʏ : {mention} 🥀"
            )

            try:

                popped = check.pop(0)

                if popped:
                    await auto_clean(popped)

                if not check:

                    try:
                        await CallbackQuery.edit_message_text(
                            txt
                        )
                    except Exception:
                        pass

                    await app.send_message(
                        CallbackQuery.message.chat.id,
                        text=_["admin_6"].format(
                            mention,
                            CallbackQuery.message.chat.title,
                        ),
                        reply_markup=close_markup(_),
                    )

                    _progress_state.pop(
                        chat_id,
                        None,
                    )

                    try:
                        return await Shivi.stop_stream(
                            chat_id
                        )
                    except Exception:
                        return

            except Exception:

                try:
                    await CallbackQuery.edit_message_text(
                        txt
                    )
                except Exception:
                    pass

                _progress_state.pop(
                    chat_id,
                    None,
                )

                try:
                    return await Shivi.stop_stream(
                        chat_id
                    )
                except Exception:
                    return

        else:

            txt = (
                "➻ sᴛʀᴇᴀᴍ ʀᴇ-ᴘʟᴀʏᴇᴅ 🎄\n"
                "│ \n"
                f"└ʙʏ : {mention} 🥀"
            )

        await CallbackQuery.answer()

        if not check:
            return

        queued = check[0]["file"]

        title = (
            check[0]["title"]
        ).title()

        user = check[0]["by"]

        duration = check[0]["dur"]

        streamtype = check[0]["streamtype"]

        videoid = check[0]["vidid"]

        status = (
            True
            if str(streamtype) == "video"
            else None
        )

        # ----------------------------------------------
        # RESET PROGRESS
        # ----------------------------------------------

        db[chat_id][0]["played"] = 0

        _progress_state[chat_id] = {
            "played": 0,
            "time": time.monotonic(),
        }

        exis = check[0].get("old_dur")

        if exis:

            db[chat_id][0]["dur"] = exis

            db[chat_id][0]["seconds"] = (
                check[0]["old_second"]
            )

            db[chat_id][0]["speed_path"] = None

            db[chat_id][0]["speed"] = 1.0

        # ==================================================
        # LIVE
        # ==================================================

        if "live_" in queued:

            n, link = await YouTube.video(
                videoid,
                True,
            )

            if n == 0:

                return await CallbackQuery.message.reply_text(
                    text=_["admin_7"].format(title),
                    reply_markup=close_markup(_),
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

                return await CallbackQuery.message.reply_text(
                    _["call_6"]
                )

            button = stream_markup(
                _,
                chat_id,
            )

            img = await get_thumb(
                videoid
            )

            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    (
                        f"https://t.me/{app.username}"
                        f"?start=info_{videoid}"
                    ),
                    title[:23],
                    duration,
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

            await CallbackQuery.edit_message_text(
                txt,
                reply_markup=close_markup(_),
            )

        # ==================================================
        # VIDEO
        # ==================================================

        elif "vid_" in queued:

            mystic = await CallbackQuery.message.reply_text(
                _["call_7"],
                disable_web_page_preview=True,
            )

            try:

                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=status,
                )

            except Exception:

                return await mystic.edit_text(
                    _["call_6"]
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
                    file_path,
                    video=status,
                    image=image,
                )

            except Exception:

                return await mystic.edit_text(
                    _["call_6"]
                )

            button = stream_markup(
                _,
                chat_id,
            )

            img = await get_thumb(
                videoid
            )

            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    (
                        f"https://t.me/{app.username}"
                        f"?start=info_{videoid}"
                    ),
                    title[:23],
                    duration,
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

            await CallbackQuery.edit_message_text(
                txt,
                reply_markup=close_markup(_),
            )

            try:
                await mystic.delete()
            except Exception:
                pass

        # ==================================================
        # INDEX
        # ==================================================

        elif "index_" in queued:

            try:

                await Shivi.skip_stream(
                    chat_id,
                    videoid,
                    video=status,
                )

            except Exception:

                return await CallbackQuery.message.reply_text(
                    _["call_6"]
                )

            button = stream_markup(
                _,
                chat_id,
            )

            run = await CallbackQuery.message.reply_photo(
                photo=STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(
                    button
                ),
            )

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

            await CallbackQuery.edit_message_text(
                txt,
                reply_markup=close_markup(_),
            )

        # ==================================================
        # TELEGRAM / SOUNDCLOUD / NORMAL
        # ==================================================

        else:

            if (
                videoid == "telegram"
                or videoid == "soundcloud"
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

            try:

                await Shivi.skip_stream(
                    chat_id,
                    queued,
                    video=status,
                    image=image,
                )

            except Exception:

                return await CallbackQuery.message.reply_text(
                    _["call_6"]
                )

            # ------------------------------------------
            # TELEGRAM
            # ------------------------------------------

            if videoid == "telegram":

                button = stream_markup(
                    _,
                    chat_id,
                )

                run = await CallbackQuery.message.reply_photo(
                    photo=(
                        TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        SUPPORT_CHAT,
                        title[:23],
                        duration,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"

            # ------------------------------------------
            # SOUNDCLOUD
            # ------------------------------------------

            elif videoid == "soundcloud":

                button = stream_markup(
                    _,
                    chat_id,
                )

                run = await CallbackQuery.message.reply_photo(
                    photo=(
                        SOUNCLOUD_IMG_URL
                        if str(streamtype) == "audio"
                        else TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        SUPPORT_CHAT,
                        title[:23],
                        duration,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"

            # ------------------------------------------
            # NORMAL
            # ------------------------------------------

            else:

                button = stream_markup(
                    _,
                    chat_id,
                )

                img = await get_thumb(
                    videoid
                )

                run = await CallbackQuery.message.reply_photo(
                    photo=img,
                    caption=_["stream_1"].format(
                        (
                            f"https://t.me/{app.username}"
                            f"?start=info_{videoid}"
                        ),
                        title[:23],
                        duration,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        button
                    ),
                )

                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

            await CallbackQuery.edit_message_text(
                txt,
                reply_markup=close_markup(_),
            )


# ======================================================
# 🎧 LIVE PROGRESS TIMER
# ======================================================

async def markup_timer():

    while True:

        await asyncio.sleep(3)

        try:

            active_chats = await get_active_chats()

        except Exception:

            continue

        now = time.monotonic()

        for chat_id in active_chats:

            try:

                # --------------------------------------
                # CHECK PLAYING
                # --------------------------------------

                if not await is_music_playing(chat_id):

                    _progress_state.pop(
                        chat_id,
                        None,
                    )

                    continue

                # --------------------------------------
                # GET DB
                # --------------------------------------

                playing = db.get(chat_id)

                if not playing:
                    continue

                if not playing[0]:
                    continue

                data = playing[0]

                # --------------------------------------
                # MESSAGE
                # --------------------------------------

                mystic = data.get("mystic")

                if not mystic:
                    continue

                # --------------------------------------
                # DURATION
                # --------------------------------------

                try:

                    duration_seconds = int(
                        data.get(
                            "seconds",
                            0,
                        )
                    )

                except Exception:

                    duration_seconds = 0

                if duration_seconds <= 0:
                    continue

                # --------------------------------------
                # DB POSITION
                # --------------------------------------

                try:

                    db_played = int(
                        data.get(
                            "played",
                            0,
                        )
                    )

                except Exception:

                    db_played = 0

                db_played = max(
                    0,
                    min(
                        db_played,
                        duration_seconds,
                    ),
                )

                # --------------------------------------
                # TIMER STATE
                # --------------------------------------

                state = _progress_state.get(
                    chat_id
                )

                if state is None:

                    played = db_played

                    _progress_state[chat_id] = {
                        "played": played,
                        "time": now,
                    }

                else:

                    old_played = int(
                        state.get(
                            "played",
                            0,
                        )
                    )

                    old_time = float(
                        state.get(
                            "time",
                            now,
                        )
                    )

                    elapsed = int(
                        now - old_time
                    )

                    # ----------------------------------
                    # SEEK / REPLAY DETECTION
                    # ----------------------------------

                    if abs(
                        db_played - old_played
                    ) > max(
                        elapsed + 4,
                        5,
                    ):

                        played = db_played

                    else:

                        played = (
                            old_played
                            + max(
                                0,
                                elapsed,
                            )
                        )

                    played = max(
                        0,
                        min(
                            played,
                            duration_seconds,
                        ),
                    )

                    _progress_state[chat_id] = {
                        "played": played,
                        "time": now,
                    }

                # --------------------------------------
                # SAVE PLAYED
                # --------------------------------------

                data["played"] = played

                # --------------------------------------
                # LANGUAGE
                # --------------------------------------

                try:

                    language = await get_lang(
                        chat_id
                    )

                    _ = get_string(
                        language
                    )

                except Exception:

                    _ = get_string(
                        "en"
                    )

                # --------------------------------------
                # CREATE BUTTON
                # --------------------------------------

                buttons = stream_markup_timer(
                    _,
                    chat_id,
                    seconds_to_min(
                        played
                    ),
                    data.get(
                        "dur",
                        seconds_to_min(
                            duration_seconds
                        ),
                    ),
                )

                # --------------------------------------
                # UPDATE TELEGRAM
                # --------------------------------------

                try:

                    await mystic.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(
                            buttons
                        )
                    )

                except Exception:

                    pass

            except Exception:

                continue


# ======================================================
# 🚀 START TIMER
# ======================================================

asyncio.create_task(
    markup_timer()
)
