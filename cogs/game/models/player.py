
class Player(object):
    def __init__(self, uid, player_name = None, bio = None, level = 1, experience = 0, cash = 0, hitpoints = 100, energy = 100, group_id = None, is_developer = False, is_moderator = False, dev_level = 0, mod_level = 0) -> None:
        self.uid = uid
        self.player_name = player_name
        self.bio = bio
        self.level = level
        self.experience = experience
        self.cash = cash
        self.hitpoints = hitpoints
        self.energy = energy
        self.group_id = group_id
        self.is_developer = is_developer
        self.is_moderator = is_moderator
        self.dev_level = dev_level
        self.mod_level = mod_level
