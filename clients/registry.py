import asyncio
import traceback
from datetime import datetime
from functools import wraps

from pyrogram_styled import errors
from pyrogram_styled.filters import Filter
from pyrogram_styled.handlers import EditedMessageHandler, MessageHandler

import config
from logs import logger

from .bot import bot


class HandlerRegistry:
    _handlers = []
    _edited_handlers = []

    @classmethod
    def _create_wrapped_handler(cls, original_func):
        @wraps(original_func)
        async def wrapped_handler(client, message):
            try:
                if asyncio.iscoroutinefunction(original_func):
                    await original_func(client, message)
                else:
                    original_func(client, message)
            except (
                errors.FloodWait,
                errors.FloodPremiumWait,
                errors.SlowmodeWait,
            ) as e:
                logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
                await asyncio.sleep(e.value)
                await original_func(client, message)
            except (
                errors.ChatWriteForbidden,
                errors.ChatSendMediaForbidden,
                errors.ChatSendPhotosForbidden,
                errors.MessageNotModified,
                errors.MessageIdInvalid,
                errors.ChatSendPlainForbidden,
            ):
                pass
            except Exception as e:
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_id = message.from_user.id if message.from_user else "Unknown"
                chat_id = message.chat.id if message.chat else "Unknown"
                chat_username = (
                    f"@{message.chat.username}"
                    if message.chat.username
                    else "Private Group"
                )
                command = message.text
                error_trace = traceback.format_exc()

                error_message = (
                    f"<b>Error:</b> {type(e).__name__}\n"
                    f"<b>Date:</b> {date_time}\n"
                    f"<b>Chat ID:</b> {chat_id}\n"
                    f"<b>Chat Username:</b> {chat_username}\n"
                    f"<b>User ID:</b> {user_id}\n"
                    f"<b>Command/Text:</b>\n<pre language='python'><code>{command}</code></pre>\n\n"
                    f"<b>Traceback:</b>\n<pre language='python'><code>{error_trace}</code></pre>"
                )
                try:
                    await bot.send_message(config.LOG_SELLER, error_message)
                except Exception:
                    pass

        return wrapped_handler

    @classmethod
    def add_message_handler(cls, filters: Filter, original_func, group: int):
        wrapped_func = cls._create_wrapped_handler(original_func)
        handler = MessageHandler(wrapped_func, filters)
        cls._handlers.append((handler, group))

    @classmethod
    def add_edited_message_handler(cls, filters: Filter, original_func, group: int):
        wrapped_func = cls._create_wrapped_handler(original_func)
        handler = EditedMessageHandler(wrapped_func, filters)
        cls._edited_handlers.append((handler, group))

    @classmethod
    def apply_handlers(cls, client):
        for handler, group in cls._handlers:
            client.add_handler(handler, group)
        for handler, group in cls._edited_handlers:
            client.add_handler(handler, group)
