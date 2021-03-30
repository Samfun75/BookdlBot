import logging
import asyncio
from pyrogram import idle
from bookdl.telegram import BookDLBot

logger = logging.getLogger(__name__)
async def main():
    await BookDLBot.start()
    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.error("KeyboardInterruption: Services Terminated!")
