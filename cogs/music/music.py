import logging

from discord.ext import commands
from .player import Player

logger = logging.getLogger("musicplayer")

class Music:
    def __init__(self) -> None:
        self.__players  = {}

    def create_player(self, ctx: commands.Context) -> Player:
        """Create player instance"""
        if ctx.guild.id in self.__players:
            return self.__players.get(ctx.guild.id)

        player = Player(ctx)
        self.__players[ctx.guild.id] = player
        logger.info(f"Created Player instance (Guild ID: {player.channel.guild.id})")
        return player

    def get_player(self, player_id: int) -> Player:
        """Fetch player instance from ID"""
        return self.__players.get(player_id) if player_id in self.__players else None

    def close_player(self, player_id: int) -> None:
        """Delete player instance"""
        player = self.get_player(player_id)

        if player:
            logger.info(f"Destroyed Player instance (Guild ID: {player.channel.guild.id})")
            player.loop.create_task(player.stop())
            self.__players.pop(player_id)
