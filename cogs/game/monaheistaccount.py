import discord
from discord import app_commands
from discord.ext import commands
from .monaheist import MonaHeist
from .controller.playercontroller import PlayerController
from .colors import *

class MonaHeistAccount(MonaHeist):
    def __init__(self, client: commands.Bot):
        super().__init__(client)

    @app_commands.command(name='register', description='Create a MonaHeist account.')
    @app_commands.describe(name='Character name.')
    async def register(self, interaction: discord.Interaction, name: str) -> None:
        uid = interaction.user.id

        resp = PlayerController.register(uid, name)
        if not resp.success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=red,
                    description=resp.message
                )
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                color=pink,
                description='You are now registered.'
            )
        )
