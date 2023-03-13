import discord

from discord import app_commands
from discord.ext import commands

from .values.colors import default, danger, success, warn

from .handlers.player_handler import PlayerHandler

class MonaHeist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name='register', description='Create a Mona Heist account.')
    async def register(self, interaction: discord.Interaction) -> None:
        resp = PlayerHandler.on_register(interaction.user.id, interaction.user.name)

        embed = discord.Embed(
            colour = success if resp.success else danger,
            description = "You are now registered."  if resp.success else "Registration failed."
        )

        await interaction.response.send_message(embed=embed)

    @commands.command()
    async def migrate(self, ctx):
        from .schemas import schema
        await ctx.send("Initialization successful.")
