#
# helpers.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements various helpers for executing queries
# in the sqlite database.
#
import sqlite3
import threading


write_lock = threading.Lock()

def open_connection() -> sqlite3.Connection:
    return sqlite3.connect("project.db")


#
# fetch_one
#
# PURPOSE: Executes a query and gets the first result
# 
# PARAMS:
# conn - the database connection
# query -  the query as a parameterized SQL string
# args - arguments for the parameterized query.
#
# Returns the first result of the query.
#
def fetch_one(conn: sqlite3.Connection, query: str, args: tuple):
    cur = conn.cursor()
    execute_query(cur, query, args)
    return cur.fetchone()


#
# fetch_all
#
# PURPOSE: Executes a query and gets all results
# 
# PARAMS:
# conn - the database connection
# query -  the query as a parameterized SQL string
# args - arguments for the parameterized query.
#
# Returns the results of the query
#
def fetch_all(conn: sqlite3.Connection, query: str, args: tuple):
    cur = conn.cursor()
    execute_query(cur, query, args)
    return cur.fetchall()


#
# write_to_db
#
# PURPOSE: Executes a modifying query.
# 
# PARAMS:
# conn - the database connection
# query -  the query as a parameterized SQL string
# args - arguments for the parameterized query.
#
def write_to_db(conn: sqlite3.Connection, query: str, args: tuple):
    with write_lock:
        cur = conn.cursor()
        execute_query(cur, query, args)
        conn.commit()


#
# execute_query
#
# PURPOSE: Executes a query.
# 
# PARAMS:
# cursor - the table cursor
# query -  the query as a parameterized SQL string
# args - arguments for the parameterized query.
#
def execute_query(cursor, query: str, args: tuple):
    if args and args != None:
        cursor.execute(query, args)
    else:
        cursor.execute(query)
