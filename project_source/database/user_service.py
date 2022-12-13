#
# user_service.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements a service for interacting with client
# related data in the database.
#
from project_source.database.queries import get_users, register_user, user_exists


class UserService():

    #
    # get_client_list
    #
    # PURPOSE: Retrieves the list of all clients registered
    # in the system.
    #
    # Returns an array containing all of the client's usernames.
    #
    def get_client_list(self):
        data = get_users()
        return data

    #
    # get_or_create
    #
    # PURPOSE: Creates a client if it doesn't exist.
    #
    def get_or_create(self, username):
        exists = user_exists(username)
        if not exists:
            register_user(username)