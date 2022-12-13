from typing import Union
from unittest import IsolatedAsyncioTestCase

from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from rsocket.payload import Payload
from project_source.client_module.client_streams import ClientDownloadSubscriber, ClientUploadSubscriber
from project_source.client_module.client_task import do_command
from project_source.common.commands import Command
from project_source.common.constants import EXPERIMENT_NAME, FILENAME, LARGE_CHUNK, MESSAGE, NUM_TESTS, OWNER, SIZE, SUBJECT, SUCCESS, USERNAME
from project_source.common.helpers import create_payload, parse_payload
from project_source.common.response_keys import CLIENT_LIST, FILE_LIST, STATUS

class MockSubscriber(DefaultSubscriber):
    pass

class MockChannelRequester():
    def __init__(self):
        pass

    def initial_request_n(self, n: int):
        pass
    
    def subscribe(self, subscriber: Union[ClientDownloadSubscriber, ClientUploadSubscriber]):
        subscriber.on_complete()
        if hasattr(subscriber, "established_event"):
            subscriber.established_event.set()
        subscriber.num_chunks = 100
        subscriber.error_flag = False

class MockRSocketClient():
    def __init__(self):
        pass
    
    def request_channel(self, data, publisher: DefaultPublisher, complete = None):
        publisher.subscribe(MockSubscriber())
        return MockChannelRequester()
    
    async def request_response(self, payload: Payload):
        data = parse_payload(payload)
        message_type = data[MESSAGE]
        response = None

        if message_type == Command.DELETE:
            response = {
                STATUS: SUCCESS
            }

        elif message_type == Command.FILES:
            response = {
                STATUS: SUCCESS,
                FILE_LIST: [
                  {FILENAME: "test.txt", OWNER: "owner"}
                ]
            }

        elif message_type == Command.GRANT:
            response = {
                STATUS: SUCCESS
            }

        elif message_type == Command.LIST:
            response = {
                STATUS: SUCCESS,
                CLIENT_LIST: ["user1", "user2", "user3"]
            }

        elif message_type == Command.REGISTER:
            response = {
                STATUS: SUCCESS
            }

        elif message_type == Command.REVOKE:
            response = {
                STATUS: SUCCESS
            }

        return create_payload(response)


class Test(IsolatedAsyncioTestCase):

    # nothing to really assert here
    # but we can look at the output for exceptions
    # if there are any, then some test failed.
    def setUp(self):
        self.client = MockRSocketClient()

    async def test_download(self):
        data = {
            MESSAGE: Command.DOWNLOAD,
            FILENAME: "small.txt",
            OWNER: "owner",
            SIZE: LARGE_CHUNK
        }
        await do_command(self.client, data)

    async def test_automate(self):
        data = {
            MESSAGE: Command.AUTOMATE,
            EXPERIMENT_NAME: "test_exp",
            NUM_TESTS: "10",
            FILENAME: "small.txt",
            OWNER: "owner",
            SIZE: LARGE_CHUNK
        }
        await do_command(self.client, data)

    async def test_upload(self):
        data = {
            MESSAGE: Command.UPLOAD,
            FILENAME: "small.txt",
            OWNER: "owner"
        }
        await do_command(self.client, data)

    async def test_delete(self):
        data = {
            MESSAGE: Command.DELETE,
            FILENAME: "small.txt",
            OWNER: "owner"
        }
        await do_command(self.client, data)

    async def test_files(self):
        data = {
            MESSAGE: Command.FILES,
            USERNAME: ""
        }
        await do_command(self.client, data)
    
    async def test_grant(self):
        data = {
            MESSAGE: Command.GRANT,
            SUBJECT: "user1",
            FILENAME: "file.txt",
            OWNER: "user2"
        }
        await do_command(self.client, data)

    async def test_list(self):
        data = {
            MESSAGE: Command.LIST
        }
        await do_command(self.client, data)
    
    async def test_register(self):
        data = {
            MESSAGE: Command.REGISTER,
            USERNAME: "user"
        }
        await do_command(self.client, data)
    
    async def test_revoke(self):
        data = {
            MESSAGE: Command.REVOKE,
            SUBJECT: "user1",
            FILENAME: "file.txt",
            OWNER: "user2"
        }
        await do_command(self.client, data)
