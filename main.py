"""
Project name: Yae Miko - Discord Bot [discord.py]
Author: cxrvxxx
Repository URL: https://github.com/cxrvxxx/yae-miko
Description: A feature-packed Discord bot using discord.py
"""
# standard imports
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# bot core imports
from core import colors
from core.config import Config
from core.logger import console_log
from core.prefix import prefix
from cogs.admin import Database

# load and read token from .env
load_dotenv()
token = os.getenv('TOKEN')

# required dirs
folders = ["config", "data", "playlists"]
for folder in folders:
    if not os.path.exists(f"./{folder}/"):
        os.mkdir(dir)

#bot subclass
class YaeMiko(commands.Bot):
    """
    The main class used to run the bot

    Attributes
    ----------
    prefix
    """

    def __init__(self):
        self.prefix = prefix
        self.config = {}
        super().__init__(
            command_prefix=prefix,
            help_command=None,
            intents=discord.Intents().all()
        )

    async def setup_hook(self):
        """Performs setup tasks on before the bot starts"""
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                # cut off the .py from the file name
                await self.load_extension(f"cogs.{filename[:-3]}")

        await self.tree.sync(guild=discord.Object(id=907119292410130433))

    async def on_ready(self):
        """Called when the bot has finished loading"""
        console_log(f"Connected to discord as {client.user}.")
        # set activity status
        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "Ei's domain. (y!)"
            )
        )

        # init per guild config
        for guild in client.guilds:
            config_path = f'./config/{guild.id}.ini'
            self.config[guild.id] = Config(config_path)

    async def close(self):
        await super().close()
        await self.session.close()

# define client
client = YaeMiko()

# command to set prefix per guild
@client.command()
async def setprefix(ctx, *, arg):
    """Sets the bot prefix per guild"""
    model = Database(ctx.guild.id)

    if model.get_access(ctx.author.id) < 3:
        await ctx.send(
            embed = discord.Embed(
                description = "You must have at least access level 3 to use this command.",
                colour = colors.red
            )
        )
        return

    config = client.config[ctx.guild.id]

    config.set('main', 'prefix', arg)

    await ctx.send(
        embed = discord.Embed(
            description = f"Server prefix has been set to **[{arg}]**.",
            colour = colors.pink
        )
    )

# run bot
if __name__ == "__main__":
    client.run(token)
