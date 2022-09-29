import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from core import colors
from core.config import Config
from core.logger import console_log

# load and read token from .env
load_dotenv()
token = os.getenv('TOKEN')

# set intents
intents = discord.Intents().all()
intents.typing = False
intents.presences = False
intents.message_content = True

# fetch guild prefix
def prefix(client, message):
    config = client.config[message.guild.id]

    pf = config.get(__name__, 'prefix')
    if pf:
        return pf
    else:
        return "y!"

#bot subclass
class YaeMiko(commands.Bot):
    def __init__(self):
        self.prefix = prefix
        self.config = {}
        super().__init__(
            command_prefix=prefix,
            help_command=None,
            intents=intents
        )

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                # cut off the .py from the file name
                await self.load_extension(f"cogs.{filename[:-3]}")
        
        await self.tree.sync(guild=discord.Object(id=907119292410130433))

    async def on_ready(self):
        # init per guild config
        for guild in client.guilds:
            config_path = f'./config/{guild.id}.ini'
            self.config[guild.id] = Config(config_path)

        console_log(f"Connected to discord as {client.user}.")
        # set activity status
        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.watching,
                name = "Ei's domain. (y!)"
            )
        )

    async def close(self):
        await super().close()
        await self.session.close()

# define client
client = YaeMiko()

# command to set prefix per guild
@client.command()
async def setprefix(ctx, *, arg):
    from cogs.admin import Database as db

    db = db(ctx.guild.id)
    
    if db.get_access(ctx.author.id) < 3:
        await ctx.send(
            embed = discord.Embed(
                description = "You must have at least access level 3 to use this command.",
                colour = colors.red
            )
        )
        return

    config = client.config[ctx.guild.id]

    config.set(__name__, 'prefix', arg)

    await ctx.send(
        embed = discord.Embed(
            description = f"Server prefix has been set to **[{arg}]**.",
            colour = colors.pink
        )
    )

# run bot
if __name__ == "__main__":
    client.run(token)