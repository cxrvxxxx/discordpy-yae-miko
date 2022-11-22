"""Prefix Module"""

def prefix(client, message):
    """Retrieve custom prefix from config or return default prefix"""
    config = client.config[message.guild.id]

    pref = config.get('main', 'prefix')

    return pref if pref else "y!"
