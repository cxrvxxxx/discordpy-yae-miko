import sqlite3 as sql

from typing import List, Any
from abc import ABCMeta

from ..settings import SAVEFILE_PATH

class PlayerModel(ABCMeta):
    @staticmethod
    def get_player(uid: int) -> List[Any]:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM players WHERE id=?", (uid,))
        data = c.fetchone()

        conn.close()

        return data

    @staticmethod
    def create_player(player_data) -> None:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO players VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (*player_data,)
        )

        conn.commit()
        conn.close()
    
    @staticmethod
    def update_player(**player_data) -> None:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("""
            UPDATE users
            SET
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
                id=:id""",
            {**player_data}
        )
        
        conn.commit()
        conn.close()
