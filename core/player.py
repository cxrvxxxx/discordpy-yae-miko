"""
Music Player
    Provides an easy way to stream audio to discord
    from a song title or a youtube link.
"""
# Standard imports
from typing import List, Dict, ClassVar, Optional, Any, Union, Callable
import asyncio

# Third party-library imports
import aiohttp
import youtube_dl
import discord
from discord.ext import commands

# Core imports
import logsettings
from core import colors
from core.message import Responses
from core.ui import player_controls

# Logger
logger = logsettings.logging.getLogger("musicplayer")

class Song:
    """
    A class used to contain song data

    Attributes
    -----------
    source
        source URL used for fetching song data
    title
        song title
    author
        song uploader
    url
        song URL
    thumbnail
        song thumbnail URL

    Methods
    ---------
    set_source(source)
        set song source URL
    set_title(title)
        set song title
    set_author(author)
        set song author
    set_url(url)
        set song URL
    set_thumbnail(thumbnail)
        set song thumbnail URL
    """
    def __init__(self, source: str, title: str, author: str, url: str, thumbnail: str):
        self.__SOURCE    : str = source
        self.__TITLE     : str = title
        self.__AUTHOR    : str = author
        self.__URL       : str = url
        self.__THUMBNAIL : str = thumbnail

    @property
    def source(self) -> str:
        """Return song source URL"""
        return self.__SOURCE

    @property
    def title(self) -> str:
        """Return song title"""
        return self.__TITLE

    @property
    def author(self) -> str:
        """Return song author"""
        return self.__AUTHOR

    @property
    def url(self) -> str:
        """Return song URL"""
        return self.__URL

    @property
    def thumbnail(self) -> str:
        """Return song thumbnail URL"""
        return self.__THUMBNAIL

