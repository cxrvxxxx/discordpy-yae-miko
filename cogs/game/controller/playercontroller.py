from ..models.playermodel import PlayerModel
from ..objects.player import Player
from ..objects.response import Response

class PlayerController(object):
    @staticmethod
    def register(uid: int, name: str) -> None:
        player_data = PlayerModel.get_player(uid)

        if player_data:
            return Response(False, message="Already registered.")
        
        player = Player(
            uid, name
        )
        
        PlayerModel.save_player(player)

        return Response(True, data={'player': player})
    
    @staticmethod
    def profile(uid: int) -> None:
        player_data = PlayerModel.get_player(uid)

        if not player_data:
            return Response(False, message="No data.")
        
        player = Player(*player_data)

        return Response(True, data={'player': player})
