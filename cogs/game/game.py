from .models.player import PlayerModel

class Game:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.players = PlayerModel()