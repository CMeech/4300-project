#
# server_handler.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements the class that parses
# client messages and determines what to do
# afterwards.
#
from typing import Optional, Tuple


from reactivestreams.publisher import Publisher
from reactivestreams.subscriber import Subscriber
from rsocket.helpers import create_future
from rsocket.local_typing import Awaitable
from rsocket.payload import Payload
from rsocket.request_handler import BaseRequestHandler
from project_source.common.commands import Command
from project_source.common.constants import (
    ENCODE_TYPE,
    ERROR,
    FILENAME,
    MESSAGE,
    OWNER,
    SIZE,
    SUBJECT,
    SUCCESS,
    USERNAME
)
from project_source.common.helpers import create_payload, parse_payload
from project_source.common.messages import DATA_ERROR, INVALID_MESSAGE

from project_source.common.response_keys import CLIENT_LIST, FILE_LIST, STATUS
from project_source.database.file_service import FileService
from project_source.database.sanitize import sanitize_alphanumeric
from project_source.database.user_service import UserService
from project_source.server_module.server_streams import (
    ServerDownloadPublisher,
    ServerDownloadSubscriber,
    ServerUploadSubscriber,
    ServerUploadPublisher
)


#
# ServerHandler
#
# PURPOSE: Implements the server handling logic.
#
class ServerHandler(BaseRequestHandler):
    def __init__(self, file_service=None, user_service=None):
        if file_service == None and user_service == None:
            self.file_service = FileService()
            self.user_service = UserService()
        else:
            # this will let us inject a file service so we can test
            self.file_service = file_service
            self.user_service = user_service


    #
    # request_response
    #
    # PURPOSE: Handles requests that require an immediate response.
    # Sends a single message back to the client.
    #
    async def request_response(self, payload: Payload) -> Awaitable[Payload]:
        try:
            data_dict = parse_payload(payload)
            message_type = data_dict[MESSAGE]

            if message_type == Command.DELETE:
                message = self.delete_file(data_dict)

            elif message_type == Command.FILES:
                message = self.send_files_list(data_dict)

            elif message_type == Command.GRANT:
                message = self.grant_access(data_dict)

            elif message_type == Command.LIST:
                message = self.send_client_list()

            elif message_type == Command.REGISTER:
                message = self.register_user(data_dict)

            elif message_type == Command.REVOKE:
                message = self.revoke_access(data_dict)
            else:
                message = {
                    STATUS: ERROR
                }
                print(INVALID_MESSAGE)

        except Exception:
            message = {
                STATUS: ERROR
            }
            print(DATA_ERROR)
        
        return create_future(create_payload(message))
    

    #
    # request_channel
    #
    # PURPOSE: Given a request for channel establishment, sets up
    # two one-way streams (using a Publisher and a Subscriber) for
    # communication with the client.
    #
    async def request_channel(self, payload: Payload) -> Tuple[Optional[Publisher], Optional[Subscriber]]:
        data_dict = parse_payload(payload)
        message_type = data_dict[MESSAGE]
        
        if message_type == Command.UPLOAD:
            return self.get_file_from_client(data_dict)
        elif message_type == Command.DOWNLOAD:
            return self.send_file_to_client(data_dict)


    #
    # get_file_from_client
    #
    # PURPOSE: Sets up streams for receiving a file from the
    # client.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def get_file_from_client(self, data) -> Tuple[Optional[Publisher], Optional[Subscriber]]:
        publisher = ServerUploadPublisher()
        subscriber = ServerUploadSubscriber(data[OWNER], data[FILENAME], publisher, self.file_service)
        return (publisher, subscriber)


    #
    # send_file_to_client
    #
    # PURPOSE: Sets up the streams required for sending
    # a file to a client.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def send_file_to_client(self, data) -> Tuple[Optional[Publisher], Optional[Subscriber]]:
        publisher = ServerDownloadPublisher()
        subscriber = ServerDownloadSubscriber(
            data[SUBJECT],
            data[OWNER],
            data[FILENAME],
            publisher,
            data[SIZE],
            self.file_service
        )
        return (publisher, subscriber)


    #
    # send_client_list
    #
    # PURPOSE: Sends the list of clients in the system
    # to the client.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def send_client_list(self):
        clients = self.user_service.get_client_list()
        return {
            CLIENT_LIST: clients,
            STATUS: SUCCESS
        }


    #
    # register_user
    #
    # PURPOSE: Registers the client and returns a
    # status message.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def register_user(self, data):
        username = sanitize_alphanumeric(data[USERNAME])
        self.user_service.get_or_create(username)
        return {
            STATUS: SUCCESS
        }


    #
    # send_files_list
    #
    # PURPOSE: Responds with the list of files that
    # the client has access to.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def send_files_list(self, data):
        username = data[USERNAME]
        files = self.file_service.list_files(username)
        return {
            FILE_LIST: files,
            STATUS: SUCCESS
        }


    #
    # grant_access
    #
    # PURPOSE: Grants the client access to a specific file.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def grant_access(self, data):
        status = SUCCESS
        filename = data[FILENAME]
        owner = data[OWNER]
        subject = data[SUBJECT]


        if not self.file_service.create_acl_entry(filename, owner, subject):
            status = ERROR
        
        return {
            STATUS: status
        }


    #
    # revoke_access
    #
    # PURPOSE: Revokes the client access from a specific file.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def revoke_access(self, data):
        filename = data[FILENAME]
        owner = data[OWNER]
        subject = data[SUBJECT]

        self.file_service.delete_acl_entry(filename, owner, subject)
        
        return {
            STATUS: SUCCESS
        }


    #
    # delete_file
    #
    # PURPOSE: Deletes a client's file.
    #
    # PARAM:
    # data - the data from the client's request
    #
    def delete_file(self, data):
        filename = data[FILENAME]
        owner = data[OWNER]

        success = self.file_service.delete_file(owner, filename)
        
        return {
            STATUS: SUCCESS if success else ERROR
        }
