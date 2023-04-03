import discord
from discord import app_commands
from discord.ext import commands

from ..monaheist import MonaHeist

class MonaHeistAccount(MonaHeist):
    def __init__(self, client: commands.Bot):
        super().__init__(client)

    @app_commands.command(name='register', description='Create a MonaHeist account.')
    async def register(self, interaction: discord.Interaction) -> None:
        pass