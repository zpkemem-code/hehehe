import random
import traceback
from datetime import datetime
from gc import get_objects
from time import time
from uuid import uuid4

from pyrogram_styled import enums
from pyrogram_styled.helpers import ikb
from pyrogram_styled.raw.functions import Ping
from pyrogram_styled.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InlineQueryResultArticle,
                            InlineQueryResultCachedAnimation,
                            InlineQueryResultCachedDocument,
                            InlineQueryResultCachedPhoto,
                            InlineQueryResultCachedSticker,
                            InlineQueryResultCachedVideo,
                            InlineQueryResultCachedVoice,
                            InputTextMessageContent)

from clients import bot, navy, session
from config import BOT_NAME, HELPABLE, SUDO_OWNERS, URL_LOGO, USENAME_OWNER
from database import dB, state
from helpers import ButtonUtils, Tools, get_time, paginate_modules, start_time
from logs import logger

from .pmpermit_command import DEFAULT_TEXT, LIMIT

async def help_cmd(client, message):

    if not client.get_arg(message):
        query = "help"
        chat_id = (
            message.chat.id if len(message.command) < 2 else message.text.split()[1]
        )
        try:
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                chat_id,
                bot.me.username,
                query,
            )
            if inline:
                return await message.delete()
        except Exception as error:
            return await message.reply(f"Error: {str(error)}")
    else:
        nama = f"{client.get_arg(message)}"
        pref = client.get_prefix(client.me.id)
        x = next(iter(pref))
        text_help2 = f"**SMALL USERBOT BY @FLOOTUST**"
        if nama in HELPABLE:
            return await message.reply(
                f"{HELPABLE[nama].__HELP__.format(x, text_help2)}",
            )
        else:
            return await message.reply(
                f"<b>Tidak ada modul bernama <code>{nama}</code></b>"
            )


async def inline_cmd(client, message):
    uniq = f"{str(uuid4())}"
    query = f"alive {uniq.split('-')[0]}"
    try:
        inline = await ButtonUtils.send_inline_bot_result(
            message, message.chat.id, bot.me.username, query
        )
        if inline:
            return await message.delete()
    except Exception as error:
        return await message.reply(f"Error: {str(error)}")


