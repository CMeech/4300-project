import unittest

from project_source.common.commands import COMMAND_LENGTHS, INVALID_LENGTH, Command, get_command_length, parse_command
from project_source.common.constants import EXPERIMENT_NAME, FILENAME, INVALID, LARGE_CHUNK, MESSAGE, NUM_TESTS, OWNER, SIZE, SUBJECT, USERNAME


class TestCommands(unittest.TestCase):
    def test_get_command_length(self):
        self.assertEqual(get_command_length("jibberish"), INVALID_LENGTH)
        self.assertEqual(get_command_length(Command.AUTOMATE), COMMAND_LENGTHS[Command.AUTOMATE])

    def invalid_command(self):
        request = parse_command("random", "cash")
        self.assertEqual(request[MESSAGE], INVALID)
        pass

    def test_automate(self):
        expected = {
            MESSAGE: Command.AUTOMATE,
            NUM_TESTS: "10",
            EXPERIMENT_NAME: "test",
            FILENAME: "file.txt",
            OWNER: "owner",
            SUBJECT: "cash",
            SIZE: LARGE_CHUNK
        }
        request = parse_command("automate test 10 file.txt owner large", "cash")
        self.assertEqual(request, expected)

    
    def test_automate_missing_tokens(self):
        expected = {
            MESSAGE: INVALID
        }
        request = parse_command("automate test file.txt owner large", "cash")
        self.assertEqual(request, expected)

    def test_delete(self):
        expected = {
            MESSAGE: Command.DELETE,
            FILENAME: "file.txt",
            OWNER: "cash"
        }
        request = parse_command("delete file.txt", "cash")
        self.assertEqual(request, expected)

    def test_download(self):
        expected = {
            MESSAGE: Command.DOWNLOAD,
            FILENAME: "file.txt",
            OWNER: "user1",
            SUBJECT: "cash",
            SIZE: LARGE_CHUNK
        }
        request = parse_command("download file.txt user1 large", "cash")
        self.assertEqual(request, expected)
    
    def test_list_files(self):
        expected = {
            MESSAGE: Command.FILES,
            USERNAME: "cash"
        }
        request = parse_command("files", "cash")
        self.assertEqual(request, expected)
    
    def test_grant(self):
        expected = {
            MESSAGE: Command.GRANT,
            FILENAME: "file.txt",
            OWNER: "cash",
            SUBJECT: "user1",
        }
        request = parse_command("grant file.txt user1", "cash")
        self.assertEqual(request, expected)

    def test_help(self):
        expected = {
            MESSAGE: Command.HELP,
        }
        request = parse_command("help ", "cash")
        self.assertEqual(request, expected)
    
    def test_client_list(self):
        expected = {
            MESSAGE: Command.LIST,
        }
        request = parse_command("list ", "cash")
        self.assertEqual(request, expected)

    def test_upload(self):
        expected = {
            MESSAGE: Command.UPLOAD,
            OWNER: "cash",
            FILENAME: "file.txt"
        }
        request = parse_command("upload file.txt ", "cash")
        self.assertEqual(request, expected)