class Player:
    """
    A class used to stream audio to Discord

    Attributes
    ----------
    __ctx
        Context of the command
    __loop
        Bot event loop
    __queue
        List of songs to be played
    __is_playing
        Flag if the player is playing anything
    __now_playing
        Song that is currently being played
    __on_play
        Function name to call when a song is played
    __volume
        Player volume
    __YDL_OPTIONS
        YoutubeDL options
    __FFMPEG_OPTIONS
        FFMPEG options

    Methods
    --------
    now_playing()
        Fetch currently playing song
    set_volume(volume)
        Set player volume
    dequeue(index)
        Remove an item from the queue
    get_loop()
        Fetch bot event loop
    get_queue()
        Fetch current player queue
    get_channel()
        Fetch channel the player was created from
    get_volume()
        Fetch player volume
    fetch_track(query)
        Process query and returns a song instance
    play_song()
        Handles audio streaming to Discord
    play(query)
        Entry point for playing audio
    skip()
        Skip currently playing song
    stop()
        Stop audio stream
    """
    def __init__(self, ctx: discord.ext.commands.Context) -> None:
        self.__ctx         : commands.Context           = ctx
        self.__queue       : List[Song]                 = []
        self.__is_playing  : bool                       = False
        self.__now_playing : Song                       = None
        self.__last_song   : Song                       = None
        self.__ui          : PlayerUI                   = PlayerUI()
        self.__volume      : float                      = 1.0
        self.__YDL_OPTIONS : Dict[str, Union[str, int]] = {
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

    async def fetch_track(self, query: str) -> Song:
        """Process query and returns a song instance"""
        # skip process if user passed a youtube URL
        if query.startswith("https://www.youtube.com/watch?v="):
            src = query
            logger.debug(f"Received video URL, parsing skipped (ID: {self.__ctx.guild.id})")
        # otherwise, process query to get a yotuube link
        else:
            search_url = "https://www.youtube.com/results?search_query="
            for key in query.split():
                search_url += f"{key}+"
            search_url = search_url[:-1]

            logger.debug(f"Parsed query into YTSearch URL (ID: {self.__ctx.guild.id})")

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    html = await response.text()
            logger.debug(f"Retrieved HTML data (ID: {self.__ctx.guild.id})")

            src = "https://www.youtube.com/"
            for i in range(html.find("watch?v"), len(html)):
                if html[i] == '"':
                    break
                src += html[i]

        ytdl = youtube_dl.YoutubeDL(self.__YDL_OPTIONS)
        data = await self.loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(src, download = False)
        )
        logger.debug(f"Extracted video data from URL (ID: {self.__ctx.guild.id})")

        title = data["title"]
        channel = data["uploader"]
        url = "https://www.youtube.com/watch?v=" + data["id"]
        thumbnail = data["thumbnail"]

        return Song(data["url"], title, channel, url, thumbnail)

    def play_song(self, silent: Optional[bool] = False) -> None:
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
            logger.debug(f"Transitioned to next song in the queue (ID: {self.__ctx.guild.id})")
            self.loop.create_task(
                self.__ui.renderNowPlaying(self)
            )
        except IndexError: # Expected error when there are no more tracks in queue
            self.__now_playing = None
            self.__is_playing = False
            logger.debug(f"Playback failed, queue might be empty (ID: {self.__ctx.guild.id})")

        if not self.now_playing and not self.is_playing:
            self.loop.create_task(
                self.__ui.clearPlayerControls(self)
            )

        return self.__now_playing

    async def play(
        self,
        query: str,
        silent: Optional[bool] = False
    ) -> Dict[str, Union[bool, Song]]:
        """Entry point for playing audio"""
        for i in range(1, 3 + 1):
            song = await self.fetch_track(query)

            if song:
                logger.debug(f"Video data fetched (ID: {self.__ctx.guild.id})")
                break

            logger.debug(f"Failed to fetch song data. Retry: {i} (ID: {self.__ctx.guild.id})")

        if song:
            self.__queue.append(song)
            logger.debug(f"Queued track (ID: {self.__ctx.guild.id})")
            if self.is_playing:
                await self.__ui.renderNowPlaying(self)
                logger.debug(f"Updated player controls (ID: {self.__ctx.guild.id}")

        if not self.__is_playing and song:
            logger.debug(f"Started playback (ID: {self.__ctx.guild.id})")
            song = self.play_song(silent=silent)

        return {
            "queued": song in self.__queue,
            "song": song if song else None
        }

    # Player control methods
    def set_volume(self, volume: int) -> float:
        """Set player volume"""
        volume = volume if volume in range (1, 100 + 1) else 100
        self.__volume = volume / 100
        self.__ctx.voice_client.source.volume = float(self.__volume)
        return self.__volume

    def dequeue(self, index: int) -> Song:
        """Remove an item from the queue"""
        return self.__queue.pop(int(index)- 1)

    async def skip(self, interaction: Optional[discord.Interaction]) -> Union[Song, None]:
        """Skip currently playing song"""
        if self.__is_playing:
            self.__ctx.voice_client.stop()
            logger.debug(f"Skippped to next track (ID: {self.__ctx.guild.id})")

            if interaction:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{self.__now_playing.title}**."
                    ),
                    delete_after=10
                )

            await self.__ui.renderNowPlaying(self)

    async def prev(self, interaction: Optional[discord.Interaction]=None) -> Union[Song, None]:
        """Play the previous song"""
        if self.__is_playing and self.__last_song:
            self.__queue.insert(0, self.__last_song)
            self.__last_song = None
            self.__ctx.voice_client.stop()
            logger.debug(f"Skipped to previous track (ID: {self.__ctx.guild.id})")

            if interaction:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{self.__now_playing.title}**."
                    ),
                    delete_after=10
                )

            await self.__ui.renderNowPlaying(self)

    async def pause(self, interaction: Optional[discord.Interaction]=None) -> Union[Song, None]:
        """Pauses playback of current song"""
        if self.__is_playing:
            self.__is_playing = False
            self.__ctx.voice_client.pause()
            logger.debug(f"Paused playback (ID: {self.__ctx.guild.id})")

            if interaction:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Paused 🎶 **{self.__now_playing.title}**."
                    ),
                    delete_after=10
                )

                await self.__ui.renderNowPlaying(self)

    async def resume(self, interaction: Optional[discord.Interaction]=None) -> Union[Song, None]:
        """Resumes playback of current song"""
        if not self.__is_playing:
            self.__is_playing = True
            self.__ctx.voice_client.resume()
            logger.debug(f"Resumed playback (ID: {self.__ctx.guild.id})")

            if interaction:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Resumed 🎶 **{self.__now_playing.title}**."
                    ),
                    delete_after=10
                )

                await self.__ui.renderNowPlaying(self)

    async def stop(self, interaction: Optional[discord.Interaction]=None) -> None:
        """Stop audio stream"""
        if self.__is_playing:
            self.__now_playing = None
            self.__queue.clear()
            logger.debug(f"Cleared queue (ID: {self.__ctx.guild.id})")
            self.__ctx.voice_client.stop()
            logger.debug(f"Stopped playback (ID: {self.__ctx.guild.id})")

            if interaction:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{self.__now_playing.title}**."
                    ),
                    delete_after=10
                )

            await self.__ui.renderNowPlaying(self)

