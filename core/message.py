"""
A module for handling pre-formatted messages
"""
from typing import Optional, Union
import discord
from discord.ext import commands
from core import colors

async def send_basic_response(
    ctx: commands.Context,
    message: discord.Message,
    color: discord.Color,
    delete_after: Optional[Union[int, None]] = None
) -> discord.Message:
    """
    Send an embed-only message
    """
    return await ctx.send(
        embed = discord.Embed(
            description = message,
            colour = color
        ),
        delete_after = delete_after
    )

async def send_error_message(
    ctx: commands.Context,
    message: discord.Message
) -> discord.Message:
    """Error message, self-destructs after 10 seconds"""
    return await ctx.send(
        embed=discord.Embed(
            description=message,
            colour=colors.red
        ),
        delete_after=10
    )

async def send_notif(
    ctx: commands.Context,
    message: discord.Message
) -> discord.Message:
    """Notification message, self-destructs after 10 seconds"""
    return await ctx.send(
        embed=discord.Embed(
            description=message,
            colour=colors.pink
        ),
        delete_after=10
    )

class Responses:
    # TODO: dynamically assign these from file
    bot_disconnect: str = "Disconnecting from voice since no one else is in the channel."
    bot_is_connected: str = "Already connected to voice channel **[{channel_name}]**."
    bot_not_connected: str = "Not connected to a **voice channel**."
    bot_on_connect: str = "Connected to **[{vc_name}]** and bound to **[{channel_name}]**."
    music_empty_queue:str =  "The queue is **empty**."
    music_no_pause: str = "Cannot pause because nothing is playing."
    music_no_player: str = "There is no **active player**."
    music_no_previous: str = "Cannot play previous song."
    music_no_resume: str = "Cannot resume because nothing is playing."
    music_no_skip: str = "Cannot skip because the queue is empty."
    music_player_fav_add: str = "Added **{title}** to your favorites."
    msuic_player_fav_invalid: str = "Invalid song ID."
    music_player_fav_rm: str = "**{title}** has been removed from your favorites."
    music_player_no_fav: str = "It seems that you haven't added any song to your favorites yet."
    music_player_no_song: str = "There is no **song** currently playing."
    music_player_volume: str = "Player volume: **{volume}%**."
    music_player_volume_invalid: str = "The volume must be between **0** to **100**."
    music_wrong_channel: str = "The player can only be controlled from **[{channel_name}]**."
    user_no_voice: str = "You are not connected to a **voice channel**."