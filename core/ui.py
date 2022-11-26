from typing import Optional, Any
import asyncio
import discord
from discord.ui import *
from core import colors

class PlayButton(Button):
    def __init__(self, ctx, freeze: bool = False) -> None:
        disabled = True if freeze else False
        super().__init__(label = "Play", style = discord.ButtonStyle.primary, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.invoke(self.ctx.bot.get_command("resume"))
        await interaction.message.edit(view=player_controls(self.ctx))
        await interaction.response.defer()

class PauseButton(Button):
    def __init__(self, ctx, freeze: bool = False):
        disabled = True if freeze else False
        super().__init__(label = "Pause", style = discord.ButtonStyle.success, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.invoke(self.ctx.bot.get_command("pause"), normal=False)
        await interaction.message.edit(view=player_controls(self.ctx, paused = True))
        await interaction.response.defer()


class PrevButton(Button):
    def __init__(self, ctx, freeze: bool = False):
        disabled = True if freeze else False
        super().__init__(label = "Prev", style = discord.ButtonStyle.primary, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.invoke(self.ctx.bot.get_command("prev"), normal=False)
        await interaction.response.defer()

class NextButton(Button):
    def __init__(self, ctx, freeze: bool = False):
        disabled = True if freeze else False
        super().__init__(label = "Next", style = discord.ButtonStyle.primary, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.invoke(self.ctx.bot.get_command("skip"), normal=False)
        await interaction.message.edit(view=None)

class StopButton(Button):
    def __init__(self, ctx, freeze: bool = False):
        disabled = True if freeze else False
        super().__init__(label = "Stop", style = discord.ButtonStyle.danger, disabled=disabled)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.invoke(self.ctx.bot.get_command("leave"))
        await interaction.message.edit(view=None)

def player_controls(ctx, freeze: bool = False, paused: bool = False):
        view = View()
        play_button = PlayButton(ctx, freeze) if paused else PauseButton(ctx, freeze)
        BUTTONS = (PrevButton(ctx, freeze), play_button, StopButton(ctx, freeze), NextButton(ctx, freeze))

        for button in BUTTONS:
            view.add_item(button)

        return view