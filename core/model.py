import sqlite3

class Database:
    def __init__(self, guild_id) -> None:
        # init database controller
        path_to_db = f'./data/{guild_id}.db'
        self.conn = sqlite3.connect(path_to_db)
        self.c = self.conn.cursor()

        # init database table
        with self.conn:
            self.c.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER, access INTEGER)")

    def get_access(self, uid) -> int:
        with self.conn:
            self.c.execute("SELECT access FROM users WHERE uid=:uid", {"uid": uid})
            access = self.c.fetchone()

        if access:
            return access[0]
        else:
            return 0

    def compare_access(self, uid_a, uid_b) -> bool:
        return uid_a if self.get_access(uid_a) > self.get_access(uid_b) else uid_b

    def add_user(self, uid, access) -> None:
        with self.conn:
            self.c.execute("SELECT * FROM users WHERE uid=:uid", {"uid": uid})
            data = self.c.fetchone()

            if not data:
                self.c.execute("INSERT INTO users VALUES (:uid, :access)", {"uid": uid, "access": access})

    def delete_user(self, uid) -> None:
        with self.conn:
            self.c.execute("DELETE FROM users WHERE uid=:uid", {"uid": uid})

    def update(self, uid, access) -> None:
        self.add_user(uid, access)
        with self.conn:
            self.c.execute("UPDATE users SET access=:access WHERE uid=:uid", {"uid": uid, "access": access})