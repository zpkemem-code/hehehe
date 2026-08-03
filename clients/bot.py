import asyncio
import importlib
import traceback

from datetime import datetime
from functools import wraps


from pyrogram_styled import (
    StopPropagation,
    errors,
    types,
    filters,
)


from pyrogram_styled.handlers import (
    MessageHandler,
    CallbackQueryHandler,
)


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

            in_memory=True,

            # penting untuk pyrogram_styled
            plugins=None,

            **kwargs
        )



    def on_message(
        self,
        filters=None,
        group=0
    ):

        def decorator(func):

            @wraps(func)
            async def wrapper(
                client,
                message
            ):

                try:

                    return await func(
                        client,
                        message
                    )


                except (
                    errors.FloodWait,
                    errors.FloodPremiumWait
                ) as e:


                    logger.warning(
                        f"FloodWait {e.value}s"
                    )


                    await asyncio.sleep(
                        e.value
                    )


                    return await func(
                        client,
                        message
                    )


                except (
                    errors.ChatWriteForbidden,
                    errors.ChatSendMediaForbidden,
                    errors.ChatSendPhotosForbidden,
                    errors.MessageNotModified,
                    errors.MessageIdInvalid,
                ):

                    return


                except StopPropagation:

                    raise


                except Exception:


                    try:

                        error = traceback.format_exc()


                        text = (
                            message.text
                            or message.caption
                            or "-"
                        )


                        report = f"""
<b>BOT ERROR</b>

<b>Time:</b>
{datetime.now()}


<b>User:</b>
{getattr(message.from_user,'id','-')}


<b>Chat:</b>
{getattr(message.chat,'id','-')}


<b>Message:</b>

<pre>{text}</pre>


<b>Traceback:</b>

<pre>{error}</pre>
"""


                        await self.send_message(
                            LOG_BACKUP,
                            report
                        )


                    except Exception as err:

                        logger.error(
                            f"Error logger : {err}"
                        )



            self.add_handler(

                MessageHandler(
                    wrapper,
                    filters
                ),

                group
            )


            return func


        return decorator





    def on_callback_query(
        self,
        filters=None,
        group=0
    ):

        def decorator(func):

            self.add_handler(

                CallbackQueryHandler(
                    func,
                    filters
                ),

                group
            )


            return func


        return decorator





    async def _load_plugins(self):


        for plugin in _PLUGINS:


            try:


                module = importlib.import_module(
                    f"plugins.{plugin}"
                )


                module_name = getattr(
                    module,
                    "__MODULES__",
                    None
                )


                if module_name:

                    HELPABLE[
                        module_name.lower()
                    ] = module


                logger.info(
                    f"Loaded plugin : {plugin}"
                )


            except Exception as e:


                logger.error(
                    f"Plugin {plugin} error : {e}"
                )






    async def add_reseller(self):


        sellers = await dB.get_list_from_var(
            BOT_ID,
            "SELLER"
        )


        for user in SUDO_OWNERS:

            if user not in sellers:

                await dB.add_to_var(
                    BOT_ID,
                    "SELLER",
                    user
                )



        if OWNER_ID not in sellers:

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

                AKSES_DEPLOY.append(
                    user
                )



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

        self.username = self.me.username

        self.fullname = (
            f"{self.me.first_name} "
            f"{self.me.last_name or ''}"
        )


        self.mention = self.me.mention



        commands = [

            types.BotCommand(
                "start",
                "Start bot"
            ),

            types.BotCommand(
                "bug",
                "Report bug"
            ),

            types.BotCommand(
                "request",
                "Request feature"
            ),

            types.BotCommand(
                "restart",
                "Restart userbot"
            ),

        ]



        await self.set_bot_commands(
            commands,
            scope=types.BotCommandScopeAllPrivateChats()
        )



        if IS_JASA_PRIVATE:


            await self.set_bot_commands(

                commands +

                [

                    types.BotCommand(
                        "addprem",
                        "Berikan akses deploy"
                    ),

                    types.BotCommand(
                        "addseller",
                        "Tambah seller"
                    ),

                    types.BotCommand(
                        "unseller",
                        "Hapus seller"
                    ),

                    types.BotCommand(
                        "listseller",
                        "List seller"
                    ),

                    types.BotCommand(
                        "cekubot",
                        "Cek userbot"
                    ),

                ],

                scope=types.BotCommandScopeChat(
                    chat_id=OWNER_ID
                )

            )



        await self._load_plugins()


        await self.add_reseller()



        logger.info(
            f"🔥 {self.username} Bot Started 🔥"
        )




bot = Bot()


@bot.on_message(
    filters.command("test")
)
async def test_command(client, message):

    await message.reply_text(
        "✅ Pyrogram Styled OK"
    )