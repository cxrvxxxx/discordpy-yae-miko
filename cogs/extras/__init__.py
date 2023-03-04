from .extras import Extras

async def setup(client):
    await client.add_cog(Extras(client))
