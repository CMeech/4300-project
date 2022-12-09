#
#
#

import logging
import os
from pathlib import Path
from typing import Optional
from reactivestreams.subscription import Subscription
from reactivestreams.subscriber import DefaultSubscriber
from reactivestreams.publisher import DefaultPublisher
from project_source.common.constants import (
    COMPLETE,
    ENCODE_TYPE,
    FILENAME_TEMPLATE,
    FILES_DIR,
    PROJECT_SRC,
    READ_BYTES,
    SERVER_MODULE,
    WRITE_BYTES
)
from project_source.common.helpers import create_byte_payload, parse_byte_payload, parse_payload

from project_source.common.messages import (
    ACCESS_DENIED,
    CHUNK_RECEIVED,
    CHUNK_SENT,
    DOWNLOAD_ERROR,
    FILE_CREATED,
    FILE_SENT,
    UPLOAD_ERROR
)
from project_source.database.file_service import FileService


class AccessDeniedException(Exception):
        pass


class ServerUploadPublisher(DefaultPublisher):
    def complete(self):
        self._subscriber.on_complete()


    def error(self, exception: Exception):
        self._subscriber.on_error(exception)


class ServerUploadSubscriber(DefaultSubscriber):
    def __init__(self, username, filename, publisher, file_service):
        self.error = None
        self.file_writer = None
        self.filename = filename
        self.owner = username
        self.subscription: Optional[Subscription] = None
        self.publisher: ServerUploadPublisher = publisher
        self.file_service : FileService = file_service
        # make sure the we can record the file in the database
        try:
            self.file_service.create_file(self.owner, self.filename)
            # get the file ready
            root_path = Path(os.getcwd()).resolve().parent
            file_path = os.path.join(root_path, PROJECT_SRC, SERVER_MODULE, FILES_DIR, FILENAME_TEMPLATE.format(username, filename))
            self.file_writer = open(file_path, WRITE_BYTES)
        except OSError as ose:
            self.error = ose
            self.file_writer = None
        except Exception as e:
            self.error = e
            self.file_writer = None


    def on_next(self, value: bytes, is_complete=False):
        if is_complete:
            self.on_complete()
            return
        if self.error == None:
            try:
                data = parse_byte_payload(value)
                logging.info(CHUNK_RECEIVED.format(data))
                self.file_writer.write(data)
            except Exception as e:
                self.on_error(e)
        else:
            self.on_error(self.error)


    def on_error(self, exception: Exception):
        message = UPLOAD_ERROR.format(self.filename, self.owner)
        print(message)
        if self.file_writer != None:
            self.file_writer.close()
        try:
            self.file_service.delete_file(self.owner, self.filename)
        except Exception as e:
            pass # can't do much here, stale data should hopefully be replaced
        logging.error(exception)
        self.publisher.error(RuntimeError(message))


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.file_writer.close()
        self.publisher.complete()
        print(FILE_CREATED.format(self.filename))


class ServerDownloadPublisher(DefaultPublisher):
    def complete(self):
        self._subscriber.on_complete()


    def upload_bytes(self, value, complete=False):
        self._subscriber.on_next(value, complete)


    def error(self, exception: Exception):
        self._subscriber.on_error(exception)


class ServerDownloadSubscriber(DefaultSubscriber):
    def __init__(self, user, owner, filename, publisher, chunk_size, file_service):
        self.chunk_size = chunk_size
        self.file_reader = None
        self.file_service: FileService = file_service
        self.error = None
        self.filename = filename
        self.owner = owner
        self.user = user
        self.subscription: Optional[Subscription] = None
        self.publisher: ServerDownloadPublisher = publisher

        # make sure we can read the file and that the user has access
        try:
            if self.file_service.has_access(self.filename, self.owner, self.user):
                root_path = Path(os.getcwd()).resolve().parent
                file_path = os.path.join(root_path, PROJECT_SRC, SERVER_MODULE, FILES_DIR, FILENAME_TEMPLATE.format(owner, filename))
                self.file_reader = open(file_path, READ_BYTES)
            else:
                self.error = AccessDeniedException()
        except OSError as ose:
            self.error = ose
            self.file_reader = None
        except Exception as e:
            self.error = e
            self.file_reader = None


    def on_next(self, value: bytes, is_complete=False):
        if is_complete:
            return
        if self.error == None:
            try:
                chunk = self.file_reader.read(self.chunk_size)
                while chunk:
                    logging.info(CHUNK_SENT.format(chunk))
                    self.publisher.upload_bytes(create_byte_payload(chunk))
                    chunk = self.file_reader.read(self.chunk_size)

                self.publisher.upload_bytes(create_byte_payload(COMPLETE.encode(ENCODE_TYPE)), True)

                self.publisher.complete()
            except Exception as e:
                self.on_error(e)
        else:
            self.on_error(self.error)


    def on_error(self, exception: Exception):
        message = ACCESS_DENIED if isinstance(exception, AccessDeniedException) else DOWNLOAD_ERROR.format(self.filename, self.owner)
        print(message)
        if self.file_reader != None:
            self.file_reader.close()
        logging.error(exception)
        self.publisher.error(RuntimeError(message))


    def on_subscribe(self, subscription: Subscription):
        self.subscription = subscription


    def on_complete(self):
        self.file_reader.close()
        self.publisher.complete()
        print(FILE_SENT.format(self.filename))
