from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class BankTransaction(object):
    transaction_id: int
    sender_id: int
    receiver_id: int
    bank_id: int
    amount: int
    process_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str. Any]:
        return {
            'transactionId': self.transaction_id,
            'senderId': self.sender_id,
            'receiverId': self.receiver_id,
            'bankId': self.bank_id,
            'amount': self.amount,
            'process_date': self.process_date
        }
