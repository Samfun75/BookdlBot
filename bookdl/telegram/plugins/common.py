from ...telegram import Common
from bookdl.database.files import BookdlFiles
from bookdl.database.users import BookdlUsers
from pyrogram import filters, emoji, Client
from pyrogram.types import Message, InlineQuery, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: Client, m: Message):
    await BookdlUsers().insert_user(m.from_user.id)
    if len(m.command) > 1:
        if m.command[1].split("-")[0] == 'plf':
            mongo_id = m.command[1].split("-", 1)[1]
            file_details = await BookdlFiles().get_file_by_mongo_id(mongo_id)

            if file_details is not None:
                file_message = await c.get_messages(
                    chat_id=file_details['chat_id'],
                    message_ids=file_details['msg_id'])

                await m.reply_document(document=file_message.document.file_id)
    else:
        await m.reply_text(
            text=f"Hello! My name is **Bookdl Bot** {emoji.BOOKS} \n"
            "I can help you download books try typing in inline mode",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f'Search {emoji.MAGNIFYING_GLASS_TILTED_LEFT}',
                        switch_inline_query_current_chat="")
                ],
                [
                    InlineKeyboardButton(
                        f'Search from downloaded {emoji.MAGNIFYING_GLASS_TILTED_LEFT}',
                        switch_inline_query_current_chat="dl: ")
                ]
            ]))


@Client.on_message(filters.command("help", prefixes=["/"]))
async def help_message_handler(c: Client, m: Message):
    await m.reply_text(
        text="Hello! I'm **BookdlBot.**\n"
        "Original bot [SamfunBookdlBot](https://t.me/SamfunBookdlbot)\n"
        "Source [Bookdlbot](https://github.com/Samfun75/BookdlBot)\n\n"
        "Here are the commands you can use:\n"
        "/start : Start the bot.\n"
        "/help: Show this helpful message\n\n"
        "You can also download books by sending the link if you have a book link from the following sites\n"
        "library.lol, libgen.lc, libgen.gs or b-ok.cc\n\n"
        "Or you can send the book's md5 like so\n"
        "MD5:a382109f7fdde3be5b2cb4f82d97443b\n\n"
        "If you send a document(book) or audio(audiobook) to the dustbin channel, the bot "
        "will save the document or audio to the database and it is available for search.\n\n"
        "Conversion to PDF from other ebook types is done using ConvertAPI",
        disable_web_page_preview=True)


@Client.on_message(group=-1)
async def stop_user_from_doing_anything(_, message: Message):
    allowed_users = Common().allowed_users
    if allowed_users:
        if message.chat.id in allowed_users or message.chat.id == Common(
        ).bot_dustbin:
            message.continue_propagation()
        else:
            message.stop_propagation()
    else:
        message.continue_propagation()


@Client.on_inline_query(group=-1)
async def stop_user_from_doing_anything_inline(_, iq: InlineQuery):
    allowed_users = Common().allowed_users
    if allowed_users and iq.from_user:
        if iq.from_user.id not in allowed_users:
            iq.stop_propagation()
        else:
            iq.continue_propagation()
    else:
        if iq.from_user:
            iq.continue_propagation()
        else:
            iq.stop_propagation()
