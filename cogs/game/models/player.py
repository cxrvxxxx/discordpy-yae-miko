from typing import Union
import os
import json
import mysql.connector as mysql
from datetime import datetime
from ..objects.player import Player

class PlayerModel(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'mysql_config.json'), 'r') as f:
            self.MYSQL_CONFIG = json.load(f)

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