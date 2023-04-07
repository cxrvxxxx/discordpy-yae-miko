import random
import math

from ..objects.player import Player

class ActionModel(object):
    @Player.ensure_level
    def do_work(self, player: Player, custom_level: int=None, cash_multiplier: float=1.0, exp_multiplier: float=1.0) -> bool:
        if not isinstance(player, Player):
            return False
        
        cash = round(random.randint(player.level, player.level * 3) * cash_multiplier)

        base = math.log(custom_level, 1.1) if custom_level else self.level
        upper_limit = round(1 + base * 2 * exp_multiplier)
        lower_limit = 0 if custom_level else self.level
        exp = random.randint(lower_limit, upper_limit)

        player.cash += cash
        player.experience += exp

        return True