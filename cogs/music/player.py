import logging
import asyncio
from typing import Dict, List, Union

import discord
from discord.ext import commands

from .song import Song, fetch_track
from .ui import PlayerUI

logger = logging.getLogger("musicplayer")

class Player:
    def __init__(self, ctx: discord.ext.commands.Context) -> None:
        self.__ctx         : commands.Context           = ctx
        self.__channel     : discord.TextChannel        = ctx.channel
        self.__is_playing  : bool                       = False
        self.__now_playing : Song                       = None
        self.__queue       : List[Song]                 = []
        self.__history     : List[Song]                 = []
        self.__volume      : float                      = 1.0
        self.__ui          : PlayerUI                   = PlayerUI(self.channel)
        self.__FFMPEG_OPTS : Dict[str, str]             = {
            "options": "-vn -loglevel quiet -hide_banner -nostats",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"
        }

    # Extended attributes
    @property
    def FFMPEG_OPTS(self) -> Dict[str, str]:
        """Return ffmpeg options"""
        return self.__FFMPEG_OPTS
    
    @property
    def channel(self) -> discord.TextChannel:
        """Return player channel"""
        return self.__channel

    @property
    def ctx(self) -> commands.Context:
        """Returns the player context"""
        return self.__ctx

    @property
    def channel(self) -> discord.TextChannel:
        """Fetch channel the player was created from"""
        return self.__ctx.channel

    @property
    def is_playing(self) -> bool:
        """Check if player state is playing"""
        return self.__is_playing
    
    @is_playing.setter
    def is_playing(self, state: bool) -> None:
        self.__is_playing = state

    @property
    def history(self) -> Song:
        """Returns the song that was played previously"""
        return self.__history

    def append_history(self, song: Song) -> None:
        """Append song to history"""
        if not song:
            return
        
        self.__history.append(song)

    @property
    def loop(self) -> asyncio.BaseEventLoop:
        """Returns the event loop"""
        return self.__ctx.bot.loop

    @property
    def now_playing(self) -> Song:
        """Fetch currently playing song"""
        return self.__now_playing
    
    @now_playing.setter
    def now_playing(self, song: Song) -> None:
        """Set currently playing song"""
        if not song:
            return
        
        self.__now_playing = song

    @property
    def queue(self) -> List[Song]:
        """Fetch current player queue"""
        tracklist = []

        if self.__now_playing:
            tracklist.append(self.__now_playing)

        if len(self.__queue) > 0:
            for song in self.__queue:
                tracklist.append(song)

        return tracklist
    
    def enqueue(self, song: Song) -> None:
        """Add a song to the queue"""
        if not song:
            return
        
        self.__queue.append(song)

    def dequeue(self, index: int = 0) -> Song:
        if len(self.queue) < 1 and index in range(0, len(self.queue)):
            return
        
        return self.__queue.pop(index)

    @property
    def volume(self) -> float:
        """Fetch player volume"""
        return self.__volume
    
    @volume.setter
    def volume(self, value: int) -> None:
        if not value in range( 1, 100 + 1):
            return
        
        self.__volume = float(value / 100)

    @property
    def ui(self) -> PlayerUI:
        return self.__ui
    
    def update_ui(self) -> None:
        self.loop.create_task(self.ui.render_np(
            self.now_playing,
            self.is_playing,
            onPlay=self.resume if not self.is_playing else None,
            onPause=self.pause if self.is_playing else None,
            onPrev=self.prev if len(self.history) > 0 else None,
            onSkip=self.skip if len(self.queue) - 1 > 0 else None,
            onStop=self.stop
        ))

    def play_song(self) -> None:
        """Handles audio streaming to Discord"""
        try:
            if self.now_playing:
                self.append_history(self.now_playing)

            self.now_playing = self.dequeue()

            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    self.now_playing.source,
                    **self.FFMPEG_OPTS
                ),
                volume = self.volume
            )

            for i in range(1, 3 + 1):
                self.ctx.voice_client.play(source, after = lambda error: self.play_song())

                if not self.ctx.voice_client.is_playing():
                    logger.debug(f"Playback failed. Retry: {i} (ID: {self.ctx.guild.id})")
                    continue
                break

            self.is_playing = True

            self.update_ui()

            logger.debug(f"Transitioned to next song in the queue (ID: {self.ctx.guild.id})")
        # Expected error when there are no more tracks in queue
        except IndexError:
            self.now_playing = None
            self.is_playing = False

            logger.debug(f"Playback failed, queue might be empty (ID: {self.__ctx.guild.id})")

            # FIXME: update ui
            self.loop.create_task(self.ui.remove_controls())

        return self.now_playing

    async def play(self, query: str, interaction: discord.Interaction) -> Dict[str, Union[bool, Song]]:
        """Entry point for playing audio"""
        for i in range(1, 3 + 1):
            song = await fetch_track(query, self.loop)

            if song:
                logger.debug(f"Video data fetched (ID: {self.ctx.guild.id})")
                break

            logger.debug(f"Failed to fetch song data. Retry: {i} (ID: {self.ctx.guild.id})")

        if song:
            self.enqueue(song)
            logger.debug(f"Queued track (ID: {self.ctx.guild.id})")

        if self.is_playing:
            await self.ui.send_queue_msg(interaction, song)
            self.update_ui()

        if not self.is_playing and song:
            logger.debug(f"Started playback (ID: {self.ctx.guild.id})")
            song = self.play_song()

        return song

    # Player controls
    def set_volume(self, volume: int) -> float:
        """Set player volume"""
        self.volume = volume
        self.ctx.voice_client.source.volume = self.volume

        return self.volume

    def remove_song(self, index: int) -> Union[Song, None]:
        """Remove an item from the queue"""
        if not index in range(0, len(self.queue)):
            return
        
        self.update_ui()
        
        return self.dequeue(index - 1)

    async def skip(self, **kwargs) -> Union[Song, None]:
        """Skip currently playing song"""
        if self.is_playing and len(self.queue) > 0:
            self.ctx.voice_client.stop()

            await self.ui.send_skip_msg(kwargs.get('interaction'), self.now_playing)

            logger.debug(f"Skippped to next track (ID: {self.ctx.guild.id})")

            return self.now_playing

    async def prev(self, **kwargs) -> Union[Song, None]:
        """Play the previous song"""
        if self.is_playing and len(self.history) > 0:
            self.__queue.insert(0, self.history[-1])
            self.ctx.voice_client.stop()

            await self.ui.send_skip_msg(kwargs.get('interaction'), self.now_playing)

            logger.debug(f"Skipped to previous track (ID: {self.ctx.guild.id})")
            
            return self.now_playing

    async def pause(self, **kwargs) -> Union[Song, None]:
        """Pauses playback of current song"""
        if self.is_playing:
            self.is_playing = False
            self.ctx.voice_client.pause()

            self.update_ui()
            await self.ui.send_pause_msg(kwargs.get('interaction'), self.now_playing)

            logger.debug(f"Paused playback (ID: {self.__ctx.guild.id})")

            return self.now_playing

    async def resume(self, **kwargs) -> Union[Song, None]:
        """Resumes playback of current song"""
        if not self.is_playing:
            self.is_playing = True
            self.ctx.voice_client.resume()

            self.update_ui()
            await self.ui.send_resume_msg(kwargs.get('interaction'), self.now_playing)

            logger.debug(f"Resumed playback (ID: {self.__ctx.guild.id})")

            return self.now_playing

    async def stop(self, **kwargs) -> Union[Song, None]:
        """Stop audio stream"""
        if self.is_playing:
            song = self.now_playing
            self.now_playing = None
            self.__queue.clear()

            logger.debug(f"Cleared queue (ID: {self.__ctx.guild.id})")

            self.ctx.voice_client.stop()

            logger.debug(f"Stopped playback (ID: {self.__ctx.guild.id})")

            await self.ui.remove_controls()
            await self.ui.send_stop_msg(kwargs.get('interaction'), self.now_playing)

            return song
