import os
import asyncio
import discord
from discord.ext import commands
from core import colors
from core.player import Music
from core.logger import console_log
from core.ui import player_controls
from core.message import *

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
        # auto disconnect
        if member == self.client.user:
            return

        autodc_enabled = self.config[member.guild.id].getboolean(__name__, 'voice_auto_disconnect')
        if not before and after and not autodc_enabled:
            return
        
        guild = self.client.get_guild(member.guild.id)

        if not guild.voice_client:
            return

        console_log("Auto-disconnect timer started.")
        await asyncio.sleep(10)

        # redundancy check in case the bot already disconnected
        if not guild.voice_client:
            return

        if len(guild.voice_client.channel.members) < 2:
            # unbind channel and clear player
            channel = self.music.get_player(guild.id).get_channel()
            self.music.close_player(guild.id)
        
            await send_notif(channel, Responses.bot_disconnect)
            await guild.voice_client.disconnect()
        else:
            console_log("Auto-disconnect timer ended. There are users in the channel.")

    @commands.command()
    async def join(self, ctx):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return
        if ctx.voice_client:
            await send_error_message(
                ctx,
                Responses.bot_is_connected.format(
                    channel_name=ctx.voice_client.channel.name
                )
            )
            return

        await ctx.author.voice.channel.connect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)

        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if player and ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        if not ctx.voice_client:
            await ctx.invoke(self.client.get_command("join"))

        if not player:
            player = self.music.create_player(ctx, on_play = "nowplaying")
            await send_notif(
                ctx,
                Responses.bot_on_connect.format(
                    vc_name=ctx.author.voice.channel.name,
                    channel_name=ctx.channel.name
                )
            )

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

            await ctx.send(embed=embed, delete_after=10)

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        queue = player.get_queue()

        if not queue:
            await send_error_message(
                ctx,
                Responses.music_empty_queue
            )
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
        if player.last_np_msg:
            await player.last_np_msg.delete()

        player.last_np_msg = await ctx.send(embed=embed, view=player_controls(ctx))

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        await ctx.message.delete()
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        queue = player.get_queue()

        if not queue:
            await send_error_message(
                ctx,
                Responses.music_empty_queue
            )
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

        songs = "There are no songs in the queue."

        if len(queue) > 1:
            songs = ""
            overflow = 0

            for index, song in enumerate(queue):
                if index == 0:
                    continue

                line = f"\n `{index}` {song.get_title()}"
                if index < 10:
                    songs += line
                else:
                    overflow += 1

            if overflow > 0:
                songs += f"\n\n...and **` {overflow} `** more songs."

        embed.add_field(
            name="🎶 Up Next...",
            value=songs,
            inline=False
        )

        embed.set_footer(text=f"If you like this song, use '{pf}fave' to add this to your favorites!")
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(aliases=['rm'])
    async def remove(self, ctx, index):
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        song = player.dequeue(index)
        queue = player.get_queue()

        if not queue:
            await send_error_message(
                ctx,
                Responses.music_empty_queue
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Song removed from queue."
        )
        embed.set_thumbnail(
            url=song.get_thumbnail()
        )
        embed.set_author(
                name=f"{song.get_title()}",
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
        await ctx.send(embed=embed, delete_after=10)

        await ctx.message.delete()

    @commands.command()
    async def prev(self, ctx, normal: bool = True):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        song = await player.prev()

        if not song:
            await send_error_message(
                ctx,
                Responses.music_no_previous
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Playing last song, 🎶 **{song.get_title()}**."
        )

        await ctx.send(embed=embed, delete_after=10)

        # if invoked from button callback
        if not normal:
            return

        await ctx.message.delete()

    @commands.command()
    async def skip(self, ctx, normal: bool = True):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        song = await player.skip()

        if not song:
            await send_error_message(
                ctx,
                Responses.music_no_skip
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Skipping 🎶 **{song.get_title()}**."
        )

        await ctx.send(embed=embed, delete_after=10)

        # if invoked from button callback
        if not normal:
            return

        await ctx.message.delete()

    @commands.command()
    async def pause(self, ctx, normal: bool = True):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        song = await player.pause()

        if not song:
            await send_error_message(
                ctx,
                Responses.music_no_pause
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Paused 🎶 **{song.get_title()}**."
        )

        await ctx.send(embed=embed, delete_after=10)

        # if invoked from button callback
        if not normal:
            return

        await ctx.message.delete()

    @commands.command()
    async def resume(self, ctx, normal: bool = True):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        song = await player.resume()

        if not song:
            await send_error_message(
                ctx,
                Responses.music_no_resume
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Resumed 🎶 **{song.get_title()}**."
        )

        await ctx.send(embed=embed, delete_after=10)

        # if invoked from button callback
        if not normal:
            return

        await ctx.message.delete()

    @commands.command(aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        if not ctx.voice_client:
            await send_error_message(
                ctx,
                Responses.bot_not_connected
            )
            return

        player = self.music.get_player(ctx.guild.id)

        if player:
            if ctx.channel != player.get_channel():
                await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
                return

            self.music.close_player(ctx.guild.id)

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Disconnected from **[{ctx.voice_client.channel.name}]** and unbound from **[{player.get_channel().name if player else 'channel'}]**."
        )        

        await ctx.voice_client.disconnect()
        await ctx.send(embed=embed)

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx, vol = None):
        player = self.music.get_player(ctx.guild.id)

        if not vol:
            await send_notif(
                ctx,
                Responses.music_player_volume.format(
                    volume=int(player.get_volume() * 100)
                )
            )
            return

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        vol = float(vol)
        if vol < 0 or vol > 100:
            await send_error_message(
                ctx,
                Responses.music_player_volume_invalid
            )
            return

        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        
        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        volume = player.set_volume(vol)

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Volume set to **{int(volume * 100)}%**."
        )

        await ctx.send(embed=embed, delete_after=10)

    @commands.command()
    async def fave(self, ctx):
        player = self.music.get_player(ctx.guild.id)
        if not player:
            await send_error_message(
                ctx,
                Responses.music_no_player
            )
            return

        song = player.now_playing
        if not song:
            await send_notif(
                ctx,
                Responses.music_player_no_song
            )
            return

        with open(f"playlists/{ctx.author.id}.txt", 'a', encoding="utf8") as f:
            f.write(f"{song.get_title()}\n")

        await send_notif(
            ctx,
            Responses.music_player_fav_add.format(
                title=song.get_title()
            )
        )

    @commands.command()
    async def unfave(self, ctx, i: int):
        i = i - 1
        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
            songs = f.read().splitlines()

        playlist = ""
        for index, song in enumerate(songs):
            if index == i:
                await send_notif(
                    ctx,
                    Responses.music_player_fav_rm.format(
                        title=song
                    )
                )
            else:
                playlist = playlist + f"{song}\n"

        with open(f"playlists/{ctx.author.id}.txt", 'w', encoding="utf8") as a:
            a.write(playlist)

    @commands.command(aliases=['faves', 'favelist', 'favlist'])
    async def favorites(self, ctx):
        pf = self.client.prefix(self.client, ctx.message)

        try:
            with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
                songs = f.read().splitlines()

            playlist = ""
            for index, song in enumerate(songs, start=1):
                playlist = playlist + f"`{index}` {song}\n"

            playlist = "None" if playlist == "" else playlist

            embed = discord.Embed(colour=colors.pink, title="❤️ Liked Songs", description=playlist)
            embed.set_footer(text=f"Use `{pf}unfave <id>` to remove an item from your favorites.")
            await ctx.send(embed=embed)
        except FileNotFoundError:
            await send_error_message(
                ctx,
                Responses.music_player_no_fav
            )   

    @commands.command(aliases=['playfaves', 'pl', 'pf'])
    async def playliked(self, ctx, number=None):
        if not ctx.author.voice:
            await send_error_message(
                ctx,
                Responses.user_no_voice
            )
            return

        if not ctx.voice_client:
            await ctx.invoke(self.client.get_command('join'))

        player = self.music.get_player(ctx.guild.id)

        if not player:
            player = self.music.create_player(ctx, "nowplaying")

        if ctx.channel != player.get_channel():
            await send_error_message(
                ctx,
                Responses.music_wrong_channel.format(
                    channel_name=player.get_channel().name
                )
            )
            return

        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
            songs = f.read().splitlines()

        if number:
            try:
                number = int(number) - 1
            except:
                await send_error_message(
                    ctx,
                    Responses.msuic_player_fav_invalid
                )
                return

            await player.play(songs[number])
            return

        desc = "Processing, please wait..."
        msg = await player.get_channel().send(
            embed=discord.Embed(
                colour=colors.pink,
                title="❤️ Playing songs that you like",
                description=desc
            )
        )

        desc = ""
        for index, song in enumerate(songs, start=1):
            desc += f"`{index}` {song}\n"
            
            await msg.edit(
                embed=discord.Embed(
                    colour=colors.pink,
                    title=f"❤️ Playing songs that you like ({index}/{len(songs)})",
                    description=desc
                )
            )
            await player.play(song, silent=True)

        await msg.edit(
            embed=discord.Embed(
                colour=colors.pink,
                title=f"❤️ Playing songs that you like",
                description=desc
            ), view=player_controls(ctx)
        )

async def setup(client):
    await client.add_cog(Voice(client))
