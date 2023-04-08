# Standard imports
from __future__ import annotations
from typing import Dict, Union
import json
import logging
import os

# Third party imports
import discord
from discord.ext import commands
from discord.ui import View

# Package imports
from . import colors
from .queue import Queue
from .song import Song, fetch_track
from .ui import components

class Player:
    def __init__(self, ctx: discord.ext.commands.Context) -> None:
        self.__ctx         : commands.Context           = ctx
        self.__last_song   : Song                       = Song
        self.__logger      : logging.Logger             = logging.getLogger("music.player")
        self.__is_playing  : bool                       = False
        self.__now_playing : Song                       = None
        self.__queue       : Queue                      = Queue()
        self.__ui          : PlayerUI                   = PlayerUI(self.ctx, self)
        self.__volume      : float                      = 1.0

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
    def is_playing(self) -> bool:
        """Check if player state is playing"""
        return self.__is_playing
    
    @is_playing.setter
    def is_playing(self, state: bool) -> None:
        self.__is_playing = state

    @property
    def last_song(self) -> Song:
        """Returns the song that was played previously"""
        return self.__last_song

    @last_song.setter
    def last_song(self, song: Song) -> None:
        """Store last played song"""
        if not song: return
        self.last_song = song

    @property
    def logger(self) -> logging.Logger:
        """Return the logger for this class"""
        return self.__logger

    @property
    def now_playing(self) -> Song:
        """Fetch currently playing song"""
        return self.__now_playing
    
    @now_playing.setter
    def now_playing(self, song: Song) -> None:
        """Set currently playing song"""
        if not song: return
        self.__now_playing = song

    @property
    def queue(self) -> Queue:
        """Fetch current player queue"""
        return self.__queue
    
    @property
    def ui(self) -> PlayerUI:
        """Fetch player ui controller"""
        return self.__ui

    @property
    def volume(self) -> float:
        """Fetch player volume"""
        return self.__volume
    
    @volume.setter
    def volume(self, value: int) -> None:
        if not value in range( 1, 100 + 1): return
        self.__volume = float(value / 100)

    def play_song(self) -> None:
        """Handles audio streaming to Discord"""
        try: # Attempt to play the first song in the queue
            self.last_song = self.now_playing
            self.now_playing = self.queue.dequeue()

            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    self.now_playing.source,
                    **self.FFMPEG_OPTS
                ),
                volume=self.volume
            )

            for i in range(1, 3 + 1):
                self.ctx.voice_client.play(source, after=lambda error: self.play_song())

                if self.ctx.voice_client.is_playing():
                    self.is_playing = True

                    self.ui.set_screen()
                    self.ui.set_controls()
                    self.ctx.bot.loop.create_task(self.ui.render_screen())

                    self.logger.debug(f"Transitioned to next song in the queue (ID: {self.ctx.guild.id})")
                    break
                
                self.logger.debug(f"Playback failed. Retry: {i} (ID: {self.ctx.guild.id})")
        except IndexError: # Expected error when there are no more tracks in queue
            self.now_playing = None
            self.is_playing = False

            self.ui.remove_controls()

            self.ctx.bot.loop.create_task(self.ui.render_screen())

            self.logger.debug(f"Playback failed, queue might be empty (ID: {self.ctx.guild.id})")

        return self.now_playing

    async def play(self, query: str) -> Union[Song, None]:
        """Entry point for playing audio"""
        song = await fetch_track(query)

        if song:
            self.queue.enqueue(song)

            self.ui.set_controls()
            self.ctx.bot.lopp.create_task(self.ui.render_screen())

            self.logger.debug(f"Queued track (ID: {self.ctx.guild.id})")

            if not self.is_playing:
                self.logger.debug(f"Started playback (ID: {self.ctx.guild.id})")
                song = self.play_song()

            return song

    # Player controls
    def set_volume(self, volume: int) -> Union[float, None]:
        """Set player volume"""
        if not self.ctx.voice_client: return

        self.ctx.voice_client.source.volume = self.volume = volume

        return self.volume

    def remove_song(self, index: int) -> Union[Song, None]:
        """Remove an item from the queue"""
        if not index in range(0, self.queue.size()): return

        return self.queue.dequeue(index - 1)

    async def skip(self) -> Union[Song, None]:
        """Skip currently playing song"""
        if not self.is_playing: return

        self.ctx.voice_client.stop()
        self.logger.debug(f"Skippped to next track (ID: {self.ctx.guild.id})")

        return self.now_playing

    async def prev(self) -> Union[Song, None]:
        """Play the previous song"""
        if not self.last_song: return

        self.queue.enqueue(0, self.history[-1])

        if self.is_playing:
            self.ctx.voice_client.stop()
            self.play_song()

        self.logger.debug(f"Skipped to previous track (ID: {self.ctx.guild.id})")

        return self.now_playing

    async def pause(self) -> Union[Song, None]:
        """Pauses playback of current song"""
        if not self.is_playing: return

        self.is_playing = False
        self.ctx.voice_client.pause()

        self.logger.debug(f"Paused playback (ID: {self.__ctx.guild.id})")

        return self.now_playing

    async def resume(self) -> Union[Song, None]:
        """Resumes playback of current song"""
        if self.is_playing or not self.ctx.voice_client: return

        self.is_playing = True
        self.ctx.voice_client.resume()

        self.logger.debug(f"Resumed playback (ID: {self.__ctx.guild.id})")

        return self.now_playing

    async def stop(self) -> Union[Song, None]:
        """Stop audio stream"""
        if not self.is_playing and not self.ctx.voice_client: return

        song = self.now_playing
        self.now_playing = None

        self.queue.items.clear()
        self.logger.debug(f"Cleared queue (ID: {self.__ctx.guild.id})")

        self.ctx.voice_client.stop()
        self.logger.debug(f"Stopped playback (ID: {self.__ctx.guild.id})")

        return song

class PlayerUI(object):
    def __init__(self, player: 'Player') -> None:
        self.player: 'Player' = player
        self.host_message: discord.Message = None
        self.display_embed: discord.Embed = None
        self.controls: discord.ui.View = None

    async def render_screen(self) -> None:
        if not self.host_message:
            await self.player.ctx.send(embed=self.display_embed, view=self.controls)
            return

        await self.host_message.edit(embed=self.display_embed, view=self.controls)

    def set_screen(self) -> None:
        song = self.player.now_playing

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Now playing in **{self.player.ctx.channel.name}**"
        )
        embed.set_thumbnail(
            url=song.thumbnail
        )
        embed.set_author(
                name=f"{song.title}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )
        embed.set_footer(
            text=f"If you like this song, use '/fave' to add this to your favorites!"
        )

        self.display_embed = embed

    def set_controls(self) -> discord.ui.View:
        self.controls = PlayerControls.create_controls(self.player)

    def remove_controls(self) -> None:
        self.controls = None

class PlayerControls(object):
    @staticmethod
    def create_controls(player: Player) -> View:
        view = View(timeout=None)

        prev_button = components.PrevButton(player.prev, False if player.last_song else True)
        
        if player.is_playing:
            play_button = components.PauseButton(player.pause)
        else:
            play_button = components.PlayButton(player.resume)

        stop_button = components.StopButton(player.stop)
        next_button = components.NextButton(player.skip, False if player.queue.size != 0 else True)

        map(view.add_item, [prev_button, play_button, stop_button, next_button])
        return view
