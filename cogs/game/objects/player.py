from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Player(object):
    _id: int
    _player_name: str
    _bio: str = None
    _level: int = 1
    _experience: int = 0
    _cash: int = 0
    _hitpoints: int = 100
    _energy: int = 100
    _group_id: int = None
    _is_developer: bool = False
    _is_moderator: bool = False
    _dev_level: int = 0
    _mod_level: int = 0

    @property
    def player_id(self) -> int:
        return self._id

    @property
    def player_name(self) -> str:
        return self._player_name
    
    @player_name.setter
    def player_name(self, name: str) -> None:
        self._player_name = name

    @property
    def bio(self) -> str:
        return self._bio
    
    @bio.setter
    def bio(self, text: str) -> None:
        self._bio = text

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

    @property
    def cash(self) -> int:
        return self._cash
    
    @cash.setter
    def cash(self, cash: int) -> int:
        self._cash = cash

    @property
    def hitpoints(self) -> int:
        return self._hitpoints
    
    @hitpoints.setter
    def hitpoints(self, value: int) -> None:
        self._hitpoints = value

    @property
    def energy(self) -> int:
        return self._energy
    
    @energy.setter
    def energy(self, value: int) -> None:
        self._energy = value

    @property
    def group_id(self) -> int:
        return self._group_id
    
    @group_id.setter
    def group_id(self, id: int) -> None:
        self._group_id = id

    @property
    def is_developer(self) -> bool:
        return self._is_developer
    
    @is_developer.setter
    def is_developer(self, value: bool) -> None:
        self._is_developer = value

    @property
    def is_moderator(self) -> bool:
        return self._is_moderator
    
    @is_moderator.setter
    def is_moderator(self, value: bool) -> None:
        self._is_moderator = value

    @property
    def dev_level(self) -> int:
        return self._dev_level
    
    @dev_level.setter
    def dev_level(self, value: int) -> None:
        self._dev_level = value

    @property
    def mod_level(self) -> int:
        return self._mod_level
    
    @mod_level.setter
    def mod_level(self, value: int) -> None:
        self._mod_level = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.player_id,
            'player_name': self.player_name,
            'bio': self.bio,
            'level': self.level,
            'experience': self.experience,
            'cash': self.cash,
            'hitpoints': self.hitpoints,
            'energy': self.energy,
            'group_id': self.group_id,
            'is_developer': 1 if self.is_developer else 0,
            'is_moderator': 1 if self.is_moderator else 0,
            'dev_level': self.dev_level,
            'mod_level': self.mod_level
        }
