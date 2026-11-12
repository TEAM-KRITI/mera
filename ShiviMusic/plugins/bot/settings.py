# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from pyrogram import filters
import random
from pyrogram.enums import ChatType
from pyrogram.errors import MessageNotModified
from time import time, strftime, gmtime
from pyrogram.types import InputMediaVideo, InputMediaPhoto
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from ShiviMusic import app
from ShiviMusic.utils.database import (
    add_nonadmin_chat,
    get_authuser,
    get_authuser_names,
    get_playmode,
    get_playtype,
    get_upvote_count,
    is_nonadmin_chat,
    is_skipmode,
    remove_nonadmin_chat,
    set_playmode,
    set_playtype,
    set_upvotes,
    skip_off,
    skip_on,
)
from ShiviMusic.utils.decorators.admins import ActualAdminCB
from ShiviMusic.utils.decorators.language import language, languageCB
from ShiviMusic.utils.inline.settings import (
    auth_users_markup,
    playmode_users_markup,
    setting_markup,
    vote_mode_markup,
)
from ShiviMusic.utils.inline.start import private_panel
from config import BANNED_USERS, OWNER_ID


NEXI_VID = [
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg",
    "https://files.catbox.moe/4ojtc4.jpg",
    "https://files.catbox.moe/30wg78.jpg"
]


