from __future__ import annotations
from typing import Dict
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Player(object):
    player_id: int
    level: int = 1
    experience: int = 0
    cash: int = 0
    bankId: int = None
    join_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, any]:
        return {
            'playerId': self.player_id,
            'level': self.level,
            'experience': self.experience,
            'cash': self.cash,
            'bankId': self.bankId,
            'joinDate': self.join_date
        }
