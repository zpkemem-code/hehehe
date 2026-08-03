import traceback

from clients import bot
from command import (restart_userbot, add_prem_user, add_seller, addexpired_user, backup,
                     cb_evaluasi_bot, cb_gitpull2, cb_shell, cek_expired,
                     get_prem_user, get_seles_user, getid_bot,
                     incoming_message, lapor_bug, outgoing_reply, request_bot,
                     restore, send_broadcast, send_ubot_1, setimg_start,
                     start_home, un_prem_user, un_seller, unexpired)
from helpers import CMD
from logs import logger


@CMD.BOT(
    [
        "id",
        "restart",
        "setimg",
        "start",
        "request",
        "bug",
        "getubot",
        "restore",
        "backup",
        "sh",
        "shell",
        "e",
        "eval",
        "reboot",
        "update",
        "reload",
        "addprem",
        "unprem",
        "listprem",
        "addexpired",
        "unexpired",
        "cek",
        "addseller",
        "unseller",
        "listseller",
        "broadcast",
    ]
)
async def _(client, message):
    try:
        command = message.command
        logger.info(f"Bot command:{command}")
        if command[0] == "setimg":
            return await setimg_start(client, message)
        elif command[0] == "id":
            return await getid_bot(client, message)
        elif command[0] == "restart":
            return await restart_userbot(client, message)
        elif command[0] == "start":
            return await start_home(client, message)
        elif command[0] == "request":
            return await request_bot(client, message)
        elif command[0] == "bug":
            return await lapor_bug(client, message)
        elif command[0] == "getubot":
            return await send_ubot_1(client, message)
        elif command[0] == "restore":
            return await restore(client, message)
        elif command[0] == "backup":
            return await backup(client, message)
        elif command[0] in ["sh", "shell"]:
            return await cb_shell(client, message)
        elif command[0] in ["e", "eval"]:
            return await cb_evaluasi_bot(client, message)
        elif command[0] in ["reboot", "update", "reload"]:
            return await cb_gitpull2(client, message)
        elif command[0] == "addprem":
            return await add_prem_user(client, message)
        elif command[0] == "unprem":
            return await un_prem_user(client, message)
        elif command[0] == "listseller":
            return await get_seles_user(client, message)
        elif command[0] == "addexpired":
            return await addexpired_user(client, message)
        elif command[0] == "cek":
            return await cek_expired(client, message)
        elif command[0] == "unexpired":
            return await unexpired(client, message)
        elif command[0] == "unseller":
            return await un_seller(client, message)
        elif command[0] == "addseller":
            return await add_seller(client, message)
        elif command[0] == "listprem":
            return await get_prem_user(client, message)
        elif command[0] == "broadcast":
            return await send_broadcast(client, message)
    except Exception:
        logger.error(f"Error command bot: {traceback.format_exc()}")


@CMD.CHAT_FORWARD("OUTGOING", bot)
async def _(client, message):
    return await outgoing_reply(client, message)


@CMD.CHAT_FORWARD("INCOMING", bot)
async def _(client, message):
    return await incoming_message(client, message)

