import os
import discord
from discord.ext import commands
from .config import Config
from . import logsettings

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
    def __init__(self, **kwargs) -> None:
        super().__init__(
            command_prefix=self.prefix,
            help_command=None,
            intents=discord.Intents().all()
        )
        self.test_guild = discord.Object(id=kwargs.get('TEST_GUILD_ID'))
        self.config = {}
        self.logger = logsettings.logging.getLogger("bot")
        self.MODULES = kwargs.get('modules')

    def prefix(self, client: commands.Bot, message: discord.Message) -> str:
        """Retrieve custom prefix from config or return default prefix"""
        config = client.config[message.guild.id]

        pref = config.get('main', 'prefix')

        return pref if pref else "y!"


    async def setup_hook(self) -> None:
        """Performs setup tasks on before the bot starts"""
        # Setting up directories
        folders = (
            "config", "data", "playlists", "logs"
        )
        for folder in folders:
            if not os.path.exists(f"./{folder}/"):
                os.mkdir(dir)

        if self.MODULES:
            for module in self.MODULES:
                await self.load_extension(module)

        # FIXME: Syncing application commands must be moved to command
        # synced = await self.tree.sync(guild=discord.Object(id="907119292410130433"))
        # logger.info(f"Synced {len(synced)} command(s).")

    async def on_ready(self) -> None:
        """Called when the bot has finished loading"""
        self.logger.info(f"Connected to discord as {self.user}")
        # Setting bot activity status
        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "Ei's domain. (y!)"
            )
        )

        # Config initialization
        for guild in self.guilds:
            config_path = f'./config/{guild.id}.ini'
            self.config[guild.id] = Config(config_path)
            self.config[guild.id].set('main', 'name', guild.name)
    
    async def on_guild_join(self, guild: discord.Guild) ->None:
        """Application commands sync for newly joined guilds"""
        self.tree.copy_global_to(guild=guild)
        try:
            self.logger.debug(f'Syncing commands for newly joined guild: {guild.id}')
            synced = await self.tree.sync(guild=guild)
        except discord.HTTPException:
            self.logger.debug("An error occurred while syncing application commands")
        finally:
            self.logger.debug(f"Sync finished ({len(synced)} commands)")

    async def close(self) -> None:
        """Bot shutdown"""
        await super().close()
        await self.session.close()