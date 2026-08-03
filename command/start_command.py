import random
import pytz

from datetime import datetime

from pyrogram_styled import enums
from pyrogram_styled.helpers import ikb

from clients import bot
from config import KYNAN, LOG_SELLER, SUDO_OWNERS

from database import dB, state
from helpers import (
    Basic_Effect,
    ButtonUtils,
    Message,
    Tools,
    no_commands,
)

from logs import logger



# ==============================
# TUTORIAL USERBOT
# ==============================

async def tungtoriyal(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply(
            "**Bisanya private chat, GOBLOK**"
        )


    text = await Message.cara_buat_userbot()


    buttons = ikb([
        [
            (
                "❌ Tutup",
                "buttonclose"
            )
        ]
    ])


    return await message.reply(
        text=text,
        reply_markup=buttons
    )



# ==============================
# RESIKO USERBOT
# ==============================

async def Resiko_Userbot(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply(
            "**Bisanya private chat, GOBLOK**"
        )


    text = await Message.RESIKO_MENGGUNAKAN_USERBOT()


    return await message.reply(
        text
    )



# ==============================
# MEDIA START
# ==============================

async def gen_image(client):

    file_id = await dB.get_var(
        client.me.id,
        "IMAGE_START"
    )


    if not file_id:
        return None



    if file_id.startswith("AgAC"):

        return {
            "photo": file_id
        }


    return {
        "video": file_id
    }



# ==============================
# SET MEDIA START
# ==============================

async def setimg_start(client, message):

    user = (
        message.from_user
        if message.from_user
        else message.sender_chat
    )


    if not user:
        return


    if user.id not in KYNAN:
        return



    if message.reply_to_message:


        proses = await message.reply(
            "**Tunggu sebentar..**"
        )


        reply = message.reply_to_message



        if not reply.media:

            return await proses.edit(
                "**Balas foto atau video.**"
            )



        data = Tools.get_file_id(reply)


        file_id = data.get(
            "file_id"
        )


        await dB.set_var(
            client.me.id,
            "IMAGE_START",
            file_id
        )



        return await proses.edit(
            "**Media start berhasil disimpan.**"
        )




    if len(message.command) > 1:


        arg = message.command[1].lower()



        if arg in [
            "off",
            "disable"
        ]:


            await dB.remove_var(
                client.me.id,
                "IMAGE_START"
            )


            return await message.reply(
                "**Media start dimatikan.**"
            )



    return await message.reply(
        "**Balas foto/video atau gunakan `/setimg off`.**"
    )



# ==============================
# SET ADS
# ==============================

async def setads_bot(client, message):

    user = (
        message.from_user
        if message.from_user
        else message.sender_chat
    )


    if not user:
        return



    if user.id not in KYNAN:
        return




    if not message.reply_to_message:

        return await message.reply(
            "**Balas pesan teks terlebih dahulu.**"
        )



    text = (
        message.reply_to_message.text
        or
        message.reply_to_message.caption
        or ""
    )



    await dB.set_var(
        client.me.id,
        "ads",
        text
    )



    return await message.reply(
        "**Ads berhasil disimpan.**"
    )



# ==============================
# START BOT
# ==============================

async def start_home(client, message):


    if message.chat.type != enums.ChatType.PRIVATE:

        return await message.reply(
            "**Gunakan bot lewat private chat.**"
        )



    tz = pytz.timezone(
        "Asia/Jakarta"
    )


    jam = datetime.now(tz).hour



    if 4 <= jam < 11:

        waktu = "☀ Selamat pagi"


    elif 11 <= jam < 15:

        waktu = "🌤 Selamat siang"


    elif 15 <= jam < 18:

        waktu = "🌇 Selamat sore"


    else:

        waktu = "🌙 Selamat malam"




    users = await dB.get_list_from_var(
        client.me.id,
        "BROADCAST"
    )



    if message.from_user.id not in users:

        await dB.add_to_var(
            client.me.id,
            "BROADCAST",
            message.from_user.id
        )




    buttons = ButtonUtils.start_menu(
        is_admin=(
            message.from_user.id
            in SUDO_OWNERS
        )
    )



    text = await Message.welcome_message(
        client,
        message
    )



    text += (
        f"\n\n<b>{waktu}</b>"
        "\nSenang bertemu denganmu disini 🤔"
    )



    image = await gen_image(
        client
    )



    if image:


        if "photo" in image:

            return await message.reply_photo(
                photo=image["photo"],
                caption=text,
                reply_markup=buttons
            )



        if "video" in image:

            return await message.reply_video(
                video=image["video"],
                caption=text,
                reply_markup=buttons
            )



    return await message.reply(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True
    )

# ==============================
# EDIT BUTTON MARKUP
# ==============================

async def button_bot(client, message):

    if not message.text:
        return


    args = message.text.split(
        None,
        1
    )


    if len(args) < 2:
        return await message.reply(
            "**Masukkan link pesan.**"
        )


    link = args[1]


    tujuan, msg_id = Tools.extract_ids_from_link(
        link
    )


    data = state.get(
        message.from_user.id,
        "edit_reply_markup"
    )


    if not data:
        return await message.reply(
            "**Tidak ada data tombol.**"
        )



    teks, button = ButtonUtils.parse_msg_buttons(
        data
    )



    if button:

        button = await ButtonUtils.create_inline_keyboard(
            button
        )



    return await client.edit_message_reply_markup(
        chat_id=tujuan,
        message_id=msg_id,
        reply_markup=button
    )



# ==============================
# GET MEDIA ID
# ==============================

async def getid_bot(client, message):

    if len(message.command) < 2:
        return



    if not message.reply_to_message:
        return await message.reply(
            "**Balas pesan media.**"
        )



    query = message.command[1]



    try:

        media = Tools.get_file_id(
            message.reply_to_message
        )



        data = {

            "file_id":
                media.get("file_id"),

            "type":
                media.get("message_type")
        }



        state.set(
            message.from_user.id,
            query,
            data
        )



        return await message.reply(
            "**ID berhasil disimpan.**"
        )



    except Exception as e:

        logger.error(
            str(e)
        )



# ==============================
# REQUEST FEATURE
# ==============================

async def request_bot(client, message):

    user_id = message.from_user.id



    if not message.reply_to_message:

        return await message.reply(
            "<b>Silahkan reply pesan untuk request fitur.</b>"
        )



    forward = await client.forward_messages(

        chat_id=LOG_SELLER,

        from_chat_id=message.chat.id,

        message_ids=message.reply_to_message.id

    )



    await dB.set_var(

        forward.id,

        f"REQUEST_{forward.id}",

        user_id

    )



    return await message.reply(
        "<b>Request berhasil dikirim.</b>"
    )



# ==============================
# LAPOR BUG
# ==============================

async def lapor_bug(client, message):

    if client.me.id != bot.id:
        return



    user_id = message.from_user.id



    if not message.reply_to_message:

        return await message.reply(
            "<b>Reply pesan error terlebih dahulu.</b>"
        )



    forward = await client.forward_messages(

        chat_id=LOG_SELLER,

        from_chat_id=message.chat.id,

        message_ids=message.reply_to_message.id

    )



    await dB.set_var(

        forward.id,

        f"BUG_{forward.id}",

        user_id

    )



    return await message.reply(
        "<b>Laporan bug berhasil dikirim.</b>"
    )



# ==============================
# INCOMING ASK
# ==============================

async def incoming_message(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return



    if message.sticker:
        return



    text = (
        message.text
        or
        message.caption
        or ""
    )



    if not text:
        return



    if text.startswith("/"):
        return



    if text in no_commands:
        return



    if not text.startswith("#ask"):
        return




    forward = await client.forward_messages(

        chat_id=LOG_SELLER,

        from_chat_id=message.chat.id,

        message_ids=message.id

    )



    await dB.set_var(

        forward.id,

        f"FORWARD_{forward.id}",

        message.from_user.id

    )



# ==============================
# REPLY ADMIN
# ==============================

async def outgoing_reply(client, message):

    if not message.reply_to_message:
        return



    reply = message.reply_to_message



    for prefix in [

        "REQUEST_",

        "BUG_",

        "FORWARD_"

    ]:


        user_id = await dB.get_var(

            reply.id,

            f"{prefix}{reply.id}"

        )



        if user_id:


            return await client.copy_message(

                chat_id=user_id,

                from_chat_id=message.chat.id,

                message_id=message.id

            )



# ==============================
# CALLBACK START
# ==============================

async def start_home_cb(client, callback):


    users = await dB.get_list_from_var(

        client.me.id,

        "BROADCAST"

    )



    if callback.from_user.id not in users:

        await dB.add_to_var(

            client.me.id,

            "BROADCAST",

            callback.from_user.id

        )



    buttons = ButtonUtils.start_menu(

        is_admin=(

            callback.from_user.id

            in SUDO_OWNERS

        )

    )



    text = await Message.welcome_message(

        client,

        callback.message

    )



    return await callback.edit_message_text(

        text=text,

        reply_markup=buttons,

        disable_web_page_preview=True

    )