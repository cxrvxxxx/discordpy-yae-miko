from dataclasses import dataclass
from .item import Item

@dataclass
class Armor(Item):
    _type: int
    _protection: int

    @property
    def type(self) -> int:
        return self._type
    
    @property
    def protection(self) -> int:
        return self._protection
    
    @protection.setter
    def protection(self, value: int) -> None:
        self._protection = value
