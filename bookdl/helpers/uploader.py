import os
import time
import shutil
import logging
import asyncio
import requests
import aiofiles
from pathlib import Path
import humanfriendly as size
from bookdl.helpers import Util
from bookdl.common import Common
from pyrogram.types import Message
from bookdl.telegram import BookDLBot
from bookdl.database.files import BookdlFiles
from pyrogram.errors import FloodWait, MessageNotModified

logger = logging.getLogger(__name__)
status_progress = {}


class Uploader:
    @staticmethod
    async def upload_book(file_path: Path, ack_msg: Message, md5: str):
        ack_msg = await ack_msg.edit_text('About to upload book...')
        _, detail = await Util().get_detail(
            md5=md5, return_fields=['coverurl', 'title'])
        cover_url = detail['coverurl']
        thumb = await Uploader().get_thumb(cover_url, ack_msg)
        status_progress[f"{ack_msg.chat.id}{ack_msg.message_id}"] = {}
        status_progress[f"{ack_msg.chat.id}{ack_msg.message_id}"][
            "last_upload_updated"] = time.time()
        try:
            file_message = await ack_msg.reply_document(
                document=file_path,
                progress=Uploader().upload_progress_hook,
                progress_args=[
                    ack_msg.chat.id, ack_msg.message_id, file_path.name
                ],
                thumb=thumb,
                caption=file_path.name)
            await ack_msg.delete()
            await Uploader().send_file_to_dustbin(file_message, md5, detail)
        except FloodWait as e:
            logger.error(e)
            await asyncio.sleep(e.x)
        except Exception as e:
            logger.error(e)
        finally:
            if Path.is_dir(Path(file_path).parent):
                shutil.rmtree(Path(file_path).parent)

    @staticmethod
    async def send_file_to_dustbin(file_message: Message, md5: str,
                                   detail: dict):
        fd_msg = await file_message.copy(chat_id=Common().bot_dustbin)

        await BookdlFiles().insert_new_files(
            title=detail['title'],
            file_name=fd_msg.document.file_name,
            msg_id=fd_msg.message_id,
            chat_id=fd_msg.chat.id,
            md5=md5,
            file_type=fd_msg.document.mime_type,
            coverurl=detail['coverurl'] if detail['coverurl'] else '',
            file_id=fd_msg.document.file_id)

    @staticmethod
    async def upload_progress_hook(current, total, chat_id, message_id,
                                   file_name):
        if (time.time() - status_progress[f"{chat_id}{message_id}"]
            ["last_upload_updated"]) > 1:
            try:
                await BookDLBot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"Uploading: **{file_name}**\n"
                    f"Status: **{size.format_size(current, binary=True)}** of **{size.format_size(total, binary=True)}**"
                )
            except MessageNotModified as e:
                logger.error(e)
            except FloodWait as e:
                logger.error(e)
                await asyncio.sleep(e.x)

            status_progress[f"{chat_id}{message_id}"][
                "last_upload_updated"] = time.time()

    @staticmethod
    async def get_thumb(url: str, ack_msg: Message):
        file_name = os.path.basename(url)
        thumb_file = Path.joinpath(
            Common().working_dir,
            Path(f'{ack_msg.chat.id}+{ack_msg.message_id}'), Path(file_name))
        resp = requests.get(url, allow_redirects=True)
        async with aiofiles.open(thumb_file, mode='wb') as dl_file:
            await dl_file.write(resp.content)
        return thumb_file
