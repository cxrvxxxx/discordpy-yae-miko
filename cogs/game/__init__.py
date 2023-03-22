from .main import MonaHeist

async def setup(client) -> None:
    await client.add_cog(MonaHeist(client))