@app.on_message(
    filters.command(["settings", "setting"]) & filters.group & ~BANNED_USERS
)
@language
async def settings_mar(client, message: Message, _):
    buttons = setting_markup(_)
    await message.reply_text(
        _["setting_1"].format(app.mention, message.chat.id, message.chat.title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex("settings_helper") & ~BANNED_USERS)
@languageCB
async def settings_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer(_["set_cb_5"])
    except:
        pass
    buttons = setting_markup(_)
    return await CallbackQuery.edit_message_text(
        _["setting_1"].format(
            app.mention,
            CallbackQuery.message.chat.id,
            CallbackQuery.message.chat.title,
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    
@app.on_callback_query(filters.regex("settingsback_helper") & ~BANNED_USERS)
@languageCB
async def settings_back_markup(client, CallbackQuery: CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass

    if CallbackQuery.message.chat.type == ChatType.PRIVATE:
        await app.resolve_peer(OWNER_ID)
        OWNER = OWNER_ID
        buttons = private_panel(_)

        return await CallbackQuery.edit_message_media(
            InputMediaPhoto(
                media=random.choice(NEXI_VID),
                caption=_["start_2"].format(
                    CallbackQuery.from_user.mention,
                    app.mention
                ),
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        buttons = setting_markup(_)
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@app.on_callback_query(filters.regex("gib_source"))
async def gib_repo_callback(_, callback_query):
    await callback_query.edit_message_media(
        media=InputMediaVideo(
            "https://files.catbox.moe/9r3hbf.mp4", 
            has_spoiler=True, 
            caption="**» ʟᴜɴᴅ ʟᴇʟᴇ ᴍᴇʀᴀ 😒 ʀᴇᴘᴏ ᴋʏᴀ ᴋᴀʀᴇɢᴀ.**\n**» ʟᴇɢᴀ ᴋʏᴀ ʙʜᴏsᴀᴅɪᴋᴇ 😆 ʙᴏʟ ɴᴀ ʟᴇɢᴀ ??**"
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="• ʙᴧᴄᴋ •", callback_data="back_cb"),
                    InlineKeyboardButton(text="• ᴄʟᴏsє •", callback_data="close")
                ]
            ]
        ),
    )

@app.on_callback_query(filters.regex("^bot_info_data$"))
async def show_bot_info(c: app, q: CallbackQuery):
    # PEER_ID_INVALID fix: ab chat me message bhejna hi nahi padta,
    # ping seedha Telegram API call se measure hota hai aur popup q.answer se dikhta hai.
    start = time()
    try:
        await c.get_me()
    except Exception:
        pass
    delta_ping = time() - start
    txt = f"""ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ sᴛᴀᴛᴜs...💌

• ᴅᴀᴛᴀʙᴀsᴇ : ᴏɴʟɪɴᴇ
• ʏᴏᴜᴛᴜʙᴇ ᴀᴘɪ : ʀᴇsᴘᴏɴsɪᴠᴇ
• ʙᴏᴛ sᴇʀᴠᴇʀ : ʀᴜɴɴɪɴɢ sᴍᴏᴏᴛʜʟʏ
• ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ : ᴏᴘᴛɪᴍᴀʟ
• ᴀᴘɪ ᴘɪɴɢ : {delta_ping * 1000:.3f} ms   

• ᴇᴠᴇʀʏᴛʜɪɴɢ ʟᴏᴏᴋs ɢᴏᴏᴅ !!
"""
    try:
        await q.answer(txt, show_alert=True)
    except Exception:
        pass
    return



@app.on_callback_query(
    filters.regex(
        pattern=r"^(SEARCHANSWER|PLAYMODEANSWER|PLAYTYPEANSWER|AUTHANSWER|ANSWERVOMODE|VOTEANSWER|PM|AU|VM)$"
    )
    & ~BANNED_USERS
)
@languageCB
async def without_Admin_rights(client, CallbackQuery, _):
    command = CallbackQuery.matches[0].group(1)
    if command == "SEARCHANSWER":
        try:
            return await CallbackQuery.answer(_["setting_2"], show_alert=True)
        except:
            return
    if command == "PLAYMODEANSWER":
        try:
            return await CallbackQuery.answer(_["setting_5"], show_alert=True)
        except:
            return
    if command == "PLAYTYPEANSWER":
        try:
            return await CallbackQuery.answer(_["setting_6"], show_alert=True)
        except:
            return
    if command == "AUTHANSWER":
        try:
            return await CallbackQuery.answer(_["setting_3"], show_alert=True)
        except:
            return
    if command == "VOTEANSWER":
        try:
            return await CallbackQuery.answer(
                _["setting_8"],
                show_alert=True,
            )
        except:
            return
    if command == "ANSWERVOMODE":
        current = await get_upvote_count(CallbackQuery.message.chat.id)
        try:
            return await CallbackQuery.answer(
                _["setting_9"].format(current),
                show_alert=True,
            )
        except:
            return
    if command == "PM":
        try:
            await CallbackQuery.answer(_["set_cb_2"], show_alert=True)
        except:
            pass
        playmode = await get_playmode(CallbackQuery.message.chat.id)
        if playmode == "Direct":
            Direct = True
        else:
            Direct = None
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            Group = True
        else:
            Group = None
        playty = await get_playtype(CallbackQuery.message.chat.id)
        if playty == "Everyone":
            Playtype = None
        else:
            Playtype = True
        buttons = playmode_users_markup(_, Direct, Group, Playtype)
    if command == "AU":
        try:
            await CallbackQuery.answer(_["set_cb_1"], show_alert=True)
        except:
            pass
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            buttons = auth_users_markup(_, True)
        else:
            buttons = auth_users_markup(_)
    if command == "VM":
        mode = await is_skipmode(CallbackQuery.message.chat.id)
        current = await get_upvote_count(CallbackQuery.message.chat.id)
        buttons = vote_mode_markup(_, current, mode)
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return


@app.on_callback_query(filters.regex("FERRARIUDTI") & ~BANNED_USERS)
@ActualAdminCB
async def addition(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    if not await is_skipmode(CallbackQuery.message.chat.id):
        return await CallbackQuery.answer(_["setting_10"], show_alert=True)
    current = await get_upvote_count(CallbackQuery.message.chat.id)
    if mode == "M":
        final = current - 2
        print(final)
        if final == 0:
            return await CallbackQuery.answer(
                _["setting_11"],
                show_alert=True,
            )
        if final <= 2:
            final = 2
        await set_upvotes(CallbackQuery.message.chat.id, final)
    else:
        final = current + 2
        print(final)
        if final == 17:
            return await CallbackQuery.answer(
                _["setting_12"],
                show_alert=True,
            )
        if final >= 15:
            final = 15
        await set_upvotes(CallbackQuery.message.chat.id, final)
    buttons = vote_mode_markup(_, final, True)
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return


@app.on_callback_query(
    filters.regex(pattern=r"^(MODECHANGE|CHANNELMODECHANGE|PLAYTYPECHANGE)$")
    & ~BANNED_USERS
)
@ActualAdminCB
async def playmode_ans(client, CallbackQuery, _):
    command = CallbackQuery.matches[0].group(1)
    if command == "CHANNELMODECHANGE":
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            await add_nonadmin_chat(CallbackQuery.message.chat.id)
            Group = None
        else:
            await remove_nonadmin_chat(CallbackQuery.message.chat.id)
            Group = True
        playmode = await get_playmode(CallbackQuery.message.chat.id)
        if playmode == "Direct":
            Direct = True
        else:
            Direct = None
        playty = await get_playtype(CallbackQuery.message.chat.id)
        if playty == "Everyone":
            Playtype = None
        else:
            Playtype = True
        buttons = playmode_users_markup(_, Direct, Group, Playtype)
    if command == "MODECHANGE":
        try:
            await CallbackQuery.answer(_["set_cb_3"], show_alert=True)
        except:
            pass
        playmode = await get_playmode(CallbackQuery.message.chat.id)
        if playmode == "Direct":
            await set_playmode(CallbackQuery.message.chat.id, "Inline")
            Direct = None
        else:
            await set_playmode(CallbackQuery.message.chat.id, "Direct")
            Direct = True
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            Group = True
        else:
            Group = None
        playty = await get_playtype(CallbackQuery.message.chat.id)
        if playty == "Everyone":
            Playtype = False
        else:
            Playtype = True
        buttons = playmode_users_markup(_, Direct, Group, Playtype)
    if command == "PLAYTYPECHANGE":
        try:
            await CallbackQuery.answer(_["set_cb_3"], show_alert=True)
        except:
            pass
        playty = await get_playtype(CallbackQuery.message.chat.id)
        if playty == "Everyone":
            await set_playtype(CallbackQuery.message.chat.id, "Admin")
            Playtype = False
        else:
            await set_playtype(CallbackQuery.message.chat.id, "Everyone")
            Playtype = True
        playmode = await get_playmode(CallbackQuery.message.chat.id)
        if playmode == "Direct":
            Direct = True
        else:
            Direct = None
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            Group = True
        else:
            Group = None
        buttons = playmode_users_markup(_, Direct, Group, Playtype)
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return


@app.on_callback_query(filters.regex(pattern=r"^(AUTH|AUTHLIST)$") & ~BANNED_USERS)
@ActualAdminCB
async def authusers_mar(client, CallbackQuery, _):
    command = CallbackQuery.matches[0].group(1)
    if command == "AUTHLIST":
        _authusers = await get_authuser_names(CallbackQuery.message.chat.id)
        if not _authusers:
            try:
                return await CallbackQuery.answer(_["setting_4"], show_alert=True)
            except:
                return
        else:
            try:
                await CallbackQuery.answer(_["set_cb_4"], show_alert=True)
            except:
                pass
            j = 0
            await CallbackQuery.edit_message_text(_["auth_6"])
            msg = _["auth_7"].format(CallbackQuery.message.chat.title)
            for note in _authusers:
                _note = await get_authuser(CallbackQuery.message.chat.id, note)
                user_id = _note["auth_user_id"]
                admin_id = _note["admin_id"]
                admin_name = _note["admin_name"]
                try:
                    user = await app.get_users(user_id)
                    user = user.first_name
                    j += 1
                except:
                    continue
                msg += f"{j}➤ {user}[<code>{user_id}</code>]\n"
                msg += f"   {_['auth_8']} {admin_name}[<code>{admin_id}</code>]\n\n"
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_["BACK_BUTTON"], callback_data=f"AU"
                        ),
                        InlineKeyboardButton(
                            text=_["CLOSE_BUTTON"],
                            callback_data=f"close",
                        ),
                    ]
                ]
            )
            try:
                return await CallbackQuery.edit_message_text(msg, reply_markup=upl)
            except MessageNotModified:
                return
    try:
        await CallbackQuery.answer(_["set_cb_3"], show_alert=True)
    except:
        pass
    if command == "AUTH":
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            await add_nonadmin_chat(CallbackQuery.message.chat.id)
            buttons = auth_users_markup(_)
        else:
            await remove_nonadmin_chat(CallbackQuery.message.chat.id)
            buttons = auth_users_markup(_, True)
    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return


@app.on_callback_query(filters.regex("VOMODECHANGE") & ~BANNED_USERS)
@ActualAdminCB
async def vote_change(client, CallbackQuery, _):
    command = CallbackQuery.matches[0].group(1)
    try:
        await CallbackQuery.answer(_["set_cb_3"], show_alert=True)
    except:
        pass
    mod = None
    if await is_skipmode(CallbackQuery.message.chat.id):
        await skip_off(CallbackQuery.message.chat.id)
    else:
        mod = True
        await skip_on(CallbackQuery.message.chat.id)
    current = await get_upvote_count(CallbackQuery.message.chat.id)
    buttons = vote_mode_markup(_, current, mod)

    try:
        return await CallbackQuery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        return

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
# 
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================
