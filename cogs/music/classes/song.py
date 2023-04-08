from dataclasses import dataclass
from typing import Union
import aiohttp
import json
import logging
import os
import yt_dlp

@dataclass(frozen=True)
class Song:
    source: str
    title: str
    author: str
    url: str
    thumbnail: str

async def fetch_track(query: str) -> Union[Song, None]:
        """Process query and returns a song instance"""
        logger = logging.getLogger("music.song")
        
        if query.startswith("https://www.youtube.com/watch?v="): # skip process if user passed a youtube URL
            src = query
            logger.debug(f"Received video URL '{query}', parsing skipped")
        else: # otherwise, process query to get a yotuube link
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

        with open(os.path.join(os.path.dirname(__file__), '..', 'ydl_options.json'), 'r') as f:
            YDL_OPTIONS = json.load(f)
        
        ytdl = yt_dlp.YoutubeDL(YDL_OPTIONS)
        data = ytdl.extract_info(src, download=False)
        if not data:
            logger.debug(f"Failed to extract video data from URL {src}")
            return
        
        logger.debug(f"Extracted video data from URL {src}")

        return Song(
            data["url"],
            data["title"],
            data["uploader"], "https://www.youtube.com/watch?v=" + data["id"],
            data["thumbnail"]
        )
