def prefix(client, message):
    config = client.config[message.guild.id]

    pf = config.get('main', 'prefix')
    if pf:
        return pf
    else:
        return "y!"