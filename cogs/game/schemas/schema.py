import sqlite3 as sql

from ..settings import SAVEFILE_PATH

conn = sql.connect(SAVEFILE_PATH)
c = conn.cursor()

c.execute("PRAGMA foreign_keys = ON")

c.execute("""CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name VARCHAR(24),
    bio VARCHAR(255),
    level INTEGER,
    experience INTEGER,
    cash INTEGER,
    hitpoints INTEGER,
    energy INTEGER,
    group_id INTEGER,
    is_developer INTEGER,
    is_moderator INTEGER,
    dev_level INTEGER,
    mod_level INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER,
    name VARCHAR(24),
    description VARCHAR(255),
    required_level INTEGER,
    join_type INTEGER,
    FOREIGN KEY (owner_id) REFERENCES players(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS weapons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    description VARCHAR(255),
    owner_id INTEGER,
    type VARCHAR(8),
    level INTEGER,
    experience INTEGER,
    damange INTEGER,
    energy_cost INTEGER,
    FOREIGN KEY (owner_id) REFERENCES players(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS armors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    description VARCHAR(255),
    owner_id INTEGER,
    type VARCHAR(10),
    level INTEGER,
    experience INTEGER,
    protection INTEGER,
    FOREIGN KEY (owner_id) REFERENCES players(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30),
    description VARCHAR(255),
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES players(id)
)""")

c.execute("""CREATE TABLE IF NOT EXISTS shop_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER,
    item_id INTEGER,
    price INTEGER,
    close_time DATETIME,
    FOREIGN KEY (shop_id) REFERENCES shops(id),
    FOREIGN KEY (item_id) REFRENCES items(id)
)""")

conn.commit()
conn.close()