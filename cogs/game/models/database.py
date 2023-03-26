import sqlite3 as sql

class Database(object):
    def __init__(self, filename: str) -> None:
        self.fn = filename

    def __enter__(self) -> sql.Connection:
        self.conn = sql.connect(fr'./data/{self.fn}')
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.conn.commit()

        self.conn.close()
