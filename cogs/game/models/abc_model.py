from abc import ABCMeta
import os
import json

class AbstractModel(ABCMeta):
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'mysql_config.json'), 'r') as f:
            self.MYSQL_CONFIG = json.load(f)
