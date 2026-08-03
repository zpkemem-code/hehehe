import traceback

from command import (tungtoriyal, Resiko_Userbot, support_contact, update_kode_all, send_ubot_1, backup, token_cmd, tools_token, support_contact, tungtoriyal, acc_page, callback_alert, cancel_payment, cb_help,
                     cb_notes, cek_expired_cb, cek_status_akun, closed_bot,
                     closed_user, confirm_pay, contact_admins, del_userbot,
                     kurang_tambah, mari_buat_userbot, page_acc, pm_warn,
                     prevnext_userbot, reset_prefix, restart_userbot,
                     selected_topic, start_home, start_home_cb, tools_acc, tools_userbot,
                     user_aggre, show_beli_options,
                     handle_confirm_qris, handle_get_qris, handle_cancel_purchase, 
                     handle_kurang_bulan, handle_tambah_bulan, handle_confirm_durasi)
from clients import bot
from pyrogram_styled import filters
from logs import logger

@bot.on_message(
    filters.regex(
        r"^(🚀 Buat Userbot 🚀|✨ Pembuatan Ulang Userbot|✅ Lanjutkan Buat Userbot|🚫 Resiko Userbot 🚫|🔙 Kembali 🔙|🏠 Home 🏠|💎 Status 💎|🛒 Beli Userbot 🛒|📥 Backup DB 📥|📂 Cek Users 📂|🌐 Update 🌐|♻️ Restart ♻️|📝 Cara Buat 📝|🔑 Token Login 🔑)$"
    )
)
async def menu_button(client, message):
    try:
        text = message.text

        if text in [
            "🚀 Buat Userbot 🚀",
            "✨ Pembuatan Ulang Userbot",
            "✅ Lanjutkan Buat Userbot",
        ]:
            return await mari_buat_userbot(client, message)

        elif text == "🚫 Resiko Userbot 🚫":
            return await Resiko_Userbot(client, message)

        elif text in [
            "🔙 Kembali 🔙",
            "🏠 Home 🏠",
        ]:
            return await start_home(client, message)

        elif text == "💎 Status 💎":
            return await cek_status_akun(client, message)

        elif text == "🛒 Beli Userbot 🛒":
            return await show_beli_options(client, message)

        elif text == "📥 Backup DB 📥":
            return await backup(client, message)

        elif text == "📂 Cek Users 📂":
            return await send_ubot_1(client, message)

        elif text == "🌐 Update 🌐":
            return await update_kode_all(client, message)

        elif text == "♻️ Restart ♻️":
            return await restart_userbot(client, message)

        elif text == "📝 Cara Buat 📝":
            return await tungtoriyal(client, message)

        elif text == "🔑 Token Login 🔑":
            return await token_cmd(client, message)

    except Exception as er:
        logger.error(
            f"Menu button error: {er}"
        )


@bot.on_callback_query()
async def _(client, callback):
    try:
        query = callback.data
        logger.info(f"Name callback query: {query}")

        if query == "create_userbot":
            await callback.answer()
            return await mari_buat_userbot(
                client,
                callback.message
            )

        elif query == "starthome":
            return await start_home_cb(client, callback)

        elif query.startswith("use_token") or query.startswith("revoke_token"):
            return await tools_token(client, callback)

        elif query == "buttonclose":
            return await closed_bot(client, callback)

        elif query == "restart":
            return await restart_userbot(client, callback)
        elif query.startswith("close"):
            return await closed_user(client, callback)
        elif query == ("go_payment"):
            return await user_aggre(client, callback)
        elif query == "kurang_bulan":
            return await handle_kurang_bulan(client, callback)
        elif query == "tambah_bulan":
            return await handle_tambah_bulan(client, callback)
        elif query == "confirm_durasi":
            return await handle_confirm_durasi(client, callback)
        elif query.startswith("kurang") or query.startswith("tambah"):
            return await kurang_tambah(client, callback)
        elif query == ("batal_payment"):
            return await cancel_payment(client, callback)
        elif query.startswith("cb_"):
            return await cb_notes(client, callback)
        elif query.startswith("alertcb_"):
            return await callback_alert(client, callback)
        elif query.startswith("pm_warn"):
            return await pm_warn(client, callback)
        elif query.startswith("del_ubot"):
            return await del_userbot(client, callback)
        elif query.startswith("prev_ub") or query.startswith("next_ub"):
            return await prevnext_userbot(client, callback)
        elif (
            query.startswith("get_otp")
            or query.startswith("get_phone")
            or query.startswith("get_faktor")
            or query.startswith("ub_deak")
            or query.startswith("deak_akun")
        ):
            return await tools_userbot(client, callback)
        elif query.startswith("help_"):
            return await cb_help(client, callback)
        elif query.startswith("cek_masa_aktif"):
            return await cek_expired_cb(client, callback)
        elif query.startswith("selectedtopic_"):
            return await selected_topic(client, callback)
        elif query.startswith("tools_acc"):
            return await tools_acc(client, callback)
        elif query.startswith("acc_page"):
            return await acc_page(client, callback)
        elif query.startswith("bcpg_acc"):
            return await page_acc(client, callback)
        elif query.startswith("confirm_qris_"):
            return await handle_confirm_qris(client, callback)
        elif query.startswith("confirm"):
            return await confirm_pay(client, callback)
        elif query.startswith("get_qris_"):
            return await handle_get_qris(client, callback)
        elif query == "cancel_purchase":
            return await handle_cancel_purchase(client, callback)
    except Exception:
        logger.error(f"Callback error: {traceback.format_exc()}")