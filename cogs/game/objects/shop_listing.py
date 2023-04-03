from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass
class ShopListing(object):
    shop_listing_id: int
    perk_id: int
    shop_id: int
    stock: int
    price: int
    added_date: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'shopListingId': self.shop_listing_id,
            'perkId': self.perk_id,
            'shopId': self.shop_id,
            'stock': self.stock,
            'price': self.price,
            'addedDate': self.added_date
        }
