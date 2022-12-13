import unittest

from project_source.database.helpers import fetch_all, fetch_one, write_to_db

class MockCursor():
    def __init__(self):
        self.executed = False

    def execute(self, args=None):
        self.executed = True

    def fetchone(self):
        return "dummy"

    def fetchall(self):
        return []

class MockConnection():
    def __init__(self):
        self.cursor_obj = MockCursor()
        self.committed = False

    def cursor(self) -> MockCursor:
        return self.cursor_obj

    def commit(self):
        self.committed = True

class TestDBHelpers(unittest.TestCase):

    def test_fetch_one(self):
        conn = MockConnection()
        data = fetch_one(conn, "SELECT * FROM users", None)
        self.assertTrue(conn.cursor().executed)
        self.assertEqual(data, "dummy")
    
    def test_fetch_one(self):
        conn = MockConnection()
        data = fetch_all(conn, "SELECT * FROM users", None)
        self.assertTrue(conn.cursor().executed)
        self.assertEqual(data, [])

    def test_write(self):
        conn = MockConnection()
        write_to_db(conn, "INSERT INTO users VALUES ('username')", None)
        self.assertTrue(conn.cursor().executed)
        self.assertTrue(conn.committed)