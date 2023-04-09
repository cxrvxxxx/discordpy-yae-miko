import discord
from discord import app_commands
from discord.ext import commands

from ..monaheist import MonaHeist
from ..game import Game
from .. import colors

class MonaHeistAccount(MonaHeist):
    def __init__(self, client: commands.Bot) -> None:
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
            value=f"Registered: {player.join_date}",
            inline=False
        )
        embed.add_field(
            name="Player Statistics",
            value=f"".join([f'{data}\n' for data in f'{player}'.split(',')[1:-2]]),
            inline=False
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_author(name='MonaHeist 2.0')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='profile', description="Check someone's profile.")
    @app_commands.describe(member='User to check.')
    async def profile(self, interaction: discord.Interaction, member: discord.Member) -> None:
        game = Game(interaction.user.id)

        player = game.players.get_player(member.id)

        if not player:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=colors.red,
                    description="No user found."
                )
            )
            return
        
        embed = discord.Embed(
            color=colors.pink,
            title=f"Showing {member.nick}'s profile",
            description=f"{member.mention}"
        )
        embed.add_field(
            name="Account Information",
            value=f"Registered: {player.join_date}",
            inline=False
        )
        embed.add_field(
            name="Player Statistics",
            value="".join([f'{data}\n' for data in f'{player}'.split(',')[1:-2]]),
            inline=False
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_author(name='MonaHeist 2.0')
        await interaction.response.send_message(embed=embed)
