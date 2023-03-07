import logging

import discord
from discord.ui import Button, View

from core import colors

from .song import Song

logger = logging.getLogger("musicplayer")

class PlayButton(Button):
    def __init__(self, onClick) -> None:
        super().__init__(label="Play", style=discord.ButtonStyle.primary)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.onClick(interaction=interaction)

class PauseButton(Button):
    def __init__(self, onClick):
        super().__init__(label="Pause", style=discord.ButtonStyle.success)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.onClick(interaction=interaction)

class PrevButton(Button):
    def __init__(self, onClick, disabled):
        super().__init__(label="Prev", style=discord.ButtonStyle.primary, disabled=disabled)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.onClick:
            return
        
        await self.onClick(interaction=interaction)

class NextButton(Button):
    def __init__(self, onClick, disabled):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, disabled=disabled)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.onClick(interaction=interaction)

class StopButton(Button):
    def __init__(self, onClick):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)
        self.onClick = onClick

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.onClick(interaction=interaction)

def player_controls(isPlaying, **kwargs) -> View:
        view = View(timeout=None)
        
        view.add_item(PrevButton(kwargs.get('onPrev'), False if kwargs.get('onPrev') else True))
        play_button_state = PauseButton(kwargs.get('onPause')) if isPlaying else PlayButton(kwargs.get('onPlay'))
        view.add_item(play_button_state)
        view.add_item(StopButton(kwargs.get('onStop')))
        view.add_item(NextButton(kwargs.get('onSkip'), False if kwargs.get('onSkip') else True))

        return view

class PlayerUI:
    def __init__(self, channel: discord.TextChannel):
        self.__channel: discord.TextChannel = channel
        self.__screen: discord.Message = None

    @property
    def channel(self) -> discord.TextChannel:
        return self.__channel
    
    @property
    def screen(self) -> discord.Message:
        return self.__screen
    
    @screen.setter
    def screen(self, msg: discord.Message):
        self.__screen = msg

    async def render_np(self, song: Song, isPlaying: bool, **kwargs):
        embed = discord.Embed(
            colour=colors.pink,
            description=f"Now playing in **{self.channel.name}**"
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

        view = player_controls(isPlaying, **kwargs)

        if not self.screen:
            self.screen = await self.channel.send(embed=embed, view=view)
            logger.debug(f"Created screen for player (ID: {self.screen.guild.id})")
            return
  
        self.screen = await self.screen.edit(embed=embed, view=view)
        logger.debug(f"Updated screen for player (ID: {self.screen.guild.id})")

    async def send_skip_msg(self, interaction: discord.Interaction, song: Song):
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Stopped 🎶 **{song.title}**."
            ),
            delete_after=10
        )
        
    async def send_pause_msg(self, interaction: discord.Interaction, song: Song):
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Paused 🎶 **{song.title}**."
            ),
            delete_after=10
        )
        
    async def send_resume_msg(self, interaction: discord.Interaction, song: Song):
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Resumed 🎶 **{song.title}**."
            ),
            delete_after=10
        )

    async def send_stop_msg(self, interaction: discord.Interaction, song: Song):
        await interaction.response.send_message(
            embed=discord.Embed(
                colour=colors.pink,
                description=f"Stopped 🎶 **{song.title}**."
            ),
            delete_after=10
        )

    async def send_queue_msg(self, interaction: discord.Interaction, song: Song):
        embed = discord.Embed(
            colour=colors.pink,
            description="Successfully added to queue."
        )
        embed.set_thumbnail(url=song.thumbnail)
        embed.set_author(
            name=f"{song.title}",
            icon_url="https://i.imgur.com/rcXLQLG.png"
        )

        await interaction.response.send_message(embed=embed, delete_after=10)

    async def delete_screen(self):
        if not self.screen:
            return
        
        logger.debug(f"Deleted screen for player (ID: {self.screen.guild.id})")
        await self.screen.delete()
        self.screen = None

    async def remove_controls(self):
        if not self.screen:
            return

        self.screen = await self.screen.edit(
            view=None
        )
        logger.debug(f"Removed controls for player (ID: {self.screen.guild.id})")
