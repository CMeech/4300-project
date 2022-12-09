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
    def list_files(self, username: str):
        return list_files(username)


    def create_acl_entry(self, filename: str, owner: str, subject: str) -> str:
        if has_access(owner, subject, filename):
            return True
        else:
            if file_exists(owner, filename):
                grant_access(owner, subject, filename)
                return True
            else:
                return False


    def delete_acl_entry(self, filename: str, owner: str, subject: str) -> str:
        if has_access(owner, subject, filename):
            revoke_access(owner, subject, filename)


    def has_access(self, filename: str, owner: str, subject: str) -> bool:
        return has_access(owner, subject, filename)


    def create_file(self, owner :str, filename: str) -> bool:
        create_file(owner, filename)
        grant_access(owner, owner, filename)


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

