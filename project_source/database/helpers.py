import sqlite3
import threading


write_lock = threading.Lock()

def open_connection() -> sqlite3.Connection:
    return sqlite3.connect("project.db")


def fetch_one(conn: sqlite3.Connection, query: str, args: tuple):
    cur = conn.cursor()
    execute_query(cur, query, args)
    return cur.fetchone()


def fetch_all(conn: sqlite3.Connection, query: str, args: tuple):
    cur = conn.cursor()
    execute_query(cur, query, args)
    return cur.fetchall()


def write_to_db(conn: sqlite3.Connection, query: str, args: tuple):
    with write_lock:
        cur = conn.cursor()
        execute_query(cur, query, args)
        conn.commit()


def execute_query(cursor, query: str, args: tuple):
    if args and args != None:
        cursor.execute(query, args)
    else:
        cursor.execute(query)
