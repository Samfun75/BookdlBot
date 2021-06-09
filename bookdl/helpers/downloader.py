import asyncio
import logging
import mimetypes
from pathlib import Path

from sanitize_filename.sanitize_filename import sanitize
from ..helpers import Util
import humanfriendly as size
from libgenesis import Libgen
from bookdl.common import Common
from pyrogram.types import Message
from bookdl.telegram import BookDLBot
from bookdl.helpers.uploader import Uploader
from bookdl.database.files import BookdlFiles
from pyrogram.errors import MessageNotModified, FloodWait

logger = logging.getLogger(__name__)
status_progress = {}


class Downloader:
    @staticmethod
    async def download_book(md5: str, msg: Message):
        ack_msg = await msg.reply_text('About to download book...', quote=True)
        book = await BookdlFiles().get_file_by_md5(md5=md5)
        _, detail = await Util().get_detail(
            md5, return_fields=['extension', 'title', 'coverurl'])

        if book and book['file_name'].split('.')[-1] == detail['extension']:
            await BookDLBot.copy_message(chat_id=msg.chat.id,
                                         from_chat_id=book['chat_id'],
                                         message_id=book['msg_id'])
            await ack_msg.delete()
            return
        link = f'http://library.lol/main/{md5}'

        file = await Libgen().download(
            link,
            dest_folder=Path.joinpath(
                Common().working_dir,
                Path(f'{ack_msg.chat.id}+{ack_msg.message_id}')),
            progress=Downloader().download_progress_hook,
            progress_args=[
                ack_msg.chat.id, ack_msg.message_id, detail['title']
            ])
        file_path = '[SamfunBookdlbot] ' + sanitize(
            detail['title']) + f'.{detail["extension"]}'
        if Path.is_file(file):
            Path.rename(file, file_path)
        await Uploader().upload_book(
            file_path if Path.is_file(file_path) else file,
            ack_msg,
            md5,
            detail=detail)

    @staticmethod
    async def download_progress_hook(current, total, chat_id, message_id,
                                     title):
        try:
            await BookDLBot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Downloading: **{title}**\n"
                f"Status: **{size.format_size(current, binary=True)}** of **{size.format_size(total, binary=True)}**"
            )
        except MessageNotModified as e:
            logger.error(e)
        except FloodWait as e:
            logger.error(e)
            await asyncio.sleep(e.x)
