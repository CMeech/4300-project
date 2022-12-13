#
# client_task.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements the message sending and receiving
# logic for the client application.
#
import asyncio
import logging
import os
from pathlib import Path
import time

from rsocket.rsocket_client import RSocketClient
from project_source.client_module.client_streams import (
    ClientDownloadPublisher,
    ClientDownloadSubscriber,
    ClientUploadPublisher,
    ClientUploadSubscriber
)
from project_source.client_module.experiments.benchmark import Benchmark
from project_source.client_module.experiments.experiment import Experiment
from project_source.common.commands import Command, parse_command
from project_source.common.constants import (
    CLIENT_MODULE,
    FILENAME,
    FILES_DIR,
    LARGE_CHUNK,
    MAX_REQUEST_NUMBER,
    MESSAGE,
    INVALID,
    NUM_TESTS,
    OWNER,
    PROJECT_SRC,
    READ_BYTES,
    SIZE,
    SUBJECT,
    SUCCESS,
    EXPERIMENT_NAME,
    USERNAME
)
from project_source.common.helpers import create_byte_payload, create_payload, parse_payload

from project_source.common.messages import (
    ACCESS_GRANTED,
    ACCESS_REVOKED,
    AUTOMATE_ERROR,
    CLIENT_NAME,
    CLIENTS,
    DATA_ERROR,
    DELETE_ERROR,
    EMPTY,
    FILE,
    FILE_DELETED,
    FILE_DOWNLOADED,
    FILE_UPLOADED,
    FILES,
    GENERIC_ERROR,
    GRANT_ERROR,
    HELP,
    INPUT_PROMPT,
    INVALID_COMMAND,
    INVALID_USERNAME,
    LOGGED_IN,
    REVOKE_ERROR,
    RUNNING_TESTS,
    SENDING,
    TEST_COMPLETED,
    UPLOAD_ERROR
)
from project_source.common.response_keys import CLIENT_LIST, FILE_LIST, STATUS
from project_source.database.sanitize import sanitize_alphanumeric

#
# run_client
#
# PURPOSE: Runs the receives input from the user and
# performs the appropriate action.
# 
# PARAMS:
# client -  The socket used to send/receive data
# username - provided by the user
#
async def run_client(client: RSocketClient, username: str):
    valid_username = sanitize_alphanumeric(username)
    if valid_username != EMPTY:
        register_success = await register_user(client, valid_username)
        if register_success:
            input_text = input(INPUT_PROMPT)

            # the next block is the core logic of the client
            while input_text != Command.QUIT:
                cmd_data = parse_command(input_text, valid_username)
                if cmd_data[MESSAGE] == Command.HELP:
                    print(HELP)
                elif cmd_data[MESSAGE] != INVALID:
                    task = asyncio.create_task(do_command(client, cmd_data))
                    await task
                else:
                    print(INVALID_COMMAND)

                input_text = input(INPUT_PROMPT)
    else:
        print(INVALID_USERNAME)


#
# do_command
#
# PURPOSE: Parses the data to be sent to the server and
# determines what to do with it.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def do_command(client: RSocketClient, data):
    try:
        logging.info(SENDING.format(data))
        if data[MESSAGE] == Command.AUTOMATE:
            await automate_download(client, data)

        elif data[MESSAGE] == Command.DELETE:
            await delete_file(client, data)

        elif data[MESSAGE] == Command.DOWNLOAD:
            await download_file(client, data)

        elif data[MESSAGE] == Command.FILES:
            await get_file_list(client, data)

        elif data[MESSAGE] == Command.GRANT:
            await grant_access(client, data)

        elif data[MESSAGE] == Command.LIST:
            await get_client_list(client, data)

        elif data[MESSAGE] == Command.REVOKE:
            await revoke_access(client, data)

        elif data[MESSAGE] == Command.UPLOAD:
            await upload_file(client, data)
    except asyncio.CancelledError:
        pass


#
# get_client_list
#
# PURPOSE: Retrieves the list of all clients registered
# in the system.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def get_client_list(client: RSocketClient, data):
    payload = create_payload(data)
    try:
        result = await client.request_response(payload)
        result_data = parse_payload(result)
        if result_data[STATUS] == SUCCESS:
            print_client_list(result_data[CLIENT_LIST])
        else:
            print(GENERIC_ERROR)
    except Exception as e:
        logging.info(e)
        print(DATA_ERROR)


#
# print_client_list
#
# PURPOSE: Prints the users of the system where
# each user is on its own line.
# 
# PARAMS:
# client_list - An array of strings.
#
def print_client_list(client_list):
    print(CLIENTS)
    for client_name in client_list:
        print(CLIENT_NAME.format(client_name))


#
# register_user
#
# PURPOSE: Registers a user in the database.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
# Returns a boolean indicating if registration was successful.
#
async def register_user(client: RSocketClient, username: str) -> bool:
    request_data = {
        MESSAGE: Command.REGISTER,
        USERNAME: username
    }

    payload = create_payload(request_data)

    try:
        result = await client.request_response(payload)
        if parse_payload(result)[STATUS] == SUCCESS:
            print(LOGGED_IN.format(username))
            return True
    except Exception as e:
        logging.info(e)
        print(DATA_ERROR)
    return False


#
# get_file_list
#
# PURPOSE: Retrieves a list of files that the current
# user has access to.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def get_file_list(client: RSocketClient, data):
    payload = create_payload(data)
    try:
        result = await client.request_response(payload)
        result_data = parse_payload(result)
        if result_data[STATUS] == SUCCESS:
            print_file_list(parse_payload(result)[FILE_LIST])
        else:
            print(GENERIC_ERROR)
    except Exception as e:
        logging.info(e)
        print(DATA_ERROR)


