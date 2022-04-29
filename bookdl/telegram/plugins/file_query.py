import asyncio
from pyrogram import emoji
from pyrogram import Client
from ..utils import filters
from libgenesis import Libgen
from ...telegram import Common
from bookdl.database.files import BookdlFiles
from pyrogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, \
     InlineQueryResultCachedDocument


@Client.on_inline_query()
async def inline_query_handler(c: Client, iq: InlineQuery):
    q = iq.query.strip()
    res = []
    if len(q) < 2:
        await iq.answer(
            results=[],
            switch_pm_text='You must enter at least 2 characters to search',
            switch_pm_parameter="okay",
        )
        return
    if q.startswith('dl:'):
        q = q.split(':')[1].strip()
        q_res_data = await BookdlFiles().get_file_by_name(q, 50)
        if q_res_data:
            for file in q_res_data:
                res.append(
                    InlineQueryResultCachedDocument(
                        id=str(file['_id']),
                        document_file_id=file['file_id'],
                        caption=file['title'],
                        title=file['title'],
                        description=f"File Name: {file['file_name']}\n"
                        f"File Type: {file['file_type']}",
                    ))
    else:
        if q:
            result = await Libgen(result_limit=50
                                  ).search(query=q,
                                           return_fields=[
                                               'title', 'pages', 'language',
                                               'publisher', 'year', 'author',
                                               'extension', 'coverurl',
                                               'volumeinfo', 'mirrors', 'md5'
                                           ])
            if result is not None:
                for item in result:
                    res.append(
                        InlineQueryResultArticle(
                            title=result[item]['title'],
                            description=f"Author: {result[item]['author']}\n"
                            f"Volume: {result[item]['volumeinfo']}   Year: {result[item]['year']}  Pages: {result[item]['pages']}\n"
                            f"Language: {result[item]['language']}  Extension: {result[item]['extension']}\n"
                            f"Publisher: {result[item]['publisher']}\n",
                            thumb_url="https://cdn3.iconfinder.com/data/icons/"
                            "education-vol-1-34/512/15_File_files_office-256.png"
                            if result[item]['coverurl'] is None else
                            result[item]['coverurl'],
                            input_message_content=InputTextMessageContent(
                                message_text=f"MD5: {result[item]['md5']}\n"
                                f"Title: **{result[item]['title']}**\n"
                                f"Author: **{result[item]['author']}**"),
                            reply_markup=None))

    if res:
        await iq.answer(results=res, cache_time=60, is_personal=False)
    else:
        await iq.answer(
            results=[],
            cache_time=7,
            switch_pm_text=f'{emoji.CROSS_MARK} No results for "{q}"',
            switch_pm_parameter="okay",
        )


@Client.on_message(filters.chat(Common().bot_dustbin) &
                   (filters.document | filters.audio),
                   group=0)
async def manually_save_to_db(c: Client, m: Message):
    if m.audio is not None:
        await BookdlFiles().insert_new_files(title=m.audio.title,
                                             file_name=m.audio.file_name,
                                             msg_id=m.id,
                                             chat_id=m.chat.id,
                                             md5='md5',
                                             file_type=m.audio.mime_type,
                                             coverurl='',
                                             file_id=m.audio.file_id)
        ack_msg = await m.reply_text(
            text=f'**{m.audio.file_name}** has been added to DB.', quote=True)
    else:
        await BookdlFiles().insert_new_files(title=m.document.file_name,
                                             file_name=m.document.file_name,
                                             msg_id=m.id,
                                             chat_id=m.chat.id,
                                             md5='md5',
                                             file_type=m.document.mime_type,
                                             coverurl='',
                                             file_id=m.document.file_id)
        ack_msg = await m.reply_text(
            text=f'**{m.document.file_name}** has been added to DB.',
            quote=True)

    await asyncio.sleep(3)
    await ack_msg.delete()
