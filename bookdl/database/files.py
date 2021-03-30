import re
from bookdl.database import BookdlDB
from bson.objectid import ObjectId


class BookdlFiles:
    def __init__(self):
        """
        MegaFiles is the mongo collection that holds the documents for the files that are uploaded via the bot.

        Functions:
            insert_new_files: save new documents to the collection that contains details of the new files that are
            uploaded.
            count_files_by_url: count and returns the number of documents for the file with the same url.
            get_files_by_url: returns the documents for the files with a given url.
            get_file_by_file_id: returns the document for the file with the given telegram file_id.
            get_file_by_file_name: returns the documents for the files with the given file name.
        """
        self.files_collection = BookdlDB().db['TestFiles']

    async def insert_new_files(self, title: str, file_name: str, msg_id: int, chat_id: int,
                               md5: str, file_type: str, coverurl: str, file_id: str):
        self.files_collection.insert_one({
            "title": title,
            "file_name": file_name,
            "msg_id": msg_id,
            "chat_id": chat_id,
            "md5": md5,
            "file_type": file_type,
            "coverurl": coverurl,
            "file_id": file_id
        })

    async def count_files_by_md5(self, md5: str):
        return self.files_collection.count({"md5": md5})

    async def get_file_by_md5(self, md5: str):
        return self.files_collection.find_one({"md5": md5})

    async def get_file_by_mongo_id(self, file_id: str):
        return self.files_collection.find_one({"_id": ObjectId(file_id)})

    async def get_file_by_name(self, file_name: str, row_limit: int):
        return self.files_collection.find({
            "title":
            re.compile(file_name, re.IGNORECASE)
        }).limit(row_limit)
