import asyncio
import unittest

from project_source.client_module.client_streams import ClientDownloadPublisher, ClientDownloadSubscriber, ClientUploadSubscriber
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from project_source.common.constants import BEGIN, CHUNK_CAP, ENCODE_TYPE, MESSAGE

from project_source.common.helpers import create_byte_payload, parse_payload

# used so we track the control flow
# the actual publishers just send data via socket
class MockClientDownloadPublisher(DefaultPublisher):
    def __init__(self):
        self.error_occurred = False
        self.started = False
        self.completed = False

    def begin(self, value):
        parsed = parse_payload(value)
        if parsed == {MESSAGE: BEGIN}:
            self.started = True
    
    def error(self, error):
        self.error_occurred = True
    
    def complete(self):
        self.completed = True


class TestClientStreams(unittest.TestCase):

    def test_download_file_from_server(self):
        try:
            complete = asyncio.Event()
            download_publisher = MockClientDownloadPublisher()
            download_publisher.subscribe(DefaultSubscriber())
            download_subscriber = ClientDownloadSubscriber(
                "test",
                "file.txt",
                download_publisher,
                complete,
                # set automated to true so no actual data is written
                True
            )
            # ensure proper construction
            self.assertFalse(download_publisher.completed)
            self.assertFalse(download_publisher.started)
            self.assertIsNone(download_subscriber.error)

            download_subscriber.on_next(None)
            self.assertFalse(download_publisher.completed)
            self.assertTrue(download_publisher.started)

            # send data until complettion
            for i in range(CHUNK_CAP+1):
                download_subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)))

            self.assertFalse(download_publisher.error_occurred)
            self.assertTrue(download_publisher.completed)
            self.assertTrue(complete.is_set())
            # the extra chunk should be ignored
            self.assertEqual(download_subscriber.num_chunks, CHUNK_CAP)

        except Exception as e:
            self.fail()


    def test_download_file_from_server_error(self):
        try:
            complete = asyncio.Event()
            download_publisher = MockClientDownloadPublisher()
            download_publisher.subscribe(DefaultSubscriber())
            download_subscriber = ClientDownloadSubscriber(
                "test",
                "file.txt",
                download_publisher,
                complete,
                # set automated to true so no actual data is written
                True
            )
            # ensure proper construction
            self.assertIsNone(download_subscriber.error)
            
            download_subscriber.on_next(None)
            self.assertTrue(download_publisher.started)

            # send some data, no errors should happen here, should not complete
            download_subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)))
            self.assertFalse(download_publisher.error_occurred)
            self.assertIsNone(download_subscriber.error)
            self.assertFalse(complete.is_set())
            self.assertEqual(download_subscriber.num_chunks, 1)

            # signal an error has occured. No exceptions should be caught here.
            download_subscriber.on_next("test")
            self.assertTrue(download_publisher.error_occurred)
            self.assertFalse(download_publisher.completed)
            self.assertTrue(complete.is_set())

            # receiving more data should do nothing, will log the error again.
            # number of chunks should not change
            download_subscriber.on_next(create_byte_payload("test".encode(ENCODE_TYPE)))
            self.assertEqual(download_subscriber.num_chunks, 1)


        except Exception as e:
            self.fail()


    def test_upload_file_to_server(self):
        try:
            established = asyncio.Event()
            complete = asyncio.Event()
            upload_subscriber = ClientUploadSubscriber(
                established,
                complete
            )

            # indicates that the server is ready
            upload_subscriber.on_next(None)
            self.assertTrue(established.is_set())
            self.assertFalse(complete.is_set())

            # indicate that we are done sending
            upload_subscriber.on_complete()
            self.assertTrue(established.is_set())
            self.assertTrue(complete.is_set())

        except Exception as e:
            self.fail()


    def test_upload_file_to_server_error(self):
        try:
            established = asyncio.Event()
            complete = asyncio.Event()
            upload_subscriber = ClientUploadSubscriber(
                established,
                complete
            )

            # indicates an error occurred, stop blocking
            upload_subscriber.on_error(Exception("some error occurred"))
            self.assertTrue(established.is_set())
            self.assertTrue(complete.is_set())

        except Exception as e:
            self.fail()
