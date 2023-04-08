import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    "version"                   : 1,
    "disabled_existing_loggers" : False,
    "formatters"                : {
        "verbose"       : {
            "format": "%(levelname)-7s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard"      : {
            "format": "%(levelname)-7s - %(name)-15s : %(message)s"
        }
    },
    "handlers"                  : {
        "console"       : {
            "level"     : "DEBUG",
            "class"     : "logging.StreamHandler",
            "formatter" : "standard"
        },
        "console2"      : {
            "level"     : "WARNING",
            "class"     : "logging.StreamHandler",
            "formatter" : "standard"
        },
        "file"          : {
            "level"     : "INFO",
            "class"     : "logging.FileHandler",
            "formatter" : "verbose",
            "filename"  : "logs/discord.log",
            "mode"      : "w"
        }
    },
    "loggers"                   : {
        "bot"           : {
            "handlers"  : ["console"],
            "level"     : "DEBUG",
            "propagate" : False
        },
        "discord"       : {
            "handlers"  : ["console2", "file"],
            "level"     : "INFO",
            "propagate" : False
        },
        "music.song"   : {
            "handlers"  : ["console"],
            "level"     : "DEBUG",
            "propagate" : False
        },
        "music.player"   : {
            "handlers"  : ["console"],
            "level"     : "DEBUG",
            "propagate" : False
        },
        "music.player.ui"   : {
            "handlers"  : ["console"],
            "level"     : "DEBUG",
            "propagate" : False
        },
        "bot.admin"   : {
            "handlers"  : ["console"],
            "level"     : "DEBUG",
            "propagate" : False
        },
    }
}

dictConfig(LOGGING_CONFIG)
