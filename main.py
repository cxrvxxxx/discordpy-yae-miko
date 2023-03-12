"""
This file contains the code for starting an instance
of the bot.
"""
import os
import version
from dotenv import load_dotenv
from core.bot import YaeMiko
from modules import INSTALLED_MODULES

# Version information
VERSION_INFO = {
    "PROJECT_NAME"    : version.APP_NAME,
    "VERSION"         : version.__version__,
    "AUTHOR"          : version.__author__,
    "REPO_URL"        : version.__url__,
    "TEST_GUILD_ID"   : 907119292410130433,
}

# Running the bot.
if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    client = YaeMiko(**VERSION_INFO, modules=INSTALLED_MODULES)
    client.run(TOKEN, root_logger=True)
