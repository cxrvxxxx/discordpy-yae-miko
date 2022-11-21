import discord
import os
import asyncio

from discord.ext import commands
from core.player import Music
from core import colors
from cogs.admin import send_basic_response
from core.logger import console_log

# default config values
settings = {
    'voice_auto_disconnect': 'True'
}

# init dir
if not os.path.exists('playlists'):
    os.mkdir('playlists')

class Voice(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.music = Music()

        self.config = client.config

    @commands.Cog.listener()
    async def on_ready(self):
        # init config data for this cog
        for guild in self.client.guilds:
            for key, value in settings.items():
                if not self.config[guild.id].get(__name__, key):
                    self.config[guild.id].set(__name__, key, value)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # triggered only when update comes from bot
        if member == self.client.user:
            console_log(f"{self.client.user} updated VoiceState")
            try:
                in_voice = member.voice.channel
            except:
                in_voice = None
            finally:
                if not in_voice and self.players.get(member.guild.id):
                    # player from Music class
                    player = self.players.get(member.guild.id)
                    player.disable()
                    self.players.pop(member.guild.id)
                    console_log(f"Cleared player for {member.guild.name}")
            
        # triggered only when update comes from users
        if member != self.client.user:
            config = self.config[member.guild.id]
            channel = self.channels.get(member.guild.id)
            auto_disconnect = config.getboolean(__name__, 'voice_auto_disconnect')
            guild = self.client.get_guild(member.guild.id)

            # do nothing if the bot is not connected
            if not guild.voice_client:
                return

            user_count = len(guild.voice_client.channel.members)

            if (user_count < 2 and auto_disconnect) and channel:
                console_log("Auto-disconnect timer started.")
                await asyncio.sleep(180)

                user_count = len(guild.voice_client.channel.members)
                if user_count < 2:
                    # unbind channel and clear player
                    try:
                        player = self.music.get_player(guild.id)

                        self.music.close_player(self.client.loop, guild.id)
                    except:
                        console_log("Could not clear player because there is none.")
                
                    await send_basic_response(channel, f"Disconnecting from **[{guild.voice_client.channel.name}]** and unbound from **[{channel.name}]** since no one else is in the channel.", colors.pink)
                    await guild.voice_client.disconnect()
                else:
                    console_log("Auto-disconnect timer ended. There are users in the channel.")

    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
            return
        if ctx.voice_client:
            await send_basic_response(ctx, f"Already connected to voice channel **[{ctx.voice_client.channel.name}]**.", colors.red)
            return

        await ctx.author.voice.channel.connect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        if not ctx.author.voice:
            await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
            return

        player = self.music.get_player(ctx.guild.id)

        if player and ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        if not ctx.voice_client:
            await ctx.invoke(self.client.get_command("join"))

        if not player:
            player = self.music.create_player(ctx, on_play = "nowplaying")
            await send_basic_response(ctx, f"Connected to **[{ctx.author.voice.channel.name}]** and bound to **[{ctx.channel.name}]**.", colors.pink)

        result = await player.play(query)
        if result.get("queued"):
            song = result.get("song")
            embed = discord.Embed(
                colour=colors.pink,
                description=f"Successfully added to queue by {ctx.author.mention}."
            )
            embed.set_thumbnail(url=song.get_thumbnail())
            embed.set_author(
                name=f"{song.get_title()}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )

            await ctx.send(embed=embed)

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_basic_response (ctx, "There is no **active player**.", colors.red)
            return

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        queue = player.get_queue()

        if not queue:
            await send_basic_response (ctx, "The queue is **empty** because there is nothing being currently played.", colors.red)
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Now playing in **{ctx.author.voice.channel.name}**"
        )
        embed.set_thumbnail(
            url=queue[0].get_thumbnail()
        )
        embed.set_author(
                name=f"{queue[0].get_title()}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )

        embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_basic_response (ctx, "There is no **active player**.", colors.red)
            return

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        queue = player.get_queue()

        if not queue:
            await send_basic_response (ctx, "The queue is **empty** because there is nothing being currently played.", colors.red)
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Now playing in **{ctx.author.voice.channel.name}**"
        )
        embed.set_thumbnail(
            url=queue[0].get_thumbnail()
        )
        embed.set_author(
                name=f"{queue[0].get_title()}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )

        songs = ""
        if len(queue) <= 1:
            songs = "There are no songs in the queue."
        else:
            for index, song in enumerate(queue):
                if index == 0:
                    pass
                else:
                    songs = songs + f"\n `{index}` {song.get_title()}"

        embed.add_field(
            name="🎶 Up Next...",
            value=songs,
            inline=False
        )

        embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        if not ctx.author.voice:
            await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
            return

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_basic_response(ctx, "There is no **active player**.", colors.red)
            return

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        song = await player.skip()

        if not song:
            await send_basic_response(ctx, f"There is nothing to skip**.", colors.red)
            return

        await send_basic_response(ctx, f"Skipping 🎶 **{song.get_title()}**.", colors.pink)

    @commands.command(aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        if not ctx.voice_client:
            await send_basic_response(ctx, "Not connected to a **voice channel**.", colors.red)
            return

        player = self.music.get_player(ctx.guild.id)

        if player:
            if ctx.channel != player.get_channel():
                await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
                return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Disconnected from **[{ctx.voice_client.channel.name}]** and unbound from **[{player.get_channel().name if player else 'channel'}]**."
        )        

        await ctx.send(embed=embed)
        await ctx.voice_client.disconnect()

    # TODO: pause, resume, volume, favlist, fave, unfave

async def setup(client):
    await client.add_cog(Voice(client))

# import discord
# import asyncio
# import os
# import asyncio
# import aiohttp
# import re
# try:
#     import youtube_dl
#     import discord
#     has_voice = True
# except ImportError:
#     has_voice = False

# from discord.ext import commands
# from core.logger import console_log
# from core import colors

# if has_voice:
#     youtube_dl.utils.bug_reports_message = lambda: ''
#     ydl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "source_address": "0.0.0.0"})

# class EmptyQueue(Exception):
#     """Cannot skip because queue is empty"""
    
# class NotConnectedToVoice(Exception):
#     """Cannot create the player because bot is not connected to voice"""
    
# class NotPlaying(Exception):
#     """Cannot <do something> because nothing is being played"""
    
# async def ytbettersearch(query):
#     url = f"https://www.youtube.com/results?search_query={query}"
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             html = await resp.text()
#     index = html.find('watch?v')
#     url = ""
#     while True:
#         char = html[index]
#         if char == '"':
#             break
#         url += char
#         index += 1
#     url = f"https://www.youtube.com/{url}"
#     return url

# async def get_video_data(url, search, bettersearch, loop):
#     if not has_voice:
#         raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

#     if not search and not bettersearch:
#         data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
#         source = data["url"]
#         url = "https://www.youtube.com/watch?v="+data["id"]
#         title = data["title"]
#         description = data["description"]
#         views = data["view_count"]
#         duration = data["duration"]
#         thumbnail = data["thumbnail"]
#         channel = data["uploader"]
#         channel_url = data["uploader_url"]
#         return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
#     else:
#         if bettersearch:
#             url = await ytbettersearch(url)
#             data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
#             source = data["url"]
#             url = "https://www.youtube.com/watch?v="+data["id"]
#             title = data["title"]
#             description = data["description"]
#             views = data["view_count"]
#             duration = data["duration"]
#             thumbnail = data["thumbnail"]
#             channel = data["uploader"]
#             channel_url = data["uploader_url"]
#             return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
#         elif search:
#             ytdl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto", "source_address": "0.0.0.0"})
#             data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
#             try:
#                 data = data["entries"][0]
#             except KeyError or TypeError:
#                 pass
#             del ytdl
#             source = data["url"]
#             url = "https://www.youtube.com/watch?v="+data["id"]
#             title = data["title"]
#             description = data["description"]
#             views = data["view_count"]
#             duration = data["duration"]
#             thumbnail = data["thumbnail"]
#             channel = data["uploader"]
#             channel_url = data["uploader_url"]
#             return Song(source, url, title, description, views, duration, thumbnail, channel, channel_url, False)
        
# def check_queue(ctx, opts, music, after, on_play, loop):
#     if not has_voice:
#         raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

#     try:
#         song = music.queue[ctx.guild.id][0]
#     except IndexError:
#         return
#     if not song.is_looping:
#         try:
#             music.queue[ctx.guild.id].pop(0)
#         except IndexError:
#             return
#         if len(music.queue[ctx.guild.id]) > 0:
#             source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source, **opts))
#             ctx.voice_client.play(source, after=lambda error: after(ctx, opts, music, after, on_play, loop))
#             song = music.queue[ctx.guild.id][0]
#             loop.create_task(ctx.invoke(ctx.bot.get_command('nowplaying')))
#             if on_play:
#                 loop.create_task(on_play(ctx, song))
                
#     else:
#         source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(music.queue[ctx.guild.id][0].source, **opts))
#         ctx.voice_client.play(source, after=lambda error: after(ctx, opts, music, after, on_play, loop))
#         song = music.queue[ctx.guild.id][0]
#         if on_play:
#             loop.create_task(on_play(ctx, song))

# class Music(object):
#     def __init__(self):
#         if not has_voice:
#             raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

#         self.queue = {}
#         self.players = []

#     def create_player(self, ctx, **kwargs):
#         if not ctx.voice_client:
#             raise NotConnectedToVoice("Cannot create the player because bot is not connected to voice")
#         player = MusicPlayer(ctx, self, **kwargs)
#         self.players.append(player)
#         return player
        
#     def get_player(self, **kwargs):
#         guild = kwargs.get("guild_id")
#         channel = kwargs.get("channel_id")
#         for player in self.players:
#             if guild and channel and player.ctx.guild.id == guild and player.voice.channel.id == channel:
#                 return player
#             elif not guild and channel and player.voice.channel.id == channel:
#                 return player
#             elif not channel and guild and player.ctx.guild.id == guild:
#                 return player
#         else:
#             return None

# class MusicPlayer(object):
#     def __init__(self, ctx, music, **kwargs):
#         if not has_voice:
#             raise RuntimeError("DiscordUtils[voice] install needed in order to use voice")

#         self.ctx = ctx
#         self.voice = ctx.voice_client
#         self.loop = ctx.bot.loop
#         self.music = music
        
#         if self.ctx.guild.id not in self.music.queue.keys():
#             self.music.queue[self.ctx.guild.id] = []
        
#         self.after_func = check_queue
#         self.on_play_func = self.on_queue_func = self.on_skip_func = self.on_stop_func = self.on_pause_func = self.on_resume_func = self.on_loop_toggle_func = self.on_volume_change_func = self.on_remove_from_queue_func = None
        
#         ffmpeg_error = kwargs.get("ffmpeg_error_betterfix", kwargs.get("ffmpeg_error_fix"))
#         if ffmpeg_error and "ffmpeg_error_betterfix" in kwargs.keys():
#             self.ffmpeg_opts = {"options": "-vn -loglevel quiet -hide_banner -nostats", "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
#         elif ffmpeg_error:
#             self.ffmpeg_opts = {"options": "-vn", "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin"}
#         else:
#             self.ffmpeg_opts = {"options": "-vn", "before_options": "-nostdin"}
    
#     def disable(self):
#         self.music.players.remove(self)
    
#     def on_queue(self, func):
#         self.on_queue_func = func
    
#     def on_play(self, func):
#         self.on_play_func = func
    
#     def on_skip(self, func):
#         self.on_skip_func = func
    
#     def on_stop(self, func):
#         self.on_stop_func = func
    
#     def on_pause(self, func):
#         self.on_pause_func = func
    
#     def on_resume(self, func):
#         self.on_resume_func = func
    
#     def on_loop_toggle(self, func):
#         self.on_loop_toggle_func = func
    
#     def on_volume_change(self, func):
#         self.on_volume_change_func = func
    
#     def on_remove_from_queue(self, func):
#         self.on_remove_from_queue_func = func
    
#     async def queue(self, url, search=False, bettersearch=False):
#         song = await get_video_data(url, search, bettersearch, self.loop)
#         self.music.queue[self.ctx.guild.id].append(song)
        
#         if self.on_queue_func:
#             await self.on_queue_func(self.ctx, song)
        
#         return song
    
#     async def play(self):
#         source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.music.queue[self.ctx.guild.id][0].source, **self.ffmpeg_opts))
#         self.voice.play(source, after=lambda error: self.after_func(self.ctx, self.ffmpeg_opts, self.music, self.after_func, self.on_play_func, self.loop))
#         song = self.music.queue[self.ctx.guild.id][0]
        
#         if self.on_play_func:
#             await self.on_play_func(self.ctx, song)
        
#         return song
    
#     async def skip(self, force=False):
#         if len(self.music.queue[self.ctx.guild.id]) == 0:
#             raise NotPlaying("Cannot loop because nothing is being played")
#         elif not len(self.music.queue[self.ctx.guild.id]) > 1 and not force:
#             raise EmptyQueue("Cannot skip because queue is empty")
#         else:
#             old = self.music.queue[self.ctx.guild.id][0]
#             old.is_looping = False if old.is_looping else False
#             self.voice.stop()
            
#             try:
#                 new = self.music.queue[self.ctx.guild.id][0]
#                 if self.on_skip_func:
#                     await self.on_skip_func(self.ctx, old, new)
#                 return (old, new)
#             except IndexError:
#                 if self.on_skip_func:
#                     await self.on_skip_func(self.ctx, old)
#                 return old        
    
#     async def stop(self):
#         try:
#             self.music.queue[self.ctx.guild.id] = []
#             self.voice.stop()
#             self.music.players.remove(self)
#         except:
#             raise NotPlaying("Cannot loop because nothing is being played")
        
#         if self.on_stop_func:
#             await self.on_stop_func(self.ctx)
    
#     async def pause(self):
#         try:
#             self.voice.pause()
#             song = self.music.queue[self.ctx.guild.id][0]
#         except:
#             raise NotPlaying("Cannot pause because nothing is being played")
        
#         if self.on_pause_func:
#             await self.on_pause_func(self.ctx, song)
        
#         return song
    
#     async def resume(self):
#         try:
#             self.voice.resume()
#             song = self.music.queue[self.ctx.guild.id][0]
#         except:
#             raise NotPlaying("Cannot resume because nothing is being played")
        
#         if self.on_resume_func:
#             await self.on_resume_func(self.ctx, song)
        
#         return song
    
#     def current_queue(self):
#         try:
#             return self.music.queue[self.ctx.guild.id]
#         except KeyError:
#             raise EmptyQueue("Queue is empty")
    
#     def now_playing(self):
#         try:
#             return self.music.queue[self.ctx.guild.id][0]
#         except:
#             return None
    
#     async def toggle_song_loop(self):
#         try:
#             song = self.music.queue[self.ctx.guild.id][0]
#         except:
#             raise NotPlaying("Cannot loop because nothing is being played")
        
#         if not song.is_looping:
#             song.is_looping = True
#         else:
#             song.is_looping = False
        
#         if self.on_loop_toggle_func:
#             await self.on_loop_toggle_func(self.ctx, song)
        
#         return song
    
#     async def change_volume(self, vol):
#         self.voice.source.volume = vol
        
#         try:
#             song = self.music.queue[self.ctx.guild.id][0]
#         except:
#             raise NotPlaying("Cannot loop because nothing is being played")
        
#         if self.on_volume_change_func:
#             await self.on_volume_change_func(self.ctx, song, vol)
        
#         return (song, vol)
    
#     async def remove_from_queue(self, index):
#         if index == 0:
#             try:
#                 song = self.music.queue[self.ctx.guild.id][0]
#             except:
#                 raise NotPlaying("Cannot loop because nothing is being played")
            
#             await self.skip(force=True)
#             return song
        
#         song = self.music.queue[self.ctx.guild.id][index]
#         self.music.queue[self.ctx.guild.id].pop(index)
        
#         if self.on_remove_from_queue_func:
#             await self.on_remove_from_queue_func(self.ctx, song)
        
#         return song
    
#     def delete(self):
#         self.music.players.remove(self)
        
# class Song(object):
#     def __init__(self, source, url, title, description, views, duration, thumbnail, channel, channel_url, loop):
#         self.source = source
#         self.url = url
#         self.title = title
#         self.description = description
#         self.views = views
#         self.name = title
#         self.duration = duration
#         self.thumbnail = thumbnail
#         self.channel = channel
#         self.channel_url = channel_url
#         self.is_looping = loop

# music = Music()

# # default config values
# settings = {
#     'voice_auto_disconnect': 'True'
# }

# # init dir
# if not os.path.exists('playlists'):
#     os.mkdir('playlists')

# # send untitled embed
# async def send_basic_response(ctx, message, color):
#     await ctx.send(embed=discord.Embed(description = message, colour = color))

# class Voice(commands.Cog):
#     def __init__(self, client):
#         self.client = client
#         self.config = client.config

#         self.players = {}
#         self.channels = {}

#     @commands.Cog.listener()
#     async def on_ready(self):
#         # init config data for this cog
#         for guild in self.client.guilds:
#             for key, value in settings.items():
#                 if not self.config[guild.id].get(__name__, key):
#                     self.config[guild.id].set(__name__, key, value)

#     @commands.Cog.listener()
#     async def on_voice_state_update(self, member, before, after):
#         # triggered only when update comes from bot
#         if member == self.client.user:
#             console_log(f"{self.client.user} updated VoiceState")
#             try:
#                 in_voice = member.voice.channel
#             except:
#                 in_voice = None
#             finally:
#                 if not in_voice and self.players.get(member.guild.id):
#                     # player from Music class
#                     player = self.players.get(member.guild.id)
#                     player.disable()
#                     self.players.pop(member.guild.id)
#                     console_log(f"Cleared player for {member.guild.name}")
            
#         # triggered only when update comes from users
#         if member != self.client.user:
#             config = self.config[member.guild.id]
#             channel = self.channels.get(member.guild.id)
#             auto_disconnect = config.getboolean(__name__, 'voice_auto_disconnect')
#             guild = self.client.get_guild(member.guild.id)

#             # do nothing if the bot is not connected
#             if not guild.voice_client:
#                 return

#             user_count = len(guild.voice_client.channel.members)

#             if (user_count < 2 and auto_disconnect) and channel:
#                 console_log("Auto-disconnect timer started.")
#                 await asyncio.sleep(180)

#                 user_count = len(guild.voice_client.channel.members)
#                 if user_count < 2:
#                     # unbind channel and clear player
#                     try:
#                         self.channels.pop(member.guild.id)
#                         self.players.pop(member.guild.id)
#                     except:
#                         console_log("Could not clear player because there is none.")
                
#                     await send_basic_response(channel, f"Disconnecting from **[{guild.voice_client.channel.name}]** and unbound from **[{channel.name}]** since no one else is in the channel.", colors.pink)
#                     await guild.voice_client.disconnect()
#                 else:
#                     console_log("Auto-disconnect timer ended. There are users in the channel.")

#     @commands.command(aliases=['toggleadc'])
#     async def toggleautodisconnect(self, ctx):
#         config = self.config[ctx.guild.id]

#         value = config.getboolean(__name__, 'voice_auto_disconnect')
#         config.set(__name__, 'voice_auto_disconnect', False if value else True)

#         await send_basic_response(ctx, f"Automatic voice channel disconnection **{'disabled' if value else 'enabled'}**.", colors.pink)

#     @commands.command(aliases=['musichelp'])
#     async def music(self, ctx):
#         pf = self.client.prefix(self.client, ctx.message)

#         embed = discord.Embed(colour=colors.pink, title="Music Player", description="Guide & Commands")
#         embed.add_field(name="How to play?", value="Connect to a voice channel and use the commands below to interact with the player.", inline=False)
#         embed.add_field(name="Commands", value=f"**{pf}join** - Yae joins your voice channel.\n**{pf}play <url/song title>** - Plays the specified youtube url or song.\n**{pf}queue** - Displays the current queue.\n**{pf}skip** - Play the next song in the queue.\n**{pf}leave** - Yae stops playing and disconnects from the voice channel.\n**{pf}volume <0-100>** - Set the volume for the currently playing track.\n**{pf}pause** - Pause the current track.\n**{pf}resume** - Resume playback.\n**{pf}fave <optional: url>** - Adds the currently playing track to your favorites. If a link is provided, add that instead.\n**{pf}favorites** - Show your favorite tracks.\n**{pf}unfave <id>** - Removes the specified track from your favorites.", inline=False)
#         await ctx.send(embed=embed)

#     @commands.command()
#     async def join(self, ctx, silent=False):
#         if not ctx.author.voice:
#             await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
#             return
#         if ctx.voice_client:
#             await send_basic_response(ctx, f"Already connected to voice channel **[{ctx.voice_client.channel.name}]**.", colors.red)
#             return

#         self.channels[ctx.guild.id] = ctx.channel
#         await ctx.author.voice.channel.connect()

#         # does not send response if silent is true
#         if not silent:
#             await send_basic_response(ctx, f"Connected to **[{ctx.author.voice.channel.name}]** and bound to **[{ctx.channel.name}]**.", colors.pink)

#     @commands.command(aliases=['p'])
#     async def play(self, ctx, *, url = None):
#         pf = self.client.prefix(self.client, ctx.message)

#         try:
#             if not url:
#                 return

#             if url.startswith('https://open.spotify.com/'):
#                 await send_basic_response(ctx, "Spotify playlists are currently not supported.", colors.red)
#                 return

#             if not ctx.voice_client:
#                 await ctx.invoke(self.client.get_command('join'))

#             if ctx.channel != self.channels[ctx.guild.id]:
#                 await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#                 return
            
#             player = self.players.get(ctx.guild.id)
#             if not player:
#                 player = music.create_player(ctx, ffmpeg_error_betterfix=True)
#                 self.players[ctx.guild.id] = player
                
#             if not player.now_playing():
#                 await player.queue(url, search=True)
#                 song = await player.play()

#                 embed = discord.Embed(
#                     colour=colors.pink,
#                     description=f"Now playing in **{ctx.author.voice.channel.name}**\nAdded by {ctx.author.mention}"
#                 )
#                 embed.set_thumbnail(url=song.thumbnail)
#                 embed.set_author(
#                     name=f"{song.name}",
#                     icon_url="https://i.imgur.com/rcXLQLG.png"
#                 )
#                 embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
#             else:
#                 song = await player.queue(url, search=True)

#                 embed = discord.Embed(
#                     colour=colors.pink,
#                     description=f"Successfully added to queue by {ctx.author.mention}."
#                 )
#                 embed.set_thumbnail(url=song.thumbnail)
#                 embed.set_author(
#                     name=f"{song.name}",
#                     icon_url="https://i.imgur.com/rcXLQLG.png"
#                 )

#             await ctx.send(embed=embed)
#             await ctx.message.delete()

#         # handles 'Not Connected To Voice' error
#         except discord.ClientException:
#             console_log(f"An error occurred while trying to play music in {ctx.guild.name}.")

#             await ctx.invoke(self.client.get_command('resetplayer'), from_error=True)
#             await asyncio.sleep(1)
#             await ctx.invoke(self.client.get_command('join'), silent=True)

#     @commands.command(aliases=['np'])
#     async def nowplaying(self, ctx):
#         pf = self.client.prefix(self.client, ctx.message)

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response (ctx, "There is no **active player**.", colors.red)
#             return

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response (ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id].name}]**.", colors.red)
#             return

