# Yae Miko - DIscord Bot
A feature-packed Discord Bot built using __Python__.

Invite **Yae Miko** to your Discord server using [this link](https://discord.com/api/oauth2/authorize?client_id=904245816552742922&permissions=1789390220887&scope=bot%20applications.commands)

# Self-Hosting

## Requirements
1. [Python 3.10.7+](https://www.python.org/downloads/)
2. [FFMPEG](https://ffmpeg.org/)

## Libraries/Frameworks
1. [python-dotenv 0.21.0+](https://pypi.org/project/python-dotenv/)
2. [discord.py 2.1.0+](https://pypi.org/project/discord.py/)
3. [youtube_dl 2021.12.17](https://pypi.org/project/youtube_dl/)

Install [Git for Windows](https://gitforwindows.org/).

Open __Git Bash__ and clone the repository using the command:

    git clone https://github.com/cxrvxxxx/yae-miko
    
Navigate into the folder that was just cloned:

    cd yae-miko
    
Create a `.env` file:

    touch .env
    
Open the newly created `.env` file and paste the code below. Replace ``token here`` with your Bot's token.
If you do not have a Discord Bot set up, you can do so by following this [guide](https://discordpy.readthedocs.io/en/stable/discord.html).

    TOKEN=token here
    
Save and close the `.env` file. In the terminal/console, you can now run the bot using this command:

    py main.py
    
The bot is now online and can start receiving commands.
