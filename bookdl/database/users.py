from bookdl.database import BookdlDB


class BookdlUsers:
    def __init__(self):
        """
        BookdlUsers is the mongo collection for the documents that holds the details of the users.

        Functions:
            insert_user: insert new documents, that contains the details of the new users who started using the bot.

            get_user: return the document that contains the user_id for the the given telegram user id.

        """
        self.user_collection = BookdlDB().db["Users"]

    async def insert_user(self, user_id: int):
        if self.user_collection.count_documents({"user_id": user_id}) > 0:
            return False
        else:
            self.user_collection.insert_one(
                {
                    "user_id": user_id,
                    "downloaded": [],
                }
            )

    async def get_user(self, user_id: int):
        return self.user_collection.find_one({"user_id": user_id})