#         queue = player.current_queue()

#         if not queue:
#             await send_basic_response (ctx, "The queue is **empty** because there is nothing being currently played.", colors.red)
#             return

#         embed = discord.Embed(
#             colour=colors.pink,
#             description=f"Now playing in **{ctx.author.voice.channel.name}**"
#         )
#         embed.set_thumbnail(
#             url=queue[0].thumbnail
#         )
#         embed.set_author(
#                 name=f"{queue[0].name}",
#                 icon_url="https://i.imgur.com/rcXLQLG.png"
#             )

#         embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
#         await ctx.send(embed=embed)

#     @commands.command(aliases=['q'])
#     async def queue(self, ctx):
#         pf = self.client.prefix(self.client, ctx.message)

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response (ctx, "There is no **active player**.", colors.red)
#             return

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response (ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id].name}]**.", colors.red)
#             return

#         queue = player.current_queue()

#         if not queue:
#             await send_basic_response (ctx, "The queue is **empty** because there is nothing being currently played.", colors.red)
#             return

#         embed = discord.Embed(
#             colour=colors.pink,
#             description=f"Now playing in **{ctx.author.voice.channel.name}**"
#         )
#         embed.set_thumbnail(
#             url=queue[0].thumbnail
#         )
#         embed.set_author(
#                 name=f"{queue[0].name}",
#                 icon_url="https://i.imgur.com/rcXLQLG.png"
#             )

