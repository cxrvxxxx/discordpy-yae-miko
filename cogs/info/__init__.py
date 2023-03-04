from .info import Info

async def setup(client):
    await client.add_cog(Info(client))