async def get_inline_help(result, inline_query):
    user_id = inline_query.from_user.id
    prefix = navy.get_prefix(user_id)
    text_help = (
        await dB.get_var(user_id, "text_help")
        or f"**SMALL USERBOT BY @FLOOTUST**"
    )
    full = f"<a href=tg://user?id={inline_query.from_user.id}>{inline_query.from_user.first_name} {inline_query.from_user.last_name or ''}</a>"
    msg = "👋 hai! saya adalah small userbot, saya bisa membantu pengguna untuk melakukan broadcast dengan lebih mudah dan instant.\n\n✏️ silahkan klik salah satu module dibawah ini untuk memunculkan command, penjelasan dan cara pengunaannya.".format(
        " ".join(prefix),
        len(HELPABLE),
        full,
        text_help,
    )
    result.append(
        InlineQueryResultArticle(
            title="Help Menu!",
            description=" Command Help",
            thumb_url=URL_LOGO,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return result


async def alive_inline(result, inline_query):
    try:
        uniq = str(inline_query.query.split()[1])
        self = inline_query.from_user.id
        pmper = None
        status = None
        start = datetime.now()
        ping = (datetime.now() - start).microseconds / 1000
        upnya = await get_time((time() - start_time))
        me = session.get_session(self)
        try:
            peer = navy._get_my_peer[self]
            users = len(peer["private"])
            group = len(peer["group"])
        except Exception:
            users = random.randrange(await me.get_dialogs_count())
            group = random.randrange(await me.get_dialogs_count())
        await me.invoke(Ping(ping_id=0))
        seles = await dB.get_list_from_var(bot.me.id, "SELLER")
        if self in SUDO_OWNERS:
            status = "[Admins]"
        elif self in seles:
            status = "[Seller]"
        else:
            status = "[Costumer]"
        cekpr = await dB.get_var(self, "PMPERMIT")
        if cekpr:
            pmper = "enable"
        else:
            pmper = "disable"
        get_exp = await dB.get_expired_date(self)
        exp = get_exp.strftime("%d-%m-%Y")
        plan = await dB.get_var(self, "plan")
        is_pro = "pro" if plan == "is_pro" else plan
        txt = f"""
<b>{BOT_NAME}</b>
    <b>status:</b> {status} 
    <b>dc_id:</b> <code>{me.me.dc_id}</code>
    <b>plan_ubot:</b> **{is_pro}**
    <b>ping_dc:</b> <code>{str(ping).replace('.', ',')} ms</code>
    <b>anti_pm:</b> <code>{pmper}</code>
    <b>peer_users:</b> <code>{users} users</code>
    <b>peer_group:</b> <code>{group} group</code>
    <b>peer_ubot:</b> <code>{session.get_count()} ubot</code>
    <b>uptime:</b> <code>{upnya}</code>
    <b>expires:</b> <code>{exp}</code>
"""
        msge = f"<blockquote>{txt}</blockquote>"
        button = ikb([[("Close", f"close alive {uniq}")]])
        media = await dB.get_var(self, "ALIVE_PIC")
        if media:
            file_id = str(media["file_id"])
            type = str(media["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedDocument,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "reply_markup": button,
            }
            if type == "photo":
                kwargs["caption"] = msge
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs["caption"] = msge
                kwargs["video_file_id"] = file_id
                kwargs["title"] = "Video with Button"
            elif type == "animation":
                kwargs["caption"] = msge
                kwargs["animation_file_id"] = file_id
            elif type in ["audio", "document"]:
                kwargs["caption"] = msge
                kwargs["document_file_id"] = file_id
                kwargs["title"] = f"{type.capitalize()} with Button"
            elif type == "sticker":
                kwargs["caption"] = msge
                kwargs["document_file_id"] = file_id
                kwargs["title"] = f"{type.capitalize()} with Button"
            elif type == "voice":
                kwargs["caption"] = msge
                kwargs["voice_file_id"] = file_id
                kwargs["title"] = "Voice with Button"

            result_obj = result_class(**kwargs)
            result.append(result_obj)
        else:
            result.append(
                InlineQueryResultArticle(
                    title=BOT_NAME,
                    description="Get Alive Of Bot.",
                    input_message_content=InputTextMessageContent(msge),
                    thumb_url=URL_LOGO,
                    reply_markup=button,
                )
            )
        return result
    except Exception:
        logger.error(traceback.format_exc())
        return None


async def pmpermit_inline(result, inline_query):
    try:
        client = inline_query.from_user.id
        uniq = str(inline_query.query.split()[1])
        him = int(inline_query.query.split()[2])
        get_id = state.get(uniq, f"idm_{him}")
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        gtext = await dB.get_var(client, "PMTEXT")
        pm_text = gtext if gtext else DEFAULT_TEXT
        pm_warns = await dB.get_var(client, "PMLIMIT") or LIMIT
        Flood = state.get(client, him)
        teks, button = ButtonUtils.parse_msg_buttons(pm_text)
        button = await ButtonUtils.create_inline_keyboard(button, client)
        def_button = ikb(
            [
                [
                    (
                        f"You have a warning {Flood} of {pm_warns} !!",
                        f"pm_warn {client} {him}",
                        "callback_data",
                    )
                ]
            ]
        )
        if button:
            for row in def_button.inline_keyboard:
                button.inline_keyboard.append(row)
        else:
            button = def_button
        tekss = await Tools.escape_filter(message, teks, Tools.parse_words)
        media = await dB.get_var(client, "PMMEDIA")
        if media:
            file_id = str(media["file_id"])
            type = str(media["type"])
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedPhoto,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": tekss,
                "reply_markup": button,
            }
            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["photo_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})
            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    title="PMPermit NOn-Media",
                    input_message_content=InputTextMessageContent(
                        tekss,
                        disable_web_page_preview=True,
                    ),
                    reply_markup=button,
                )
            )
        return result
    except Exception:
        logger.error(f"Pmpermit: {traceback.format_exc()}")
        raise


async def getnote_inline(result, inline_query):
    uniq = str(inline_query.query.split()[1])
    note = str(inline_query.query.split()[2])
    logger.info(f"Data notes: {note}")
    gw = inline_query.from_user.id
    _id = state.get(gw, "in_notes")
    message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
    noteval = await dB.get_var(gw, note, "notes")
    if not noteval:
        return
    btn_close = ikb([[("Close", f"close getnote {uniq} {note}")]])
    state.set("close_notes", "getnote", btn_close)
    try:
        tks = noteval["result"].get("text")
        type = noteval["type"]
        file_id = noteval["file_id"]
        note, button = ButtonUtils.parse_msg_buttons(tks)
        teks = await Tools.escape_filter(message, note, Tools.parse_words)
        button = await ButtonUtils.create_inline_keyboard(button, gw)
        for row in btn_close.inline_keyboard:
            button.inline_keyboard.append(row)
        if type != "text":
            type_mapping = {
                "photo": InlineQueryResultCachedPhoto,
                "video": InlineQueryResultCachedVideo,
                "animation": InlineQueryResultCachedAnimation,
                "audio": InlineQueryResultCachedDocument,
                "document": InlineQueryResultCachedDocument,
                "sticker": InlineQueryResultCachedSticker,
                "voice": InlineQueryResultCachedVoice,
            }
            result_class = type_mapping[type]
            kwargs = {
                "id": str(uuid4()),
                "caption": teks,
                "reply_markup": button,
                "parse_mode": enums.ParseMode.HTML,
            }

            if type == "photo":
                kwargs["photo_file_id"] = file_id
            elif type == "video":
                kwargs.update({"video_file_id": file_id, "title": "Video with Button"})
            elif type == "animation":
                kwargs["animation_file_id"] = file_id
            elif type == "audio":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "document":
                kwargs.update(
                    {"document_file_id": file_id, "title": "Document with Button"}
                )
            elif type == "sticker":
                kwargs["sticker_file_id"] = file_id
            elif type == "voice":
                kwargs.update({"voice_file_id": file_id, "title": "Voice with Button"})

            result.append(result_class(**kwargs))
        else:
            result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Send Inline!",
                    reply_markup=button,
                    input_message_content=InputTextMessageContent(
                        teks,
                        parse_mode=enums.ParseMode.HTML,
                    ),
                )
            )
        return result
    except Exception:
        logger.error(f"Error notes: {traceback.format_exc()}")


