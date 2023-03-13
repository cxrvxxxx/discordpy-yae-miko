import sqlite3 as sql

from typing import Union
from abc import ABCMeta

from ..objects.player import Player
from ..settings import SAVEFILE_PATH
from ..factories.player_factory import PlayerFactory
from ..exceptions.player_exceptions import *

class PlayerModel(ABCMeta):
    @staticmethod
    def get_player(uid: int) -> Union[Player, None]:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM players WHERE id=?", (uid,))
        data = c.fetchone()

        if not data:
            raise PlayerNotFoundException(f"Cannot find player with ID {uid}")

        return PlayerFactory.create_player(*data)

    @staticmethod
    def create_player(uid, player_name, **kwargs) -> Player:
        player = PlayerModel.get_player(uid)

        if player:
            raise PlayerCreateException("Player is already exists.")

        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                uid,
                player_name,
                kwargs.get('bio'),
                kwargs.get('level', 1),
                kwargs.get('experience', 0),
                kwargs.get('cash', 0),
                kwargs.get('hitpoints', 100),
                kwargs.get('energy', 160),
                kwargs.get('group_id'),
                kwargs.get('is_developer', 0),
                kwargs.get('is_moderator', 0),
                kwargs.get('dev_level', 0),
                kwargs.get('mod_level', 0),
            )
        )

        conn.commit()
        conn.close()

        player = PlayerModel.get_player(uid)

        return player
    
    @staticmethod
    def update_player(player: Player) -> Player:
        existing_player = PlayerModel.get_player(player.player_id)

        if not existing_player:
            raise PlayerNotFoundException("Cannot update a non-existing player.")
        
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
            {
                'id': player.player_id,
                'player_name': player.name,
                'bio': player.bio,
                'level': player.level,
                'experience': player.experience,
                'cash': player.cash,
                'hitpoints': player.hitpoints,
                'energy': player.energy,
                'group_id': player.group_id,
                'is_developer': player.is_developer,
                'is_moderator': player.is_moderator,
                'dev_level': player.dev_level,
                'mod_level': player.mod_level
            })
        
        conn.commit()
        conn.close()

        existing_player = PlayerModel.get_player(player.player_id)
        return existing_player
