import discord

from discord import app_commands
from discord.ext import commands

from .game import Game
from .values.colors import default, danger, success, warn

class MonaHeist(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.game = Game()

    @app_commands.command(name='register', description='Create a Mona Heist account.')
    async def register(self, interaction: discord.Interaction) -> None:
        user = self.game.create_user(interaction.user.id)

        if not user:
            embed = discord.Embed(
                color = danger,
                description = 'Registration failed. (Existing user)'
            )

            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            color = success,
            description = 'You are now registered.'
        )
        await interaction.response.send_message(embed=embed)