#         songs = ""
#         if len(queue) <= 1:
#             songs = "There are no songs in the queue."
#         else:
#             for index, song in enumerate(queue):
#                 if index == 0:
#                     pass
#                 else:
#                     songs = songs + f"\n `{index}` {song.name}"

#         embed.add_field(
#             name="🎶 Up Next...",
#             value=songs,
#             inline=False
#         )

#         embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
#         await ctx.send(embed=embed)

#     @commands.command()
#     async def resume(self, ctx):
#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         song = await player.resume()
#         self.players[ctx.guild.id] = player

#         await send_basic_response(ctx, f"Resuming **{song.name}** in **{self.channels.get(ctx.guild.id).name}**", colors.pink)

#     @commands.command()
#     async def volume(self, ctx, vol):
#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         vol = float(vol)
#         if vol < 0 or vol > 100:
#             await send_basic_response(ctx, "The volume must be between **0** to **100**.", colors.red)
#             return

#         if not ctx.author.voice:
#             await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         song, volume = await player.change_volume(vol / 100)

#         self.players[ctx.guild.id] = player

#         await send_basic_response(ctx, f"Volume set to **{int(volume * 100)}%** for **{song.name}**.", colors.pink)

#     @commands.command()
#     async def pause(self, ctx):
#         if not ctx.author.voice:
#             await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
#             return

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         song = await player.pause()

