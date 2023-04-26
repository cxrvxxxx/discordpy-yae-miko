from dataclasses import dataclass, field
from typing import List, Union, Callable

try:
    import discord
except Exception:
    raise Exception("discord.py is not installed")

@dataclass
class EmbedPaginator(object):
    _channel: discord.TextChannel
    _cur: int = field(default=0, init=False)
    _embeds: List = field(default=[], init=False)
    _message: discord.Message = field(default=None, init=False)

    def add_embed(self, embed: discord.Embed) -> None:
        if not isinstance(embed, discord.Embed):
            return
    
        self._embeds.appen(embed)

    def _isEmpty(self) -> bool:
        return True if len(self._embeds) < 1 else False

    def _get_current(self) -> Union[discord.Embed, None]:
        if not len(self._embeds) > 1:
            return
        
        return self._embeds[self._cur]
    
    def _get_view(self) -> discord.ui.View:
        view = discord.ui.View(timeout=None)

        prev_button = NavButton("Prev", self.prev_page, True if self._cur == 0 else False)
        next_button = NavButton("Next", self.next_page, True if self._cur == len(self._embeds) - 1 else False)

        view.add_item(prev_button)
        view.add_item(next_button)
        
        return view
    
    async def next_page(self) -> Union[discord.Embed, None]:
        if not len(self._embeds) > 1 or self._cur == len(self._embeds) - 1 or not self._message:
            return
        
        self._cur += 1
        self._message = await self._message.edit(
            embed=self._get_current(),
            view=self._get_view()
        )
    
    async def prev_page(self) -> Union[discord.Embed, None]:
        if self._cur == 0 or not self._message:
            return
        
        self._cur -= 1
        self._message = await self._message.edit(
            embed=self._get_current(),
            view=self._get_view()
        )
    
    async def send(self) -> discord.Message:
        self._message =  await self._channel.send(
            embed=self._get_current(),
            view=self._get_view()
        )

class NavButton(discord.ui.Button):
    def __init__(self, label: str, on_click: Callable, disabled: bool=False) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.primary, disabled=disabled)
        self.on_click = on_click

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.on_click()
