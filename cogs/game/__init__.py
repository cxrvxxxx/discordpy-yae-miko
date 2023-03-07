from .commands import MonaHeist

async def setup(client):
    await client.add_cog(MonaHeist(client))
