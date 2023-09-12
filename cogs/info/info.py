import discord

from discord.ext import commands
from core import colors

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def info(self, ctx: commands.Context):
        embed = discord.Embed(
            title=self.client.version.get("name"),
            description=self.client.version.get("description"),
            colour=colors.pink
        )
        
        embed.add_field(
            name="Version",
            value=self.client.version.get("version")
        )

        embed.add_field(
            name="Author",
            value=self.client.version.get("author")
        )

        embed.add_field(
            name="GitHub URL",
            value=self.client.version.get("url")
        )

        embed.add_field(
            name="License",
            value=self.client.version.get("license")
        )

        await ctx.send(embed=embed)
