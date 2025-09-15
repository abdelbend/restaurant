import sqlite3
from contextlib import contextmanager

DB_PATH = 'restaurant.db'


def create_connection(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS menu (
            item  TEXT PRIMARY KEY,
            price INTEGER NOT NULL CHECK(price >= 0)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customer (
            name     TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            orders   TEXT NOT NULL,
            order_id INTEGER NOT NULL
        )
        """
    )
    # Helpful index to group/scan orders
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customer_order_id ON customer(order_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name)")
    conn.commit()


def seed_menu_if_empty(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) AS c FROM menu")
    row = cur.fetchone()
    if row and row[0] == 0:
        # Basic starter menu
        items = [
            ("Burger", 8),
            ("Pizza", 12),
            ("Pasta", 10),
            ("Salad", 7),
            ("Soda", 2),
        ]
        cur.executemany("INSERT INTO menu(item, price) VALUES(?, ?)", items)
        conn.commit()


def is_write_query(sql: str) -> bool:
    first = sql.lstrip().split(" ", 1)[0].upper()
    return first in {"INSERT", "UPDATE", "DELETE", "REPLACE"}


def execute(conn: sqlite3.Connection, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    if is_write_query(sql):
        conn.commit()
    return cur


def query_all(conn: sqlite3.Connection, sql: str, params=()):
    cur = execute(conn, sql, params)
    return cur.fetchall()


def query_one(conn: sqlite3.Connection, sql: str, params=()):
    cur = execute(conn, sql, params)
    return cur.fetchone()

