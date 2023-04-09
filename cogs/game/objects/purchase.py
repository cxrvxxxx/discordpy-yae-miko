from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class Purchase(object):
    purchase_id: int
    perk_id: int
    quantity: int
    buyerId: int
    purchase_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'purchaseId': self.purchase_id,
            'perkId': self.perk_id,
            'quantity': self.quantity,
            'buyerId': self.buyerId,
            'purchaseDate': self.purchase_date
        }
