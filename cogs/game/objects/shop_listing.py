from dataclasses import dataclass

@dataclass
class ShopListing(object):
    _id: int
    _shop_id: int
    _item_id: int
    _price: int
    _close_time: object #TODO: set to DateTime object

    @property
    def listing_id(self) -> int:
        return self._id
    
    @property
    def shop_id(self) -> int:
        return self._shop_id
    
    @property
    def item_id(self) -> int:
        return self._item_id
    
    @property
    def price(self) -> int:
        return self._price
    
    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @property
    def close_time(self) -> object: #TODO: set tp DateTime object
        return self._close_time
    
    @close_time.setter
    def close_time(self, datetime: object) -> None:
        self._close_time = datetime
    