import logging
import asyncio
from typing import Dict, List, Union, Optional

import discord
from discord.ext import commands
from . import song, ui

logger = logging.getLogger("musicplayer")

Song = song.Song
fetch_track = song.fetch_track

class Player:
    def __init__(self, ctx: discord.ext.commands.Context) -> None:
        self.__ctx         : commands.Context           = ctx
        self.__queue       : List[Song]                 = []
        self.__is_playing  : bool                       = False
        self.__now_playing : Song                       = None
        self.__last_song   : Song                       = None
        self.__volume      : float                      = 1.0
        self.__ui          : ui.PlayerUI                = ui.PlayerUI()
        self.__FFMPEG_OPTS : Dict[str, str]             = {
            "options": "-vn -loglevel quiet -hide_banner -nostats",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"
        }

    # Extended attributes
    @property
    def channel(self) -> discord.TextChannel:
        """Fetch channel the player was created from"""
        return self.__ctx.channel

    @property
    def is_playing(self) -> bool:
        """Check if player state is playing"""
        return self.__is_playing

    @property
    def last_song(self) -> Song:
        """Returns the song that was played previously"""
        return self.__last_song

    @property
    def loop(self) -> asyncio.BaseEventLoop:
        """Returns the event loop"""
        return self.__ctx.bot.loop

    @property
    def now_playing(self) -> Song:
        """Fetch currently playing song"""
        return self.__now_playing

    @property
    def queue(self) -> List[Song]:
        """Fetch current player queue"""
        tracklist = []
        overflow = 0

        if self.__now_playing:
            tracklist.append(self.__now_playing)

        if len(self.__queue) > 0:
            for song in self.__queue:
                if overflow < 15:
                    tracklist.append(song)

        return tracklist

    @property
    def volume(self) -> float:
        """Fetch player volume"""
        return self.__volume

    def play_song(self) -> None:
        """Handles audio streaming to Discord"""
        try:
            self.__last_song = self.__now_playing
            self.__now_playing = self.__queue.pop(0)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    self.__now_playing.source,
                    **self.__FFMPEG_OPTS
                ),
                volume = self.__volume
            )

            for i in range(1, 3 + 1):
                self.__ctx.voice_client.play(source, after = lambda error: self.play_song())
                if self.__ctx.voice_client.is_playing():
                    logger.debug(f"Playback failed. Retry: {i} (ID: {self.__ctx.guild.id})")
                    break

            self.__is_playing = True
            self.loop.create_task(self.__ui.render_screen(self, self.channel, self.now_playing))
            logger.debug(f"Transitioned to next song in the queue (ID: {self.__ctx.guild.id})")
        except IndexError: # Expected error when there are no more tracks in queue
            self.__now_playing = None
            self.__is_playing = False
            self.loop.create_task(self.__ui.remove_controls())
            logger.debug(f"Playback failed, queue might be empty (ID: {self.__ctx.guild.id})")

        return self.__now_playing

    async def play(self, query: str) -> Dict[str, Union[bool, Song]]:
        """Entry point for playing audio"""
        for i in range(1, 3 + 1):
            song = await fetch_track(query, self.loop)

            if song:
                logger.debug(f"Video data fetched (ID: {self.__ctx.guild.id})")
                break

            logger.debug(f"Failed to fetch song data. Retry: {i} (ID: {self.__ctx.guild.id})")

        if song:
            self.__queue.append(song)
            await self.__ui.refresh_controls(self)
            logger.debug(f"Queued track (ID: {self.__ctx.guild.id})")

        if not self.__is_playing and song:
            logger.debug(f"Started playback (ID: {self.__ctx.guild.id})")
            song = self.play_song()

        return song

    # Player controls
    def set_volume(self, volume: int) -> float:
        """Set player volume"""
        volume = volume if volume in range (1, 100 + 1) else 100
        self.__volume = volume / 100
        self.__ctx.voice_client.source.volume = float(self.__volume)
        return self.__volume

    def dequeue(self, index: int) -> Song:
        """Remove an item from the queue"""
        return self.__queue.pop(int(index)- 1)

    async def skip(self) -> Union[Song, None]:
        """Skip currently playing song"""
        if self.__is_playing:
            self.__ctx.voice_client.stop()
            await self.__ui.refresh_controls(self)
            logger.debug(f"Skippped to next track (ID: {self.__ctx.guild.id})")
            return self.now_playing

    async def prev(self) -> Union[Song, None]:
        """Play the previous song"""
        if self.__is_playing and self.__last_song:
            self.__queue.insert(0, self.__last_song)
            self.__last_song = None
            self.__ctx.voice_client.stop()
            await self.__ui.refresh_controls(self)
            logger.debug(f"Skipped to previous track (ID: {self.__ctx.guild.id})")
            return self.now_playing

    async def pause(self) -> Union[Song, None]:
        """Pauses playback of current song"""
        if self.__is_playing:
            self.__is_playing = False
            self.__ctx.voice_client.pause()
            await self.__ui.refresh_controls(self, paused=True)
            logger.debug(f"Paused playback (ID: {self.__ctx.guild.id})")
            return self.now_playing

    async def resume(self) -> Union[Song, None]:
        """Resumes playback of current song"""
        if not self.__is_playing:
            self.__is_playing = True
            self.__ctx.voice_client.resume()
            await self.__ui.refresh_controls(self)
            logger.debug(f"Resumed playback (ID: {self.__ctx.guild.id})")
            return self.now_playing

    async def stop(self) -> Union[Song, None]:
        """Stop audio stream"""
        if self.__is_playing:
            song = self.__now_playing
            self.__now_playing = None
            self.__queue.clear()
            logger.debug(f"Cleared queue (ID: {self.__ctx.guild.id})")
            self.__ctx.voice_client.stop()
            logger.debug(f"Stopped playback (ID: {self.__ctx.guild.id})")
            await self.__ui.remove_controls()

            return song
