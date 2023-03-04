import logging
import asyncio
from typing import Dict, Union

import aiohttp
import yt_dlp

logger = logging.getLogger("musicplayer")

YDL_OPTIONS : Dict[str, Union[str, int]] = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0"
}

class Song:
    def __init__(self, source: str, title: str, author: str, url: str, thumbnail: str):
        self.source    : str = source
        self.title     : str = title
        self.author    : str = author
        self.url       : str = url
        self.thumbnail : str = thumbnail

async def fetch_track(query: str, loop: asyncio.BaseEventLoop) -> Song:
        """Process query and returns a song instance"""
        # skip process if user passed a youtube URL
        if query.startswith("https://www.youtube.com/watch?v="):
            src = query
            logger.debug(f"Received video URL '{query}', parsing skipped")
        # otherwise, process query to get a yotuube link
        else:
            search_url = "https://www.youtube.com/results?search_query="
            for key in query.split():
                search_url += f"{key}+"
            search_url = search_url[:-1]

            logger.debug(f"Parsed '{query}' query into YTSearch URL")

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    html = await response.text()
            logger.debug(f"Retrieved HTML data")

            src = "https://www.youtube.com/"
            for i in range(html.find("watch?v"), len(html)):
                if html[i] == '"':
                    break
                src += html[i]
        
        ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(src, download = False))
        logger.debug(f"Extracted video data from URL {src}")

        title = data["title"]
        channel = data["uploader"]
        url = "https://www.youtube.com/watch?v=" + data["id"]
        thumbnail = data["thumbnail"]

        return Song(data["url"], title, channel, url, thumbnail)
