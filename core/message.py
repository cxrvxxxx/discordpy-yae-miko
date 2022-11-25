import asyncio
from typing import Union

import discord
from discord.ext import commands
from discord.ui import View

class MessageManager:
    __channel: discord.TextChannel
    __last_message: discord.Message
    __current: discord.Message
    ctx: commands.Context

    def __init__(self, ctx, channel: discord.TextChannel) -> None:
        self.__channel = channel
        self.__last_message = None
        self.__current = None
        self.ctx = ctx

    @property
    def channel(self) -> discord.TextChannel:
        return self.__channel

    async def send_message(self, content: str = None, embed: discord.Embed=None, view: View=None, delete_after: bool = None) -> None:
        self.__current = await self.ctx.send(
            content=content,
            embed=embed,
            view=view,
            delete_after=delete_after
        )

    async def update(self, content: str = None, embed: discord.Embed=None, view: View=None) -> None:
        self.__last_message = self.__current
        self._current = await self.__current.edit(
            content=content,
            embed=embed,
            view=view,
        )

    async def notify(self, content: str = None, embed: discord.Embed=None, view: View=None, delete_after: bool = None) -> None:
        self.__last_message = self.__current
        self.__current = await self._current.edit(
            content=content,
            embed=embed,
            view=view,
        )

        self.__restore_after(delete_after)

    async def __restore_after(self, time: Union[int, float]) -> None:
        asyncio.sleep(time)
        temp = self.__current
        self.__current = await self.__current.edit(
            content=self.__last_message.content,
            embeds=self.__last_message.embeds,
            view=self.__last_message.view,
        )
        self.__last_message = temp
