"""NOTICE: THIS MODULE HAS BEEN DEPRECATED

Guild settings config handler"""
import os

from configparser import ConfigParser

if not os.path.exists('config'):
    os.mkdir('config')

class Config:
    """Config class"""
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = ConfigParser()
        self.config.read(config_path)

    def get(self, section, key, fallback=None):
        """Returns unformatted value from config"""
        section, key = str(section), str(key)
        self.config.read(self.config_path)
        value = self.config.get(section, key, fallback=fallback)
        return value

    def getint(self, section, key, fallback=None):
        """Returns integer value from config"""
        section, key = str(section), str(key)
        self.config.read(self.config_path)
        value = self.config.getint(section, key, fallback=fallback)
        return value

    def getboolean(self, section, key, fallback=None):
        """Returns boolean value from config"""
        section, key = str(section), str(key)
        self.config.read(self.config_path)
        value = self.config.getboolean(section, key, fallback=fallback)
        return value

    def set(self, section, key, value):
        """Set config value to config"""
        key = str(key)
        value = str(value)

        self.config.read(self.config_path)

        if not section in self.config.sections():
            self.config[section] = {}

        self.config[section][key] = value

        with open(self.config_path, 'w', encoding="utf-8") as conf:
            self.config.write(conf)

    def delete(self, section, key):
        """Deletes a config value from config"""
        key = str(key)

        self.config.read(self.config_path)

        if not section in self.config.sections():
            return

        if not self.get(section, key):
            return

        self.config[section].pop(key)

        with open(self.config_path, 'w', encoding="utf-8") as conf:
            self.config.write(conf)

    def has_section(self, section):
        """Checks if a section exists in config"""
        if section in self.config.sections():
            return True

        return False