#
# print_file_list
#
# PURPOSE: Prints the list of files that the current user
# has access to. Each file gets its own line and also
# displays its owner.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
def print_file_list(file_list):
    print(FILES)
    for file in file_list:
        print(FILE.format(file[FILENAME], file[OWNER]))


#
# upload_file
#
# PURPOSE: Uploads a file to the server with the current
# user as its owner.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def upload_file(client: RSocketClient, data):
    filename = data[FILENAME]
    root_path = Path(os.getcwd()).resolve().parent
    file_path = os.path.join(root_path, PROJECT_SRC, CLIENT_MODULE, FILES_DIR, filename)

    complete = asyncio.Event()
    established = asyncio.Event()

    # setup the communication streams
    chunk_publisher = ClientUploadPublisher()
    channel_subscriber = ClientUploadSubscriber(established, complete)
    channel = client.request_channel(create_payload(data), chunk_publisher, None)
    channel.initial_request_n(MAX_REQUEST_NUMBER)
    channel.subscribe(channel_subscriber)

    # wait until the server is ready
    await established.wait()
    
    try:
        file = open(file_path, READ_BYTES)
        chunk = file.read(LARGE_CHUNK)

        # send the chunks, stop if the server sends an error
        while chunk and channel_subscriber.error == None:
            chunk_publisher.upload_bytes(create_byte_payload(chunk))
            chunk = file.read(LARGE_CHUNK)

        chunk_publisher.complete()
        await complete.wait()
        print(FILE_UPLOADED)
        file.close()
    except OSError as ose:
        logging.info(ose)
        chunk_publisher.error(ose)
        print(UPLOAD_ERROR.format(filename, data[OWNER]))
    except Exception as e:
        file.close()
        chunk_publisher.error(ose)
        logging.info(e)
        print(UPLOAD_ERROR.format(filename, data[OWNER]))


#
# download_file
#
# PURPOSE: Downloads a file from the server.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
# Returns a Benchmark object that includes data about
# the download.
#
async def download_file(client: RSocketClient, data, automated: bool = False) -> Benchmark:
    bench = None
    start_time = None
    end_time = None
    filename = data[FILENAME]
    owner = data[OWNER]
    complete = asyncio.Event()

    # setup the communication streams
    publisher = ClientDownloadPublisher()
    subscriber = ClientDownloadSubscriber(owner, filename, publisher, complete, automated)
    channel = client.request_channel(create_payload(data), publisher, None)
    channel.initial_request_n(MAX_REQUEST_NUMBER)
    channel.subscribe(subscriber)

    start_time = time.time()
    # wait until the server is done sending data
    # The QUIC implementation freezes here due to the header bug
    await complete.wait()
    end_time = time.time()

    # if successful, note the download latency (in seconds) and throughput (in chunks)
    if not subscriber.error and subscriber.num_chunks != 0:
        print(FILE_DOWNLOADED.format(filename))
        bench = Benchmark(data[SIZE], subscriber.num_chunks, end_time - start_time)
        print(bench)

    return bench


#
# grant_access
#
# PURPOSE: Grants a user access to one of the
# current user's files.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def grant_access(client: RSocketClient, data):
    payload = create_payload(data)
    try:
        result = await client.request_response(payload)
        if parse_payload(result)[STATUS] == SUCCESS:
            print(ACCESS_GRANTED.format(data[SUBJECT]))
        else:
            print(GRANT_ERROR)
    except Exception as e:
        logging.info(e)
        print(DATA_ERROR)


#
# revoke_access
#
# PURPOSE: Revokes access for a user from one of the
# current user's files.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def revoke_access(client: RSocketClient, data):
    payload = create_payload(data)
    try:
        result = await client.request_response(payload)
        if parse_payload(result)[STATUS] == SUCCESS:
            print(ACCESS_REVOKED.format(data[SUBJECT]))
        else:
            print(REVOKE_ERROR)
    except Exception as e:
        logging.info(e)
        print(DATA_ERROR)


#
# delete_file
#
# PURPOSE: Deletes one of the current user's
# files from the server.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def delete_file(client: RSocketClient, data):
    payload = create_payload(data)
    try:
        result = await client.request_response(payload)
        if parse_payload(result)[STATUS] == SUCCESS:
            print(FILE_DELETED)
        else:
            print(DELETE_ERROR)
    except Exception as e:
        logging.info(e)
        print(DELETE_ERROR)


#
# automate_download
#
# PURPOSE: Given a number n representing the number of
# automated downloads, this downloads a file n times,
# records the throughput and latency for each and then
# outputs the results to a CSV file.
# 
# PARAMS:
# client -  The socket used to send/receive data
# data - the data to be sent to the server
#
async def automate_download(client: RSocketClient, data):
    num_tests = int(data[NUM_TESTS])
    test_name = sanitize_alphanumeric(data[EXPERIMENT_NAME])
    tests_done = 0

    try:
        # set the download command
        data[MESSAGE] = Command.DOWNLOAD
        experiment = Experiment(test_name)
        print(RUNNING_TESTS)

        if experiment.error is None:
            # run the tests and save the results
            while(tests_done < num_tests):
              bench = await download_file(client, data, True)
              if bench != None:
                  experiment.add_entry(bench)
                  tests_done = tests_done + 1
                  logging.info(TEST_COMPLETED.format(tests_done))

            experiment.save_to_csv()
        else:
            print(AUTOMATE_ERROR)
    except Exception as e:
        experiment = None
