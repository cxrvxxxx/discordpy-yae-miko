import discord
from discord import app_commands
from discord.ext import commands

from ..monaheist import MonaHeist
from ..game import Game
from .. import colors

class MonaHeistActions(MonaHeist):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__(client)

    @commands.cooldown(1, 90, commands.BucketType.user)
    @app_commands.command(name='work', description='Earn money and exp.')
    async def work(self, interaction: discord.Interaction) -> None:
        game = Game(interaction.guild_id)

        