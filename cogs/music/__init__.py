from .music import Voice

async def setup(client) -> None:
    """Adds the cog to the client"""
    await client.add_cog(Voice(client))
