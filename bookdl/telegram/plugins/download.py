import re
import os
import time
import requests
import aiofiles
import shutil
import asyncio
import logging
import tldextract
from pathlib import Path
from ..utils import filters
import humanfriendly as size
from libgenesis import Libgen
from bookdl.common import Common
from pyrogram import emoji, Client
from bookdl.telegram import BookDLBot
from bookdl.database.files import BookdlFiles
from bookdl.database.users import BookdlUsers
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


mirrors = ['library.lol', 'libgen.lc', 'libgen.gs', 'b-ok.cc']
status_progress = {}


@Client.on_message(filters.private & filters.text, group=0)
async def new_message_dl_handler(c: Client, m: Message):
    await BookdlUsers().insert_user(m.from_user.id)

    me = await c.get_me()

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://  domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE)

    td = tldextract.extract(m.text)
    domain = str(td.domain) + '.' + str(td.suffix)

    if re.match(regex, m.text) and domain in mirrors:
        md5 = await get_md5(m.text)
        md5_count = await BookdlFiles().count_files_by_md5(md5)
        if md5_count == 0:
            await book_process(m, md5)
        else:
            url_details = await BookdlFiles().get_file_by_md5(md5)
            files = [
                f"<a href='http://t.me/{me.username}"
                f"?start=plf-{file['_id']}'>{file['file_name']} - {file['file_type']}</a>"
                for file in url_details
            ]
            files_msg_formatted = '\n'.join(files)

            await m.reply_text(
                f"I also do have the following files that were uploaded earlier with the same url:\n"
                f"{files_msg_formatted}",
                disable_web_page_preview=True,
                quote=True)
            await book_process(m, md5)


async def get_md5(link: str) -> str:
    regex_md5 = re.compile(
        r'(?<=/main/)([\w-]+)|(?<=md5=)([\w-]+)|(?<=/md5/)([\w-]+)'
    )
    match = re.search(regex_md5, link)
    if match is not None:
        for md5 in match.groups():
            if md5 is not None:
                return md5
    return None


async def get_detail(md5: str, return_fields: list = []) -> dict:
    result = await Libgen().search(query=md5,
                                   search_field='md5',
                                   return_fields=['title', 'author', 'publisher', 'year', 'language', 'volumeinfo',
                                                  'filesize', 'extension', 'timeadded', 'timelastmodified', 'coverurl'] if not return_fields else return_fields)
    return result


async def get_formatted(detail: dict) -> str:
    formated = ''
    formated += 'Title: **' + str(detail['title']) + '**\n'
    formated += 'Author: **' + str(detail['author']) + '**\n'
    formated += 'Volume: **' + str(detail['volumeinfo']) + '**\n'
    formated += 'Publisher: **' + str(detail['publisher']) + '**\n'
    formated += 'Year: **' + str(detail['year']) + '**\n'
    formated += 'Language: **' + str(detail['language']) + '**\n'
    formated += f"Size: **{size.format_size(int(detail['filesize']), binary=True)}**\n"
    formated += 'Extention: **' + str(detail['extension']) + '**\n'
    formated += 'Added Time: **' + str(detail['timeadded']) + '**\n'
    formated += 'Last Modified Time: **' + \
        str(detail['timelastmodified']) + '**\n'
    return formated


async def book_process(msg: Message, md5: str):

    detail = await get_detail(md5)
    if detail:
        book_id = list(detail.keys())[0]
        inline_buttons = []
        inline_buttons.append([
            InlineKeyboardButton(
                text=f"{emoji.FLOPPY_DISK} Download Book",
                callback_data=f"download_{msg.chat.id}_{msg.message_id}_{md5}")
        ])
        formated = await get_formatted(detail[book_id])

        if detail[book_id]['coverurl']:
            await msg.reply_photo(
                photo=detail[book_id]['coverurl'],
                caption=f"**Book Detail**\n\n"
                f"{formated}",
                reply_markup=InlineKeyboardMarkup(inline_buttons),
                quote=True)
        else:
            await msg.reply_text(
                text=f"**Book Detail**\n\n"
                f"{formated}",
                reply_markup=InlineKeyboardMarkup(inline_buttons),
                disable_web_page_preview=True,
                quote=True)
    else:
        await msg.reply_text(
            text="Couldn't get details for this Book. Sorry, Try searching in the bot or get another supported link!",
            reply_markup=None,
            quote=True)


