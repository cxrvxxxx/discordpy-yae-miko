import discord
from discord import app_commands
from discord.ext import commands
from .monaheist import MonaHeist
from .controller.playercontroller import PlayerController
from .objects.player import Player
from .objects.response import Response
from .colors import *

class MonaHeistAccount(MonaHeist):
    def __init__(self, client: commands.Bot):
        super().__init__(client)

    @app_commands.command(name='register', description='Create a MonaHeist account.')
    @app_commands.describe(name='Character name.')
    async def register(self, interaction: discord.Interaction, name: str) -> None:
        uid: int = interaction.user.id
        resp: Response = PlayerController.register(uid, name)

        if not resp.success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red,
                    description=resp.message
                )
            )
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                color=pink,
                description='You are now registered.'
            )
        )

    @app_commands.command(name='me', description="Show your user profile.")
    async def me(self, interaction: discord.Interaction) -> None:
        uid: int = interaction.user.id
        resp: Response = PlayerController.profile(uid)

        if not resp.success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red,
                    description=resp.message
                )
            )
            return
        
        player: Player = resp.data.get('player')

        embed = discord.Embed(
            color=pink,
            title=f"{player.player_name}'s profile",
            description=interaction.user.mention
        )
        embed.add_field(
            name="Bio",
            value=player.bio if player.bio else "No bio",
            inline=False
        )
        embed.add_field(
            name="Account Information",
            value="".join([ f'{key}: {value}\n' for key, value in player.account_info().items()]),
            inline=False
        )
        embed.add_field(
            name="Character Information",
            value="".join([f'{key}: {value}\n' for key, value in player.char_stats().items()]),
            inline=False
        )
        embed.add_field(
            name="Affiliations",
            value="".join([f'{key}: {value}\n' for key, value in player.affiliations().items()]),
            inline=False
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_author(name=interaction.user.nick)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='profile', description="Check a user's profile.")
    @app_commands.describe(member='User to check.')
    async def profile(self, interaction: discord.Interaction, member: discord.Member) -> None:
        uid: int = member.id
        resp: Response = PlayerController.profile(uid)

        if not resp.success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red,
                    description=resp.message
                )
            )
            return
        
        player: Player = resp.data.get('player')

        embed = discord.Embed(
            color=pink,
            title=f"{player.player_name}'s profile",
            description=interaction.user.mentions
        )
        embed.add_field(
            name="Bio",
            value=player.bio if player.bio else "No bio",
            inline=False
        )
        embed.add_field(
            name="Account Information",
            value="".join([ f'{key}: {value}\n' for key, value in player.account_info().items()]),
            inline=False
        )
        embed.add_field(
            name="Character Information",
            value="".join([f'{key}: {value}\n' for key, value in player.char_stats().items()]),
            inline=False
        )
        embed.add_field(
            name="Affiliations",
            value="".join([f'{key}: {value}\n' for key, value in player.affiliations().items()]),
            inline=False
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=member.nick)
        await interaction.response.send_message(embed=embed)
