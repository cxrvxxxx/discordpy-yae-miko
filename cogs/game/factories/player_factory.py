from abc import ABCMeta

from typing import List, Any, Union, Dict
from ..objects.player import Player

class PlayerFactory(ABCMeta):
    @staticmethod
    def create_player(player_id: int, player_name: str, **kwargs) -> Player:
        return Player(
            player_id,
            player_name,
            kwargs.get('bio', None),
            kwargs.get('level', 1),
            kwargs.get('experience', 0),
            kwargs.get('cash', 0),
            kwargs.get('hitpoints', 100),
            kwargs.get('energy', 100),
            kwargs.get('group_id', None),
            kwargs.get('is_developer', False),
            kwargs.get('is_moderator', False),
            kwargs.get('dev_level', 0),
            kwargs.get('mod_level', 0)
        )

    @staticmethod
    def to_list(player: Player) -> Union[List[Any], None]:
        if not isinstance(player, Player):
            return
        
        return [
            player.player_id,
            player.name,
            player.bio,
            player.level,
            player.experience,
            player.cash,
            player.hitpoints,
            player.energy,
            player.group_id,
            player.is_developer,
            player.is_moderator,
            player.dev_level,
            player.mod_level
        ]

    @staticmethod
    def to_dict(player: Player) -> Union[Dict[str, Any], None]:
        if not isinstance(player, Player):
            return
        
        return {
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
        }
