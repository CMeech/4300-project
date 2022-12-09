import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
from reactivestreams.subscription import Subscription
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from rsocket.payload import Payload
from project_source.common.constants import CHUNK_CAP, CLIENT_MODULE, COMPLETE, ENCODE_TYPE, FILENAME_TEMPLATE, FILES_DIR, PROJECT_SRC, WRITE_BYTES
from project_source.common.helpers import create_payload, parse_byte_payload, parse_payload

from project_source.common.messages import CHUNK_RECEIVED, DOWNLOADING, FILE_UPLOADED, SENDING_PENDING


class ClientUploadPublisher(DefaultPublisher):
        def upload_bytes(self, value):
            self._subscriber.on_next(value)

        def error(self, exception: Exception):
            self._subscriber.on_error(exception)

        def complete(self):
            print(SENDING_PENDING)
            self._subscriber.on_complete()


# Used to receive messages from the server indicatating ready or complete.
class ClientUploadSubscriber(DefaultSubscriber):
    def __init__(self, established_event: asyncio.Event, complete_event: asyncio.Event):
        self.established_event = established_event
        self.complete_event = complete_event
        self.error = None


    def on_error(self, exception: Exception):
        print(exception)
        self.error = exception
        self.subscription.cancel()
        self.established_event.set()
        self.complete_event.set()


    def on_next(self, value: bytes, is_complete=False):
        # this is how we indicate the server is ready to receive
        self.established_event.set()
        if is_complete:
            self.complete_event.set()


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.complete_event.set()


# Indicates to the server that we are ready for downloading
class ClientDownloadPublisher(DefaultPublisher):
    def begin(self, value: Payload):
        self._subscriber.on_next(value)


    def error(self, exception: Exception):
        self._subscriber.on_error(exception)


    def complete(self):
        self._subscriber.on_complete()


# Stores the downloaded bytes
class ClientDownloadSubscriber(DefaultSubscriber):
    def __init__(self, owner, filename, publisher, complete_event: asyncio.Event, automated: bool):
        self.completed = False
        self.error = None
        self.error_flag: bool = False
        self.file_writer = None
        self.automated: bool = automated
        self.num_chunks: int = 0
        self.subscription: Optional[Subscription] = None
        self.publisher: ClientDownloadPublisher = publisher
        self.complete_event: asyncio.Event = complete_event
        self.filename: str = filename
        self.owner: str = owner
        try:
            root_path = Path(os.getcwd()).resolve().parent
            file_path = os.path.join(root_path, PROJECT_SRC, CLIENT_MODULE, FILES_DIR, FILENAME_TEMPLATE.format(owner, filename))
            self.file_writer = open(file_path, WRITE_BYTES)
            print(DOWNLOADING)
        except OSError as ose:
            self.error = ose
            self.file_writer = None
        except Exception as e:
            self.file_writer = None
            self.error = e


    def on_next(self, value: Payload, is_complete=False):
        if is_complete:
            self.on_complete()
            return
        if self.error == None:
            if value:
                try:
                    if not self.completed:
                        data = parse_byte_payload(value)
                        logging.info(CHUNK_RECEIVED.format(data))
                        # for automated tests, we don't want the I/O to affect the benchmark times
                        if not self.automated:
                            self.file_writer.write(data)
                        self.num_chunks = self.num_chunks + 1
                        if self.num_chunks >= CHUNK_CAP:
                            self.on_complete()
                except Exception as e:
                    self.on_error(e)
            else:
                # if we get an empty request, we have received OK from the server
                self.publisher.begin(create_payload({}))
        else:
            self.on_error(self.error)


    def on_error(self, exception: Exception):
        self.error_flag = True
        logging.error(exception)
        print(exception)
        if self.file_writer:
            self.file_writer.close()
        self.complete_event.set()
        self.publisher.error(exception)


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.completed = True
        self.file_writer.close()
        self.publisher.complete()
        self.complete_event.set()
