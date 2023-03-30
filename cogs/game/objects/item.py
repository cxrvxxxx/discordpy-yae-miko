from abc import ABCMeta
from dataclasses import dataclass

@dataclass
class Item(ABCMeta):
    _id: int
    _item_name: str
    _description: str
    _owner_id: int
    _level: int
    _experience: int
    _item_type: int

    @property
    def item_id(self) -> int:
        return self._id
    
    @property
    def item_name(self) -> str:
        return self._item_name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def owner_id(self) -> int:
        return self._owner_id
    
    @owner_id.setter
    def owner_did(self, id: int) -> None:
        self._owner_id = id

    @property
    def level(self) -> int:
        return self._level
    
    @level.setter
    def level(self, level: int) -> None:
        self._level = level

    @property
    def experience(self) -> int:
        return self._experience
    
    @experience.setter
    def experience(self, value: int) -> None:
        self._experience = value