async def download_book(md5: str, msg: Message):
    ack_msg = await msg.reply_text(
        'About to download book...',
        quote=True
    )
    link = f'http://library.lol/main/{md5}'
    file_path = await Libgen().download(link, dest_folder=Path.joinpath(Common().working_dir, Path(f'{ack_msg.chat.id}+{ack_msg.message_id}')))
    status_progress[f"{ack_msg.chat.id}{ack_msg.message_id}"] = {}
    await upload_book(file_path, ack_msg, md5)

async def get_thumb(url: str, ack_msg: Message):
    file_name = os.path.basename(url)
    thumb_file = Path.joinpath(Common().working_dir,Path(f'{ack_msg.chat.id}+{ack_msg.message_id}'),Path(file_name))
    resp = requests.get(url, allow_redirects=True)
    async with aiofiles.open(thumb_file, mode='wb') as dl_file:
        await dl_file.write(resp.content)
    return thumb_file

async def upload_book(file_path: Path, ack_msg: Message, md5: str):
    ack_msg = await ack_msg.edit_text(
        'About to upload book...'
    )
    file_name = os.path.basename(file_path)
    detail = await get_detail(md5=md5, return_fields=['coverurl', 'title'])
    book_id = list(detail.keys())[0]
    cover_url = detail[book_id]['coverurl']
    thumb = await get_thumb(cover_url, ack_msg)
    status_progress[f"{ack_msg.chat.id}{ack_msg.message_id}"]["last_upload_updated"] = time.time()
    try:
        file_message = await ack_msg.reply_document(
            document=file_path,
            progress=upload_progress_hook,
            progress_args=[ack_msg.chat.id, ack_msg.message_id, file_name],
            thumb=thumb,
            caption=detail[book_id]['title']
        )
        await ack_msg.delete()
        await send_file_to_dustbin(file_message, md5)
    except FloodWait as e:
        logging.error(e)
        await asyncio.sleep(e.x)
    except Exception as e:
        logging.error(e)
    finally:
        if Path.is_dir(Path(file_path).parent):
            shutil.rmtree(Path(file_path).parent)


async def send_file_to_dustbin(file_message: Message, md5: str,):
    fd_msg = await file_message.copy(chat_id=Common().bot_dustbin)
    detail = await get_detail(md5)
    book_id = list(detail.keys())[0]
    await BookdlFiles().insert_new_files(
        title=detail[book_id]['title'],
        file_name=fd_msg.document.file_name,
        msg_id=fd_msg.message_id,
        chat_id=fd_msg.chat.id,
        md5=md5,
        file_type=fd_msg.document.mime_type,
        coverurl=detail[book_id]['coverurl'] if detail[book_id]['coverurl'] else '',
        file_id=fd_msg.document.file_id
    )


async def upload_progress_hook(current, total, chat_id, message_id, file_name):
    if (time.time() - status_progress[f"{chat_id}{message_id}"]["last_upload_updated"]) > 1:
        try:
            await BookDLBot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Uploading: **{file_name}**\n"
                     f"Status: **{size.format_size(current, binary=True)}** of **{size.format_size(total, binary=True)}**"
            )
        except MessageNotModified as e:
            logging.error(e)
        except FloodWait as e:
            logging.error(e)
            await asyncio.sleep(e.x)

        status_progress[f"{chat_id}{message_id}"][
            "last_upload_updated"] = time.time()


@Client.on_callback_query(filters.callback_query("download"), group=1)
async def callback_download_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')

    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None
    org_msg = await c.get_messages(
        cb_chat, cb_message_id) if cb_message_id is not None else None
    md5 = str(params[2]) if len(params) > 2 else None

    await cb.answer()
    await download_book(md5, org_msg)
