import asyncio, datetime, random, os, io, pytz
from pyrogram_styled.enums import ChatType
from pyrogram_styled.errors import FloodPremiumWait, FloodWait, UserBannedInChannel
from clients import bot, session
from config import BLACKLIST_GCAST, OWNER_ID
from database import dB
from logs import logger

async def add_auto_text(message):
    client = message._client
    auto_text = await dB.get_var(client.me.id, "MSG_AUTOBC") or []
    rep = message.reply_to_message
    for item in auto_text:
        try:
            await client.delete_messages("me", item["message_id"])
        except Exception:
            pass
    await dB.set_var(client.me.id, "MSG_AUTOBC", [])
    auto_text = []
    if not rep:
        return
    saved_msg = await rep.copy("me")
    content_type = None
    if rep.text:
        content_type = "text"
    elif rep.photo:
        content_type = "photo"
    elif rep.video:
        content_type = "video"
    elif rep.voice:
        content_type = "voice"
    elif rep.audio:
        content_type = "audio"
    elif rep.document:
        content_type = "document"
    elif rep.sticker:
        content_type = "sticker"
    elif rep.animation:
        content_type = "animation"
    elif rep.contact:
        content_type = "contact"
    else:
        return
    auto_text.append({"type": content_type, "message_id": saved_msg.id})
    await dB.set_var(client.me.id, "MSG_AUTOBC", auto_text)

async def text_autogcast(client):
    auto_text_vars = await dB.get_var(client.me.id, "MSG_AUTOBC")
    if not auto_text_vars:
        return []
    list_ids = [int(data["message_id"]) for data in auto_text_vars]
    list_text = []
    for ids in list_ids:
        msg = await client.get_messages("me", ids)
        text = msg.text or msg.caption
        list_text.append(text)
    return list_text

async def get_auto_gcast_messages(client):
    entries = await dB.get_var(client.me.id, "MSG_AUTOBC") or []
    return [await client.get_messages("me", int(e["message_id"])) for e in entries]


async def StartAutoBC(client, user_id, time):
    waktu = pytz.timezone("Asia/Jakarta")
    try:
        await asyncio.sleep(time)
        await dB.set_var(
            user_id, "LAST_BROADCAST", int(datetime.datetime.now(waktu).timestamp())
        )
        while await dB.get_var(user_id, "AUTOBC_STATUS"):
            delay = await dB.get_var(user_id, "DELAY_AUTOBC") or 60
            messages = await get_auto_gcast_messages(client)
            rounds = await dB.get_var(user_id, "AUTOBC_ROUNDS") or 0
            groupss = await dB.get_var(user_id, "DELAY_AUTOBC_GROUP") or 3
            if not messages:
                await client.send_message(
                    "me", f"**❌ Tidak ada pesan yang disimpan.**"
                )
                await dB.set_var(user_id, "AUTOBC_STATUS", False)
                break
            blacklist = set(
                await dB.get_list_from_var(user_id, "BLACKLIST_GCAST") or []
            ) | set(BLACKLIST_GCAST)
            safe_broadcast_shared = random.choice(messages)
            group, failed = 0, 0
            async for dialog in client.get_dialogs():
                if (
                    dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
                    and dialog.chat.id not in blacklist
                ):
                    try:
                        await asyncio.sleep(int(groupss))
                        await safe_broadcast_shared.forward(dialog.chat.id)
                        group += 1
                    except (FloodWait, FloodPremiumWait) as e:
                        if e.value > 180:
                          failed += 1
                          continue
                        else:
                            await asyncio.sleep(e.value)
                            try:
                               await safe_broadcast_shared.forward(dialog.chat.id)
                               group += 1
                            except Exception:
                               failed += 1
                               continue
                    except UserBannedInChannel:
                        failed += 1
                        continue
                    except Exception:
                        failed += 1
                        continue
                        
            rounds += 1
            await dB.set_var(user_id, "AUTOBC_ROUNDS", rounds)
            await dB.set_var(
                user_id, "LAST_BROADCAST", int(datetime.datetime.now(waktu).timestamp())
            )
            SUMMARY_AUTOBC = (
                f"""<i><b>✏️ STATUS AUTO SHARE</b> (BC) ✨</i>

<i><b>-- Putaran Ke</b> {rounds} <b>Kali</b></i>
<i><b>✅ Berhasil Terkirim</b> {group} <b>Chat</b></i>
<i><b>❌ Gagal Terkirim</b> {failed} <b>Chat</b></i>
<i><b>📇 Daftar Blacklist</b> {len(blacklist)} <b>Chat</b></i>

<i><b>⏳ Jeda Groups</b> {groupss} <b>Detik</b></i>
<i><b>⏰ Jeda Putaran</b> {delay} <b>Menit</b></i>"""
             )
            await client.send_message("me", SUMMARY_AUTOBC)
            await asyncio.sleep(delay * 60)
    except Exception as e:
        await client.send_message("me", f"<b><i>Error: {str(e)}</i></b>")
        logger.error(f"[ERROR AUTOBC] USERBOT: {user_id}, Error: {str(e)}")

