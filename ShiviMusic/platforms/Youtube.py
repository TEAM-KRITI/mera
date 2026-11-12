import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
import aiohttp
 
from ShiviMusic import app
from config import ARC_API_URL, ARC_API_KEY
 
 
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))
 
 
async def _arc_request_download(video_id: str, is_video: bool) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{ARC_API_URL.rstrip('/')}/youtube/v2/download",
            params={"query": video_id, "isVideo": str(is_video).lower(), "api_key": ARC_API_KEY},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            if resp.status != 200:
                return {}
            return await resp.json(content_type=None)
 
 
async def _arc_poll_job(job_id: str, retries: int = 15, interval: int = 3) -> str | None:
    async with aiohttp.ClientSession() as session:
        for _ in range(retries):
            async with session.get(
                f"{ARC_API_URL.rstrip('/')}/youtube/jobStatus",
                params={"job_id": job_id, "api_key": ARC_API_KEY},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    job = data.get("job", {})
                    if job.get("status") == "done":
                        return job.get("result", {}).get("cdn")
                    if job.get("status") == "error":
                        return None
            await asyncio.sleep(interval)
    return None
 
 
async def _arc_get_cdn(video_id: str, is_video: bool) -> str | None:
    data = await _arc_request_download(video_id, is_video)
    if not data:
        return None
 
    job_id = data.get("job_id")
    if not job_id:
        return data.get("result", {}).get("cdn")
 
    return await _arc_poll_job(job_id)
 
 
async def _save_from_cdn(cdn: str, file_path: str) -> bool:
    match = re.match(r"https?://(?:t\.me|telegram\.dog)/([^/]+)/(\d+)", cdn)
    if match:
        username, message_id = match.group(1), int(match.group(2))
        msg = await app.get_messages(username, message_id)
        if not msg or not (msg.audio or msg.video or msg.document):
            return False
        downloaded = await app.download_media(msg, file_name=file_path)
        return bool(downloaded)
 
    async with aiohttp.ClientSession() as session:
        async with session.get(cdn, timeout=aiohttp.ClientTimeout(total=600)) as resp:
            if resp.status != 200:
                return False
            with open(file_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(131072):
                    f.write(chunk)
    return True
 
 
async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
 
    os.makedirs("downloads", exist_ok=True)
    file_path = os.path.join("downloads", f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path
 
    try:
        cdn = await _arc_get_cdn(video_id, is_video=False)
        if not cdn:
            return None
 
        if not await _save_from_cdn(cdn, file_path):
            return None
 
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None
 
 
async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None
 
    os.makedirs("downloads", exist_ok=True)
    file_path = os.path.join("downloads", f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path
 
    try:
        cdn = await _arc_get_cdn(video_id, is_video=True)
        if not cdn:
            return None
 
        if not await _save_from_cdn(cdn, file_path):
            return None
 
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        return None
 
 
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
 
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))
 
    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None
 
    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid
 
    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]
 
    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]
 
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
 
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"
 
    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids
 
    async def _exact_info(self, vidid: str):
        """Last fallback: yt_dlp se exact video ka info (search par bharosa nahi)."""

        def _run():
            opts = {"quiet": True, "skip_download": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(self.base + vidid, download=False)

        info = await asyncio.get_event_loop().run_in_executor(None, _run)
        if not info or info.get("id") != vidid:
            return None
        secs = info.get("duration")
        if secs:
            secs = int(secs)
            h, m, sec = secs // 3600, secs % 3600 // 60, secs % 60
            dur = f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"
        else:
            dur = "0:00"
        return {
            "title": info.get("title") or vidid,
            "duration": dur,
            "id": vidid,
            "link": self.base + vidid,
            "thumbnails": [{"url": info.get("thumbnail") or f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg"}],
        }

    async def track(self, link: str, videoid: Union[bool, str] = None):
        expected = link if videoid else None  # exact video id (agar di gayi ho)
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        if expected is None:
            m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", link)
            expected = m.group(1) if m else None

        chosen = None
        if expected:
            # URL search kabhi-kabhi galat (doosre) video deta hai -> id match karo
            for q in (link, expected):
                items = (await VideosSearch(q, limit=8).next())["result"]
                chosen = next((r for r in items if r.get("id") == expected), None)
                if chosen:
                    break
            if not chosen:
                try:
                    chosen = await self._exact_info(expected)
                except Exception:
                    chosen = None
            if not chosen:
                raise ValueError(f"Exact video not found: {expected}")
        else:
            items = (await VideosSearch(link, limit=1).next())["result"]
            if not items:
                raise ValueError("No result found")
            chosen = items[0]

        title = chosen["title"]
        duration_min = chosen["duration"]
        vidid = chosen["id"]
        yturl = chosen["link"]
        thumbnail = chosen["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link
 
    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid
 
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            return None, False
        except Exception:
            return None, False
 
YouTube = YouTubeAPI()
