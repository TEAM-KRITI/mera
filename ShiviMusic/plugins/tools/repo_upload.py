import os
import zipfile
import subprocess
import shutil
import time
import re
import asyncio
from pyrogram import filters
from ShiviMusic import app
from github import Github, GithubException
from config import OWNER_ID  

TEMP_DIR = "temp_repos"
os.makedirs(TEMP_DIR, exist_ok=True)

TEMP_CONFIG = {}

def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc.stdout

def safe_rm(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

def config_valid():
    if not TEMP_CONFIG:
        return False
    if time.time() - TEMP_CONFIG.get("timestamp", 0) > 300:
        TEMP_CONFIG.clear()
        return False
    return True


@app.on_message(filters.command("gitconfig") & filters.user(OWNER_ID))
async def gitconfig(client, message):
    if len(message.command) < 4:
        return await message.reply(
            "**» ᴜsᴀɢᴇ :-** `/gitconfig username email token`"
        )
    name = message.command[1]
    email = message.command[2]
    token = message.command[3]
    TEMP_CONFIG.update({"name": name, "email": email, "token": token, "timestamp": time.time()})
    await message.reply("✅ **ɢɪᴛʜᴜʙ ᴄᴏɴꜰɪɢ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!** (ᴠᴀʟɪᴅ ꜰᴏʀ **10 ᴍɪɴᴜᴛᴇs**)")


@app.on_message(filters.command(["gitupload", "gt"]) & filters.user(OWNER_ID))
async def gitupload(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "**» ᴜsᴀɢᴇ :-** `/gitupload repo_name private/public branch_name` **(ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴢɪᴘ ғɪʟᴇ)**"
        )

    if not config_valid():
        return await message.reply("**⚠️ ᴄᴏɴꜰɪɢ ᴇxᴘɪʀᴇᴅ ᴏʀ ɴᴏᴛ sᴇᴛ!**\n\n**» ᴘʟᴇᴀsᴇ ʀᴜɴ** `/gitconfig` **ғɪʀsᴛ.**")

    GITHUB_NAME = TEMP_CONFIG["name"]
    GITHUB_EMAIL = TEMP_CONFIG["email"]
    GITHUB_TOKEN = TEMP_CONFIG["token"]
    g = Github(GITHUB_TOKEN)

    repo_name = message.command[1]
    visibility = message.command[2].lower() if len(message.command) >= 3 else "public"
    is_private = visibility == "private"
    branch_name = message.command[3] if len(message.command) >= 4 else "main"

    replied = message.reply_to_message
    if not (replied and replied.document and replied.document.file_name.endswith(".zip")):
        return await message.reply("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ **ᴢɪᴘ** ғɪʟᴇ!")

    zip_path = os.path.join(TEMP_DIR, replied.document.file_name)
    extract_root = os.path.join(TEMP_DIR, f"{repo_name}_extract")
    final_path = os.path.join(TEMP_DIR, f"{repo_name}_final")

    safe_rm(zip_path)
    safe_rm(extract_root)
    safe_rm(final_path)


    status = await message.reply("**⏳ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇqᴜᴇsᴛ...**")

    try:
        await replied.download(file_name=zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_root)

        inner_items = os.listdir(extract_root)
        inner_dirs = [d for d in inner_items if os.path.isdir(os.path.join(extract_root, d))]
        inner_files = [f for f in inner_items if os.path.isfile(os.path.join(extract_root, f))]

        if len(inner_dirs) == 1 and not inner_files:
            shutil.move(os.path.join(extract_root, inner_dirs[0]), final_path)
        else:
            shutil.move(extract_root, final_path)

        for root, dirs, _ in os.walk(final_path):
            if ".git" in dirs:
                safe_rm(os.path.join(root, ".git"))

        user = g.get_user()
        repo = user.create_repo(repo_name, private=is_private, description="🎉 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ᴜᴘʟᴏᴀᴅ ʙʏ :- ᴋɪʀᴛɪ ʙᴏᴛs 🌺", auto_init=False)


        run(["git", "init"], cwd=final_path)
        run(["git", "config", "user.email", GITHUB_EMAIL], cwd=final_path)
        run(["git", "config", "user.name", GITHUB_NAME], cwd=final_path)
        remote_url = repo.clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
        run(["git", "remote", "add", "origin", remote_url], cwd=final_path)
        run(["git", "add", "."], cwd=final_path)

        status_out = subprocess.run(["git", "status", "--porcelain"], cwd=final_path, text=True, capture_output=True)
        if status_out.stdout.strip():
            run(["git", "commit", "-m", "ᴋɪʀᴛɪ ʙᴏᴛs !!"], cwd=final_path)
        else:
            run(["git", "commit", "--allow-empty", "-m", "ᴋɪʀᴛɪ ʙᴏᴛs !!"], cwd=final_path)

        run(["git", "branch", "-M", branch_name], cwd=final_path)
        run(["git", "push", "-u", "origin", branch_name], cwd=final_path)

    except Exception as e:
        safe_rm(zip_path)
        safe_rm(extract_root)
        safe_rm(final_path)
        await status.delete()
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{e}`")

    # Cleanup
    safe_rm(zip_path)
    safe_rm(extract_root)
    safe_rm(final_path)
    await status.delete()
    await message.reply(
        f"✅ **ʀᴇᴘᴏ** `{repo_name}` **ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        f"🔒 **ᴠɪsɪʙɪʟɪᴛʏ :-** `{'Private' if is_private else 'Public'}`\n"
        f"🌿 **ʙʀᴀɴᴄʜ :-** `{branch_name}`\n\n"
        f"🔗 **ᴜʀʟ :-** {repo.html_url}"
    )


@app.on_message(filters.command(["renamerepo", "rnrepo"]) & filters.user(OWNER_ID))
async def renamerepo(client, message):
    # Sirf OWNER_ID wala user hi use kar sakta hai (filters.user(OWNER_ID))
    if len(message.command) < 3:
        return await message.reply(
            "**» ᴜsᴀɢᴇ :-** `/renamerepo old_repo_name new_repo_name`"
        )

    if not config_valid():
        return await message.reply(
            "**⚠️ ᴄᴏɴꜰɪɢ ᴇxᴘɪʀᴇᴅ ᴏʀ ɴᴏᴛ sᴇᴛ!**\n\n**» ᴘʟᴇᴀsᴇ ʀᴜɴ** `/gitconfig` **ғɪʀsᴛ.**"
        )

    old_name = message.command[1].strip()
    new_name = message.command[2].strip()

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", new_name):
        return await message.reply(
            "⚠️ **ɪɴᴠᴀʟɪᴅ ɴᴀᴍᴇ!** ᴏɴʟʏ ʟᴇᴛᴛᴇʀs, ɴᴜᴍʙᴇʀs, `-`, `_` ᴀɴᴅ `.` ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ."
        )

    status = await message.reply("**⏳ ʀᴇɴᴀᴍɪɴɢ ʀᴇᴘᴏ...**")

    def _rename():
        g = Github(TEMP_CONFIG["token"])
        login = g.get_user().login

        # Repo kisi bhi owner (user ya org) ke under ho sakta hai:
        # 1) full "owner/repo" diya ho to wahi
        # 2) warna /gitconfig wala username/org, phir token wale account ke under
        if "/" in old_name:
            candidates = [old_name]
        else:
            owners = []
            for o in (TEMP_CONFIG.get("name"), login):
                if o and o not in owners:
                    owners.append(o)
            candidates = [f"{o}/{old_name}" for o in owners]

        repo = None
        for full in candidates:
            try:
                repo = g.get_repo(full)
                break
            except GithubException as e:
                if e.status != 404:
                    raise

        if repo is None:
            try:
                names = [r.full_name for r in g.get_user().get_repos()[:15]]
            except Exception:
                names = []
            raise LookupError(
                "Repo not found: " + ", ".join(candidates)
                + ("\nAvailable: " + ", ".join(names) if names else "")
            )

        repo.edit(name=new_name)
        return repo.html_url

    try:
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(None, _rename)
    except LookupError as e:
        await status.delete()
        return await message.reply(
            f"❌** ʀᴇᴘᴏ ɴᴏᴛ ꜰᴏᴜɴᴅ!**\n\n`{e}`\n\n"
            "**» ᴛɪᴘ :-** `/renamerepo owner/repo new_name` ᴜsᴇ ᴋᴀʀᴏ, ᴀᴜʀ ᴛᴏᴋᴇɴ ᴍᴇɪɴ `repo` ssᴄᴏᴘᴇ ʜᴏɴᴀ ᴄʜᴀʜɪʏᴇ."
        )
    except GithubException as e:
        await status.delete()
        msg = e.data.get("message", str(e)) if isinstance(e.data, dict) else str(e)
        if e.status in (401, 403):
            msg += " (token invalid ya admin permission nahi hai)"
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{msg}`")
    except Exception as e:
        await status.delete()
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{e}`")

    await status.delete()
    await message.reply(
        f"✅ **ʀᴇᴘᴏ ʀᴇɴᴀᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        f"📛 **ᴏʟᴅ :-** `{old_name}`\n"
        f"🆕 **ɴᴇᴡ :-** `{new_name}`\n\n"
        f"🔗 **ᴜʀʟ :-** {url}"
    )
