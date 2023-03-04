from .admin import Admin

async def setup(client):
    await client.add_cog(Admin(client))
