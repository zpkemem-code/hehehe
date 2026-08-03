import asyncio
import importlib
import traceback
from datetime import datetime
from functools import wraps

from pyrogram_styled import StopPropagation, errors, types
from pyrogram_styled.handlers import CallbackQueryHandler, MessageHandler

from config import (
    AKSES_DEPLOY,
    API_HASH,
    API_ID,
    BOT_ID,
    BOT_NAME,
    BOT_TOKEN,
    HELPABLE,
    IS_JASA_PRIVATE,
    LOG_BACKUP,
    OWNER_ID,
    SUDO_OWNERS,
)

from database import dB
from logs import logger
from plugins import _PLUGINS

from .base import BaseClient


class Bot(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            device_model=BOT_NAME,
            plugins={
                "root": "plugins"
            },
            in_memory=True,
            **kwargs,
        )

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            @wraps(func)
            async def wrapper(client, message):
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(client, message)
                    else:
                        func(client, message)

                except (
                    errors.FloodWait,
                    errors.FloodPremiumWait
                ) as e:
                    logger.warning(
                        f"FloodWait: Sleeping {e.value}s"
                    )

                    await asyncio.sleep(e.value)
                    await func(client, message)

                except (
                    errors.ChatWriteForbidden,
                    errors.ChatSendMediaForbidden,
                    errors.ChatSendPhotosForbidden,
                    errors.MessageNotModified,
                    errors.MessageIdInvalid,
                ):
                    pass

                except StopPropagation:
                    raise

                except Exception as e:
                    try:
                        date_time = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        user_id = (
                            message.from_user.id
                            if message.from_user
                            else "Unknown"
                        )

                        chat_id = (
                            message.chat.id
                            if message.chat
                            else "Unknown"
                        )

                        chat_username = (
                            f"@{message.chat.username}"
                            if message.chat
                            and message.chat.username
                            else "Private/Group"
                        )

                        command = (
                            message.text
                            or message.caption
                            or "-"
                        )

                        error_trace = traceback.format_exc()

                        error_message = (
                            f"<b>Error:</b> {type(e).__name__}\n"
                            f"<b>Date:</b> {date_time}\n"
                            f"<b>Chat ID:</b> {chat_id}\n"
                            f"<b>Username:</b> {chat_username}\n"
                            f"<b>User ID:</b> {user_id}\n\n"
                            f"<b>Command:</b>\n"
                            f"<pre>{command}</pre>\n\n"
                            f"<b>Traceback:</b>\n"
                            f"<pre>{error_trace}</pre>"
                        )

                        await self.send_message(
                            LOG_BACKUP,
                            error_message,
                        )

                    except Exception as log_error:
                        logger.error(
                            f"Error sending log: {log_error}"
                        )

            handler = MessageHandler(
                wrapper,
                filters
            )

            self.add_handler(
                handler,
                group
            )

            return func

        return decorator


    def on_callback_query(
        self,
        filters=None,
        group=-1
    ):
        def decorator(function):

            self.add_handler(
                CallbackQueryHandler(
                    function,
                    filters
                ),
                group
            )

            return function

        return decorator


    async def add_reseller(self):

        for user in SUDO_OWNERS:
            if user not in await dB.get_list_from_var(
                BOT_ID,
                "SELLER"
            ):
                await dB.add_to_var(
                    BOT_ID,
                    "SELLER",
                    user
                )

        if OWNER_ID not in await dB.get_list_from_var(
            BOT_ID,
            "SELLER"
        ):
            await dB.add_to_var(
                BOT_ID,
                "SELLER",
                OWNER_ID
            )

        sellers = await dB.get_list_from_var(
            BOT_ID,
            "SELLER"
        )

        for user in sellers:

            if user not in AKSES_DEPLOY:
                AKSES_DEPLOY.append(user)

            if not await dB.get_var(
                user,
                "plan"
            ):
                await dB.set_var(
                    user,
                    "plan",
                    "is_pro"
                )


    async def start(self):

        await super().start()

        self.id = self.me.id
        self.fullname = (
            f"{self.me.first_name} "
            f"{self.me.last_name or ''}"
        )

        self.username = self.me.username
        self.mention = self.me.mention


        commands = [
            types.BotCommand(
                "start",
                "Start the bot."
            ),
            types.BotCommand(
                "bug",
                "Report a bug."
            ),
            types.BotCommand(
                "request",
                "Feature request."
            ),
            types.BotCommand(
                "restart",
                "Restart userbot."
            ),
        ]


        await self.set_bot_commands(
            commands,
            scope=types.BotCommandScopeAllPrivateChats()
        )


        if IS_JASA_PRIVATE:

            owner_commands = [
                types.BotCommand(
                    "addprem",
                    "Berikan akses deploy."
                ),
                types.BotCommand(
                    "addseller",
                    "Tambah seller."
                ),
                types.BotCommand(
                    "unseller",
                    "Hapus seller."
                ),
                types.BotCommand(
                    "listseller",
                    "List seller."
                ),
                types.BotCommand(
                    "cekubot",
                    "Cek userbot."
                ),
            ]

            await self.set_bot_commands(
                commands + owner_commands,
                scope=types.BotCommandScopeChat(
                    chat_id=OWNER_ID
                ),
            )


        # Load plugin manual
        for modul in _PLUGINS:

            try:
                imported_module = importlib.import_module(
                    f"plugins.{modul}"
                )

                module_name = getattr(
                    imported_module,
                    "__MODULES__",
                    ""
                ).lower()


                if module_name:
                    HELPABLE[module_name] = imported_module


            except Exception as e:

                logger.error(
                    f"Failed load plugin {modul}: {e}"
                )


        await self.add_reseller()

        logger.info(
            f"🔥 {self.username} Bot Started 🔥"
        )


bot = Bot()