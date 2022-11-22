import asyncio
import aiohttp
import youtube_dl
import discord

class PlayerAlreadyExists(Exception):
    pass

class Music(object):
    def __init__(self):
        self.__players = {}

    def create_player(self, ctx, on_play = None):
        if ctx.guild.id in self.__players.keys():
            return self.__players.get(ctx.guild.id)

        player = Player(ctx, on_play)
        self.__players[ctx.guild.id] = player
        return player

    def get_player(self, player_id):
        return self.__players.get(player_id) if player_id in self.__players.keys() else None

    def close_player(self, player_id):
        player = self.get_player(player_id)

        if player:
            player.get_loop().create_task(player.stop())
            self.__players.pop(player_id)

class Player(object):
    def __init__(self, ctx, on_play):
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
    def now_playing(self):
        return self.__now_playing

    def set_volume(self, volume):
        volume = volume if volume in range (1, 100 + 1) else 100
        self.__volume = volume / 100
        self.__ctx.voice_client.source.volume = self.__volume
        return self.__volume

    def dequeue(self, index):
        return self.__queue.pop(int(index)- 1)
        
    def get_loop(self):
        return self.__loop

    def get_queue(self):
        tracklist = []
        
        if self.__now_playing:
            tracklist.append(self.__now_playing)

        if len(self.__queue) > 0:
            for song in self.__queue:
                tracklist.append(song)

        return tracklist

    def get_channel(self):
        return self.__ctx.channel

    async def fetch_track(self, query):
        if query.startswith("https://www.youtube.com/watch?v="):
            src = query
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

        ytdl = youtube_dl.YoutubeDL(self.__YDL_OPTIONS)
        data = await self.__loop.run_in_executor(None, lambda: ytdl.extract_info(src, download = False))
        title = data["title"]
        channel = data["uploader"]
        url = "https://www.youtube.com/watch?v=" + data["id"]
        thumbnail = data["thumbnail"]
        return Song(data["url"], title, channel, url, thumbnail)

    def play_song(self):
        try:
            self.__now_playing = self.__queue.pop(0)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.__now_playing.get_source(), **self.__FFMPEG_OPTS), volume = self.__volume)
            self.__ctx.voice_client.play(source, after = lambda error: self.play_song())
            
            self.__is_playing = True

            if self.__on_play:
                on_play = self.__ctx.bot.get_command(self.__on_play)

                if on_play:
                    self.__loop.create_task(self.__ctx.invoke(on_play))
        except IndexError:
            self.__is_playing = False
            print("Reached end of queue") # remove after debugging
            print(self.__now_playing)
            return

    async def play(self, query):
        song = await self.fetch_track(query)

        if song:
            self.__queue.append(song)

        if not self.__is_playing:
            self.play_song()

        return {
            "queued": True if song in self.__queue else False,
            "song": song
        }

    async def skip(self):
        if self.__is_playing:
            song = self.__now_playing
            self.__ctx.voice_client.stop()
            self.play_song()
            return song
        
        return

    async def stop(self):
        if self.__is_playing:
            self.__now_playing = None
            self.__queue.clear()
            self.__ctx.voice_client.stop()

class Song(object):
    def __init__(self, source, title, author, url, thumbnail):
        self.set_source(source)
        self.set_title(title)
        self.set_author(author)
        self.set_url(url)
        self.set_thumbnail(thumbnail)

    def set_source(self, source):
        self.__source = source

    def set_title(self, title):
        self.__title = title

    def set_author(self, author):
        self.__author = author

    def set_url(self, url):
        self.__url = url

    def set_thumbnail(self, thumbnail):
        self.__thumbnail = thumbnail

    def get_source(self):
        return self.__source

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_url(self):
        return self.__url

    def get_thumbnail(self):
        return self.__thumbnail