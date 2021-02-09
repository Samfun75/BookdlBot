"""BookDLBot Pyrogram Client."""
from pyrogram import Client
from bookdl.common import Common

if Common().is_env:
    BookDLBot = Client(
        api_id=Common().tg_api_id,
        api_hash=Common().tg_api_hash,
        session_name=Common().bot_session,
        bot_token=Common().bot_api_token,
        workers=200,
        workdir=Common().working_dir,
        plugins=dict(root="bookdl/telegram/plugins"),
        app_version="1.0",
        device_model="Heroku",
        system_version="Ubuntu/Linux"
    )
else:
    BookDLBot = Client(
        session_name=Common().bot_session,
        bot_token=Common().bot_api_token,
        workers=200,
        workdir=Common().working_dir,
        config_file=Common().app_config_file
    )
