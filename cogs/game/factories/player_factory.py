from abc import ABCMeta

from ..objects.player import Player

class PlayerFactory(ABCMeta):
    @staticmethod
    def create_player(*data) -> Player:
        return Player(*data)
