import pymysql
from typing import Any, Optional, Sequence

_conn = None

class Database:
    """
    Database.connect(...) to initialize a global connection used by models.
    """
    @staticmethod
    def connect(host='localhost', user=None, password=None, db=None, port=3306, charset='utf8mb4', autocommit=True, **kwargs):
        global _conn
        _conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port, charset=charset, autocommit=autocommit, cursorclass=pymysql.cursors.DictCursor, **kwargs)
        return _conn

    @staticmethod
    def connection():
        if _conn is None:
            raise RuntimeError("Database not connected. Call Database.connect(...)")
        return _conn

def execute(sql: str, params: Optional[Sequence[Any]] = None, commit: bool = True):
    conn = Database.connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        if commit:
            conn.commit()
        return cur

def executemany(sql: str, seq_of_params, commit: bool = True):
    conn = Database.connection()
    with conn.cursor() as cur:
        cur.executemany(sql, seq_of_params)
        if commit:
            conn.commit()
        return cur
