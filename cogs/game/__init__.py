from .monaheistaccount import MonaHeistAccount
from .models.database import Database

with Database("AppData.db") as conn:
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblPlayer (
        id INTEGER PRIMARY KEY,
        player_name VARCHAR(24),
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
        FOREIGN KEY (group_id) REFERENCES tblGroup(id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblGroup (
        id INTEGER PRIMARY KEY,
        owner_id INTEGER,
        group_name VARCHAR(24),
        description VARCHAR(255),
        required_level INTEGER,
        join_type INTEGER,
        FOREIGN KEY (owner_id) REFERENCES tblPlayer(id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblArmor (
        id INTEGER PRIMARY KEY,
        armor_name VARCHAR(100),
        description VARCHAR(255),
        owner_id INTEGER,
        level INTEGER,
        experience INTEGER,
        armor_type VARCHAR(24),
        FOREIGN KEY (owner_id) REFERENCES tblPlayer(id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblWeapon (
        id INTEGER PRIMARY KEY,
        weapon_name VARCHAR(100),
        description VARCHAR(255),
        owner_id INTEGER,
        level INTEGER,
        experience INTEGER,
        weapon_type VARCHAR(24),
        protection INTEGER,
        FOREIGN KEY (owner_id) REFERENCES tblPlayer(id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblShop (
        id INTEGER PRIMARY KEY,
        shop_name VARCHAR(30),
        description VARCHAR(255),
        owner_id INTEGER,
        FOREIGN KEY (owner_id) REFERENCES tblPlayer(id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS tblShopListing (
        id INTEGER PRIMARY KEY,
        shop_id INTEGER,
        item_id INTEGER,
        price INTEGER,
        close_time VARCHAR(255),
        FOREIGN KEY (shop_id) REFERENCES tblShop(id)
    )""")

async def setup(client) -> None:
    await client.add_cog(MonaHeistAccount(client))
