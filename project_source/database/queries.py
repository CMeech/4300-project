#
# queries.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements the queries used in the application.
#
import sqlite3
from project_source.common.constants import DATABASE_FILE, FILENAME, OWNER

from project_source.database.helpers import fetch_all, fetch_one, write_to_db, write_lock


def open_connection() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE_FILE)


#
# initialize_database
#
# PURPOSE: Creates the tables required for the application
#
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


#
# grant_access
#
# PURPOSE: Creates the ACL granting a client's access to a file.
#
# PARAMS:
# owner - owner of the file
# subject - client being granted access
# filename - name of the file 
#
def grant_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    write_to_db(conn, f"INSERT INTO acl (filename, owner, subject) VALUES (?,?,?)", args)
    conn.close()


#
# revoke_access
#
# PURPOSE: Removes the ACL granting a client's access to a file.
#
# PARAMS:
# owner - owner of the file
# subject - client being revoked from access
# filename - name of the file 
#
def revoke_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    write_to_db(conn, f"DELETE FROM acl WHERE filename=? AND owner=? AND subject=?", args)
    conn.close()


#
# has_access
#
# PURPOSE: Determines if the subject has access to a given file.
#
# PARAMS:
# owner - owner of the file
# subject - client being revoked from access
# filename - name of the file 
#
def has_access(owner: str, subject: str, filename: str):
    conn = open_connection()
    args = (filename, owner, subject)
    entry = fetch_one(conn, f"SELECT * FROM acl WHERE filename=? AND owner=? AND subject=?", args)
    conn.close()
    return True if entry else False


#
# create_file
#
# PURPOSE: Stores information about a newly created file.
#
# PARAMS:
# filename - the name of the new file
# owner - the owner of the file
#
def create_file(owner: str, filename: str):
    conn = open_connection()
    args = (filename, owner)
    write_to_db(conn, f"INSERT INTO files (filename, owner) VALUES (?,?)", args)
    conn.close()


#
# delete_file
#
# PURPOSE: Removes information of a deleted file.
#
# PARAMS:
# filename - the name of the deleted file
# owner - the owner of the file
#
def delete_file(owner: str, filename: str):
    conn = open_connection()
    args = (filename, owner)
    write_to_db(conn, f"DELETE FROM files WHERE filename=? and owner=?", args)
    # we have do a manual cascade
    write_to_db(conn, f"DELETE FROM acl WHERE filename=? AND owner=?", args)
    conn.close()


#
# file_exists
#
# PURPOSE: Checks if a file exists in the database.
#
# PARAMS:
# filename - the name of the deleted file
# owner - the owner of the file
#
# Returns a boolean indicating if the file exists.
#
def file_exists(owner: str, filename: str) -> bool:
    conn = open_connection()
    args = (filename, owner)
    file = fetch_one(conn, f"SELECT * FROM files WHERE filename=? AND owner=?", args)
    conn.close()
    return True if file else False


#
# list_files
#
# PURPOSE: Finds all the files that a given client has
# access to.
#
# PARAMS:
# username - the username of the client.
#
# Returns an array of file data which includes the owner and filename.
#
def list_files(username: str):
    NAME_INDEX = 0
    OWNER_INDEX = 1
    conn = open_connection()
    args = (username,)
    rows = fetch_all(conn, "SELECT filename, owner FROM acl WHERE subject = ?", args)
    files_list = [{FILENAME: file[NAME_INDEX], OWNER: file[OWNER_INDEX]} for file in rows]
    return files_list
    