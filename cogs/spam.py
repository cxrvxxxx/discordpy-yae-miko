import discord
import asyncio

from datetime import datetime
from discord.ext import commands

from core.logger import console_log
from core import colors

settings = {
    "message_pool": "5",
    "trigger_time_delta": "1500"
}

messages = {}

async def send_basic_response(channel, message, color):
    await channel.send(embed = discord.Embed(description = message, colour = color))

class AntiSpam(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.Cog.listener()
    async def on_ready(self):
        # init config data
        for guild in self.client.guilds:
            for key, value in settings.items():
                if not self.config[guild.id].get(__name__, key):
                    self.config[guild.id].set(__name__, key, value)

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        author = message.author

        config = self.config[guild.id]

        # init params
        trigger_time_delta = config.getint(__name__, 'trigger_time_delta')
        message_pool = config.getint(__name__, 'message_pool')
        current_time = datetime.now().timestamp() * 1000

        # ignore if bot
        if self.client.user == message.author:
            return

        # init message pool
        if not messages.get(author.id, None):
            messages[author.id] = []

        # add new message to pool
        messages[author.id].append(Message(message, current_time))

        # kick condition
        if len(messages[author.id]) > message_pool:
            console_log(f"ANTISPAM: Kick condition met for {author.nick if author.nick else author.name} in {guild.name}.")
            try:
                if message.guild.get_member(message.author.id):
                    # soft ban user, deleting messages in the process
                    await message.guild.ban(message.author, reason="Spamming")
                    await asyncio.sleep(1)
                    await message.guild.unban(message.author)
                    await send_basic_response(message.channel, f"Kicked **{message.author.nick if message.author.nick else message.author.name}** for spamming.", colors.pink)
            except:
                console_log(f"ANTISPAM: Could not kick user {author.id}.")
                console_log(f"ANTISPAM: Could not delete spam messages by {author.id}.")
                await send_basic_response(message.channel, f"Detected spam by **{message.author.nick if message.author.nick else message.author.name}** but could not kick user.", colors.red)
            finally:
                messages[author.id] = []

        # removed expired messages from pool
        for msg in messages[author.id]:
            time_delta = current_time - msg.time

            if time_delta > trigger_time_delta:
                messages[author.id].remove(msg)

class Message:
    def __init__(self, message, time):
        self.message = message
        self.time = time

async def setup(client):
    await client.add_cog(AntiSpam(client))