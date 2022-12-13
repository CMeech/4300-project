import asyncio
import unittest

from project_source.client_module.client_streams import ClientDownloadPublisher, ClientDownloadSubscriber, ClientUploadSubscriber
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from project_source.common.constants import CHUNK_CAP, ENCODE_TYPE, LARGE_CHUNK

from project_source.common.helpers import create_byte_payload
from project_source.server_module.server_streams import ServerDownloadSubscriber, ServerUploadSubscriber


class MockPublisher(DefaultPublisher):
    def __init__(self):
        self.error_occurred = False
        self.started = False
        self.completed = False

    def upload_bytes(self, value, complete=False):
        pass
    
    def error(self, error):
        self.error_occurred = True
    
    def complete(self):
        self.completed = True


class MockFileService():
    def __init__(self):
        self.created = False
        self.deleted = False

    def create_file(self, owner, filename):
        self.created = True
    
    def delete_file(self, owner, filename):
        self.deleted = True
    
    def has_access(self, filename, owner, user):
        if user == "another_user":
            return True
        else:
            return False


class TestServerStreams(unittest.TestCase):

    def test_receive_file_from_client(self):
        try:
            publisher = MockPublisher()
            file_service = MockFileService()
            subscriber = ServerUploadSubscriber(
                "test_user",
                "file.txt",
                publisher,
                file_service
            )
            # ensure proper construction
            self.assertFalse(publisher.completed)
            self.assertIsNone(subscriber.error)
            self.assertTrue(file_service.created)

            # receiving data, should not result in an error
            subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)))
            self.assertIsNone(subscriber.error)

            # complete the send, should not result in an error
            subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)), True)
            self.assertTrue(publisher.completed)

        except Exception as e:
            self.fail()
    

    def test_receive_file_from_client_error(self):
        try:
            publisher = MockPublisher()
            file_service = MockFileService()
            subscriber = ServerUploadSubscriber(
                "test_user",
                "file.txt",
                publisher,
                file_service
            )
            # ensure proper construction
            self.assertFalse(publisher.completed)
            self.assertIsNone(subscriber.error)
            self.assertTrue(file_service.created)

            # receive some data
            subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)))
            self.assertIsNone(subscriber.error)

            # signal an error has occured. No exceptions should be caught here.
            # server should delete any saved data
            subscriber.on_next("test")
            self.assertTrue(file_service.delete_file)
            self.assertTrue(publisher.error_occurred)

        except Exception as e:
            self.fail()


    def test_send_file_to_client(self):
        try:
            publisher = MockPublisher()
            file_service = MockFileService()
            subscriber = ServerDownloadSubscriber(
                "another_user",
                "test_user",
                "file.txt",
                publisher,
                LARGE_CHUNK,
                file_service
            )
            # ensure proper construction
            self.assertFalse(publisher.completed)
            self.assertIsNone(subscriber.error)

            # start the sending of data
            subscriber.on_next(None)
            self.assertIsNone(subscriber.error)
            self.assertTrue(publisher.completed)

            subscriber.on_complete()

        except Exception as e:
            self.fail()
    

    def test_send_file_to_client_no_access(self):
        try:
            publisher = MockPublisher()
            file_service = MockFileService()
            subscriber = ServerDownloadSubscriber(
                "user_no_access",
                "test_user",
                "file.txt",
                publisher,
                LARGE_CHUNK,
                file_service
            )
            # ensure proper construction
            self.assertFalse(publisher.completed)
            self.assertIsNotNone(subscriber.error)

            subscriber.on_next(None)
            self.assertTrue(publisher.error)

        except Exception as e:
            self.fail()


    def test_send_file_to_client_data_error(self):
        try:
            publisher = MockPublisher()
            file_service = MockFileService()
            subscriber = ServerDownloadSubscriber(
                "user_no_access",
                "test_user",
                "file.txt",
                publisher,
                -1,
                file_service
            )
            self.assertFalse(publisher.completed)
            self.assertIsNotNone(subscriber.error)

            subscriber.on_next(None)
            self.assertTrue(publisher.error)

        except Exception as e:
            self.fail()
