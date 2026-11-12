import asyncio
import os
import shutil
import socket
from datetime import datetime

import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from ShiviMusic import app
from ShiviMusic.misc import HAPP, SUDOERS, XCB
from ShiviMusic.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from ShiviMusic.utils.decorators.language import language
from ShiviMusic.utils.pastebin import ShiviBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


@app.on_message(filters.command(["getlog", "logs", "getlogs"]) & SUDOERS)
@language
async def log_(client, message, _):
    try:
        await message.reply_document(document="log.txt")
    except Exception:
        await message.reply_text(_["server_1"])


@app.on_message(filters.command(["update", "gitpull"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["server_2"])

    response = await message.reply_text(_["server_3"])

    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["server_4"])
    except InvalidGitRepositoryError:
        return await response.edit(_["server_5"])
    except Exception as e:
        return await response.edit(
            f"❖ <b>Git Error:</b>\n<code>{e}</code>"
        )

    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} >/dev/null 2>&1"
    os.system(to_exc)

    await asyncio.sleep(2)

    verification = ""
    try:
        REPO_ = repo.remotes.origin.url.split(".git")[0]

        for checks in repo.iter_commits(
            f"HEAD..origin/{config.UPSTREAM_BRANCH}"
        ):
            verification = str(checks.count())

    except Exception as e:
        return await response.edit(
            f"❖ <b>Update Check Failed:</b>\n<code>{e}</code>"
        )

    if verification == "":
        return await response.edit(_["server_6"])

    updates = ""

    def ordinal(number):
        return "%d%s" % (
            number,
            "tsnrhtdd"[
                (number // 10 % 10 != 1)
                * (number % 10 < 4)
                * number % 10 :: 4
            ],
        )

    for info in repo.iter_commits(
        f"HEAD..origin/{config.UPSTREAM_BRANCH}"
    ):
        commit_date = datetime.fromtimestamp(info.committed_date)

        updates += (
            f"<b>➣ #{info.count()}: "
            f"<a href={REPO_}/commit/{info}>{info.summary}</a> "
            f"ʙʏ -> {info.author}</b>\n"
            f"\t\t\t\t<b>➥ ᴄᴏᴍᴍɪᴛᴛᴇᴅ ᴏɴ :</b> "
            f"{ordinal(int(commit_date.strftime('%d')))} "
            f"{commit_date.strftime('%b')}, "
            f"{commit_date.strftime('%Y')}\n\n"
        )

    _update_response_ = (
        "<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n"
        "➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n"
        "<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b>\n\n"
    )

    _final_updates_ = _update_response_ + updates

    # Telegram message limit
    if len(_final_updates_) > 4096:
        try:
            # FIX:
            # AarumiBin -> ShiviBin
            url = await ShiviBin(updates)

            nrs = await response.edit(
                f"<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n"
                f"➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n"
                f"<u><b>ᴜᴩᴅᴀᴛᴇs :</b></u>\n\n"
                f'<a href="{url}">ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs</a>',
                disable_web_page_preview=True,
            )

        except Exception as e:
            # Pastebin failure should not crash update command
            short_updates = updates[:3800]

            nrs = await response.edit(
                _update_response_
                + short_updates
                + "\n\n<b>⚠️ ᴜᴩᴅᴀᴛᴇ ʟɪsᴛ ᴡᴀs ᴛʀᴜɴᴄᴀᴛᴇᴅ.</b>"
            )

    else:
        nrs = await response.edit(
            _final_updates_,
            disable_web_page_preview=True,
        )

    # Pull latest changes
    os.system(f"git stash >/dev/null 2>&1; git pull origin {config.UPSTREAM_BRANCH}")

    try:
        served_chats = await get_active_chats()

        for x in served_chats:
            try:
                await app.send_message(
                    chat_id=int(x),
                    text=_["server_8"].format(app.mention),
                )

                await remove_active_chat(x)
                await remove_active_video_chat(x)

            except Exception:
                pass

        try:
            await response.edit(
                f"{nrs.text}\n\n{_['server_7']}"
            )
        except Exception:
            pass

    except Exception:
        pass

    # Heroku restart
    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}"
                f"{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}"
                f"{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}"
                f"{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}"
                f"{XCB[10]}{XCB[2]}{XCB[5]} "
                f"{XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return

        except Exception as err:
            try:
                await response.edit(
                    f"{nrs.text}\n\n{_['server_9']}"
                )
            except Exception:
                pass

            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=_["server_10"].format(err),
            )

    # VPS restart
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text(
        "ʀᴇsᴛᴀʀᴛɪɴɢ..."
    )

    ac_chats = await get_active_chats()

    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=(
                    f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\n"
                    "ʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ "
                    "ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs."
                ),
            )

            await remove_active_chat(x)
            await remove_active_video_chat(x)

        except Exception:
            pass

    # Clean temporary directories
    for folder in ["downloads", "raw_files", "cache"]:
        try:
            shutil.rmtree(folder)
        except Exception:
            pass

    try:
        await response.edit_text(
            "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, "
            "ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs "
            "ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
        )
    except Exception:
        pass

    os.system(
        f"kill -9 {os.getpid()} && bash start"
    )