#         self.players[ctx.guild.id] = player

#         await send_basic_response(ctx, f"Paused **{song.name}** in {self.channels.get(ctx.guild.id).name}", colors.pink)

#     @commands.command()
#     async def skip(self, ctx):
#         if not ctx.author.voice:
#             await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
#             return

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         data = await player.skip(force=True)

#         self.players[ctx.guild.id] = player

#         await send_basic_response(ctx, f"Skipping 🎶 **{data[0].name}**.", colors.pink)

#     @commands.command()
#     async def remove(self, ctx, index):
#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         try:
#             song = await player.remove_from_queue(int(index))
#             await send_basic_response(ctx, f"Removed 🎶 **{song.name}** from queue.", colors.pink)
#         except:
#             await send_basic_response(ctx, "Could not remove song from the queue, perhaps the queue is empty.", colors.pink)

#         self.players[ctx.guild.id] = player

#     @commands.command(aliases=['disconnect', 'dc'])
#     async def leave(self, ctx):
#         if not ctx.voice_client:
#             await send_basic_response(ctx, "Not connected to a **voice channel**.", colors.red)
#             return

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         embed = discord.Embed(
#             colour=colors.pink,
#             description=f"Disconnected from **[{ctx.voice_client.channel.name}]** and unbound from **[{self.channels[ctx.guild.id].name}]**."
#         )

#         player = self.players.get(ctx.guild.id)
#         if player:
#             await player.stop()
#             self.players.pop(ctx.guild.id)

#         await ctx.send(embed=embed)
#         await ctx.voice_client.disconnect()

#     @commands.command()
#     async def resetplayer(self, ctx, from_error=False):
#         des_text = [
#             "**Resetting player...**\n\nIf you are having difficulty in trying to control the **music player**, this might resolve the issue.",
#             "**Resetting player...**\n\nIt seems like an error has occurred in your command. Hold on while I try to fix it for you."
#         ]

#         await ctx.invoke(self.client.get_command('leave'))

#         embed = discord.Embed(
#             colour=colors.red,
#             description=f"{des_text[0] if not from_error else des_text[1]}"
#         )

#         if from_error:
#             await ctx.invoke(self.client.get_command('join'), silent=True)

#         await ctx.send(embed=embed, delete_after=30)

#         try:    
#             await ctx.voice_client.disconnect()
#         except:
#             pass

#     @commands.command()
#     async def fave(self, ctx):
#         player = self.players.get(ctx.guild.id)
#         if not player:
#             await send_basic_response(ctx, "There is no **active player**.", colors.red)
#             return

#         song = player.now_playing()
#         if not song:
#             await send_basic_response(ctx, "There is no **song** currently playing.", colors.red)
#             return

#         with open(f"playlists/{ctx.author.id}.txt", 'a', encoding="utf8") as f:
#             f.write(f"{song.name}\n")

#         await send_basic_response(ctx, f"Added **{song.name}** to your favorites.", colors.pink)

#     @commands.command()
#     async def unfave(self, ctx, i: int):
#         i = i - 1
#         with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
#             songs = f.read().splitlines()

#         playlist = ""
#         for index, song in enumerate(songs):
#             if index == i:
#                 await send_basic_response(ctx, f"**{song}** has been removed from your favorites.", colors.pink)
#             else:
#                 playlist = playlist + f"{song}\n"

#         with open(f"playlists/{ctx.author.id}.txt", 'w', encoding="utf8") as a:
#             a.write(playlist)

#     @commands.command(aliases=['faves'])
#     async def favorites(self, ctx):
#         pf = self.client.prefix(self.client, ctx.message)

#         with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
#             songs = f.read().splitlines()

#         playlist = ""
#         for index, song in enumerate(songs, start=1):
#             playlist = playlist + f"`{index}` {song}\n"

#         embed = discord.Embed(colour=colors.pink, title="❤️ Liked Songs", description=playlist)
#         embed.set_footer(text=f"Use `{pf}unfave <id>` to remove an item from your favorites.")
#         await ctx.send(embed=embed)

#     @commands.command(aliases=['playfaves', 'pl', 'pf'])
#     async def playliked(self, ctx, number=None):
#         if not ctx.author.voice:
#             await send_basic_response(ctx, "Please connect to a voice channel first.", colors.red)
#             return

#         if not ctx.voice_client:
#             await ctx.invoke(self.client.get_command('join'))

#         if ctx.channel != self.channels[ctx.guild.id]:
#             await send_basic_response(ctx, f"The player can only be controlled from **[{self.channels[ctx.guild.id]}]**.", colors.red)
#             return

#         with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
#             songs = f.read().splitlines()

#         if number:
#             try:
#                 number = int(number) - 1
#             except:
#                 await send_basic_response(ctx, "Invalid song ID.", colors.red)
#                 return

#             await ctx.invoke(self.client.get_command('play'), url=songs[number])
#             return

#         player = self.players.get(ctx.guild.id)
#         if not player:
#             player = music.create_player(ctx, ffmpeg_error_betterfix=True)

#         for song in songs:
#             if not player.now_playing():
#                 await player.queue(song, search=True)
#                 song = await player.play()
#             else:
#                 song = await player.queue(song, search=True)

#         self.players[ctx.guild.id] = player

#         embed = discord.Embed(
#             colour=colors.pink,
#             title="❤️ Playing songs that you like",
#             description="".join(
#                 [f"`{index}` {song}\n" for index, song in enumerate(songs, start=1)]
#             )
#         )
#         await ctx.send(embed=embed)

# async def setup(client):
#     await client.add_cog(Voice(client))