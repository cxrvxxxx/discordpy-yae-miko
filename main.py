"""
This file contains the code for starting an instance
of the bot.
"""
import version
import json

from core.bot import YaeMiko
from modules import INSTALLED_MODULES

# Version information
VERSION_INFO = {
    "name": version.APP_NAME,
    "version": version.__version__,
    "description": version.__description__,
    "author": version.__author__,
    "url": version.__url__,
    "license": version.__license__
}

# Running the bot.
if __name__ == "__main__":
    with open("secrets.json", 'r') as f:
        TOKEN = json.load(f).get("token")

    client = YaeMiko(version=VERSION_INFO, modules=INSTALLED_MODULES)
    client.run(TOKEN, root_logger=True)
