"""
Project name: Yae Miko - Discord Bot [discord.py]
Author: cxrvxxx
Repository URL: https://github.com/cxrvxxx/yae-miko
Description: A feature-packed Discord bot using discord.py
"""
# Standard imports
import os
from typing import Dict

# Third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Core imports
from core.config import Config
from core.prefix import prefix
import logsettings

# Version information
PROJECT_NAME:   str = "Yae Miko - Discord Bot [discord.py]"
VERSION:        str = "1.1.1"
AUTHOR:         str = "cxrvxxxx"
REPO_URL:       str = "https://github.com/cxrvxxxx/yae-miko"

# Logger
logger = logsettings.logging.getLogger("bot")

# Subclassing commands.Bot
class YaeMiko(commands.Bot):
    """
    The main class used to run the bot

    Attributes
    ----------
    prefix
        character required to use commands

    Methods
    ----------
    setup_hook()
        Performs setup tasks on before the bot starts
    on_ready()
        Called when the bot has finished loading
    close()
        Bot shutdown
    """
    prefix: str
    config: Dict[int, Config]

    def __init__(self) -> None:
        self.prefix = prefix
        self.config = {}
        super().__init__(
            command_prefix=prefix,
            help_command=None,
            intents=discord.Intents().all()
        )

    async def setup_hook(self) -> None:
        """Performs setup tasks on before the bot starts"""
        # Setting up directories
        folders = (
            "config", "data", "playlists", "logs"
        )
        for folder in folders:
            if not os.path.exists(f"./{folder}/"):
                os.mkdir(dir)

        # Loading cogs.
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                # cut off the .py from the file name
                await self.load_extension(f"cogs.{filename[:-3]}")

        # Syncing application commands
        synced = await self.tree.sync(guild=discord.Object(id=907119292410130433))
        logger.info(f"Synced {len(synced)} command(s).")

    async def on_ready(self) -> None:
        """Called when the bot has finished loading"""
        logger.info(f"Connected to discord as {client.user}")
        # Setting bot activity status
        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "Ei's domain. (y!)"
            )
        )

        # Config initialization
        for guild in client.guilds:
            config_path = f'./config/{guild.id}.ini'
            self.config[guild.id] = Config(config_path)
            self.config[guild.id].set('main', 'name', guild.name)

    async def close(self) -> None:
        """Bot shutdown"""
        await super().close()
        await self.session.close()

# Running the bot.
if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    client = YaeMiko()
    client.run(TOKEN, root_logger=True)
