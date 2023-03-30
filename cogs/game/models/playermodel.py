from typing import List, Any
from .database import Database

from ..objects.player import Player

class PlayerModel(object):
    @staticmethod
    def get_player(uid: int) -> List[Any]:
        with Database("AppData.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM tblPlayer WHERE id=?", (uid,))
            player_data = c.fetchone()
        
        return player_data
    
    @classmethod
    def save_player(cls, player: Player) -> None:
        with Database("AppData.db") as conn:
            c = conn.cursor()
            if not cls.get_player(player.player_id):
                c.execute("""
                INSERT INTO tblPlayer
                VALUES (
                    :id,
                    :player_name,
                    :bio,
                    :level,
                    :experience,
                    :cash,
                    :hitpoints,
                    :energy,
                    :group_id,
                    :is_developer,
                    :is_moderator,
                    :dev_level,
                    :mod_level
                )""", player.to_dict())
            else:
                c.execute("""
                UPDATE tblPlayer
                SET
                    id=:id,
                    player_name=:player_name,
                    bio=:bio,
                    level=:level,
                    experience=:experience,
                    cash=:cash,
                    hitpoints=:hitpoints,
                    energy=:energy,
                    group_id=:group_id,
                    is_developer=:is_developer,
                    is_moderator=:is_moderator,
                    dev_level=:dev_level,
                    mod_level=:mod_level
                WHERE
                    id=:id
                """, player.to_dict())
