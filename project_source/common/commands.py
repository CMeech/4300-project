#
# commands.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Specifies the commands that the user can provide
# to the CLI.
#
from enum import Enum

from project_source.common.constants import (
    FILENAME,
    LARGE,
    LARGE_CHUNK,
    MESSAGE,
    INVALID,
    NUM_TESTS,
    OWNER,
    SIZE,
    SMALL_CHUNK,
    SUBJECT,
    EXPERIMENT_NAME,
    USERNAME
)


# Specifies the possible commands
class Command(str, Enum):
    AUTOMATE="automate"
    DELETE="delete"
    DOWNLOAD="download"
    FILES="files"
    GRANT="grant"
    HELP="help"
    LIST="list"
    QUIT="quit"
    REGISTER="register"
    REVOKE="revoke"
    UPLOAD="upload"


# Specifies the number of arguments for each command.
COMMAND_LENGTHS = {
    Command.AUTOMATE: 6,
    Command.DELETE: 2,
    Command.DOWNLOAD: 4,
    Command.FILES: 1,
    Command.GRANT: 3,
    Command.HELP: 1,
    Command.LIST: 1,
    Command.REVOKE: 3,
    Command.UPLOAD: 2
}

INVALID_LENGTH = -1

#
# parse_command
#
# PURPOSE: For a given line of input, parses the command
# and creates the corresponding request data to be sent
# to the server.
# 
# PARAMS:
# input_line - text obtained from the user
# username - name of the current user
#
def parse_command(input_line: str, username: str):
    tokens = input_line.split()
    message_type = tokens[0] if len(tokens) > 0 else ""
    data = {
        MESSAGE: message_type
    }
    # verify the number of arguments
    length = get_command_length(message_type)

    # see the 'help' command for the syntax of commands.
    if message_type == Command.AUTOMATE and len(tokens) == length:
        data[EXPERIMENT_NAME] = tokens[1]
        data[NUM_TESTS] = tokens[2]
        data[FILENAME] = tokens[3]
        data[OWNER] = tokens[4]
        data[SUBJECT] = username
        data[SIZE] = LARGE_CHUNK if tokens[5] == LARGE else SMALL_CHUNK

    elif message_type == Command.DELETE and len(tokens) == length:
        data[FILENAME] = tokens[1]
        data[OWNER] = username

    elif message_type == Command.DOWNLOAD and len(tokens) == length:
        data[FILENAME] = tokens[1]
        data[OWNER] = tokens[2]
        data[SUBJECT] = username
        data[SIZE] = LARGE_CHUNK if tokens[3] == LARGE else SMALL_CHUNK

    elif message_type == Command.FILES:
        data[USERNAME] = username

    elif (message_type == Command.GRANT or message_type == Command.REVOKE) and len(tokens) == length:
        data[OWNER] = username
        data[FILENAME] = tokens[1]
        data[SUBJECT] = tokens[2]

    elif message_type == Command.HELP:
        pass

    elif message_type == Command.LIST:
        pass

    elif message_type == Command.UPLOAD and len(tokens) == length:
        data[OWNER] = username
        data[FILENAME] = tokens[1]

    else:
        data[MESSAGE] = INVALID

    return data

def get_command_length(message_type: str) -> int:
    if message_type in COMMAND_LENGTHS:
        return COMMAND_LENGTHS[message_type]
    return INVALID_LENGTH
