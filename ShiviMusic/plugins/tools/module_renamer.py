# ===========================================================
# 🧩 MODULE RENAMER  (OWNER ONLY)
#
# GitHub repo ke andar main module/package folder ka naam badalta hai
# (jaise  ShiviMusic -> NayaNaam)  aur poore repo me uske imports /
# references bhi update kar deta hai. Chahe to repo ka naam bhi saath
# me change ho jata hai.
#
#   /gitconfig <name> <email> <token>          (pehle config set karo)
#   /renamemodule <repo> <old_module> <new_module> [new_repo_name]
#   alias: /rnmodule
#
# Misal:
#   /renamemodule TEAM-KRITI/Bittu- ShiviMusic KirtiMusic
#   /renamemodule Bittu- ShiviMusic KirtiMusic KirtiMusicBot
#
# Ye ek hi naya commit banata hai (purana commit sha reply me milta hai,
# galti ho to usi par wapas ja sakte ho).
# ===========================================================

import asyncio
import base64
import re

from github import Github, GithubException, InputGitTreeElement
from pyrogram import filters

from config import OWNER_ID
from ShiviMusic import app
from ShiviMusic.plugins.tools.repo_upload import TEMP_CONFIG, config_valid

_TEXT_EXT = {
    ".py", ".txt", ".md", ".yml", ".yaml", ".json", ".sh", ".toml", ".cfg",
    ".ini", ".env", ".example", ".sample", ".html", ".js", ".service", ".conf",
}
_TEXT_NAMES = {
    "dockerfile", "procfile", "makefile", ".gitignore", ".dockerignore",
    "runtime.txt", "app.json", "heroku.yml",
}
_MAX_TEXT = 1_000_000  # 1 MB se bade files ko text nahi maante
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _is_text(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower()
    if name in _TEXT_NAMES:
        return True
    dot = name.rfind(".")
    return dot != -1 and name[dot:] in _TEXT_EXT


def _resolve_repo(g: Github, name: str):
    login = g.get_user().login
    if "/" in name:
        candidates = [name]
    else:
        owners = []
        for o in (TEMP_CONFIG.get("name"), login):
            if o and o not in owners:
                owners.append(o)
        candidates = [f"{o}/{name}" for o in owners]
    for full in candidates:
        try:
            return g.get_repo(full)
        except GithubException as e:
            if e.status != 404:
                raise
    try:
        names = [r.full_name for r in g.get_user().get_repos()[:15]]
    except Exception:
        names = []
    raise LookupError(
        "Repo not found: " + ", ".join(candidates)
        + ("\nAvailable: " + ", ".join(names) if names else "")
    )


def _rename_module(repo, old: str, new: str):
    """Module folder rename + references update, ek commit me.
    Returns (files_moved, files_edited, old_commit_sha, new_commit_sha, branch)."""
    branch = repo.default_branch
    ref = repo.get_git_ref(f"heads/{branch}")
    base_commit = repo.get_git_commit(ref.object.sha)
    tree = repo.get_git_tree(base_commit.tree.sha, recursive=True)
    if tree.raw_data.get("truncated"):
        raise RuntimeError("Repo bahut bada hai (GitHub tree truncated).")

    paths = [t.path for t in tree.tree]
    if not any(p.startswith(old + "/") for p in paths):
        tops = sorted({p.split("/")[0] for p in paths if "/" in p})
        raise LookupError(
            f"Module folder '{old}' repo me nahi mila.\nTop folders: " + ", ".join(tops)
        )
    if any(p == new or p.startswith(new + "/") for p in paths):
        raise ValueError(f"'{new}' naam ka folder pehle se maujood hai.")

    # old naam ko poore word ki tarah replace karo (ShiviMusicBot jaisa naam na tute)
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")

    elements, moved, edited = [], 0, 0
    for item in tree.tree:
        if item.type == "tree":
            continue  # folders implicit hain
        path, sha = item.path, item.sha
        in_module = path.startswith(old + "/")
        new_path = new + path[len(old):] if in_module else path

        if item.type == "blob" and _is_text(path) and (item.size or 0) <= _MAX_TEXT:
            blob = repo.get_git_blob(sha)
            raw = (
                base64.b64decode(blob.content)
                if blob.encoding == "base64"
                else blob.content.encode()
            )
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = None
            if text is not None:
                new_text = pattern.sub(new, text)
                if new_text != text:
                    sha = repo.create_git_blob(new_text, "utf-8").sha
                    edited += 1

        if in_module:
            moved += 1
        # submodule (type=commit) ho ya blob: sha reuse hota hai, binary files
        # dobara upload nahi hoti
        elements.append(InputGitTreeElement(new_path, item.mode, item.type, sha=sha))

    # base_tree nahi dete -> purane paths apne aap hat jaate hain
    new_tree = repo.create_git_tree(elements)
    commit = repo.create_git_commit(
        f"Rename module {old} -> {new}", new_tree, [base_commit]
    )
    ref.edit(commit.sha)
    return moved, edited, base_commit.sha, commit.sha, branch


@app.on_message(filters.command(["renamemodule", "rnmodule"]) & filters.user(OWNER_ID))
async def renamemodule(client, message):
    # Sirf OWNER_ID (filters.user(OWNER_ID))
    if len(message.command) < 4:
        return await message.reply(
            "**» ᴜsᴀɢᴇ :-**\n"
            "`/renamemodule <repo> <old_module> <new_module> [new_repo_name]`\n\n"
            "**ᴇx :-** `/renamemodule TEAM-KRITI/Bittu- ShiviMusic KirtiMusic`"
        )

    if not config_valid():
        return await message.reply(
            "**⚠️ ᴄᴏɴꜰɪɢ ᴇxᴘɪʀᴇᴅ ᴏʀ ɴᴏᴛ sᴇᴛ!**\n\n**» ᴘʟᴇᴀsᴇ ʀᴜɴ** `/gitconfig` **ғɪʀsᴛ.**"
        )

    repo_name, old, new = (message.command[i].strip() for i in (1, 2, 3))
    new_repo = message.command[4].strip() if len(message.command) > 4 else None

    if not _IDENT.fullmatch(new):
        return await message.reply(
            "⚠️ **ɪɴᴠᴀʟɪᴅ ᴍᴏᴅᴜʟᴇ ɴᴀᴍᴇ!** ᴘʏᴛʜᴏɴ ᴘᴀᴄᴋᴀɢᴇ ᴋɪ ᴛᴀʀᴀʜ — sɪʀғ ʟᴇᴛᴛᴇʀs, "
            "ɴᴜᴍʙᴇʀs ᴀᴜʀ `_` (ɴᴜᴍʙᴇʀ sᴇ sʜᴜʀᴜ ɴᴀʜɪ)."
        )
    if old == new:
        return await message.reply("⚠️ **ᴏʟᴅ ᴀᴜʀ ɴᴇᴡ ɴᴀᴀᴍ sᴀᴍᴇ ʜᴀɪɴ!**")
    if new_repo and not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", new_repo):
        return await message.reply("⚠️ **ɪɴᴠᴀʟɪᴅ ʀᴇᴘᴏ ɴᴀᴍᴇ!**")

    status = await message.reply("**⏳ ᴍᴏᴅᴜʟᴇ ʀᴇɴᴀᴍɪɴɢ... (ᴇᴋ ᴍɪɴᴜᴛ ʟᴀɢ sᴀᴋᴛᴀ ʜᴀɪ)**")

    def _work():
        g = Github(TEMP_CONFIG["token"])
        repo = _resolve_repo(g, repo_name)
        result = _rename_module(repo, old, new)
        url = repo.html_url
        if new_repo:
            repo.edit(name=new_repo)
            url = repo.html_url
        return result, url

    try:
        loop = asyncio.get_running_loop()
        (moved, edited, old_sha, new_sha, branch), url = await loop.run_in_executor(
            None, _work
        )
    except (LookupError, ValueError) as e:
        await status.delete()
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{e}`")
    except GithubException as e:
        await status.delete()
        msg = e.data.get("message", str(e)) if isinstance(e.data, dict) else str(e)
        if e.status in (401, 403):
            msg += " (token invalid ya write/admin permission nahi hai)"
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{msg}`")
    except Exception as e:
        await status.delete()
        return await message.reply(f"❌** ᴇʀʀᴏʀ :-** `{e}`")

    await status.delete()
    await message.reply(
        "✅ **ᴍᴏᴅᴜʟᴇ ʀᴇɴᴀᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n"
        f"📦 **ᴍᴏᴅᴜʟᴇ :-** `{old}` ➜ `{new}`\n"
        + (f"📛 **ʀᴇᴘᴏ :-** `{new_repo}`\n" if new_repo else "")
        + f"📁 **ғɪʟᴇs ᴍᴏᴠᴇᴅ :-** `{moved}`   ✏️ **ᴇᴅɪᴛᴇᴅ :-** `{edited}`\n"
        f"🌿 **ʙʀᴀɴᴄʜ :-** `{branch}`\n"
        f"↩️ **ᴘʀᴇᴠɪᴏᴜs ᴄᴏᴍᴍɪᴛ :-** `{old_sha[:7]}`\n\n"
        f"🔗 {url}\n\n"
        "**» ɴᴏᴛᴇ :-** ʙᴏᴛ ᴋᴀ ʟᴏᴄᴀʟ ᴄᴏᴅᴇ ɴᴀʜɪ ʙᴀᴅᴀʟᴛᴀ — ɴᴀʏᴀ ᴄᴏᴅᴇ `git pull` / ʀᴇᴅᴇᴘʟᴏʏ ᴋᴀʀᴏ."
    )
