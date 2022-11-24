"""
Music Player
    - Provides an easy way to stream audio to discord
      from a song title or a youtube link.
"""
from typing import List, Dict, ClassVar, Optional, Any, Union

import aiohttp
import youtube_dl
import discord

from core import colors
from cogs.admin import send_basic_response

class Song:
    """
    A class used to contain song data

    Attributes
    -----------
    __source
        source URL used for fetching song data
    __title
        song title
    __author
        song uploader
    __url
        song URL
    __thumbnail
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
    __source: str
    __title: str
    __author: str
    __url: str
    __thumbnail: str

    def __init__(self, source: str, title: str, author: str, url: str, thumbnail: str):
        self.set_source(source)
        self.set_title(title)
        self.set_author(author)
        self.set_url(url)
        self.set_thumbnail(thumbnail)

    def set_source(self, source: str) -> None:
        """Set song source URL"""
        self.__source = source

    def set_title(self, title: str) -> None:
        """Set song title"""
        self.__title = title

    def set_author(self, author: str) -> None:
        """Set song author"""
        self.__author = author

    def set_url(self, url: str) -> None:
        """Set song URL"""
        self.__url = url

    def set_thumbnail(self, thumbnail: str) -> None:
        """Set song thumbnail URL"""
        self.__thumbnail = thumbnail

    def get_source(self) -> str:
        """Return song source URL"""
        return self.__source

    def get_title(self) -> str:
        """Return song title"""
        return self.__title

    def get_author(self) -> str:
        """Return song author"""
        return self.__author

    def get_url(self) -> str:
        """Return song URL"""
        return self.__url

    def get_thumbnail(self) -> str:
        """Return song thumbnail URL"""
        return self.__thumbnail

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
    __ctx: discord.ext.commands.Context
    __loop: Any
    __queue: List[Song]
    __is_playing: bool
    __now_playing: Song
    __on_play: str
    __volume: float
    __YDL_OPTIONS: Dict[str, Union[str, bool]]
    __FFMPEG_OPTS: Dict[str, str]

    def __init__(self, ctx: discord.ext.commands.Context, on_play: str) -> None:
        self.__ctx = ctx
        self.__loop = ctx.bot.loop
        self.__queue = []
        self.__is_playing = False
        self.__now_playing = None
        self.__on_play = on_play
        self.__volume = 1.0

        self.__YDL_OPTIONS = {
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

        self.__FFMPEG_OPTS = {
            "options": "-vn -loglevel quiet -hide_banner -nostats",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"
        }

    @property
    def now_playing(self) -> Song:
        """Fetch currently playing song"""
        return self.__now_playing

    def set_volume(self, volume: int) -> float:
        """Set player volume"""
        volume = volume if volume in range (1, 100 + 1) else 100
        self.__volume = volume / 100
        self.__ctx.voice_client.source.volume = float(self.__volume)
        return self.__volume

    def dequeue(self, index: int) -> Song:
        """Remove an item from the queue"""
        return self.__queue.pop(int(index)- 1)

    def get_loop(self) -> Any:
        """Fetch bot event loop"""
        return self.__loop

    def get_queue(self) -> List[Song]:
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

    def get_channel(self) -> discord.TextChannel:
        """Fetch channel the player was created from"""
        return self.__ctx.channel

    def get_volume(self) -> float:
        """Fetch player volume"""
        return self.__volume

    async def fetch_track(self, query: str) -> Song:
        """Process query and returns a song instance"""
        msg = await send_basic_response(self.__ctx, "Processing query, please wait...", colors.pink)
        # skip process if user passed a youtube URL
        if query.startswith("https://www.youtube.com/watch?v="):
            src = query
        # otherwise, process query to get a yotuube link
        else:
            search_url = "https://www.youtube.com/results?search_query="
            for key in query.split():
                search_url += f"{key}+"
            search_url = search_url[:-1]

            await msg.edit(
                embed=discord.Embed(
                    description="Fetching video...",
                    color=colors.pink
                )
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    html = await response.text()

            src = "https://www.youtube.com/"
            for i in range(html.find("watch?v"), len(html)):
                if html[i] == '"':
                    break
                src += html[i]

        await msg.edit(
                embed=discord.Embed(
                    description="Processing video data...",
                    color=colors.pink
                )
            )

        ytdl = youtube_dl.YoutubeDL(self.__YDL_OPTIONS)
        data = await self.__loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(src, download = False)
        )

        title = data["title"]
        channel = data["uploader"]
        url = "https://www.youtube.com/watch?v=" + data["id"]
        thumbnail = data["thumbnail"]
        await msg.delete()
        return Song(data["url"], title, channel, url, thumbnail)

    def play_song(self, silent: Optional[bool] = False) -> None:
        """Handles audio streaming to Discord"""
        self.__is_playing = False
        try:
            self.__now_playing = self.__queue.pop(0)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    self.__now_playing.get_source(),
                    **self.__FFMPEG_OPTS
                ),
                volume = self.__volume
            )

            while not self.__is_playing:
                self.__ctx.voice_client.play(source, after = lambda error: self.play_song())

                if self.__ctx.voice_client.is_playing():
                    self.__is_playing = True

            if self.__on_play and not silent:
                on_play = self.__ctx.bot.get_command(self.__on_play)

                if on_play:
                    self.__loop.create_task(self.__ctx.invoke(on_play))
        except IndexError:
            self.__now_playing = None
            self.__is_playing = False

        return self.__now_playing

    async def play(self, query: str, silent: Optional[bool] = False) -> Dict[str, Union[bool, Song]]:
        """Entry point for playing audio"""
        song = await self.fetch_track(query)

        if song:
            self.__queue.append(song)

        if not self.__is_playing:
            song = self.play_song(silent=silent)

        return {
            "queued": song in self.__queue,
            "song": song
        }

    async def skip(self) -> Union[Song, None]:
        """Skip currently playing song"""
        if self.__is_playing:
            song = self.__now_playing
            self.__ctx.voice_client.stop()
            self.play_song()
            return song

        return

    async def stop(self) -> None:
        """Stop audio stream"""
        if self.__is_playing:
            self.__now_playing = None
            self.__queue.clear()
            self.__ctx.voice_client.stop()

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

    def create_player(
        self,
        ctx: discord.ext.commands.Context,
        on_play: Optional[bool] = None
    ) -> Player:
        """Create player instance"""
        if ctx.guild.id in self.__players:
            return self.__players.get(ctx.guild.id)

        player = Player(ctx, on_play)
        self.__players[ctx.guild.id] = player
        return player

    def get_player(self, player_id: int) -> Player:
        """Fetch player instance from ID"""
        return self.__players.get(player_id) if player_id in self.__players else None

    def close_player(self, player_id: int) -> None:
        """Delete player instance"""
        player = self.get_player(player_id)

        if player:
            player.get_loop().create_task(player.stop())
            self.__players.pop(player_id)
