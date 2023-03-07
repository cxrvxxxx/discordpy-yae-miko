from .commands import MusicCommands

async def setup(client) -> None:
    """Adds the cog to the client"""
    await client.add_cog(MusicCommands(client))
