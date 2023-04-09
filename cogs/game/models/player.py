from typing import Union
import mysql.connector as mysql
from ..objects.player import Player
from .abc_model import AbstractModel

class PlayerModel(AbstractModel):
    def get_player(self, player_id: int) -> Union[Player, None]:
        with mysql.connect(**self.MYSQL_CONFIG) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM tblPlayer WHERE playerId=%s", (player_id,))
            player_data = c.fetchone()

        if not player_data:
            return

        return Player(*player_data)
    
    def create_player(self, player_id: int) -> Player:
        return Player(player_id)
    
    def save(self, player: Player) -> bool:
        if not isinstance(player, Player):
            return False
        
        with mysql.connect(**self.MYSQL_CONFIG) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO tblPlayer VALUES (
                %(playerId)s,
                %(level)s,
                %(experience)s,
                %(cash)s,
                %(bankId)s,
                %(joinDate)s
            )""", player.to_dict())
            conn.commit()

        return True