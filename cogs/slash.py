import discord
from discord import app_commands
from discord.ext import commands

class Slash(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!", ephemeral=True)

async def setup(client):
    await client.add_cog(Slash(client))
