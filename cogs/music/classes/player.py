from typing import Dict, Union
import asyncio
import json
import logging
import os

import discord
from discord.ext import commands

from .player_ui import PlayerUI
from .queue import Queue
from .song import Song, fetch_track

class Player:
    def __init__(self, ctx: discord.ext.commands.Context) -> None:
        self.__channel     : discord.TextChannel        = ctx.channel
        self.__ctx         : commands.Context           = ctx
        self.__is_playing  : bool                       = False
        self.__last_song   : Song                       = None
        self.__logger      : logging.Logger             = logging.getLogger("yaemiko.music.player")
        self.__now_playing : Song                       = None
        self.__queue       : Queue                      = Queue()
        self.__volume      : float                      = 1.0
        self.__ui          : PlayerUI                   = PlayerUI(self.channel)

        with open(os.path.join(os.path.dirname(__file__), '..', 'ffmpeg_options.json'), 'r') as f:
            self.__FFMPEG_OPTS = json.load(f)

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
    def last_song(self) -> Song:
        return self.__last_song
    
    @last_song.setter
    def last_song(self, song: Song) -> None:
        self.__last_song = song

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

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
    def queue(self) -> Queue:
        """Fetch current player queue"""
        return self.__queue

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
        self.loop.create_task(self.ui.render_np(self))

    def play_song(self) -> None:
        """Handles audio streaming to Discord"""
        try:
            self.last_song = self.now_playing
            self.now_playing = self.queue.dequeue()

            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    self.now_playing.source,
                    **self.FFMPEG_OPTS
                ),
                volume = self.volume
            )

            for i in range(1, 3 + 1):
                self.ctx.voice_client.play(source, after = lambda error: self.play_song())

                if self.ctx.voice_client.is_playing():
                    self.is_playing = True

                    self.update_ui()

                    self.logger.debug(f"Transitioned to next song in the queue (ID: {self.ctx.guild.id})")

                    break

                self.logger.debug(f"Playback failed. Retry: {i} (ID: {self.ctx.guild.id})")
        # Expected error when there are no more tracks in queue
        except IndexError:
            self.now_playing = None
            self.is_playing = False

            self.logger.debug(f"Playback failed, queue might be empty (ID: {self.ctx.guild.id})")

            # FIXME: update ui
            self.loop.create_task(self.ui.remove_controls())

        return self.now_playing

    async def play(self, query: str, interaction: discord.Interaction) -> Dict[str, Union[bool, Song]]:
        """Entry point for playing audio"""
        for i in range(1, 3 + 1):
            song = await fetch_track(query, self.loop)

            if song:
                self.logger.debug(f"Video data fetched (ID: {self.ctx.guild.id})")
                self.queue.enqueue(song)
                self.logger.debug(f"Queued track (ID: {self.ctx.guild.id})")

                if self.ui.screen:
                    await self.ui.send_queue_msg(interaction, song)
                    self.update_ui()
                
                if not self.is_playing:
                    song = self.play_song()
                    self.logger.debug(f"Started playback (ID: {self.ctx.guild.id})")

                break

            self.logger.debug(f"Failed to fetch song data. Retry: {i} (ID: {self.ctx.guild.id})")

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

    async def skip(self) -> Union[Song, None]:
        """Skip currently playing song"""
        self.ctx.voice_client.stop()

        self.logger.debug(f"Skippped to next track (ID: {self.ctx.guild.id})")

        return self.now_playing

    async def prev(self) -> Union[Song, None]:
        """Play the previous song"""
        self.queue.items.insert(0, self.last_song)
        self.ctx.voice_client.stop()

        self.logger.debug(f"Skipped to previous track (ID: {self.ctx.guild.id})")
        
        return self.now_playing

    async def pause(self) -> Union[Song, None]:
        """Pauses playback of current song"""
        self.is_playing = False
        self.ctx.voice_client.pause()

        self.update_ui()

        self.logger.debug(f"Paused playback (ID: {self.__ctx.guild.id})")

        return self.now_playing

    async def resume(self) -> Union[Song, None]:
        """Resumes playback of current song"""
        self.is_playing = True
        self.ctx.voice_client.resume()

        self.update_ui()

        self.logger.debug(f"Resumed playback (ID: {self.__ctx.guild.id})")

        return self.now_playing

    async def stop(self) -> Union[Song, None]:
        """Stop audio stream"""
        song = self.now_playing
        self.now_playing = None
        self.queue.items.clear()

        self.logger.debug(f"Cleared queue (ID: {self.__ctx.guild.id})")

        self.ctx.voice_client.stop()

        self.logger.debug(f"Stopped playback (ID: {self.__ctx.guild.id})")

        await self.ui.remove_controls()

        return song