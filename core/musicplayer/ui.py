import logging

import discord
from discord.ui import Button, View

from core import colors
from . import song

logger = logging.getLogger("musicplayer")

class PlayButton(Button):
    def __init__(self, player) -> None:
        super().__init__(label="Play", style=discord.ButtonStyle.primary)
        self.player = player

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.player.resume()
        await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Resumed 🎶 **{song.title}**."
                    ),
                    delete_after=10
                )


class PauseButton(Button):
    def __init__(self, player):
        super().__init__(label="Pause", style=discord.ButtonStyle.success)
        self.player = player

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.player.pause()
        await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Paused 🎶 **{song.title}**."
                    ),
                    delete_after=10
                )


class PrevButton(Button):
    def __init__(self, player):
        disabled = True if not player.last_song else False
        super().__init__(label="Prev", style=discord.ButtonStyle.primary, disabled=disabled)
        self.player = player

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.player.prev()
        await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{song.title}**."
                    ),
                    delete_after=10
                )

class NextButton(Button):
    def __init__(self, player):
        disabled = True if len(player.queue) < 2 else False
        super().__init__(label="Next", style=discord.ButtonStyle.primary, disabled=disabled)
        self.player = player

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.player.skip()
        await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{song.title}**."
                    ),
                    delete_after=10
                )

class StopButton(Button):
    def __init__(self, player):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)
        self.player = player

    async def callback(self, interaction: discord.Interaction) -> None:
        song = await self.player.stop()
        await interaction.response.send_message(
                    embed=discord.Embed(
                        colour=colors.pink,
                        description=f"Stopped 🎶 **{song.title}**."
                    ),
                    delete_after=10
                )

def player_controls(player, paused: bool=False):
        view = View(timeout=None)
        play_button = PlayButton(player) if paused else PauseButton(player)
        BUTTONS = (PrevButton(player), play_button, StopButton(player), NextButton(player))

        for button in BUTTONS:
            view.add_item(button)

        return view

class PlayerUI:
    def __init__(self):
        self.hook: discord.Message = None

    async def render_screen(self, player, channel: discord.TextChannel, song: song.Song):
        view = None

        if player.now_playing:
            embed = discord.Embed(
                colour=colors.pink,
                description=f"Now playing in **{channel.name}**"
            )
            embed.set_thumbnail(
                url=song.thumbnail
            )
            embed.set_author(
                    name=f"{song.title}",
                    icon_url="https://i.imgur.com/rcXLQLG.png"
                )
            embed.set_footer(
                text=f"If you like this song, use '/fave' to add this to your favorites!"
            )

            view = player_controls(player)

        if not self.hook:
            self.hook = await channel.send(embed=embed, view=view)
            logger.debug(f"Created screen for player (ID: {self.hook.guild.id})")
            return
        
        self.hook = await self.hook.edit(embed=embed, view=view)
        logger.debug(f"Updated screen for player (ID: {self.hook.guild.id})")

    async def delete_screen(self):
        if not self.hook:
            return
        
        logger.debug(f"Deleted screen for player (ID: {self.hook.guild.id})")
        await self.hook.delete()
        self.hook = None

    async def refresh_controls(self, player, paused=False):
        if not self.hook:
            return
        
        self.hook = await self.hook.edit(
            view=player_controls(player, paused=paused)
        )
        logger.debug(f"Updated controls for player (ID: {self.hook.guild.id})")

    async def remove_controls(self):
        if not self.hook:
            return

        self.hook = await self.hook.edit(
            view=None
        )
        logger.debug(f"Removed controls for player (ID: {self.hook.guild.id})")
