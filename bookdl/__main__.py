import logging
import asyncio
from pyrogram import idle
from bookdl.telegram import BookDLBot

logger = logging.getLogger(__name__)


async def main():
    await BookDLBot.start()
    await idle()


if __name__ == "__main__":
    BookDLBot.run(main())
    logger.info("Services Terminated!")
