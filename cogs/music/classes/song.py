from dataclasses import dataclass

import asyncio
import logging
import json
import os

import aiohttp
import yt_dlp

@dataclass(frozen=True)
class Song:
    source: str
    title: str
    author: str
    url: str
    thumbnail: str

    def __str__(self) -> str:
        return self.title

async def fetch_track(query: str, loop: asyncio.BaseEventLoop) -> Song:
        """Process query and returns a song instance"""
        # Logger
        logger = logging.getLogger("yaemiko.music.song")
        # Skip process if user passed a youtube URL
        if query.startswith("https://www.youtube.com/watch?v="):
            src = query
        # Otherwise, process query to get a yotuube link
        else:
            search_url = "https://www.youtube.com/results?search_query="
            for key in query.split():
                search_url += f"{key}+"
            search_url = search_url[:-1]

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    html = await response.text()

            src = "https://www.youtube.com/"
            for i in range(html.find("watch?v"), len(html)):
                if html[i] == '"':
                    break
                src += html[i]

        with open(os.path.join(os.path.dirname(__file__), '..', 'ydl_options.json'), 'r') as f:
            YDL_OPTIONS = json.load(f)
        
        ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(src, download = False))

        logger.debug(f"Fetched video data for query: '{query}'")

        title = data["title"]
        channel = data["uploader"]
        url = "https://www.youtube.com/watch?v=" + data["id"]
        thumbnail = data["thumbnail"]

        return Song(data["url"], title, channel, url, thumbnail)
