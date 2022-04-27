"""BookDLBot Pyrogram Client."""
from pyrogram import Client
from bookdl.common import Common


BookDLBot = Client(
    name=Common().session_name,
    api_id=Common().tg_api_id,
    api_hash=Common().tg_api_hash,
    bot_token=Common().bot_api_token,
    workers=200,
    workdir=Common().working_dir,
    plugins=dict(root="bookdl/telegram/plugins"),
    app_version="2.0",
    device_model="BookdlBot",
    system_version="Ubuntu/Linux",
    in_memory=True
)
