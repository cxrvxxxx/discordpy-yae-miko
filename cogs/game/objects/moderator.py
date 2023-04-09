from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class Moderator(object):
    mod_id: int
    player_id: int
    level: int
    date_joined: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'devId': self.mod_id,
            'playerId': self.player_id,
            'level': self.level,
            'dateJoined': self.date_joined
        }
