import discord
from discord.ui import *

import logging

# Logger
logger = logging.getLogger("musicplayer")

class PlayButton(Button):
    def __init__(self, player, disabled: bool=False) -> None:
        super().__init__(label="Play", style=discord.ButtonStyle.primary, disabled=disabled)
        self.player = player
        logger.debug(f"Created PlayButton object (ID: {self.player.channel.guild.id})")

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.player.resume(interaction=interaction)

class PauseButton(Button):
    def __init__(self, player, disabled: bool=False):
        super().__init__(label="Pause", style=discord.ButtonStyle.success, disabled=disabled)
        self.player = player
        logger.debug(f"Created PauseButton object (ID: {self.player.channel.guild.id})")

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.player.pause(interaction=interaction)

class PrevButton(Button):
    def __init__(self, player, disabled: bool=False):
        disabled = True if not player.last_song else disabled
        super().__init__(label="Prev", style=discord.ButtonStyle.primary, disabled=disabled)
        self.player = player
        logger.debug(f"Created{' DISABLED ' if disabled else ' '}PrevButton object (ID: {self.player.channel.guild.id})")

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.player.prev(interaction=interaction)

class NextButton(Button):
    def __init__(self, player, disabled: bool = False):
        disabled = True if len(player.queue) < 2 else disabled
        super().__init__(label="Next", style=discord.ButtonStyle.primary, disabled=disabled)
        self.player = player
        logger.debug(f"Created{' DISABLED ' if disabled else ' '}NextButton object (ID: {self.player.channel.guild.id})")

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.player.skip(interaction=interaction)

class StopButton(Button):
    def __init__(self, player, disabled: bool = False):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger, disabled=disabled)
        self.player = player
        logger.debug(f"Created StopButton object (ID: {self.player.channel.guild.id})")

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.player.stop(interaction=interaction)

def player_controls(player, disabled: bool=False, paused: bool=False):
        view = View(timeout=None)
        play_button = PlayButton(player, disabled) if paused else PauseButton(player, disabled)
        BUTTONS = (PrevButton(player, disabled), play_button, StopButton(player, disabled), NextButton(player, disabled))

        for button in BUTTONS:
            view.add_item(button)

        return view
