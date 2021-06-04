import time
import shutil
import asyncio
import logging
import aiohttp
import aiofiles
import convertapi
from pathlib import Path
import humanfriendly as size
from bookdl.helpers import Util
from bookdl.common import Common
from pyrogram.types import Message
from bookdl.telegram import BookDLBot
from convertapi.exceptions import ApiError
from bookdl.helpers.uploader import Uploader
from bookdl.database.files import BookdlFiles
from libgenesis.download import LibgenDownload
from pyrogram.errors import MessageNotModified, FloodWait

logger = logging.getLogger(__name__)
convert_status = {}


class Convert:
    def __init__(self):
        convertapi.api_secret = Common().convert_api

    async def convert_to_pdf(self, md5: str, msg: Message):
        ack_msg = await msg.reply_text('About to convert book to PDF...',
                                       quote=True)
        book = await BookdlFiles().get_file_by_md5(md5=md5)
        if book and book['file_type'] == 'application/pdf':
            await BookDLBot.copy_message(chat_id=msg.chat.id,
                                         from_chat_id=book['chat_id'],
                                         message_id=book['msg_id'])
            await ack_msg.delete()
            return
        _, detail = await Util().get_detail(
            md5, return_fields=['mirrors', 'title', 'extension', 'coverurl'])

        temp_dir = Path.joinpath(
            Common().working_dir,
            Path(f'{ack_msg.chat.id}+{ack_msg.message_id}'))
        if not Path.is_dir(temp_dir):
            Path.mkdir(temp_dir)
        file_path = Path.joinpath(
            temp_dir, Path(detail['title'] + '  [@SamfunBookdlbot].pdf'))

        direct_links = await LibgenDownload().get_directlink(
            detail['mirrors']['main'])
        extension = detail['extension']
        params = {
            'File': direct_links[1],
            'FileName': detail['title'],
            'PdfVersion': '2.0',
            'OpenZoom': '100',
            'PdfTitle': '@SamfunBookdlbot - ' + detail['title'],
            'RotatePage': 'ByPage'
        }
        stat_var = f"{ack_msg.chat.id}{ack_msg.message_id}"
        convert_status[stat_var] = {'Done': False}
        try:
            loop = asyncio.get_event_loop()
            convert_process = loop.run_in_executor(None, self.__convert,
                                                   params, extension, stat_var)
            start_time = time.time()
            while True:
                if convert_status[stat_var]['Done']:
                    break
                else:
                    try:
                        await ack_msg.edit_text(
                            f'Convertion to PDF started... {int(time.time() - start_time)}'
                        )
                    except MessageNotModified as e:
                        logger.error(e)
                    except FloodWait as e:
                        logger.error(e)
                        await asyncio.sleep(e.x)
                    await asyncio.sleep(2)
            Result = await convert_process
        except ApiError as e:
            logger.error(e)
            await ack_msg.edit_text(e)
            shutil.rmtree(temp_dir)
            return

        detail[
            'cost'] = 'ConvertAPI Cost: **{Result.conversion_cost}** seconds.'
        await ack_msg.edit_text(f'About to download converted file...')
        try:
            async with aiohttp.ClientSession() as dl_ses:
                async with dl_ses.get(Result.file.url) as resp:
                    total_size = int(Result.file.size)
                    file_name = Result.file.filename

                    async with aiofiles.open(file_path, mode="wb") as dl_file:
                        current = 0
                        logger.info(f'Starting download: {file_name}')
                        start_time = time.time()
                        async for chunk in resp.content.iter_chunked(1024 *
                                                                     1024):
                            await dl_file.write(chunk)
                            current += len(chunk)
                            if time.time() - start_time > 2:
                                await ack_msg.edit_text(
                                    f'Downloading: **{detail["title"]}**\n'
                                    f"Status: **{size.format_size(current, binary=True)}** of **{size.format_size(total_size, binary=True)}**"
                                )
                                start_time = time.time()
        except Exception as e:
            logger.exception(e)
            return None
        await Uploader().upload_book(file_path, ack_msg, md5, detail=detail)

    @staticmethod
    def __convert(params, extension, stat_var):
        convertapi.api_secret = Common().convert_api
        logger.info('Conversion Started...')
        try:
            result = convertapi.convert('pdf',
                                        params,
                                        from_format=extension,
                                        timeout=120)
            logger.info('Conversion Finished!')
        except ApiError as e:
            convert_status[stat_var]['Done'] = True
            logger.error('Conversion Failed!')
            raise e
        finally:
            convert_status[stat_var]['Done'] = True
        return result
