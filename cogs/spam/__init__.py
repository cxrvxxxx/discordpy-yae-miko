from .spam import AntiSpam

async def setup(client):
    await client.add_cog(AntiSpam(client))
