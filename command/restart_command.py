import asyncio
import importlib

from pyrogram_styled.types import ReplyKeyboardRemove

from clients import UserBot, bot, session
from config import BOT_NAME, USENAME_OWNER
from database import dB
from plugins import _PLUGINS

async def reset_prefix(client, message):
    mepref = [".", ",", "?", "+", "!"]
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    if user_id not in session.get_list():
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    userbot = session.get_session(user_id)
    if userbot:
        userbot.set_prefix(mepref)
        await dB.set_pref(userbot.me.id, mepref)
        return await proses.edit(
            f"<b>Your prefix has been reset to: `{' '.join(mepref)}` .</b>",
            reply_markup=ReplyKeyboardRemove(),
        )


async def restart_userbot(client, message):
    proses = await message.reply("<b>Processing...</b>")
    user_id = message.from_user.id
    get_id = session.get_session(user_id)
    if not get_id:
        return await proses.edit(
            f"<b>You are not user @{bot.me.username}!!</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
    try:
        session.remove_session(user_id)
        ubotdb = await dB.get_ubot(user_id)
        ubot = UserBot(**ubotdb)
        await ubot.start()
        for plugin in _PLUGINS:
            importlib.reload(importlib.import_module(f"plugins.{plugin}"))

        return await proses.edit(
            f"<b>✅ Userbot has been restarted {ubot.me.first_name} {ubot.me.last_name or ''} | {ubot.me.id}.</b>",
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as error:
        return await proses.edit(f"<b>{error}</b>", reply_markup=ReplyKeyboardRemove())