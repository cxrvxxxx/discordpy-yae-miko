import logging

import discord
from discord.ui import View

from core import colors

from .song import Song
from .ui import components

def player_controls(player) -> View:
        view = View(timeout=None)

        prev_button = components.PrevButton(player.prev, False if player.last_song else True)
        if player.is_playing:
            play_button = components.PauseButton(player.pause)
        else:
            play_button = components.PlayButton(player.resume)
        stop_button = components.StopButton(player.stop)
        next_button = components.NextButton(player.skip, False if player.queue.size() != 0 else True)

        view.add_item(prev_button)
        view.add_item(play_button)
        view.add_item(stop_button)
        view.add_item(next_button)

        return view

class PlayerUI:
    def __init__(self, channel: discord.TextChannel):
        self.__channel: discord.TextChannel = channel
        self.__screen: discord.Message = None
        self.__logger: logging.Logger = logging.getLogger("yaemiko.music.ui")

    @property
    def channel(self) -> discord.TextChannel:
        return self.__channel
    
    @property
    def logger(self) -> logging.Logger:
        return self.__logger
    
    @property
    def screen(self) -> discord.Message:
        return self.__screen
    
    @screen.setter
    def screen(self, msg: discord.Message):
        self.__screen = msg

    async def render_np(self, player):
        song = player.now_playing

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

        view = player_controls(player)

        if not self.screen:
            self.screen = await self.channel.send(embed=embed, view=view)
            self.logger.debug(f"Created screen for player (ID: {self.screen.guild.id})")
            return

        self.screen = await self.screen.edit(embed=embed, view=view)
        self.logger.debug(f"Updated screen for player (ID: {self.screen.guild.id})")

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
        
        self.logger.debug(f"Deleted screen for player (ID: {self.screen.guild.id})")
        await self.screen.delete()
        self.screen = None

    async def remove_controls(self):
        if not self.screen:
            return

        self.screen = await self.screen.edit(
            view=None
        )
        self.logger.debug(f"Removed controls for player (ID: {self.screen.guild.id})")
