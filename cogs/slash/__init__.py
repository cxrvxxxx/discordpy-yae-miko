from .slash import Slash

async def setup(client):
    await client.add_cog(Slash(client))
