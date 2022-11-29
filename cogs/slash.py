import discord
from discord import app_commands
from discord.ext import commands

class Slash(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(
        name="ping",
        description="Replies with Pong!"
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!", ephemeral=True)

    @app_commands.command(
        name="play",
        description="Play something."
    )
    @app_commands.describe(
        query="Title to search or URL"
    )
    async def play(
        self,
        interaction: discord.Interaction,
        *, query: str
    ) -> None:
        ctx = await self.client.get_context(interaction)
        await ctx.invoke(self.client.get_command("play"), query=query)

async def setup(client):
    await client.add_cog(Slash(client))
