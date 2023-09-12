"""
A module for playing music in voice channels
"""
# Standard imports
import asyncio
import json
import logging
import os

# Third-party library imports
import discord
from discord.ext import commands
from discord import app_commands

# Core imports
from core import colors
from core.message import send_error_message, send_notif, Responses

# Package iports
from .classes.music import Music

# init dir
if not os.path.exists('playlists'):
    os.mkdir('playlists')

class MusicCommands(commands.Cog):
    """Command class"""
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        self.client.logging_config["loggers"]["yaemiko.music"] = {
            "handlers": ["debugHandler", "fileHandler"],
            "level": "DEBUG",
            "propagate": False
        }

        self.client.logging_config["loggers"]["yaemiko.music.ui"] = {
            "handlers": ["debugHandler", "fileHandler"],
            "level": "DEBUG",
            "propagate": False
        }

        self.client.logging_config["loggers"]["yaemiko.music.player"] = {
            "handlers": ["debugHandler", "fileHandler"],
            "level": "DEBUG",
            "propagate": False
        }

        self.client.logging_config["loggers"]["yaemiko.music.song"] = {
            "handlers": ["debugHandler", "fileHandler"],
            "level": "DEBUG",
            "propagate": False
        }

        self.client.configure_logger()
        self.logger = logging.getLogger("yaemiko.music")

        self.music  = Music()
        
        with open(os.path.join(os.path.dirname(__file__), 'settings.json'), 'r') as f:
            self.MUSIC_SETTINGS = json.load(f)

    async def auto_disconnect(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Handles automatic disconnection of the bot from voice"""
        # Settings
        feautre_enabled = self.MUSIC_SETTINGS.get("enable_auto_disconnect")
        timeout = self.MUSIC_SETTINGS.get("auto_disconnect_timeout")

        if not feautre_enabled:
            return

        guild = self.client.get_guild(member.guild.id)
        # Ignore if the bost is not connected
        if not guild.voice_client:
            return

        self.logger.debug(f"Started auto-disconnect timer in guild: ({guild.id}).")
        # Delay before the bot disconnects
        await asyncio.sleep(timeout)

        user_count = len(guild.voice_client.channel.members)
        if user_count < 2:
            player = self.music.get_player(guild.id)
            channel = player.channel

            if player:
                self.music.close_player(guild.id)

            await channel.send(
                embed=discord.Embed(
                    colour=colors.pink,
                    description=Responses.bot_disconnect
                )
            )
            await guild.voice_client.disconnect()
            self.logger.debug(f"Disconnected from voice in guild: ({guild.id})")
        else:
            self.logger.debug(f"Finished timer in guild: ({guild.id}), aborting auto-disconnect")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Cog set-up function when added to client"""
        pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Called when a user updates their voice state"""
        # For updates thaat do not come from the bot
        if member != self.client.user:
            await self.auto_disconnect(member, before, after)

    @app_commands.command(name="play", description="Connect to voice and play something.")
    @app_commands.describe(query="Title or URL of audio to be played")
    async def play(self, interaction: discord.Interaction, *, query: str) -> None:
        """Plays a song from specified query"""
        if not interaction.user.voice:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.user_no_voice
                ),
                delete_after=10
            )
            return

        player = self.music.get_player(interaction.guild_id)

        if player and interaction.channel != player.channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_wrong_channel.format(
                        channel_name=player.channel.name
                    )
                ),
                delete_after=10
            )
            return

        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()

        if not player:
            player = self.music.create_player(await self.client.get_context(interaction))
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=Responses.bot_on_connect.format(
                        vc_name=interaction.user.voice.channel.name,
                        channel_name=interaction.channel.name
                    ),
                    colour=colors.pink
                )
            )

        await player.play(query, interaction)

    @app_commands.command(name="queue", description="View the list of queued songs")
    async def queue(self, interaction: discord.Interaction) -> None:
        """Displays the list of queued songs/tracks"""
        player = self.music.get_player(interaction.guild_id)

        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_no_player
                ),
                delete_after=10
            )
            return

        if player and interaction.channel != player.channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_wrong_channel.format(
                        channel_name=player.channel.name
                    )
                ),
                delete_after=10
            )
            return

        queue = player.queue

        if queue.is_empty():
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_empty_queue
                ),
                delete_after=10
            )
            return

        embed = discord.Embed(
            colour=colors.pink,
            description=f"🎶 Up Next in **{player.channel.name}**"
        )
        embed.set_thumbnail(
            url=queue.items[0].thumbnail
        )
        embed.set_author(
                name=f"{queue.items[0].title}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )

        if queue.size() > 1:
            songs = ""
            overflow = 0

            for index, song in enumerate(queue.items[1:], 2):
                if index < 10:
                    songs += f"\n `{index}` {song.title}"
                    continue
                
                overflow += 1

            if overflow > 0:
                songs += f"\n\n...and **` {overflow} `** more songs."

            embed.add_field(
                name="More tracks",
                value=songs,
                inline=False
            )

        await interaction.response.send_message(embed=embed, delete_after=10)

    @app_commands.command(name="remove", description="Removes a song from the queue")
    @app_commands.describe(index="The ID of the song to dequeue")
    async def remove(self, interaction: discord.Interaction, index: int) -> None:
        """Removes a song/track from the queue"""

        player = self.music.get_player(interaction.guild.id)

        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_no_player
                ),
                delete_after=10
            )
            return

        if player and interaction.channel != player.channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_wrong_channel.format(
                        channel_name=player.channel.name
                    )
                ),
                delete_after=10
            )
            return

        queue = player.queue

        if queue.is_empty():
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_empty_queue
                ),
                delete_after=10
            )
            return

        song = queue.dequeue(index - 1)

        embed = discord.Embed(
            colour=colors.pink,
            description="Song removed from queue."
        )
        embed.set_thumbnail(
            url=song.thumbnail
        )
        embed.set_author(
                name=f"{song.title}",
                icon_url="https://i.imgur.com/rcXLQLG.png"
            )

        await interaction.response.send_message(embed=embed, delete_after=10)

    @app_commands.command(name="leave", description="Leave current voice channel")
    async def leave(self, interaction: discord.Interaction) -> None:
        """Makes the bot disconnect from the user's voice channel"""
        if not interaction.guild.voice_client:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.bot_not_connected
                ),
                delete_after=10
            )
            return

        player = self.music.get_player(interaction.guild.id)

        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_no_player
                ),
                delete_after=10
            )
            return

        self.music.close_player(interaction.guild.id)

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Disconnected from **[{interaction.guild.voice_client.channel.name}]** and \
                        unbound from **[{player.channel.name if player else 'channel'}]**."
        )

        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(embed=embed, delete_after=10)

    @app_commands.command(name="volume", description="Set playback volume")
    @app_commands.describe(vol="Value from 0 to 100")
    async def volume(self, interaction: discord.Interaction, vol: int) -> None:
        """Sets the volume of the player"""
        player = self.music.get_player(interaction.guild.id)

        if player and interaction.channel != player.channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_wrong_channel.format(
                        channel_name=player.channel.name
                    )
                ),
                delete_after=10
            )
            return

        vol = float(vol)
        if vol < 0 or vol > 100:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_player_volume_invalid
                ),
                delete_after=10
            )
            return

        if not interaction.user.voice:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.user_no_voice
                ),
                delete_after=10
            )
            return

        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    colour=colors.red,
                    description=Responses.music_no_player
                ),
                delete_after=10
            )
            return

        volume = player.set_volume(vol)

        embed = discord.Embed(
            colour=colors.pink,
            description=f"Volume set to **{int(volume * 100)}%**."
        )

        await interaction.response.send_message(embed=embed, delete_after=10)

    @commands.command()
    async def fave(self, ctx: commands.Context) -> None:
        """Add currently playing song/track to favorites"""
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

        with open(f"playlists/{ctx.author.id}.txt", 'a', encoding="utf8") as file:
            file.write(f"{song.get_title()}\n")

        await send_notif(
            ctx,
            Responses.music_player_fav_add.format(
                title=song.get_title()
            )
        )

    @commands.command()
    async def unfave(self, ctx: commands.Context, i: int) -> None:
        """Removes the specified song from favorites"""
        i = i - 1
        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as file:
            songs = file.read().splitlines()

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

        with open(f"playlists/{ctx.author.id}.txt", 'w', encoding="utf8") as file:
            file.write(playlist)

    @commands.command(aliases=['faves', 'favelist', 'favlist'])
    async def favorites(self, ctx: commands.Context) -> None:
        """Display a list of songs/tracks added to favorites"""
        pref = self.client.prefix(self.client, ctx.message)

        try:
            with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as file:
                songs = file.read().splitlines()

            playlist = ""
            for index, song in enumerate(songs, start=1):
                playlist = playlist + f"`{index}` {song}\n"

            playlist = "None" if playlist == "" else playlist

            embed = discord.Embed(colour=colors.pink, title="❤️ Liked Songs", description=playlist)
            embed.set_footer(text=f"Use `{pref}unfave <id>` to remove an item from your favorites.")
            await ctx.send(embed=embed)
        except FileNotFoundError:
            await send_error_message(
                ctx,
                Responses.music_player_no_fav
            )

    @commands.command(aliases=['playfaves', 'pl', 'pref'])
    async def playliked(self, ctx: commands.Context, number=None):
        """Plays song(s, if specified) from favorites"""
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

        with open(f"playlists/{ctx.author.id}.txt", 'r', encoding="utf8") as file:
            songs = file.read().splitlines()

        if number:
            try:
                number = int(number) - 1
            except ValueError:
                self.logger.debug(f"Failed to convert {number} to integer type")
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
                title="❤️ Playing songs that you like",
                description=desc
            )
        )

        await ctx.invoke(self.client.get_command("nowplaying"))
