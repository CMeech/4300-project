import asyncio
from typing import Optional, Tuple
from unittest import IsolatedAsyncioTestCase
from reactivestreams.publisher import Publisher
from reactivestreams.subscriber import Subscriber
from project_source.common.commands import Command
from project_source.common.constants import ERROR, FILENAME, LARGE_CHUNK, MESSAGE, OWNER, SIZE, SUBJECT, SUCCESS, USERNAME
from project_source.common.helpers import create_payload, parse_payload
from project_source.common.response_keys import CLIENT_LIST, FILE_LIST, STATUS

from project_source.server_module.server_handler import ServerHandler


class MockFileService():

    def delete_file(self, owner, filename):
        return True
    
    def delete_acl_entry(self, filename, owner, subject):
        return
    
    def create_acl_entry(self, filename, owner, subject):
        return True
    
    def list_files(self, username):
        return [
            {
                FILENAME: "file.txt",
                OWNER: "owner"
            },
            {
                FILENAME: "file2.txt",
                OWNER: "owner"
            }
        ]


class MockUserService():
    def get_or_create(self, username):
        pass

    def get_client_list(self):
        return ["user1", "user2"]


class Test(IsolatedAsyncioTestCase):

    async def test_delete_file(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.DELETE,
            FILENAME: "test.txt",
            OWNER: "test_user"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[STATUS], SUCCESS)
    

    async def test_revoke(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.REVOKE,
            FILENAME: "test.txt",
            OWNER: "test_user",
            SUBJECT: "subject"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[STATUS], SUCCESS)


    async def test_grant(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.GRANT,
            FILENAME: "test.txt",
            OWNER: "test_user",
            SUBJECT: "subject"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[STATUS], SUCCESS)
    

    async def test_get_files(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.FILES,
            USERNAME: "owner"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[FILE_LIST], [
            {
                FILENAME: "file.txt",
                OWNER: "owner"
            },
            {
                FILENAME: "file2.txt",
                OWNER: "owner"
            }
        ])
        self.assertEqual(response[STATUS], SUCCESS)


    async def test_register(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.REGISTER,
            USERNAME: "some_user"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[STATUS], SUCCESS)

    
    async def test_get_client_list(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.LIST
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[CLIENT_LIST], ["user1", "user2"])
        self.assertEqual(response[STATUS], SUCCESS)


    async def test_invalid_message(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: "jibberish"
        }
        result: asyncio.Future = await handler.request_response(create_payload(data))
        response = parse_payload(result.result())
        self.assertEqual(response[STATUS], ERROR)


    async def test_upload_channel(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.UPLOAD,
            OWNER: "user1",
            FILENAME: "file.txt",
        }
        result: Tuple[Optional[Publisher], Optional[Subscriber]] = await handler.request_channel(create_payload(data))
        self.assertEqual(result[1].filename, "file.txt")
        self.assertEqual(result[1].owner, "user1")
    

    async def test_download_channel(self):
        file_service = MockFileService()
        user_service = MockUserService()
        handler = ServerHandler(file_service, user_service)
        data = {
            MESSAGE: Command.DOWNLOAD,
            OWNER: "owner",
            SUBJECT: "user1",
            FILENAME: "file.txt",
            SIZE: LARGE_CHUNK
        }
        result: Tuple[Optional[Publisher], Optional[Subscriber]] = await handler.request_channel(create_payload(data))
        self.assertEqual(result[1].filename, "file.txt")
        self.assertEqual(result[1].user, "user1")
        self.assertEqual(result[1].chunk_size, LARGE_CHUNK)
        self.assertEqual(result[1].owner, "owner")
        