from abc import ABCMeta

from ..objects.response import Response

from ..factories.player_factory import PlayerFactory
from ..factories.response_factory import ResponseFactory

from ..models.player import PlayerModel

class PlayerHandler(ABCMeta):
    @staticmethod
    def on_register(discord_id: int, player_name: str) -> Response:
        player_data = PlayerModel.get_player(discord_id)

        if player_data:
            return ResponseFactory.generate_response(False, None)
        
        player = PlayerFactory.create_player(discord_id, player_name)
        PlayerModel.create_player(PlayerFactory.to_list(player))

        return ResponseFactory.generate_response(True, player)
