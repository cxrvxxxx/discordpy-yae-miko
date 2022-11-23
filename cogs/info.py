import discord

from discord.ext import commands
from core import colors

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def info(self, ctx):
        pf = self.client.prefix(self.client, ctx.message)
        await ctx.send(
            embed = discord.Embed(
                title = "Yae Miko | information",
                description = f"""v1.0 by corveaux
                
                ` **Yae Miko** ` provides **essential features** such as:
                   - Server Management
                   - Security
                   - Entertainment (Games, Music)
                   - and many more!
                   
                The prefix for Yae Miko commands is ` **{pf}** `""",
                colour = colors.pink
            )
        )

async def setup(client):
    await client.add_cog(Info(client))