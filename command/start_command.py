import random
import pytz

from datetime import datetime

from pyrogram_styled import enums
from pyrogram_styled.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from clients import bot
from config import KYNAN, LOG_SELLER, SUDO_OWNERS
from database import dB, state
from helpers import Basic_Effect, Message, Tools, no_commands
from logs import logger


funny_stick = [
    "CAACAgEAAxkBAAECVMtorJH9GT_szCfdVRtMCGVtCFXRvwACEQADGAtYT0dWChBcckHcHgQ",
    "CAACAgEAAxkBAAECVMxorJIEtyQn8nOSPXmgeU6Gij7YggACBwADNXxZTxvhrdpyc0ayHgQ",
    "CAACAgEAAxkBAAECVMhorJHsaBx3RTY2rzimcbkZgjYLMwACCgADgyaRTOLFx0rARgK0HgQ",
]


def start_menu(is_admin=False):

    buttons = [
        [
            InlineKeyboardButton(
                text="🌐 Update",
                url="https://t.me/FLOOTUST"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Tutup",
                callback_data="buttonclose"
            )
        ]
    ]

    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="👑 Admin Panel",
                    callback_data="admin_panel"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )



async def tungtoriyal(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply(
            "**Bisanya private chat, GOBLOK**"
        )

    textnya = await Message.cara_buat_userbot()

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Tutup",
                    callback_data="buttonclose"
                )
            ]
        ]
    )

    return await message.reply(
        text=textnya,
        reply_markup=buttons,
        disable_web_page_preview=False,
    )



async def Resiko_Userbot(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply(
            "**Bisanya private chat, GOBLOK**"
        )

    text = await Message.RESIKO_MENGGUNAKAN_USERBOT()

    return await message.reply(text)



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



async def start_home(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply(
            "**Chat diprivate aja. GOBLOK!**"
        )


    tz = pytz.timezone(
        "Asia/Jakarta"
    )

    jam = datetime.now(tz).hour


    if 1 <= jam < 2:
        return await message.reply(
            "**TIDUR! lanjut besok lagi 😴**"
        )


    if 4 <= jam < 11:
        waktu = "☀️ Selamat pagi"

    elif 11 <= jam < 15:
        waktu = "🌤 Selamat siang"

    elif 15 <= jam < 18:
        waktu = "🌇 Selamat sore"

    else:
        waktu = "🌙 Selamat malam"



    broadcast = await dB.get_list_from_var(
        client.me.id,
        "BROADCAST"
    )


    user = message.from_user


    if user.id not in broadcast:
        await dB.add_to_var(
            client.me.id,
            "BROADCAST",
            user.id
        )



    buttons = start_menu(
        is_admin=user.id in SUDO_OWNERS
    )


    text = await Message.welcome_message(
        client,
        message
    )


    text += (
        f"\n\n<b>{waktu}</b>, "
        "senang bertemu denganmu disini! "
        "apakah ada yang bisa saya bantu? 🤔"
    )


    text += (
        "\n\nℹ️ saya adalah bot multi client, "
        "yang dimodifikasi untuk memudahkan "
        "broadcast group, channel, users, dll."
    )


    image_start = await gen_image(client)



    if image_start:

        if "video" in image_start:

            return await message.reply_video(
                video=image_start["video"],
                caption=text,
                reply_markup=buttons,
                effect_id=random.choice(Basic_Effect),
            )


        if "photo" in image_start:

            return await message.reply_photo(
                photo=image_start["photo"],
                caption=text,
                reply_markup=buttons,
                effect_id=random.choice(Basic_Effect),
            )


    return await message.reply(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=False,
        effect_id=random.choice(Basic_Effect),
    )



async def button_bot(client, message):

    link = message.text.split(None, 1)[1]

    tujuan, _id = Tools.extract_ids_from_link(link)

    txt = state.get(
        message.from_user.id,
        "edit_reply_markup"
    )

    teks, button = Message.parse_msg_buttons(txt)

    if button:
        button = await Message.create_inline_keyboard(button)

    return await client.edit_message_reply_markup(
        chat_id=tujuan,
        message_id=_id,
        reply_markup=button
    )



async def getid_bot(client, message):

    if len(message.command) < 2:
        return

    query = message.text.split()[1]

    try:

        reply = message.reply_to_message

        media = Tools.get_file_id(reply)

        data = {
            "file_id": media["file_id"],
            "type": media["message_type"]
        }

        state.set(
            message.from_user.id,
            query,
            data
        )

    except Exception as er:

        logger.error(
            str(er)
        )



async def request_bot(client, message):

    user_id = message.from_user.id


    if not message.reply_to_message:

        return await message.reply(
            "<b>Silahkan gunakan /request "
            "dengan membalas pesan.</b>"
        )


    forward = await client.forward_messages(
        chat_id=LOG_SELLER,
        from_chat_id=message.chat.id,
        message_ids=message.reply_to_message.id,
    )


    await dB.set_var(
        forward.id,
        f"REQUEST_{forward.id}",
        user_id
    )


    return await message.reply(
        "<b>Laporan berhasil dikirim.</b>"
    )



async def lapor_bug(client, message):

    if client.me.id != bot.id:
        return


    user_id = message.from_user.id


    if not message.reply_to_message:

        return await message.reply(
            "<b>Balas pesan error dengan /bug</b>"
        )


    forward = await client.forward_messages(
        chat_id=LOG_SELLER,
        from_chat_id=message.chat.id,
        message_ids=message.reply_to_message.id,
    )


    await dB.set_var(
        forward.id,
        f"BUG_{forward.id}",
        user_id
    )


    return await message.reply(
        "<b>Laporan bug berhasil dikirim.</b>"
    )



async def incoming_message(client, message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return


    if message.sticker:
        return


    text = message.text or message.caption or ""


    if (
        text.startswith("/")
        or text in no_commands
        or not text.startswith("#ask")
    ):
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



async def outgoing_reply(client, message):

    rep = message.reply_to_message

    if not rep:
        return


    for prefix in (
        "REQUEST_",
        "BUG_",
        "FORWARD_"
    ):

        user_id = await dB.get_var(
            rep.id,
            f"{prefix}{rep.id}"
        )


        if user_id:

            return await client.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.id
            )



async def start_home_cb(client, callback):

    broadcast = await dB.get_list_from_var(
        client.me.id,
        "BROADCAST"
    )


    user = callback.from_user


    if user.id not in broadcast:

        await dB.add_to_var(
            client.me.id,
            "BROADCAST",
            user.id
        )



    buttons = start_menu(
        is_admin=user.id in SUDO_OWNERS
    )


    text = await Message.welcome_message(
        client,
        callback.message
    )


    return await callback.edit_message_text(
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True,
    )