import discord
import random

from discord.ext import commands

class Extras(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def coinflip(self, ctx):
        chance = 50
        await ctx.send(f"You flipped a coin that landed on **{'heads' if random.randint(1, 100) > chance else 'tails'}**.")

async def setup(client):
    await client.add_cog(Extras(client))