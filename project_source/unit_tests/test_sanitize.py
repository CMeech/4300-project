import unittest
from project_source.database.sanitize import sanitize_alphanumeric

class TestSanitize(unittest.TestCase):

    def test_username(self):
        sanitized = sanitize_alphanumeric("(*&u@!s  $(e*&$r@1!")
        self.assertEqual(sanitized, "user1")
        sanitized = sanitize_alphanumeric("  user1  ")
        self.assertEqual(sanitized, "user1")