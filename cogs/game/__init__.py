from discord.ext.commands import Bot
from .commands.mh_account import MonaHeistAccount

async def setup(client: Bot):
    await client.add_cog(MonaHeistAccount(client))
