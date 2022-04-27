import asyncio
from pyrogram import Client
from ..utils import filters
from libgenesis import Libgen
from ...telegram import Common
from pyrogram.file_id import FileId
from bookdl.telegram import BookDLBot
from bookdl.database.files import BookdlFiles
from pyrogram.raw.functions.messages import SetInlineBotResults
from pyrogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.raw.types import InputBotInlineResultDocument, InputDocument, InputBotInlineMessageMediaAuto


@Client.on_inline_query()
async def inline_query_handler(c: Client, iq: InlineQuery):
    q = iq.query
    res = []
    if len(q.strip()) < 2:
        await iq.answer([])
        return
    if q.strip().startswith('dl:'):
        q_res_data = await BookdlFiles().get_file_by_name(
            q.split(':')[1].strip(), 50)
        if q_res_data:
            for file in q_res_data:
                file_id_obj = FileId.decode(file['file_id'])
                res.append(
                    InputBotInlineResultDocument(
                        id=str(file['_id']),
                        type='file',
                        document=InputDocument(
                            id=file_id_obj.media_id,
                            access_hash=file_id_obj.access_hash,
                            file_reference=file_id_obj.file_reference),
                        send_message=InputBotInlineMessageMediaAuto(
                            message=file['title']),
                        title=file['title'],
                        description=f"File Name: {file['file_name']}\n"
                        f"File Type: {file['file_type']}",
                    ))

            await BookDLBot.invoke(data=SetInlineBotResults(
                query_id=int(iq.id), results=res, cache_time=0))
        else:
            await iq.answer([])
        return
    else:
        if q.strip():
            result = await Libgen(result_limit=50
                                  ).search(query=q.strip(),
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
        await iq.answer(results=res, cache_time=0, is_personal=False)
    else:
        await iq.answer([])


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
