"""
This file contains the list of modules that will be loaded
once the bot starts.

To install a module, place the module folder inside the
'cogs' folder within the root directory. Ensure the that
the module folder name has no spaces.

Then add the module name to the 'INSTALLED_MODULES' list.
    Ex.
        INSTALLED_MODULES = [
            'cogs.myModule',
        ]
"""

INSTALLED_MODULES = [
    'cogs.admin',
    'cogs.info',
    'cogs.music',
    # 'cogs.slash',
    # 'cogs.spam',
    # 'cogs.game',
]
