import os
import asyncio
import discord
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
        
            await send_basic_response(channel, f"Disconnecting from voice since no one else is in the channel.", colors.pink)
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
        await ctx.send(embed=embed)

    @commands.command(aliases=['rm'])
    async def remove(self, ctx, index):
        pf = self.client.prefix(self.client, ctx.message)

        player = self.music.get_player(ctx.guild.id)

        if not player:
            await send_basic_response (ctx, "There is no **active player**.", colors.red)
            return

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        song = player.dequeue(index)
        queue = player.get_queue()

        if not queue:
            await send_basic_response (ctx, "The queue is **empty** because there is nothing being currently played.", colors.red)
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

            self.music.close_player(ctx.guild.id)

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Disconnected from **[{ctx.voice_client.channel.name}]** and unbound from **[{player.get_channel().name if player else 'channel'}]**."
        )        

        await ctx.send(embed=embed)
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx, vol = None):
        player = self.music.get_player(ctx.guild.id)

        if not vol:
            await send_basic_response(ctx, f"Player volume: **{int(player.get_volume() * 100)}%**.", colors.pink)
            return

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel()}]**.", colors.red)
            return

        vol = float(vol)
        if vol < 0 or vol > 100:
            await send_basic_response(ctx, "The volume must be between **0** to **100**.", colors.red)
            return

        if not ctx.author.voice:
            await send_basic_response(ctx, "You are not connected to a **voice channel**.", colors.red)
            return

        
        if not player:
            await send_basic_response(ctx, "There is no **active player**.", colors.red)
            return

        volume = player.set_volume(vol)

        await send_basic_response(ctx, f"Volume set to **{int(volume * 100)}%**.", colors.pink)

    @commands.command()
    async def fave(self, ctx):
        player = self.music.get_player(ctx.guild.id)
        if not player:
            await send_basic_response(ctx, "There is no **active player**.", colors.red)
            return

        song = player.now_playing
        if not song:
            await send_basic_response(ctx, "There is no **song** currently playing.", colors.red)
            return

        with open(f"playlists/{ctx.author.id}.txt", 'a', encoding="utf8") as f:
            f.write(f"{song.get_title()}\n")

        await send_basic_response(ctx, f"Added **{song.get_title()}** to your favorites.", colors.pink)

    @commands.command()
    async def unfave(self, ctx, i: int):
        i = i - 1
        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
            songs = f.read().splitlines()

        playlist = ""
        for index, song in enumerate(songs):
            if index == i:
                await send_basic_response(ctx, f"**{song}** has been removed from your favorites.", colors.pink)
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
            await send_basic_response(ctx, "It seems that you haven't added any song to your favorites yet.", colors.red)   

    @commands.command(aliases=['playfaves', 'pl', 'pf'])
    async def playliked(self, ctx, number=None):
        if not ctx.author.voice:
            await send_basic_response(ctx, "Please connect to a voice channel first.", colors.red)
            return

        if not ctx.voice_client:
            await ctx.invoke(self.client.get_command('join'))

        player = self.music.get_player(ctx.guild.id)

        if not player:
            player = self.music.create_player(ctx, "nowplaying")

        if ctx.channel != player.get_channel():
            await send_basic_response(ctx, f"The player can only be controlled from **[{player.get_channel().name}]**.", colors.red)
            return

        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as f:
            songs = f.read().splitlines()

        if number:
            try:
                number = int(number) - 1
            except:
                await send_basic_response(ctx, "Invalid song ID.", colors.red)
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
            )
        )

    # TODO: pause, resume

async def setup(client):
    await client.add_cog(Voice(client))