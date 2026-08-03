import asyncio
import contextlib
import html
import io
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from time import perf_counter
from typing import Any, Dict
from uuid import uuid4

import pyrogram_styled
import pyrogram_styled.enums
import pyrogram_styled.errors
import pyrogram_styled.helpers
import pyrogram_styled.raw
import pyrogram_styled.types
import pyrogram_styled.utils
from meval import meval
from pytz import timezone

import config
from clients import bot, navy
from database import DB_PATH, dB, state
from helpers import ButtonUtils, Message, Tools, stop_main, task
from logs import logger

eval_tasks: Dict[int, Any] = {}

import importlib


def extract_changed_modules(git_output):
    changed = []
    for line in git_output.splitlines():
        # print("DEBUG:", line)
        if "|" in line:
            file_path = line.split("|")[0].strip()
            if file_path.endswith(".py"):
                mod_path = file_path.replace("/", ".").replace(".py", "")
                changed.append(mod_path)
    return changed


def reload_modules(modules):
    reloaded = []
    for mod in modules:
        if mod in sys.modules:
            importlib.reload(importlib.import_module(f"{mod}"))
            reloaded.append(mod)
    return reloaded


async def send_ubot_1(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.SUDO_OWNERS:
        return
    return await client.send_message(
        message.from_user.id,
        await Message.userbot_list(0),
        reply_markup=ButtonUtils.account_list(0),
    )


async def restore(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.KYNAN:
        return
    reply = message.reply_to_message
    if not reply:
        return await message.reply("**Please reply to a .db or .zip file**")

    document = reply.document
    file_path = await client.download_media(document, "./")

    if file_path.endswith(".zip"):
        extract_path = "./extracted_db"
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        db_files = [f for f in os.listdir(extract_path) if f.endswith(".db")]
        if not db_files:
            return await message.reply("**No .db file found in the ZIP archive**")

        extracted_db = os.path.join(extract_path, db_files[0])
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        os.rename(extracted_db, DB_PATH)

        os.remove(file_path)
    else:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        document = reply.document
        file_path = await client.download_media(document, "./")
    await message.reply(
        f"<blockquote><b>Sukses melakukan restore database, tunggu sebentar bot akan me-restart.</blockquote></b>"
    )
    os.execl(sys.executable, sys.executable, *sys.argv)


async def backup(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.KYNAN:
        return
    now = datetime.now(timezone("Asia/Jakarta"))
    timestamp = now.strftime("%Y-%m-%d_%H:%M")
    zip_filename = f"{config.BOT_NAME}_{timestamp}.zip"
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(".env"):
            env_path = os.path.abspath(".env")
            zipf.write(env_path, os.path.basename(env_path))
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
        else:
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
    caption = now.strftime("%d %B %Y %H:%M")
    return await message.reply_document(zip_filename, caption=caption)

async def cb_shell(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.KYNAN:
        return
    if len(message.command) < 2:
        return await message.reply("Noob!!")
    cmd_text = message.text.split(maxsplit=1)[1]
    text = f"<code>{cmd_text}</code>\n\n"
    start_time = perf_counter()

    try:
        stdout, stderr = await Tools.bash(cmd_text)
    except asyncio.TimeoutError:
        text += "<b>Timeout expired!!</b>"
        return await message.reply(text)
    finally:
        duration = perf_counter() - start_time
    if cmd_text.startswith("cat "):
        filepath = cmd_text.split("cat ", 1)[1].strip()
        output_filename = os.path.basename(filepath)
    else:
        output_filename = f"{cmd_text}.txt"
    if len(stdout) > 4096:
        anuk = await message.reply("<b>Oversize, sending file...</b>")
        with open(output_filename, "w") as file:
            file.write(stdout)

        await message.reply_document(
            output_filename,
            caption=f"<b>Command completed in `{duration:.2f}` seconds.</b>",
        )
        os.remove(output_filename)
        return await anuk.delete()
    else:
        text += f"<blockquote expandable><code>{stdout}</code></blockquote>"

        if stderr:
            text += f"<blockquote expandable>{stderr}</blockquote>"
        text += f"\n<b>Completed in `{duration:.2f}` seconds.</b>"
        return await message.reply(text, parse_mode=pyrogram_styled.enums.ParseMode.HTML)


async def cb_evaluasi_bot(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.KYNAN:
        return
    if len(message.text.split()) == 1:
        await message.reply_text("<b>No Code!</b>", quote=True)
        return

    reply_text = await message.reply_text(
        "...",
        quote=True,
        reply_markup=pyrogram_styled.helpers.ikb([[("Cancel", "Canceleval")]]),
    )

    async def eval_func() -> None:
        eval_code = message.text.split(maxsplit=1)[1]
        eval_vars = {
            # PARAMETERS
            "c": client,
            "m": message,
            "u": (message.reply_to_message or message).from_user,
            "r": message.reply_to_message,
            "chat": message.chat,
            # PYROGRAM
            "asyncio": asyncio,
            "pyrogram": pyrogram,
            "raw": pyrogram_styled.raw,
            "enums": pyrogram_styled.enums,
            "types": pyrogram_styled.types,
            "errors": pyrogram_styled.errors,
            "utils": pyrogram_styled.utils,
            "helpers": pyrogram_styled.helpers,
            # LOCAL
            "bot": bot,
            "navy": navy,
            "dB": dB,
            "config": config,
            "Message": Message,
            "Tools": Tools,
            "task": task,
            "button": ButtonUtils,
            "state": state,
            "DB_PATH": DB_PATH,
        }

        start_time = client.loop.time()

        file = io.StringIO()
        with contextlib.redirect_stdout(file):
            try:
                meval_out = await meval(eval_code, globals(), **eval_vars)
                print_out = file.getvalue().strip() or str(meval_out) or "None"
            except Exception as exception:
                print_out = repr(exception)

        elapsed_time = client.loop.time() - start_time

        converted_time = Tools.convert_seconds(elapsed_time)

        final_output = (
            f"<blockquote expandable>{html.escape(print_out)}</blockquote>\n"
            f"<b>Elapsed:</b> {converted_time}"
        )
        if len(final_output) > 4096:
            output_filename = f"/tmp/output-{uuid4().hex}.txt"
            with open(output_filename, "w") as file:
                data = html.escape(print_out)
                data = data.replace("&quot;", "'")
                file.write(data)
            await message.reply_document(
                output_filename,
                caption=f"<b>Elapsed: `{converted_time}.`</b>",
            )
            os.remove(output_filename)
            await reply_text.delete()
        else:
            await reply_text.edit_text(final_output)

    task_id = message.id
    _e_task = asyncio.create_task(eval_func())

    eval_tasks[task_id] = _e_task

    try:
        await _e_task
    except asyncio.CancelledError:
        await reply_text.edit_text("<b>Process Cancelled!</b>")
    finally:
        if task_id in eval_tasks:
            del eval_tasks[task_id]


async def cb_evalusi(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.KYNAN:
        return
    if len(message.text.split()) == 1:
        await message.reply_text("<b>No Code!</b>", quote=True)
        return
    reply_text = await message.reply_text("...", quote=True)
    f"{str(uuid4())}"

    async def eval_func() -> None:
        eval_code = message.text.split(maxsplit=1)[1]
        eval_vars = {
            # PARAMETERS
            "c": client,
            "m": message,
            "u": (message.reply_to_message or message).from_user,
            "r": message.reply_to_message,
            "chat": message.chat,
            # PYROGRAM
            "asyncio": asyncio,
            "pyrogram": pyrogram,
            "raw": pyrogram_styled.raw,
            "enums": pyrogram_styled.enums,
            "types": pyrogram_styled.types,
            "errors": pyrogram_styled.errors,
            "utils": pyrogram_styled.utils,
            "helpers": pyrogram_styled.helpers,
            # LOCAL
            "bot": bot,
            "navy": navy,
            "dB": dB,
            "config": config,
            "Message": Message,
            "Tools": Tools,
            "task": task,
            "button": ButtonUtils,
            "state": state,
            "DB_PATH": DB_PATH,
        }

        start_time = client.loop.time()

        file = io.StringIO()
        with contextlib.redirect_stdout(file):
            try:
                meval_out = await meval(eval_code, globals(), **eval_vars)
                print_out = file.getvalue().strip() or str(meval_out) or "None"
            except Exception as exception:
                print_out = repr(exception)

        elapsed_time = client.loop.time() - start_time

        converted_time = Tools.convert_seconds(elapsed_time)

        final_output = (
            f"<blockquote expandable>{html.escape(print_out)}</blockquote>\n"
            f"<b>Elapsed:</b> {converted_time}"
        )
        if len(final_output) > 4096:
            output_filename = f"/tmp/output-{uuid4().hex}.txt"
            with open(output_filename, "w") as file:
                data = html.escape(print_out)
                data = data.replace("&quot;", "'")
                file.write(data)
            await message.reply_document(
                output_filename,
                caption=f"<b>Elapsed: `{converted_time}.`</b>",
            )
            os.remove(output_filename)
            await reply_text.delete()
        else:
            await reply_text.edit_text(final_output)

    task_id = message.id
    _e_task = asyncio.create_task(eval_func())

    eval_tasks[task_id] = _e_task

    try:
        await _e_task
    except asyncio.CancelledError:
        await reply_text.edit_text("<b>Process Cancelled!</b>")
    finally:
        if task_id in eval_tasks:
            del eval_tasks[task_id]


async def send_large_output(message, output):
    with io.BytesIO(str.encode(str(output))) as out_file:
        out_file.name = "update.txt"
        await message.reply_document(document=out_file)


async def update_kode_all(client, message):
    out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if "Already up to date." in str(out):
        return await message.reply(f"<blockquote expandable>{out}</blockquote>")
    elif int(len(str(out))) > 4096:
        await send_large_output(message, out)
    else:
        await message.reply(f"<blockquote expandable>{out}</blockquote>")
    await message.reply("♻️ <i>Restarting untuk memuat perubahan...</i>")
    asyncio.create_task(restart_process())


async def restart_process():
    try:
        await stop_main()
        await asyncio.sleep(2)
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        logger.error(f"❌ Gagal restart: {e}")


async def update_kode(client, message):
    out = subprocess.check_output(["git", "pull"]).decode("UTF-8")

    if "Already up to date." in out:
        return await message.reply(f"<blockquote expandable>{out}</blockquote>")

    modules = extract_changed_modules(out)
    reloaded = reload_modules(modules)
    logger.info(modules)
    logger.info(reloaded)

    text = f"<blockquote expandable>{out}</blockquote>\n"
    text += (
        f"\n♻️ Reloaded modules:\n" + "\n".join(reloaded)
        if reloaded
        else "\n⚠️ No reloadable .py modules."
    )

    if len(text) > 4096:
        return await send_large_output(message, text)
    else:
        return await message.reply(text)


async def cb_gitpull2(client, message):
    user = message.from_user if message.from_user else message.sender_chat
    if user.id not in config.SUDO_OWNERS:
        return
    if message.command[0] == "reload":
        return await update_kode(client, message)
    elif message.command[0] == "update":
        return await update_kode_all(client, message)
    elif message.command[0] == "reboot":
        await message.reply(
            "<b>✅ Bot stopped successfully. Trying to restart Userbot!!</b>"
        )
        asyncio.create_task(restart_process())

