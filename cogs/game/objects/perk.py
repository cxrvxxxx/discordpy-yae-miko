from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class Perk(object):
    perk_id: int
    name: str = None
    description: str = None
    exp_multiplier: float = 1.0
    cash_multiplier: float = 1.0
    dev_id: int = None
    create_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'perkId': self.perk_id,
            'name': self.name,
            'description': self.description,
            'expMultiplier': self.exp_multiplier,
            'cashMultiplier': self.cash_multiplier,
            'devId': self.dev_id,
            'createDate': self.create_date
        }