async def inline_autobc(results, inline):
    chat = int(inline.query.split()[1])
    _id = inline.query.split()[2]
    try:
        message = next((obj for obj in get_objects() if id(obj) == int(_id)), None)
        if not message:
            return results
        client = message._client
        per_page = 50
        page = 0
        keyboard = []
        row = []
        title, data = await client.parse_topic(chat)
        try:
            sliced = data[page * per_page : (page + 1) * per_page]
            caption = f"<blockquote expandable><b>List Topic {title}\nSilahkan pilih topic untuk diatur:\n</b>"
            for idx, topic in enumerate(sliced):
                caption += f"<b>{idx + 1}. {topic['title']}</b>\n"
                button = InlineKeyboardButton(
                    text=str(idx + 1),
                    callback_data=f"selectedtopic_{chat}_{topic['id']}_{topic['title']}",
                )
                row.append(button)
                if (idx + 1) % 5 == 0:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            caption += "</blockquote>"
        except Exception:
            logger.error(f"Inline autobc: {traceback.format_exc()}")
            return None
        results.append(
            InlineQueryResultArticle(
                title="Select Topic",
                input_message_content=InputTextMessageContent(caption),
                reply_markup=reply_markup,
            )
        )
        return results
    except Exception:
        logger.error(f"Inline autobc: {traceback.format_exc()}")
        return None