async def AutoBC():
    waktu = pytz.timezone("Asia/Jakarta")
    Users = 0
    for user_id in session.get_list():
        client = session.get_session(user_id)
        if client:
            now = int(datetime.datetime.now(waktu).timestamp())
            try:
                status = await dB.get_var(user_id, "AUTOBC_STATUS")
                if status:
                    Users += 1
                    last_broadcast = await dB.get_var(user_id, "LAST_BROADCAST") or 0
                    delay = await dB.get_var(user_id, "DELAY_AUTOBC") or 60
                    time = max(0, last_broadcast + (delay * 60) - now)
                    asyncio.create_task(StartAutoBC(client, user_id, time))
            except Exception as e:
                logger.error(f"Error AutoBC For User {user_id}: {e}")
                await bot.send_message(OWNER_ID, f"📝 [ ERROR AUTOBC ] : {str(e)}")
    logger.info(f"**Total Users AutoBC: {Users}**")
    await bot.send_message(OWNER_ID, f"**📝 Total Users AutoBC: {Users}**")
    
async def add_auto_text_fw(message):
    client = message._client
    auto_text = await dB.get_var(client.me.id, "MSG_AUTOFW") or []
    rep = message.reply_to_message
    for item in auto_text:
        try:
            await client.delete_messages("me", item["message_id"])
        except Exception:
            pass
    await dB.set_var(client.me.id, "MSG_AUTOFW", [])
    auto_text = []
    if not rep:
        return
    saved_msg = await client.forward_messages("me", rep.chat.id, rep.id)
    content_type = None
    if rep.text:
        content_type = "text"
    elif rep.photo:
        content_type = "photo"
    elif rep.video:
        content_type = "video"
    elif rep.voice:
        content_type = "voice"
    elif rep.audio:
        content_type = "audio"
    elif rep.document:
        content_type = "document"
    elif rep.sticker:
        content_type = "sticker"
    elif rep.animation:
        content_type = "animation"
    elif rep.contact:
        content_type = "contact"
    else:
        return
    auto_text.append({"type": content_type, "message_id": saved_msg.id})
    await dB.set_var(client.me.id, "MSG_AUTOFW", auto_text)

async def text_autofw(client):
    auto_text_vars = await dB.get_var(client.me.id, "MSG_AUTOFW")
    if not auto_text_vars:
        return []
    list_ids = [int(data["message_id"]) for data in auto_text_vars]
    list_text = []
    for ids in list_ids:
        msg = await client.get_messages("me", ids)
        text = msg.text or msg.caption
        list_text.append(text)
    return list_text
    
async def get_auto_fw_messages(client):
    entries = await dB.get_var(client.me.id, "MSG_AUTOFW") or []
    return [await client.get_messages("me", int(e["message_id"])) for e in entries]

