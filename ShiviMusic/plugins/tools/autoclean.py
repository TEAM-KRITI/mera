# Auto clean: har 1 ghante me cache / downloads / playback (speed) files delete karta hai
# aur LOGGER_ID me report bhejta hai. Chal rahe (active) gaane ki files delete nahi hoti.

import asyncio
import os
import shutil
import time

import psutil

import config
from config import LOGGER_ID, autoclean
from ShiviMusic import LOGGER, app

CLEAN_INTERVAL = 60 * 60   # 1 hour
MIN_FILE_AGE = 5 * 60      # 5 min se nayi files (download ho rahi) ko haath nahi lagana

FOLDERS = [
    ("cache", "🖼️", "thumbnails"),
    ("downloads", "🎵", "downloads"),
    ("playback", "⚡", "speed files"),
]


def _protected_files() -> set:
    keep = set()
    try:
        from ShiviMusic.misc import db

        for queue in db.values():
            for track in queue:
                for key in ("file", "speed_path"):
                    path = track.get(key)
                    if path:
                        keep.add(os.path.abspath(str(path)))
    except Exception:
        pass
    for path in autoclean:
        keep.add(os.path.abspath(str(path)))
    return keep


def _clean_sync():
    keep = _protected_files()
    now = time.time()
    report = {}
    for folder, _, _ in FOLDERS:
        count, size = 0, 0
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for name in files:
                    path = os.path.join(root, name)
                    try:
                        if os.path.abspath(path) in keep:
                            continue
                        if now - os.path.getmtime(path) < MIN_FILE_AGE:
                            continue
                        fsize = os.path.getsize(path)
                        os.remove(path)
                        count += 1
                        size += fsize
                    except Exception:
                        continue
            # khali sub-folders hata do (top folder rehne do)
            for root, dirs, _ in os.walk(folder, topdown=False):
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except OSError:
                        pass
        report[folder] = (count, size)
    return report


async def run_auto_clean():
    report = await asyncio.to_thread(_clean_sync)
    total_files = sum(c for c, _ in report.values())
    total_mb = sum(s for _, s in report.values()) / 1048576
    disk = shutil.disk_usage("/")
    ram = psutil.Process(os.getpid()).memory_info().rss / 1048576

    lines = ["🧹 <b>ᴀᴜᴛᴏ ᴄʟᴇᴀɴ • ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n"]
    for folder, emoji, label in FOLDERS:
        c, s = report[folder]
        lines.append(f"{emoji} <b>{label}</b> : {c} ꜰɪʟᴇs · {s / 1048576:.1f} ᴍʙ")
    lines += [
        f"\n✅ <b>ꜰʀᴇᴇᴅ</b> : {total_files} ꜰɪʟᴇs · {total_mb:.1f} ᴍʙ",
        f"💾 <b>ᴅɪsᴋ</b> : {disk.used / 1048576:.1f} ᴍʙ / {disk.total / 1048576:.1f} ᴍʙ",
        f"🧠 <b>ʀᴀᴍ</b> : {ram:.1f} ᴍʙ",
        f"⏰ <b>ɴᴇxᴛ ᴄʟᴇᴀɴ</b> : {CLEAN_INTERVAL // 3600}ʜ",
    ]
    try:
        await app.send_message(LOGGER_ID, "\n".join(lines))
    except Exception as e:
        LOGGER(__name__).error(f"Auto clean report failed: {e}")


async def _auto_clean_loop():
    while True:
        await asyncio.sleep(CLEAN_INTERVAL)
        try:
            await run_auto_clean()
        except Exception as e:
            LOGGER(__name__).error(f"Auto clean failed: {e}")


asyncio.create_task(_auto_clean_loop())
