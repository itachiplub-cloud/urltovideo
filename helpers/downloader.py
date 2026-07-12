import os
import re
import json
import subprocess
import yt_dlp
import asyncio
from config import DOWNLOAD_DIR, CACHE_DIR
from helpers.utils import sanitize_filename, format_duration, generate_unique_id


def extract_info_sync(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        raise Exception(f"Failed to extract info: {str(e)}")


async def extract_info(url: str) -> dict:
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, extract_info_sync, url)
    if not info:
        raise Exception("Could not extract video information")

    duration = info.get("duration", 0)
    title = info.get("title", "Unknown")
    uploader = info.get("uploader", "Unknown")
    thumbnail = info.get("thumbnail", None)
    formats = info.get("formats", [])

    available_qualities = []
    seen_heights = set()

    for f in formats:
        height = f.get("height")
        vcodec = f.get("vcodec", "none")
        if height and vcodec != "none" and height not in seen_heights:
            seen_heights.add(height)
            available_qualities.append(height)

    available_qualities.sort()

    quality_map = {
        2160: "🎥 2160p (4K)",
        1440: "🎥 1440p (2K)",
        1080: "🎥 1080p",
        720: "🎥 720p",
        480: "🎥 480p",
        360: "🎥 360p",
        240: "🎥 240p",
        144: "🎥 144p",
    }

    qualities = []
    for h in available_qualities:
        label = quality_map.get(h, f"🎥 {h}p")
        qualities.append({
            "height": h,
            "label": label,
            "callback": f"quality_{h}"
        })

    has_audio = any(f.get("acodec", "none") != "none" for f in formats)
    has_video = any(f.get("vcodec", "none") != "none" for f in formats)

    if has_audio and not has_video:
        qualities = [{"height": 0, "label": "🎵 Audio MP3", "callback": "quality_audio"}]
    else:
        qualities.append({"height": 0, "label": "🎵 Audio MP3", "callback": "quality_audio"})

    return {
        "title": title,
        "duration": duration,
        "duration_str": format_duration(duration),
        "uploader": uploader,
        "thumbnail": thumbnail,
        "qualities": qualities,
        "url": url,
    }


def download_video_sync(url: str, height: int, output_path: str, progress_callback=None) -> str:
    if height == 0:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'progress_hooks': [progress_callback] if progress_callback else [],
            'quiet': True,
            'no_warnings': True,
        }
    else:
        format_str = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
        ydl_opts = {
            'format': format_str,
            'merge_output_format': 'mp4',
            'outtmpl': output_path + '.%(ext)s',
            'progress_hooks': [progress_callback] if progress_callback else [],
            'quiet': True,
            'no_warnings': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for ext in ['mp4', 'webm', 'mkv', 'mp3', 'opus', 'm4a', 'ogg']:
            fpath = f"{output_path}.{ext}"
            if os.path.exists(fpath):
                return fpath

        for f in os.listdir(os.path.dirname(output_path)):
            if f.startswith(os.path.basename(output_path)):
                return os.path.join(os.path.dirname(output_path), f)

        raise Exception("Download completed but file not found")
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")


async def download_video(url: str, height: int, user_id: int, title: str) -> str:
    unique_id = generate_unique_id(user_id, url)
    safe_title = sanitize_filename(title)[:50]
    output_path = os.path.join(DOWNLOAD_DIR, str(user_id), f"{unique_id}_{safe_title}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: download_video_sync(url, height, output_path)
    )
    return result


async def get_thumbnail(url: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"thumb_{hash(url) % 10000}.jpg")
    if os.path.exists(cache_path):
        return cache_path

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'write_thumbnail': True,
        'outtmpl': cache_path.replace('.jpg', ''),
    }

    try:
        loop = asyncio.get_event_loop()
        def _dl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, _dl)

        for ext in ['jpg', 'webp', 'png']:
            p = f"{cache_path.replace('.jpg', '')}.{ext}"
            if os.path.exists(p):
                if ext != 'jpg':
                    os.rename(p, cache_path)
                return cache_path

        return None
    except Exception:
        return None
