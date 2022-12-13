#
# client_streams.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements the channel stream classes
# for uploading and downloading files on the client
# side.
#
# --- About RSocket streams ----
# on_next is the handler for application data messages.
# on_error is the handler for error messages.
# on_complete is the handler for complete messages.
#
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
from reactivestreams.subscription import Subscription
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from rsocket.payload import Payload
from project_source.common.constants import BEGIN, CHUNK_CAP, CLIENT_MODULE, FILENAME_TEMPLATE, FILES_DIR, MESSAGE, PROJECT_SRC, SUBSCRIPTION, WRITE_BYTES
from project_source.common.helpers import create_payload, parse_byte_payload

from project_source.common.messages import CHUNK_RECEIVED, DOWNLOADING, SENDING_PENDING


#
# ClientUploadPublisher
#
# PURPOSES: Pushes bytes of a file to the server
#
class ClientUploadPublisher(DefaultPublisher):
        def upload_bytes(self, value):
            self._subscriber.on_next(value)

        def error(self, exception: Exception):
            self._subscriber.on_error(exception)

        def complete(self):
            print(SENDING_PENDING)
            self._subscriber.on_complete()


#
# ClientUploadSubscriber
#
# PURPOSE: Receives messages from the server indicating
# if the server is ready to receive data or complete.
#
class ClientUploadSubscriber(DefaultSubscriber):
    def __init__(self, established_event: asyncio.Event, complete_event: asyncio.Event):
        # used by the client to check if data can be sent
        self.established_event = established_event
        self.complete_event = complete_event
        self.error = None


    def on_error(self, exception: Exception):
        print(exception)
        self.error = exception
        if hasattr(self, SUBSCRIPTION):
            self.subscription.cancel()
        self.established_event.set()
        self.complete_event.set()


    def on_next(self, value: bytes, is_complete=False):
        # this is how the server tells the client to send data.
        # we don't care what the server sends as long as we
        # get a non-error message back.
        self.established_event.set()
        if is_complete:
            self.complete_event.set()


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.complete_event.set()


#
# ClientDownloadPublisher
#
# PURPOSE: Indicates to the server that we are ready to
# receive data.
#
class ClientDownloadPublisher(DefaultPublisher):
    def begin(self, value: Payload):
        self._subscriber.on_next(value)


    def error(self, exception: Exception):
        self._subscriber.on_error(exception)


    def complete(self):
        self._subscriber.on_complete()


#
# ClientDownloadSubscriber
#
# PURPOSE: Receives data from the server and stores
# it in a file.
#
# PARAMS:
# automated - indicates if the we are running the download
#   for automated benchmarks. If so, no real data is written.
# owner - name of the file owner
# filename - name of the file tobe downloaded
# publisher - stream for sending data to the server
# complete_event - used to wait for complete message from the server
#
class ClientDownloadSubscriber(DefaultSubscriber):
    def __init__(self, owner, filename, publisher, complete_event: asyncio.Event, automated: bool):
        self.completed = False
        self.error = None
        self.file_writer = None
        self.automated: bool = automated
        self.num_chunks: int = 0
        self.subscription: Optional[Subscription] = None
        self.publisher: ClientDownloadPublisher = publisher
        self.complete_event: asyncio.Event = complete_event
        self.filename: str = filename
        self.owner: str = owner
        try:
            # try to open the flie, signal error if one occurs
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


    # this takes received data and writes it to the file.
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
                self.publisher.begin(create_payload({MESSAGE: BEGIN}))
        else:
            self.on_error(self.error)


    def on_error(self, exception: Exception):
        logging.error(exception)
        print(exception)
        if self.file_writer:
            self.file_writer.close()
        self.complete_event.set()
        self.error = exception
        self.publisher.error(exception)


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.completed = True
        self.file_writer.close()
        self.publisher.complete()
        self.complete_event.set()
