from dataclasses import dataclass

@dataclass
class Shop(object):
    _id: int
    _shop_name: str
    _description: str
    _owner_id: int

    @property
    def shop_id(self) -> int:
        return self._id
    
    @property
    def shop_name(self) -> str:
        return self._shop_name
    
    @shop_name.setter
    def shop_name(self, name: str) -> None:
        self._shop_name = name

    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, text: str) -> None:
        self._description = text
    
    @property
    def owner_id(self) -> int:
        return self._owner_id
    
    @owner_id.setter
    def owner_id(self, id: int) -> None:
        self._owner_id = id
