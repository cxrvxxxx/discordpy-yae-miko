import sqlite3 as sql

from typing import Union

from .user import User

SAVEFILE_PATH = r'./data/MonaHeist.db'

class Game:
    def __init__(self):
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY,
            level INTEGER,
            exp INTEGER,
            cash INTEGER,
            bank INTEGER
        )""")

        conn.commit()
        conn.close()

    @staticmethod
    def get_user(uid: int) -> Union[User, None]:
        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        data = c.fetchone()

        if data:
            return User(*data)

    @staticmethod
    def create_user(uid: int, level: int = 1, exp: int = 0, cash: int = 0, bank: int = 0) -> User:
        user = Game.get_user(uid)

        if user:
            return

        conn = sql.connect(SAVEFILE_PATH)
        c = conn.cursor()

        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (uid, level, exp, cash, bank,))

        conn.commit()
        conn.close()

        user = Game.get_user(uid)
        if not user:
            return
        
        return user
    
    @staticmethod
    def update_user(user: User) -> User:
        existing_user = Game.get_user(user.uid)

        if not existing_user:
            new_user = Game.create_user(user.uid, user.level, user.exp, user.cash, user.bank)
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
