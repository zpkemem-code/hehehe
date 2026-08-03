import os
import sys
from logs import logger

if not os.path.exists("downloads"):
    os.makedirs("downloads")

try:
    import asyncio
    import uvloop

    uvloop.install()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    logger.info("🚀 UvLoop successfully.")
    
except ImportError:
    logger.warning("⚠️ UvLoop tidak terinstal..")
except Exception as e:
    logger.error(f"❌ Failed setup UvLoop: {e}")

from .active import session
from .base import BaseClient
from .bot import Bot, bot
from .registry import HandlerRegistry
from .userbot import UserBot, navy

__all__ = [
    "session",
    "BaseClient",
    "UserBot",
    "navy",
    "Bot",
    "bot",
    "HandlerRegistry",
]