class Music:
    """
    A class used to manage, create, and delete player instances

    Attributes
    ----------
    __players
        List of players referenced by their Guild ID

    Methods
    ----------
    create_player(ctx, on_play)
        Create player instance
    get_player(player_id)
        Fetch player instance from ID
    close_player(player_id)
        Delete player instance
    """
    __players: ClassVar[Dict[int, Player]]

    def __init__(self) -> None:
        self.__players  = {}

    def create_player(self, ctx: discord.ext.commands.Context) -> Player:
        """Create player instance"""
        if ctx.guild.id in self.__players:
            return self.__players.get(ctx.guild.id)

        player = Player(ctx)
        self.__players[ctx.guild.id] = player
        logger.info(f"Created Player instance (Guild ID: {player.channel.guild.id})")
        return player

    def get_player(self, player_id: int) -> Player:
        """Fetch player instance from ID"""
        return self.__players.get(player_id) if player_id in self.__players else None

    def close_player(self, player_id: int) -> None:
        """Delete player instance"""
        player = self.get_player(player_id)

        if player:
            logger.info(f"Destroyed Player instance (Guild ID: {player.channel.guild.id})")
            player.loop.create_task(player.stop())
            self.__players.pop(player_id)

class PlayerUI:
    def __init__(self):
        self.hook: discord.Message = None

    async def renderNowPlaying(self, player: Player):
        song = player.now_playing
        if not song:
            await self.send(player, view=None)
            logger.debug(f"Removed player controls (ID: {player.channel.guild.id})")
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Now playing in **{player.channel.name}**"
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

        await self.send(
            player,
            embed=embed,
            view=player_controls(player, paused=True if not player.is_playing else False) if player.queue else None
        )

    async def clearPlayerControls(self, player: Player):
        await self.send(player, view=None)

    async def send(self, player, **kwargs):
        if self.hook:
            self.hook = await self.hook.edit(
                content      = kwargs.get("content"),
                embed        = kwargs.get("embed"),
                view         = kwargs.get("view", None),
                delete_after = kwargs.get("delete_after")
            )
            logger.debug(f"Updated message (ID: {self.hook.id} GUILD: {self.hook.guild.id})")
        else:
            self.hook = await player.channel.send(
                content      = kwargs.get("content"),
                embed        = kwargs.get("embed"),
                view         = kwargs.get("view"),
                delete_after = kwargs.get("delete_after")
            )
            logger.debug(f"Added message (ID: {self.hook.id} GUILD: {self.hook.guild.id})")
