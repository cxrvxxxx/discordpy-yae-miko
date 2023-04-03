import discord
from discord import app_commands
from discord.ext import commands

from ..monaheist import MonaHeist
from ..game import Game
from .. import colors

class MonaHeistAccount(MonaHeist):
    def __init__(self, client: commands.Bot):
        super().__init__(client)

    @app_commands.command(name='register', description='Create a MonaHeist account.')
    async def register(self, interaction: discord.Interaction) -> None:
        game = Game(interaction.guild_id)
        
        if game.players.get_player(interaction.user.id):
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=colors.red,
                    description="You are already registered!"
                )
            )
            return
        
        player = game.players.create_player(interaction.user.id)
        result = game.players.save(player)

        if not result:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=colors.red,
                    description="Registration failed.",
                )
            )
            return
        
        await interaction.response.send_message(
            embed=discord.Embed(
                color=colors.green,
                description="Successfully registered!"
            )
        )

    @app_commands.command(name='me', description='Show your account details.')
    async def me(self, interaction: discord.Interaction) -> None:
        game = Game(interaction.guild_id)

        player = game.players.get_player(interaction.user.id)
        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=colors.red,
                    description="You are not registered. Use `/register` to create an account."
                )
            )
            return
        
        embed = discord.Embed(
            color=colors.pink,
            title=f"Showing {interaction.user.nick}'s profile",
            description=f"{interaction.user.mention}"
        )
        embed.add_field(
            name="Account Information",
            value=f"Date registered: {player.join_date}",
            inline=False
        )
        embed.add_field(
            name="Player Statistics",
            value=f"Level: {player.level}\nExp: {player.experience}\nCash:{player.cash}",
            inline=False
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_author(name='MonaHeist 2.0')
        await interaction.response.send_message(embed=embed)
