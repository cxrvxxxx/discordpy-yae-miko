
class Player(object):
    def __init__(self, player_id, name, bio, level, experience, cash, hitpoints, energy, group_id, is_developer, is_moderator, dev_level, mod_level):
        self.__player_id = player_id
        self.__name = name
        self.__bio = bio
        self.__level = level
        self.__experience = experience
        self.__cash = cash
        self.__hitpoints = hitpoints
        self.__energy = energy
        self.__group_id = group_id
        self.__is_developer = is_developer
        self.__is_moderator = is_moderator
        self.__dev_level = dev_level
        self.__mod_level = mod_level

    @property
    def player_id(self) -> int:
        return self.__player_id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, text: str) -> None:
        if len(text) > 24:
            return
        
        self.__name = text

    @property
    def bio(self) -> str:
        return self.__bio
    
    @bio.setter
    def bio(self, text: str) -> None:
        if len(text) > 255:
            return
        
        self.__bio = text

    @property
    def level(self) -> int:
        return self.__level
    
    @level.setter
    def level(self, value: int) -> None:
        if value < 0:
            return
        
        self.__level = value

    @property
    def experience(self) -> int:
        return self.__experience
    
    @experience.setter
    def experience(self, value: int) -> None:
        if value < 0:
            return
        
        self.__experience = value

    @property
    def cash(self) -> int:
        return self.__cash
    
    @cash.setter
    def cash(self, value: int) -> None:
        if value < 0:
            return
        
        self.__cash = value

    @property
    def hitpoints(self) -> int:
        return self.__hitpoints
    
    @hitpoints.setter
    def hitpoints(self, value: int) -> None:
        if value < 0:
            return
        
        self.__hitpoints = value

    @property
    def energy(self) -> int:
        return self.__energy
    
    @energy.setter
    def energy(self, value: int) -> None:
        if value < 0:
            return
        
        self.__energy = value

    @property
    def group_id(self) -> int:
        return self.__group_id
    
    @group_id.setter
    def group_id(self, value: int) -> None:
        self.__group_id = value

    @property
    def is_developer(self) -> bool:
        return self.__is_developer
    
    @is_developer.setter
    def is_developer(self, value: int) -> None:
        self.__is_developer = False if value == 0 else True

    @property
    def is_moderator(self) -> bool:
        return self.__is_moderator
    
    @is_moderator.setter
    def is_moderator(self, value: int) -> None:
        self.__is_moderator = False if value == 0 else True

    @property
    def dev_level(self) -> int:
        return self.__dev_level
    
    @dev_level.setter
    def dev_level(self, value: int) -> None:
        if value < 0 or value > 3:
            return
        
        self.__dev_level = value

    @property
    def mod_level(self) -> int:
        return self.__mod_level
    
    @mod_level.setter
    def mod_level(self, value: int) -> int:
        if value < 0 or value > 3:
            return
        
        self.__mod_level = value
