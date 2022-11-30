from typing import Optional
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from core.colors import *

class Slash(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!", ephemeral=True)

    @app_commands.command(name="whois", description="See user info")
    @app_commands.describe(member="The user to show profile of")
    async def whois(self, interaction: discord.Interaction, member: Optional[discord.Member] = None) -> None:
        if not member:
            member = interaction.user

        roles = [role for role in member.roles]
        embed = discord.Embed(
            colour=pink,
            timestamp=datetime.now(),
            title=f"User Info - {member}"
        )
        embed.set_thumbnail(
            url=member.avatar.url
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}"
        )
        embed.add_field(
            name="ID:",
            value=member.id
        )
        embed.add_field(
            name="Display Name:",
            value=member.display_name
        )
        embed.add_field(
            name="Created Account On:",
            value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        )
        embed.add_field(
            name="Joined Server On:",
            value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        )
        embed.add_field(
            name="Roles:",
            value="".join([role.mention + "\n" for role in roles[1:]] if len(roles) > 1 else "None")
        )
        embed.add_field(
            name="Highest Role:",
            value=member.top_role.mention if len(roles) > 1 else "None"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play something.")
    @app_commands.describe(query="Title to search or URL")
    async def play(self, interaction: discord.Interaction, *, query: str) -> None:
        ctx = await self.client.get_context(interaction)
        await ctx.invoke(self.client.get_command("play"), query=query)

async def setup(client):
    await client.add_cog(Slash(client))
