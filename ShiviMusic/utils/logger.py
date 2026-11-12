import html

from pyrogram.enums import ChatMemberStatus, ChatMembersFilter, ParseMode

from ShiviMusic import app
from ShiviMusic.utils.database import is_on_off
from config import LOGGER_ID


async def get_group_extra(chat_id):
    """Group ke members count aur owner (id, name, username) ka log block."""
    count = "Unknown"
    owner_id = "Unknown"
    owner_name = "Unknown"
    owner_username = "None"

    try:
        count = await app.get_chat_members_count(chat_id)
    except Exception:
        pass

    try:
        async for adm in app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if adm.status == ChatMemberStatus.OWNER and adm.user:
                ou = adm.user
                owner_id = ou.id
                owner_name = html.escape(
                    f"{ou.first_name or ''} {ou.last_name or ''}".strip()
                    or "Unknown"
                )
                owner_username = (
                    f"@{ou.username}" if ou.username else "None"
                )
                break
    except Exception:
        pass

    return (
        f"<b>● ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ➠</b> {count}\n"
        f"<b>● ᴏᴡɴᴇʀ ɴᴀᴍᴇ ➠</b> {owner_name}\n"
    )


async def play_logs(message, streamtype):
    if await is_on_off(2):
        # Safely get play query
        if message.text:
            parts = message.text.split(None, 1)
            query = parts[1] if len(parts) > 1 else "No Query"
        else:
            query = "No Query"

        # Safely get chat/user information
        chat_id = message.chat.id
        chat_title = message.chat.title or "Private Chat"
        chat_username = (
            f"@{message.chat.username}"
            if message.chat.username
            else "None"
        )

        user_id = message.from_user.id if message.from_user else "Unknown"
        user_mention = (
            message.from_user.mention
            if message.from_user
            else "Unknown"
        )
        user_username = (
            f"@{message.from_user.username}"
            if message.from_user and message.from_user.username
            else "None"
        )

        group_extra = await get_group_extra(chat_id)

        logger_text = f"""
<b>❖ {app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>● ᴄʜᴀᴛ ɪᴅ ➠</b> <code>{chat_id}</code>
<b>● ᴄʜᴀᴛ ɴᴀᴍᴇ ➠</b> {chat_title}
<b>● ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ➠</b> {chat_username}
{group_extra}
<b>● ᴜsᴇʀ ɪᴅ ➠</b> <code>{user_id}</code>
<b>● ɴᴀᴍᴇ ➠</b> {user_mention}
<b>● ᴜsᴇʀɴᴀᴍᴇ ➠</b> {user_username}

<b>● ǫᴜᴇʀʏ ➠</b> {query}
<b>● sᴛʀᴇᴀᴍᴛʏᴘᴇ ➠</b> {streamtype}"""

        if chat_id != LOGGER_ID:
            try:
                await app.send_message(
                    chat_id=LOGGER_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception:
                pass

        return


async def track_logs(chat_id, title, vidid, source, user=None):
    """Recommend / Autoplay se gaana chalne par LOGGER group me log bhejta hai.
    Title YouTube link ke saath clickable hota hai."""
    try:
        if not await is_on_off(2):
            return
        if chat_id == LOGGER_ID:
            return

        try:
            chat = await app.get_chat(chat_id)
            chat_title = chat.title or "Private Chat"
            chat_username = f"@{chat.username}" if chat.username else "None"
        except Exception:
            chat_title, chat_username = "Unknown", "None"

        group_extra = await get_group_extra(chat_id)

        link = f"https://www.youtube.com/watch?v={vidid}"
        if user:
            user_block = (
                f"<b>● ᴜsᴇʀ ɪᴅ ➠</b> <code>{user.id}</code>\n"
                f"<b>● ɴᴀᴍᴇ ➠</b> {user.mention}\n"
                f"<b>● ᴜsᴇʀɴᴀᴍᴇ ➠</b> "
                f"{'@' + user.username if user.username else 'None'}\n\n"
            )
        else:
            user_block = "<b>● ᴜsᴇʀ ➠</b> ᴀᴜᴛᴏᴘʟᴀʏ (ʙᴏᴛ)\n\n"

        text = (
            f"<b>❖ {app.mention} ᴘʟᴀʏ ʟᴏɢ</b>\n\n"
            f"<b>● ᴄʜᴀᴛ ɪᴅ ➠</b> <code>{chat_id}</code>\n"
            f"<b>● ᴄʜᴀᴛ ɴᴀᴍᴇ ➠</b> {chat_title}\n"
            f"<b>● ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ➠</b> {chat_username}\n"
            f"{group_extra}\n"
            f"{user_block}"
            f"<b>● ᴛɪᴛʟᴇ ➠</b> <a href=\"{link}\">{html.escape(title or 'Unknown')}</a>\n"
            f"<b>● sᴛʀᴇᴀᴍᴛʏᴘᴇ ➠</b> {source}"
        )
        await app.send_message(
            chat_id=LOGGER_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        pass
