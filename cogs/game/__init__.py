from discord.ext.commands import Bot
from .commands.monaheistaccount import MonaHeistAccount

async def setip(client: Bot):
    await client.add_cog(MonaHeistAccount(client))
