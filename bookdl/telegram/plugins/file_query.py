from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.file_id import FileId
from pyrogram.raw.types import InputBotInlineResultDocument, InputDocument, InputBotInlineMessageMediaAuto
from pyrogram.raw.functions.messages import SetInlineBotResults
from bookdl.telegram import BookDLBot
from bookdl.database.files import BookdlFiles
from libgenesis import Libgen


@Client.on_inline_query()
async def inline_query_handler(c: Client, iq: InlineQuery):
    q = iq.query
    res = []

    if q.strip().startswith('dl:'):
        q_res_data = await BookdlFiles().get_file_by_name(q.split(':')[1].strip(), 50)
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
                            file_reference=file_id_obj.file_reference
                        ),
                        send_message=InputBotInlineMessageMediaAuto(
                            message=file['title']
                        ),
                        title=file['title'],
                        description=f"File Name: {file['file_name']}\n\n"
                                    f"File Type: {file['file_type']}",
                    )
                )
            await BookDLBot.send(
                data= SetInlineBotResults(
                    query_id=int(iq.id),
                    results=res,
                    cache_time=0
                )
            )
        else:
            await iq.answer([])
        return
    else:
        if q.strip():
            result = await Libgen(result_limit=50).search(query=q.strip(),
                                                          return_fields=['title', 'pages', 'language', 'publisher',
                                                                         'year', 'author', 'extension', 'coverurl',
                                                                         'volumeinfo', 'mirrors'])
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
                            "education-vol-1-34/512/15_File_files_office-256.png" if result[
                                item]['coverurl'] is None else result[item]['coverurl'],
                            input_message_content=InputTextMessageContent(
                                message_text=result[item]['mirrors']['main'],
                                disable_web_page_preview=True),
                            reply_markup=None
                        )
                    )

    if res:
        await iq.answer(results=res, cache_time=0, is_personal=False)
    else:
        await iq.answer([])
