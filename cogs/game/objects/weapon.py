from dataclasses import dataclass
from .item import Item

@dataclass
class Weapon(Item):
    _type: int
    _damage: int
    _energy_cost: int

    @property
    def type(self) -> int:
        return self._type
    
    @property
    def damage(self) -> int:
        return self._damage
    
    @damage.setter
    def damage(self, value: int) -> int:
        self._damage = value

    @property
    def energy_cost(self) -> int:
        return self._energy_cost
    
    @energy_cost.setter
    def energy_cost(self, value: int) -> None:
        self._energy_cost = value
