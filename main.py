"""
Project name: Yae Miko - Discord Bot [discord.py]
Author: cxrvxxx
Repository URL: https://github.com/cxrvxxx/yae-miko
Description: A feature-packed Discord bot using discord.py
"""
import os
from dotenv import load_dotenv
from core.bot import YaeMiko
from modules import INSTALLED_MODULES

# Version information
VERSION_INFO = {
    "PROJECT_NAME"    : "Yae Miko - Discord Bot [discord.py]",
    "VERSION"         : "1.4.3",
    "AUTHOR"          : "cxrvxxxx",
    "REPO_URL"        : "https://github.com/cxrvxxxx/yae-miko",
    "TEST_GUILD_ID"   : 907119292410130433,
}

# Running the bot.
if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    client = YaeMiko(**VERSION_INFO, modules=INSTALLED_MODULES)
    client.run(TOKEN, root_logger=True)
