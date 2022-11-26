"""Prefix Module"""
import discord
from discord.ext import commands

def prefix(client: commands.Bot, message: discord.Message) -> str:
    """Retrieve custom prefix from config or return default prefix"""
    config = client.config[message.guild.id]

    pref = config.get('main', 'prefix')

    return pref if pref else "y!"
