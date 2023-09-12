import os
import discord
import json
import logging

from discord.ext import commands
from logging.config import dictConfig

class YaeMiko(commands.Bot):
    def __init__(self, **kwargs) -> None:
        self.version = kwargs.get("version")

        with open("settings.json", 'r') as f:
            self.settings = json.load(f)

        with open("logging_config.json", 'r') as f:
            self.logging_config = json.load(f)

        self.configure_logger()

        if self.settings.get("test_guild_id"):
            self.test_guild = discord.Object(id=self.settings.get("test_guild_id"))
        else:
            self.test_guild = None

        self.logger = logging.getLogger("yaemiko")
        self.modules = kwargs.get('modules')

        super().__init__(
            command_prefix=self.prefix,
            help_command=None,
            intents=discord.Intents().all()
        )

    def configure_logger(self) -> None:
        dictConfig(self.logging_config)

    def prefix(self, client: commands.Bot, message: discord.Message) -> str:
        return self.settings.get("prefix")

    async def setup_hook(self) -> None:
        folders = (
            "config", "data", "playlists", "logs"
        )

        for folder in folders:
            if not os.path.exists(f"./{folder}/"):
                os.mkdir(f"./{folder}/")

        for module in self.modules:
            await self.load_extension(module)
            self.logger.debug(f"{module} ready.")

    async def on_ready(self) -> None:
        self.logger.debug(f"Connected to discord as {self.user}")

        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "Ei's domain. (y!)"
            )
        )

    async def close(self) -> None:
        await super().close()