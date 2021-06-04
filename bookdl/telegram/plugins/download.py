import re
import logging
import tldextract
from ..utils import filters
from bookdl.helpers import Util
from pyrogram import emoji, Client
from bookdl.helpers.convert import Convert
from bookdl.database.users import BookdlUsers
from bookdl.helpers.downloader import Downloader
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)
mirrors = ['library.lol', 'libgen.lc', 'libgen.gs', 'b-ok.cc']


@Client.on_message(filters.private & filters.text, group=0)
async def new_message_dl_handler(c: Client, m: Message):
    await BookdlUsers().insert_user(m.from_user.id)

    if m.text.startswith('MD5:'):
        md5 = m.text.splitlines()[0].split(':')[1].strip()
        await book_process(m, md5)
    else:
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
            md5 = await Util().get_md5(m.text)
            await book_process(m, md5)
        else:
            await m.reply_text(
                text=f'Sorry links from {domain} not supported.', quote=True)


async def book_process(msg: Message, md5: str):
    _, detail = await Util().get_detail(md5)
    if detail:
        inline_buttons = [[
            InlineKeyboardButton(
                text=f"{emoji.FLOPPY_DISK} Download Book",
                callback_data=f"download_{msg.chat.id}_{msg.message_id}_{md5}")
        ]]
        if detail['extension'] not in ['pdf', 'zip', 'rar']:
            inline_buttons.append([
                InlineKeyboardButton(
                    text=f"{emoji.CLOCKWISE_VERTICAL_ARROWS} Convert to PDF",
                    callback_data=
                    f"convert_{msg.chat.id}_{msg.message_id}_{md5}")
            ])
        formated = await Util().get_formatted(detail)

        if detail['coverurl']:
            await msg.reply_photo(
                photo=detail['coverurl'],
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
            text=
            "Couldn't get details for this Book. Sorry, Try searching in the bot or get another supported link or md5!",
            reply_markup=None,
            quote=True)


@Client.on_callback_query(filters.callback_query("download"), group=1)
async def callback_download_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')

    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None
    org_msg = await c.get_messages(
        cb_chat, cb_message_id) if cb_message_id is not None else None
    md5 = str(params[2]) if len(params) > 2 else None

    await cb.answer('Download starting...')
    await Downloader().download_book(md5, org_msg)


@Client.on_callback_query(filters.callback_query("convert"), group=1)
async def callback_convert_handler(c: Client, cb: CallbackQuery):
    params = cb.payload.split('_')

    cb_chat = int(params[0]) if len(params) > 0 else None
    cb_message_id = int(params[1]) if len(params) > 1 else None
    org_msg = await c.get_messages(
        cb_chat, cb_message_id) if cb_message_id is not None else None
    md5 = str(params[2]) if len(params) > 2 else None

    await cb.answer('Conversion starting...')
    await Convert().convert_to_pdf(md5, org_msg)
