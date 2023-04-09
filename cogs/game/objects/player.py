from __future__ import annotations
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Player(object):
    player_id: int
    level: int = 1
    experience: int = 0
    cash: int = 0
    bank_id: int = None
    join_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def exp_cap(self) -> int:
        return self.level ** 2 + self.level * 2 + 2
    
    @staticmethod
    def ensure_level(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            player: Player = args[1]

            while player.experience >= player.exp_cap:
                cap = player.exp_cap
                player.experience -= cap
                player.level += 1

            return result
        return wrapper

    def to_dict(self) -> Dict[str, any]:
        return {
            'playerId': self.player_id,
            'level': self.level,
            'experience': self.experience,
            'cash': self.cash,
            'bankId': self.bank_id,
            'joinDate': self.join_date
        }
    
    def __str__(self) -> str:
        return f'ID: {self.player_id}, Level: {self.level}/{self.exp_cap}, EXP: {self.experience}, Cash: ${self.cash}, Bank ID: {self.bank_id}, Registered: {self.join_date}'
