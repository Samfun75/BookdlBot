from ...telegram import Common
from bookdl.database.files import BookdlFiles
from bookdl.database.users import BookdlUsers
from pyrogram import filters, emoji, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: Client, m: Message):
    await BookdlUsers().insert_user(m.from_user.id)
    if len(m.command) > 1:
        if m.command[1].split("-")[0] == 'plf':
            file_id = m.command[1].split("-", 1)[1]
            file_details = await BookdlFiles().get_file_by_file_id(file_id)

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
            ])
        )


@Client.on_message(filters.command("help", prefixes=["/"]))
async def help_message_handler(c: Client, m: Message):
    await m.reply_text(
        text="Hello! I'm **@BookdlBot.**\n\n"
        "Here are the commands you can use:\n"
        "/start : Start the bot.\n"
        "/help: Show this helpful message")


@Client.on_message(group=-1)
async def stop_user_from_doing_anything(_, message: Message):
    allowed_users = Common().allowed_users
    if allowed_users and message.from_user:
        if message.from_user.id not in allowed_users:
            message.stop_propagation()
        else:
            message.continue_propagation()
    else:
        if message.from_user:
            message.continue_propagation()
        else:
            message.stop_propagation()
