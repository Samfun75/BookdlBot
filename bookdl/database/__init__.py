"""Bookdl is the mongo DB connection for the application."""

import sys
import pymongo
import logging
from bookdl.common import Common
from urllib.parse import quote


class BookdlDB:
    """Database init"""

    def __init__(self):

        if Common().db_username is not None and Common().db_password is not None and Common().db_host is not None:
            connection_string = f"{Common().db_type}://{Common().db_username}:{quote(Common().db_password)}@{Common().db_host}/?retryWrites=true&w=majority"

            self.db_client = pymongo.MongoClient(connection_string)
            self.db = self.db_client[Common().db_name]
        else:
            logging.info(
                "No Database Credentials or Database host Detected. \n Bot can't work without DB \n Exiting Bot...")
            sys.exit()
