from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class PlayerPerk(object):
    player_perk_id: int
    player_id: int
    perk_id:int
    quantity: int

    def to_dict(self) -> Dict[str, int]:
        return {
            'playerPerkId': self.player_perk_id,
            'playerId': self.player_id,
            'perkId': self.perk_id,
            'quantity': self.quantity
        }