async def StartAutoFW(client, user_id, time):
    waktu = pytz.timezone("Asia/Jakarta")
    try:
        await asyncio.sleep(time)
        await dB.set_var(
            user_id, "LAST_FW", int(datetime.datetime.now(waktu).timestamp())
        )
        while await dB.get_var(user_id, "AUTOFW_STATUS"):
            delay = await dB.get_var(user_id, "DELAY_AUTOFW") or 60
            messages = await get_auto_fw_messages(client)
            rounds = await dB.get_var(user_id, "AUTOFW_ROUNDS") or 0
            groupss = await dB.get_var(user_id, "DELAY_AUTOFW_GROUP") or 3
            if not messages:
                await client.send_message(
                    "me", f"**❌ Tidak ada pesan yang disimpan.**"
                )
                await dB.set_var(user_id, "AUTOFW_STATUS", False)
                return

            blacklist = set(
                await dB.get_list_from_var(user_id, "BLACKLIST_GCAST") or []
            ) | set(BLACKLIST_GCAST)

            safe_broadcast_shared = random.choice(messages)
            group, failed = 0, 0

            async for dialog in client.get_dialogs():
                if (
                    dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
                    and dialog.chat.id not in blacklist
                ):
                    try:
                        await asyncio.sleep(int(groupss))
                        await safe_broadcast_shared.forward(dialog.chat.id)
                        group += 1
                    except (FloodWait, FloodPremiumWait) as e:
                        if e.value > 180:
                          failed += 1
                          continue
                        else:
                            await asyncio.sleep(e.value)
                            try:
                               await safe_broadcast_shared.forward(dialog.chat.id)
                               group += 1
                            except Exception:
                               failed += 1
                               continue
                    except UserBannedInChannel:
                        failed += 1
                        continue
                    except Exception:
                        failed += 1
                        continue

            rounds += 1
            await dB.set_var(user_id, "AUTOFW_ROUNDS", rounds)
            await dB.set_var(
                user_id, "LAST_FW", int(datetime.datetime.now(waktu).timestamp())
            )
            SUMMARY_AUTOFW = (
                f"""<i><b>✏️ STATUS AUTO SHARE</b> (FW) ✨</i>

<i><b>-- Putaran Ke</b> {rounds} <b>Kali</b></i>
<i><b>✅ Berhasil Terkirim</b> {group} <b>Chat</b></i>
<i><b>❌ Gagal Terkirim</b> {failed} <b>Chat</b></i>
<i><b>📇 Daftar Blacklist</b> {len(blacklist)} <b>Chat</b></i>

<i><b>⏳ Jeda Groups</b> {groupss} <b>Detik</b></i>
<i><b>⏰ Jeda Putaran</b> {delay} <b>Menit</b></i>"""
            )
            
            await client.send_message("me", SUMMARY_AUTOFW)
            await asyncio.sleep(delay * 60)
    except Exception as e:
        await client.send_message("me", f"<b><i>Error: {str(e)}</i></b>")
        logger.error(f"[ERROR AUTOBC] USERBOT: {user_id}, Error: {str(e)}")

async def AutoFW():
    waktu = pytz.timezone("Asia/Jakarta")
    Users = 0
    for user_id in session.get_list():
        client = session.get_session(user_id)
        if client:
            now = int(datetime.datetime.now(waktu).timestamp())
            try:
                status = await dB.get_var(user_id, "AUTOFW_STATUS")
                if status:
                    Users += 1
                    last_broadcast = await dB.get_var(user_id, "LAST_FW") or 0
                    delay = await dB.get_var(user_id, "DELAY_AUTOFW") or 60
                    time = max(0, last_broadcast + (delay * 60) - now)
                    asyncio.create_task(StartAutoFW(client, user_id, time))
            except Exception as e:
                logger.error(f"Error Auto FW For User {user_id}: {e}")
                await bot.send_message(OWNER_ID, f"📝 [ ERROR AUTO FW ] : {str(e)}")

    logger.info(f"**Total Users Auto FW: {Users}**")
    await bot.send_message(OWNER_ID, f"**📝 Total Users Auto FW: {Users}**")










