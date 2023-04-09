from .models.player import PlayerModel
from .models.action import ActionModel

class Game:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.players = PlayerModel()
        self.actions = ActionModel()