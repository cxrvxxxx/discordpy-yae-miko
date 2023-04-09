from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class Bank(object):
    bank_id: int
    balance: int

    def to_dict(self) -> Dict[str, int]:
        return {
            'bankId': self.bank_id,
            'balance': self.balance
        }
