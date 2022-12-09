import sqlite3
from project_source.common.constants import DATABASE_FILE, FILENAME, OWNER

from project_source.database.helpers import fetch_all, fetch_one, write_to_db, write_lock


def open_connection() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_FILE)


def initialize_database() -> None:
    conn = open_connection()

    with write_lock:
        conn.execute ("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY,
          username TEXT NOT NULL,
          UNIQUE(username)
        );
    """)

        conn.execute ("""
        CREATE TABLE IF NOT EXISTS files (
          id INTEGER PRIMARY KEY,
          filename TEXT NOT NULL,
          owner TEXT NOT NULL,
          UNIQUE(owner, filename),
          FOREIGN KEY(owner) REFERENCES users(username)
        );
    """)

        conn.execute ("""
        CREATE TABLE IF NOT EXISTS acl (
          id INTEGER PRIMARY KEY,
          filename TEXT NOT NULL, 
          owner TEXT NOT NULL,
          subject TEXT NOT NULL,
          UNIQUE(filename, owner, subject)
        );
    """)

        conn.commit()
    conn.close()


def get_users():
    USER_NAME_INDEX = 0
    conn = open_connection()
    rows = fetch_all(conn, "SELECT username FROM users", None)
    user_list = [user[USER_NAME_INDEX] for user in rows]

    return user_list


def user_exists(username: str) -> bool:
    conn = open_connection()
    args = (username,)
    user = fetch_one(conn, "SELECT username FROM users where username=?", args)
    if user:
        return True
    else:
        return False


def register_user(username: str):
    conn = open_connection()
    args = (username,)
    write_to_db(conn, f"INSERT INTO users (username) VALUES (?)", args)
    conn.close()


def grant_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    write_to_db(conn, f"INSERT INTO acl (filename, owner, subject) VALUES (?,?,?)", args)
    conn.close()


def revoke_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    write_to_db(conn, f"DELETE FROM acl WHERE filename=? AND owner=? AND subject=?", args)
    conn.close()


def has_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    entry = fetch_one(conn, f"SELECT * FROM acl WHERE filename=? AND owner=? AND subject=?", args)
    conn.close()
    return True if entry else False


def create_file(owner: str, filename: str):
    conn = open_connection()
    args = (filename, owner)
    write_to_db(conn, f"INSERT INTO files (filename, owner) VALUES (?,?)", args)
    conn.close()


def delete_file(owner: str, filename: str):
    conn = open_connection()
    args = (filename, owner)
    write_to_db(conn, f"DELETE FROM files WHERE filename=? and owner=?", args)
    # we have do a manual cascade
    write_to_db(conn, f"DELETE FROM acl WHERE filename=? AND owner=?", args)
    conn.close()


def file_exists(owner: str, filename: str) -> bool:
    conn = open_connection()
    args = (filename, owner)
    file = fetch_one(conn, f"SELECT * FROM files WHERE filename=? AND owner=?", args)
    conn.close()
    return True if file else False


def list_files(username: str):
    NAME_INDEX = 0
    OWNER_INDEX = 1
    conn = open_connection()
    args = (username,)
    rows = fetch_all(conn, "SELECT filename, owner FROM acl WHERE subject = ?", args)
    files_list = [{FILENAME: file[NAME_INDEX], OWNER: file[OWNER_INDEX]} for file in rows]
    return files_list
    