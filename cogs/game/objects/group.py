from dataclasses import dataclass

@dataclass
class Group(object):
    _id: int
    _owner_id: int
    _group_name: str
    _description: str
    _required_level: int
    _join_type: int

    @property
    def group_id(self) -> int:
        return self._id
    
    @property
    def owner_id(self) -> int:
        return self._owner_id
    
    @owner_id.setter
    def owner_id(self, id: int) -> None:
        self._owner_id = id

    @property
    def group_name(self) -> str:
        return self._group_name
    
    @group_name.setter
    def group_name(self, name: str) -> None:
        self._group_name = name

    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, text: str) -> None:
        self._description = text

    @property
    def required_level(self) -> int:
        return self._required_level
    
    @required_level.setter
    def required_level(self, level: int) -> None:
        self._required_level = level

    @property
    def join_type(self) -> int:
        return self._join_type
    
    @join_type.setter
    def join_type(self, value: int) -> None:
        self._join_type = value
