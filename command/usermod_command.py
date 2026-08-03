import random
import re
from time import time
from pyrogram_styled import enums
import psutil
from database import dB
from helpers import (Emoji, Basic_Effect, Premium_Effect, Tools, animate_proses,
                     animate_proses, get_time, start_time)


async def setprefix_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await emo.get_costum_text()
    pros = await animate_proses(message, emo.proses)
    if len(message.command) < 2:
        m = message.text.split()[0]
        return await pros.edit(
            f"{emo.gagal}<b>Please provide the Prefix/Handler you want to use.</b>\n\n"
            f"Example:\n<code>{m}setprefix , . ? : ;</code>\n\n"
            f"Or use <code>none</code> if you want to use commands without a Prefix/Handler."
        )
    ub_prefix = []
    for prefix in message.command[1:]:
        if prefix.lower() == "none":
            ub_prefix.append("")
        else:
            ub_prefix.append(prefix)
    try:
        client.set_prefix(ub_prefix)
        await dB.set_pref(client.me.id, ub_prefix)
        parsed_prefix = (
            " ".join(f"<code>{prefix}</code>" for prefix in ub_prefix if prefix)
            or "none"
        )
        return await pros.edit(
            f"{emo.sukses}<b>Successfully set the Prefix to: {parsed_prefix}</b>"
        )
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>ERROR: <code>{error}</code></b>")

def get_size(bytes, suffix="b"):
    factor = 1024
    for unit in ["", " K", " M", " G", " T", " P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

async def mping_cmd(client, message):
    out, _ = await Tools.bash("ping -c2 157.15.40.61")

    matches = re.findall(
        r"time[=<]([\d.]+)\s*ms",
        out
    )

    upnya = await get_time(
        (time() - start_time)
    )

    if matches:
        ping_result = matches[-1]
    else:
        ping_result = "Timeout"


    _ping = "<pre><code>\n"
    _ping += f"Kecepatan: {ping_result} ms\n"
    _ping += f"Uptime: {upnya}"
    _ping += "</code></pre>"

    await message.reply(
        _ping
    )

    return await message.delete()

async def id_cmd(client, message):
    chat = message.chat
    your_id = message.from_user if message.from_user else message.sender_chat
    message_id = message.id
    reply = message.reply_to_message

    text = f"**Message ID:** `{message_id}`\n"
    text += f"**Your ID:** `{your_id.id}`\n"
    text += f"**Chat ID:** `{chat.id}`\n"

    if reply:
        replied_user_id = (
            reply.from_user.id
            if reply.from_user
            else reply.sender_chat.id if reply.sender_chat else None
        )
        text += "\n**Replied Message Information:**\n"
        text += f"**├ Message ID:** `{reply.id}`\n"
        if replied_user_id:
            text += f"**├ User ID:** `{replied_user_id}`\n"

        if reply.entities:
            for entity in reply.entities:
                if entity.custom_emoji_id:
                    text += f"**╰ Emoji ID:** `{entity.custom_emoji_id}`\n"

        if reply.photo:
            text += f"**╰ Photo File ID:** `{reply.photo.file_id}`\n"
        elif reply.video:
            text += f"**╰ Video File ID:** `{reply.video.file_id}`\n"
        elif reply.sticker:
            text += f"**╰ Sticker File ID:** `{reply.sticker.file_id}`\n"
        elif reply.animation:
            text += f"**╰ GIF File ID:** `{reply.animation.file_id}`\n"
        elif reply.document:
            text += f"**╰ Document File ID:** `{reply.document.file_id}`\n"

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"\n**Mentioned User ID:** `{user_id}`\n"
        except Exception:
            return await message.reply_text(f"**User tidak ditemukan.**")

    return await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.MARKDOWN,
    )













