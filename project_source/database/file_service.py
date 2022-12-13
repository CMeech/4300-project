#
# file_service.py
#
# AUTHOR: Cassius Meeches
#
# PURPOSE: Implements a service for interacting with file
# related data in the database.
#
import logging
import os
from pathlib import Path
from project_source.common.constants import FILENAME_TEMPLATE, FILES_DIR, PROJECT_SRC, SERVER_MODULE
from project_source.database.queries import (
    create_file,
    delete_file,
    file_exists,
    grant_access,
    has_access,
    list_files,
    revoke_access
)


class FileService():

    #
    # list_files
    #
    # PURPOSE: Retrieves the files that the given user
    # has access to
    # 
    # PARAMS:
    # username - the specified user
    #
    # Returns an array of objects that include filename and owner.
    #
    def list_files(self, username: str):
        return list_files(username)

    #
    # create_acl_entry
    #
    # PURPOSE: Creates an acl entry that gives the subject
    # access to the owner's file.
    #
    # PARAMS:
    # filename - the specified file
    # owner - the owner of the file
    # subject - the client being given access
    #
    # Returns a boolean indicating success.
    #
    def create_acl_entry(self, filename: str, owner: str, subject: str) -> bool:
        if has_access(owner, subject, filename):
            return True
        else:
            if file_exists(owner, filename):
                grant_access(owner, subject, filename)
                return True
            else:
                return False


    #
    # delete_acl_entry
    #
    # PURPOSE: Removes an acl entry that gives the subject
    # access to the owner's file.
    #
    # PARAMS:
    # filename - the specified file
    # owner - the owner of the file
    # subject - the client being revoked of access
    #
    # Returns a boolean indicating success.
    #
    def delete_acl_entry(self, filename: str, owner: str, subject: str) -> str:
        if has_access(owner, subject, filename):
            revoke_access(owner, subject, filename)


    #
    # has_access
    #
    # PURPOSE: Determined is the given subject has access to a file.
    #
    # PARAMS:
    # filename - the specified file
    # owner - the owner of the file
    # subject - the client being revoked of access
    #
    # Returns a boolean indicating if the subject has access.
    #
    def has_access(self, filename: str, owner: str, subject: str) -> bool:
        return has_access(owner, subject, filename)


    #
    # create_file
    #
    # PURPOSE: Stores information about a newly created file.
    #
    # PARAMS:
    # filename - the name of the new file
    # owner - the owner of the file
    #
    # Returns a boolean indicating if the subject has access.
    #
    def create_file(self, owner :str, filename: str):
        create_file(owner, filename)
        grant_access(owner, owner, filename)


    #
    # delete_file
    #
    # PURPOSE: Removes information of a deleted file.
    #
    # PARAMS:
    # filename - the name of the deleted file
    # owner - the owner of the file
    #
    # Returns a boolean indicating if the subject has access.
    #
    def delete_file(self, owner:str , filename: str) -> bool:
        success = True

        # delete the file records
        try:
            delete_file(owner, filename)
        except Exception as e:
            logging.info(e)
            success = False
        
        # delelte the actual data
        if success:
            try:
                root_path = Path(os.getcwd()).resolve().parent
                file_path = os.path.join(
                    root_path,
                    PROJECT_SRC,
                    SERVER_MODULE,
                    FILES_DIR,
                    FILENAME_TEMPLATE.format(owner, filename)
                )
                os.unlink(file_path)
            except Exception as e:
                # reverse the effects on error
                self.create_file(owner, filename)
                logging.info(e)
                success = False
        
        return success
