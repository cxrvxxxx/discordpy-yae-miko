import sqlite3 as sql

from typing import Union

from .player import Player

SAVEFILE_PATH = r'./data/MonaHeist.db'

class Game:
    def __init__(self):
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("PRAGMA foreign_keys = ON")

        c.execute("""CREATE TABLE IF NOT EXISTS players (
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
            FOREIGN KEY (group_id) REFERENCES groups(id)
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            group_name VARCHAR(24),
            description VARCHAR(255),
            required_level INTEGER,
            join_type INTEGER,
            FOREIGN KEY (owner_id) REFERENCES players(id)
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS weapons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weapon_name VARCHAR(100),
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
            armor_name VARCHAR(100),
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
            shop_name VARCHAR(30),
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

    @staticmethod
    def get_player(uid: int) -> Union[Player, None]:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM players WHERE id=?", (uid,))
        data = c.fetchone()

        if data:
            return Player(*data)

    @staticmethod
    def create_player(uid, player_name, **kwargs) -> Player:
        user = Game.get_user(uid)

        if user:
            return

        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                uid,
                player_name,
                kwargs.get('bio'),
                kwargs.get('level', 1),
                kwargs.get('exp', 0),
                kwargs.get('cash', 0),
                kwargs.get('hp', 100),
                kwargs.get('energy', 160),
                kwargs.get('group_id'),
                kwargs.get('is_dev', 0),
                kwargs.get('is_mod', 0),
                kwargs.get('dev_level', 0),
                kwargs.get('mod_level', 0),
            )
        )

        conn.commit()
        conn.close()

        user = Game.get_user(uid)
        if not user:
            return
        
        return user
    
    @staticmethod
    def update_user(player: Player) -> Player:
        existing_user = Game.get_user(player.player_id)

        if not existing_user:
            new_user = Game.create_user(player.player_id, user.level, user.exp, user.cash, user.bank)
            return new_user
        
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("""
            UPDATE users
            SET
                level=:level,
                exp=:exp,
                cash=:cash,
                bank=:bank
            WHERE
                uid=:uid""",
            {
                'level': user.level,
                'exp': user.exp,
                'cash': user.cash,
                'bank': user.bank
            })
        
        conn.commit()
        conn.close()

        existing_user = Game.get_user(user.uid)
        return existing_user
