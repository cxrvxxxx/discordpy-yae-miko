from dataclasses import dataclass

@dataclass
class Player(object):
    _id: int
    _player_name: str
    _bio: str
    _level: int
    _experience: int
    _cash: int
    _hitpoints: int
    _energy: int
    _group_id: int
    _is_developer: bool
    _is_moderator: bool
    _dev_level: int
    _dev_level: int

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
