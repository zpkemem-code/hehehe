import asyncio
import importlib
import traceback
import aiohttp
import json
from datetime import datetime, timedelta

import hydrogram
from dateutil.relativedelta import relativedelta
from pyrogram_styled.helpers import ikb
from pyrogram_styled.types import (KeyboardButton, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from pytz import timezone

from clients import UserBot, bot, navy, session
from config import (AKSES_DEPLOY, API_HASH, API_ID, BOT_ID, LOG_SELLER,
                    MAX_BOT, SUDO_OWNERS, WAJIB_JOIN, API_KEY)
from database import dB, state
from helpers import ButtonUtils, Message
from logs import logger
from plugins import _PLUGINS


async def setExpiredUser(user_id):
    if user_id in SUDO_OWNERS:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=12)
        await dB.set_expired_date(user_id, expired)
    else:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=1)
        await dB.set_expired_date(user_id, expired)


async def mari_buat_userbot(client, message):

    if hasattr(message, "message"):
        message = message.message

    user_id = message.from_user.id
    
    # CEK APAKAH USER SUDAH PUNYA AKSES (SUDAH BAYAR)
    user_plan = await dB.get_var(user_id, "plan")
    user_expired = await dB.get_expired_date(user_id)
    now = datetime.now(timezone("Asia/Jakarta"))
    
    if user_plan and user_expired and now < user_expired:
        # User sudah punya akses, langsung buat userbot
        return await create_userbots(client, message)
    
    # CEK PENDING DEPOSIT
    from database import state
    pending = state.get(user_id, "pending_deposit")
    if pending:
        text = f"""
<b>⏳ ANDA MEMILIKI PEMBAYARAN PENDING</b>

<blockquote expandable>Anda memiliki pembayaran yang belum selesai.

<b>🆔 ID Transaksi:</b> <code>{pending.get('id')}</code>
<b>💰 Jumlah:</b> Rp{pending.get('amount'):,}

Silahkan selesaikan pembayaran Anda terlebih dahulu.
Klik tombol Konfirmasi Pembayaran setelah transfer.</blockquote>
"""
        buttons = ikb([
            [("✅ Konfirmasi Pembayaran", f"confirm_qris_{pending.get('id')}_{pending.get('type')}")],
            [("❌ Cancel", "cancel_purchase")]
        ])
        return await message.reply(text, reply_markup=buttons)
    
    if session.get_count() == MAX_BOT:
        buttons = ikb(
            [[("💬 Hubungi Admins", "calladmins")], [("🔙 Back", "starthome")]]
        )
        return await message.reply(
            f"""
<b>❌ Tidak dapat membuat Userbot !</b>

<b>📚 Karena Telah Mencapai Yang Telah Di Tentukan : {session.get_count()}</b>

<b>👮‍♂ Silakan Hubungi Admins . </b>
""",
            reply_markup=buttons,
        )
    get_exp_user = await dB.get_expired_date(user_id)
    now = datetime.now(timezone("Asia/Jakarta"))
    if get_exp_user and now >= get_exp_user:
        await message.reply(
            f"**Masa aktif kamu `{get_exp_user.astimezone(timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M')}` sudah melebihi batas waktu yang ditentukan, jadi kamu tidak bisa memasang userbot lagi\n\nSilahkan lakukan pembayaran lagi untuk pemasangan userbot!!**",
            reply_markup=ikb([[("🔙 Back", "starthome")]]),
        )
        return await dB.rem_expired_date(user_id)
    if not get_exp_user and user_id not in AKSES_DEPLOY:
        text = f"<blockquote expandable><b>{await Message.policy_message()}</b>"
        text += "\n\n<i><b>SAYANGNYA, anda belum memiliki akses untuk membuat userbot kami, silahkan untuk membeli terlebih dahulu.</b></i>"
        text += "\n\n<i><b>Ads: [CHANNEL RESMI FLOOTUST](https://t.me/FLOOTUST)</b></i></blockquote>"
        
        from pyrogram_styled.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text="🛒 Beli Userbot 🛒")],
                [KeyboardButton(text="🔙 Kembali 🔙")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        return await message.reply(text, reply_markup=keyboard)
    else:
        return await create_userbots(client, message)


async def show_beli_options(client, message):
    """Menampilkan pilihan durasi dengan tombol + dan -"""
    from pyrogram_styled.helpers import ikb
    
    # State untuk menyimpan bulan dan plan
    user_id = message.from_user.id
    state.set(user_id, "temp_bulan", 1)
    state.set(user_id, "temp_plan", "basic")  # basic = 1 bulan, pro = permanen
    
    text = """
<b>🤖 PILIH DURASI USERBOT</b>

<blockquote expandable>Silahkan pilih durasi yang anda inginkan:

<b>📦 Paket:</b> Basic
<b>📅 Durasi:</b> 1 Bulan
<b>💰 Harga per bulan:</b> Rp10.000
<b>💵 Total Tagihan:</b> Rp10.000

Klik + untuk menambah durasi, - untuk mengurangi.</blockquote>
"""
    
    buttons = ikb([
        [("➖", "kurang_bulan"), ("📅 1 Bulan", "tampil_bulan"), ("➕", "tambah_bulan")],
        [("✅ Konfirmasi", "confirm_durasi"), ("❌ Cancel", "cancel_purchase")]
    ])
    
    await message.reply(text, reply_markup=buttons, disable_web_page_preview=True)


async def handle_kurang_bulan(client, callback_query):
    """Handler untuk tombol kurang bulan"""
    user_id = callback_query.from_user.id
    
    bulan = state.get(user_id, "temp_bulan") or 1
    plan = state.get(user_id, "temp_plan") or "basic"
    
    if bulan > 1:
        bulan -= 1
        state.set(user_id, "temp_bulan", bulan)
    
    # Harga per bulan
    if plan == "basic":
        harga_per_bulan = 500
        paket = "Basic"
    else:  # permanen
        harga_per_bulan = 100000
        paket = "PERMANEN"
    
    # Total (TANPA DISKON)
    total = harga_per_bulan * bulan
    
    text = f"""
<b>🤖 PILIH DURASI USERBOT</b>

<blockquote expandable>Silahkan pilih durasi yang anda inginkan:

<b>📦 Paket:</b> {paket}
<b>📅 Durasi:</b> {bulan} Bulan
<b>💰 Harga per bulan:</b> Rp{harga_per_bulan:,}
<b>💵 Total Tagihan:</b> Rp{total:,}

Klik + untuk menambah durasi, - untuk mengurangi.</blockquote>
"""
    
    buttons = ikb([
        [("➖", "kurang_bulan"), (f"📅 {bulan} Bulan", "tampil_bulan"), ("➕", "tambah_bulan")],
        [("✅ Konfirmasi", "confirm_durasi"), ("❌ Cancel", "cancel_purchase")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=buttons, disable_web_page_preview=True)


async def handle_tambah_bulan(client, callback_query):
    """Handler untuk tombol tambah bulan"""
    user_id = callback_query.from_user.id
    
    bulan = state.get(user_id, "temp_bulan") or 1
    plan = state.get(user_id, "temp_plan") or "basic"
    
    if bulan < 24:  # Maksimal 24 bulan
        bulan += 1
        state.set(user_id, "temp_bulan", bulan)
    
    # Harga per bulan
    if plan == "basic":
        harga_per_bulan = 500
        paket = "Basic"
    else:  # permanen
        harga_per_bulan = 100000
        paket = "PERMANEN"
    
    # Total (TANPA DISKON)
    total = harga_per_bulan * bulan
    
    text = f"""
<b>🤖 PILIH DURASI USERBOT</b>

<blockquote expandable>Silahkan pilih durasi yang anda inginkan:

<b>📦 Paket:</b> {paket}
<b>📅 Durasi:</b> {bulan} Bulan
<b>💰 Harga per bulan:</b> Rp{harga_per_bulan:,}
<b>💵 Total Tagihan:</b> Rp{total:,}

Klik + untuk menambah durasi, - untuk mengurangi.</blockquote>
"""
    
    buttons = ikb([
        [("➖", "kurang_bulan"), (f"📅 {bulan} Bulan", "tampil_bulan"), ("➕", "tambah_bulan")],
        [("✅ Konfirmasi", "confirm_durasi"), ("❌ Cancel", "cancel_purchase")]
    ])
    
    await callback_query.edit_message_text(text, reply_markup=buttons, disable_web_page_preview=True)


async def handle_confirm_durasi(client, callback_query):
    """Handler untuk konfirmasi durasi - lanjut ke pembayaran QRIS"""
    user_id = callback_query.from_user.id
    
    bulan = state.get(user_id, "temp_bulan") or 1
    plan = state.get(user_id, "temp_plan") or "basic"
    
    # Harga per bulan
    if plan == "basic":
        harga_per_bulan = 500
    else:
        harga_per_bulan = 100000
    
    # Total (TANPA DISKON)
    total = harga_per_bulan * bulan
    
    # Simpan data ke state untuk diproses
    state.set(user_id, "confirm_bulan", bulan)
    state.set(user_id, "confirm_total", total)
    state.set(user_id, "confirm_plan", plan)
    
    # Lanjut ke pembuatan QRIS
    await callback_query.message.delete()
    
    # Panggil fungsi buat QRIS dengan total harga
    await create_qris_and_send(client, callback_query, total, bulan, plan)


async def create_qris_and_send(client, callback_query, amount, bulan, plan):
    """Membuat QRIS dan mengirim ke user"""
    from pyrogram_styled.types import InlineKeyboardButton, InlineKeyboardMarkup
    
    user_id = callback_query.from_user.id
    
    # CEK APAKAH SUDAH ADA PENDING DEPOSIT
    pending = state.get(user_id, "pending_deposit")
    if pending:
        await callback_query.answer("⚠️ Anda sudah memiliki pending deposit! Silahkan selesaikan pembayaran.", show_alert=True)
        return
    
    await callback_query.answer("Membuat QRIS...")
    
    # Buat deposit QRIS
    qris_data = await create_qris_deposit(amount)
    
    if qris_data and qris_data.get("success"):
        deposit = qris_data.get("deposit", {})
        deposit_id = deposit.get("id", "Unknown")
        qr_image = deposit.get("qr_image", "")
        total_payment = deposit.get("total_payment", amount)
        
        # Simpan durasi ke pending deposit
        state.set(user_id, "pending_deposit", {
            "id": deposit_id,
            "amount": total_payment,
            "type": f"{bulan}bulan" if plan == "basic" else "permanen",
            "bulan": bulan,
            "plan": plan,
            "timestamp": datetime.now().timestamp()
        })
        
        text = f"""
<b>✅ KONFIRMASI PEMESANAN</b>

<blockquote expandable><b>📦 Paket:</b> {'Basic' if plan == 'basic' else 'PERMANEN'}
<b>📅 Durasi:</b> {bulan} Bulan
<b>💰 Total Pembayaran:</b> Rp{total_payment:,}
<b>🆔 ID Transaksi:</b> {deposit_id}

<b>📱 Scan QRIS di bawah untuk membayar:</b></blockquote>

⚠️ QRIS ini hanya valid 1x penggunaan.
✅ Setelah bayar, klik tombol KONFIRMASI PEMBAYARAN
"""
        
        buttons = [
            [InlineKeyboardButton(text="✅ Konfirmasi Pembayaran", callback_data=f"confirm_qris_{deposit_id}_{bulan}bulan")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_purchase")]
        ]
        
        if qr_image:
            msg = await client.send_photo(
                callback_query.message.chat.id,
                photo=qr_image,
                caption=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            state.set(user_id, "last_qris_msg", msg.id)
        else:
            text += f"\n\nSilahkan hubungi admin untuk mendapatkan QRIS."
            buttons.insert(0, [InlineKeyboardButton(text="📞 Hubungi Admin", url="https://t.me/FLOOTUST_Admin")])
            msg = await client.send_message(
                callback_query.message.chat.id,
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                disable_web_page_preview=True
            )
            state.set(user_id, "last_qris_msg", msg.id)
    else:
        text = """
<b>⚠️ SISTEM SEDANG ERROR</b>

<blockquote expandable>Maaf, sistem pembayaran sedang mengalami gangguan.
Silahkan hubungi admin untuk melakukan pembayaran manual.</blockquote>
"""
        buttons = ikb([
            [("📞 Hubungi Admin", "https://t.me/FLOOTUST_Admin")],
            [("❌ Cancel", "cancel_purchase")]
        ])
        await client.send_message(
            callback_query.message.chat.id,
            text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )


async def create_qris_deposit(amount: int):
    """Membuat deposit QRIS melalui API"""
    url = "https://digitalpediah2h.orderhostid.my.id/api/deposit/create"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "amount": amount
    }
    
    logger.info(f"Creating QRIS deposit for amount: {amount}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                logger.info(f"QRIS API Response Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"QRIS API Response: {result}")
                    return result
                else:
                    text = await response.text()
                    logger.error(f"QRIS API Error: {response.status} - {text}")
                    return None
    except Exception as e:
        logger.error(f"Error creating QRIS deposit: {e}")
        return None


async def check_qris_status(deposit_id: str):
    """Cek status deposit QRIS - menggunakan POST method"""
    url = "https://digitalpediah2h.orderhostid.my.id/api/deposit/status"
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "deposit_id": deposit_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"QRIS Status Response: {result}")
                    return result
                else:
                    logger.error(f"QRIS Status Error: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error checking QRIS status: {e}")
        return None


async def handle_confirm_qris(client, callback_query):
    """Handler untuk konfirmasi pembayaran QRIS - AUTO CEK DAN AKTIVASI"""
    from database import state
    from pyrogram_styled.helpers import ikb
    
    await callback_query.answer("Memeriksa pembayaran...")
    
    # Parse data: confirm_qris_{deposit_id}_{duration}
    raw_data = callback_query.data.replace("confirm_qris_", "")
    data_parts = raw_data.split("_")
    
    logger.info(f"Confirm QRIS raw data: {raw_data}")
    logger.info(f"Confirm QRIS parts: {data_parts}")
    
    if len(data_parts) < 2:
        await callback_query.answer("Data transaksi tidak valid!", show_alert=True)
        return
    
    deposit_id = data_parts[0]
    duration_type = data_parts[1] if len(data_parts) > 1 else "1bulan"
    user_id = callback_query.from_user.id
    
    logger.info(f"Checking payment - User: {user_id}, Deposit ID: {deposit_id}, Duration: {duration_type}")
    
    # Cek status pembayaran ke API
    status_data = await check_qris_status(deposit_id)
    
    if status_data and status_data.get("success"):
        status = status_data.get("status")
        message_status = status_data.get("message", "")
        
        logger.info(f"Payment status: {status}, Message: {message_status}")
        
        if status == "success" or "sukses" in message_status.lower() or "paid" in message_status.lower() or "success" in message_status.lower():
            # PEMBAYARAN SUKSES - LANGSUNG AKTIVASI
            await activate_userbot_access(user_id, duration_type, deposit_id)
            
            text = """
<b>✅ PEMBAYARAN BERHASIL!</b>

<blockquote expandable>Terima kasih telah melakukan pembayaran.
Akses Anda telah diaktifkan.

<b>🚀 Sekarang Anda bisa membuat Userbot:</b>
Klik tombol <b>🚀 Buat Userbot 🚀</b> di menu utama.</blockquote>
"""
            buttons = ikb([
                [("🏠 Kembali ke Menu", "starthome")]
            ])
            
            try:
                # Coba edit caption jika ada photo
                await callback_query.edit_message_caption(
                    caption=text,
                    reply_markup=buttons
                )
            except:
                try:
                    # Coba edit text jika tidak ada photo
                    await callback_query.edit_message_text(
                        text,
                        reply_markup=buttons
                    )
                except Exception as e:
                    logger.error(f"Error editing message: {e}")
                    # Kirim pesan baru
                    await client.send_message(
                        user_id,
                        text,
                        reply_markup=buttons
                    )
            
            # Hapus pending deposit
            state.set(user_id, "pending_deposit", None)
            state.set(user_id, "last_qris_msg", None)
            
        else:
            # Masih pending / belum dibayar
            text = f"""
<b>⏳ MENUNGGU PEMBAYARAN</b>

<blockquote expandable>Pembayaran Anda sedang menunggu konfirmasi.

<b>🆔 ID Transaksi:</b> <code>{deposit_id}</code>
<b>📊 Status:</b> {message_status or 'pending'}

Silahkan selesaikan pembayaran Anda terlebih dahulu.
Setelah transfer, klik tombol Cek Lagi.</blockquote>
"""
            buttons = ikb([
                [("🔄 Cek Lagi", f"confirm_qris_{deposit_id}_{duration_type}")],
                [("❌ Cancel", "cancel_purchase")]
            ])
            await callback_query.answer("Pembayaran belum selesai. Silahkan selesaikan pembayaran Anda.", show_alert=True)
            
            try:
                await callback_query.edit_message_text(text, reply_markup=buttons)
            except:
                await callback_query.message.reply(text, reply_markup=buttons)
    else:
        error_msg = "Gagal memeriksa status. Silahkan coba lagi."
        if status_data:
            error_msg = f"Status: {status_data.get('message', 'Unknown error')}"
        await callback_query.answer(error_msg, show_alert=True)
        logger.error(f"QRIS check failed: {status_data}")
        
        
async def handle_get_qris(client, callback_query):
    """Handler untuk mengambil gambar QRIS"""
    deposit_id = callback_query.data.replace("get_qris_", "")
    
    # Ambil data deposit dari API
    url = f"https://digitalpediah2h.orderhostid.my.id/api/deposit/status/{deposit_id}"
    headers = {"x-api-key": API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        qr_image = data.get("deposit", {}).get("qr_image")
                        if qr_image:
                            await callback_query.answer("Mengirim QRIS...")
                            await client.send_photo(
                                callback_query.message.chat.id,
                                photo=qr_image,
                                caption="Silahkan scan QRIS untuk melakukan pembayaran."
                            )
                            return
    except Exception as e:
        logger.error(f"Error getting QRIS: {e}")
    
    await callback_query.answer("Gagal mengambil QRIS. Silahkan hubungi admin.", show_alert=True)
    

async def handle_cancel_purchase(client, callback_query):
    """Handler untuk membatalkan pembelian dari berbagai tahap"""
    from database import state
    from helpers import ButtonUtils
    from config import SUDO_OWNERS
    
    user_id = callback_query.from_user.id
    
    await callback_query.answer("Pembelian dibatalkan")
    
    # Hapus pending deposit dari state
    pending = state.get(user_id, "pending_deposit")
    if pending:
        state.set(user_id, "pending_deposit", None)
    
    # Hapus ID pesan QRIS
    last_qris = state.get(user_id, "last_qris_msg")
    if last_qris:
        try:
            await client.delete_messages(callback_query.message.chat.id, last_qris)
        except:
            pass
        state.set(user_id, "last_qris_msg", None)
    
    # Kembali ke menu utama
    if user_id in SUDO_OWNERS:
        buttons = ButtonUtils.start_menu(is_admin=True)
    else:
        buttons = ButtonUtils.start_menu(is_admin=False)
    
    text = "✅ Pembelian telah dibatalkan.\n\nSilahkan pilih menu lain."
    
    try:
        await callback_query.edit_message_text(text, reply_markup=buttons)
    except:
        await callback_query.message.delete()
        await client.send_message(user_id, text, reply_markup=buttons)
    
    
async def activate_userbot_access(user_id: int, duration_type: str, deposit_id: str = None):
    """Aktivasi akses userbot setelah pembayaran sukses"""
    now = datetime.now(timezone("Asia/Jakarta"))
    
    if duration_type == "1bulan":
        expired = now + relativedelta(months=1)
        plan = "basic"
        duration_text = "1 Bulan"
    else:  # permanen
        expired = now + relativedelta(years=100)  # 100 tahun = permanen
        plan = "pro"
        duration_text = "PERMANEN"
    
    # Set expired date dan plan
    await dB.set_expired_date(user_id, expired)
    await dB.set_var(user_id, "plan", plan)
    
    # Tambahkan ke AKSES_DEPLOY jika belum ada
    if user_id not in AKSES_DEPLOY:
        AKSES_DEPLOY.append(user_id)
    
    # Kirim notifikasi ke user
    text = f"""
<b>✅ PEMBAYARAN BERHASIL!</b>

<blockquote expandable>Terima kasih telah melakukan pembayaran.

<b>📋 Detail Akses Anda:</b>
• ID: <code>{user_id}</code>
• Plan: <b>{plan.upper()}</b>
• Durasi: <b>{duration_text}</b>
• Masa Aktif: {expired.strftime('%Y-%m-%d %H:%M')} WIB

<b>🚀 Cara Membuat Userbot:</b>
Klik tombol <b>🚀 Buat Userbot 🚀</b> di menu utama untuk memulai pembuatan userbot.

<b>⚠️ Catatan:</b>
• Simpan baik-baik akses Anda
• Jika ada kendala, hubungi admin</blockquote>
"""
    
    await bot.send_message(user_id, text)
    
    # Kirim notifikasi ke admin
    await bot.send_message(
        LOG_SELLER,
        f"""
<b>✅ PEMBAYARAN BERHASIL - AKTIVASI USERBOT</b>
<b>├ User ID:</b> <code>{user_id}</code>
<b>├ Deposit ID:</b> <code>{deposit_id or '-'}</code>
<b>├ Durasi:</b> {duration_text}
<b>├ Plan:</b> {plan.upper()}
<b>├ Masa Aktif:</b> {expired.strftime('%Y-%m-%d %H:%M')} WIB
<b>╰ Status:</b> ✅ AKTIF
"""
    )
    
    logger.info(f"User {user_id} activated with {duration_type} plan")
    return True
    
    
async def create_userbots(client, message):
    try:
        user_id = message.from_user.id
        anu = ReplyKeyboardMarkup(
            [
                [KeyboardButton(text="📞 Kirim Kontak Saya 📞", request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        try:
            phone = await client.ask(
                user_id,
                f"<blockquote><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>",
                reply_markup=anu,
            )
            phone_number = phone.contact.phone_number
        except AttributeError:
            try:
                phone = await client.ask(
                    user_id,
                    f"<blockquote><b>Silahkan klik tombol <u>Kontak Saya</u> untuk mengirimkan Nomor Telepon Telegram Anda.</b></blockquote>",
                    reply_markup=anu,
                )
                phone_number = phone.contact.phone_number
            except Exception:
                return await bot.send_message(
                    user_id,
                    "<blockquote><b>PEA, punya mata dipake buat baca!! jangan BOKEP mulu.</b></blockquote>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
        new_client = hydrogram.Client(
            name=str(user_id),
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True,
        )
        await asyncio.sleep(1)
        get_otp = await client.send_message(
            user_id,
            f"<b> • Bot Kami Sedang Mengirim Kode OTP Ke akun Anda. Silahkan Tunggu beberapa saat...</b>",
            reply_markup=ReplyKeyboardRemove(),
        )
        await new_client.connect()
        try:
            code = await new_client.send_code(phone_number.strip())
        except hydrogram.errors.exceptions.bad_request_400.ApiIdInvalid as AID:
            await get_otp.delete()
            return await client.send_message(user_id, AID)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberInvalid as PNI:
            await get_otp.delete()
            return await client.send_message(user_id, PNI)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberFlood as PNF:
            await get_otp.delete()
            return await client.send_message(user_id, PNF)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberBanned as PNB:
            await get_otp.delete()
            return await client.send_message(user_id, PNB)
        except hydrogram.errors.exceptions.bad_request_400.PhoneNumberUnoccupied as PNU:
            await get_otp.delete()
            return await client.send_message(user_id, PNU)
        except Exception as error:
            await get_otp.delete()
            return await client.send_message(
                user_id,
                f"<b>ERROR:</b> {error}",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
        await get_otp.delete()
        while True:
            otp = await client.ask(
                user_id,
                f"<b><blockquote>Silakan Periksa Kode OTP dari <a href=tg://openmessage?user_id=777000>Akun Telegram</a> Resmi. Kirim Kode OTP ke sini setelah membaca Format di bawah ini.</b>\n\nJika Kode OTP adalah <code>12345</code> Tolong <b>[ TAMBAHKAN SPASI ]</b> kirimkan Seperti ini <code>1 2 3 4 5</code>.</blockquote></b>",
            )
            if otp.text.startswith("/"):
                return await client.send_message(
                    user_id,
                    f"<blockquote><b>Proses di batalkan.</b></blockquote>",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            otp_code = otp.text
            try:
                await new_client.sign_in(
                    phone_number.strip(),
                    code.phone_code_hash,
                    phone_code=" ".join(str(otp_code)),
                )
                break
            except hydrogram.errors.exceptions.bad_request_400.PhoneCodeInvalid:
                await client.send_message(
                    user_id, "<b>❌ Kode OTP salah. Coba lagi.</b>"
                )
                continue
            except hydrogram.errors.exceptions.bad_request_400.PhoneCodeExpired:
                return await client.send_message(
                    user_id, "<b>❌ Kode OTP Expired. Silahkan ulangi proses.</b>"
                )
            except hydrogram.errors.exceptions.bad_request_400.BadRequest as error:
                return await client.send_message(
                    user_id,
                    f"<b>ERROR:</b> {error}",
                    reply_markup=ButtonUtils.start_menu(is_admin=False),
                )
            except hydrogram.errors.exceptions.unauthorized_401.SessionPasswordNeeded:
                two_step_code = await client.ask(
                    user_id,
                    f"<b><blockquote>Akun anda Telah mengaktifkan Verifikasi Dua Langkah. Silahkan Kirimkan Passwordnya.</blockquote></b>",
                )
                if two_step_code.text.startswith("/"):
                    return await client.send_message(
                        user_id,
                        f"<blockquote><b>Proses di batalkan.</b></blockquote>",
                        reply_markup=ButtonUtils.start_menu(is_admin=False),
                    )
                new_code = two_step_code.text
                try:
                    await new_client.check_password(new_code)
                    await dB.set_var(user_id, "PASSWORD", new_code)
                except Exception as error:
                    await client.send_message(
                        user_id,
                        "<b>❌ V2L yang anda masukkan salah!!. Silahkan masukkan dengan benar.</b>",
                    )
                    continue
            break
        session_string = await new_client.export_session_string()
        await new_client.disconnect()
        new_client.storage.session_string = session_string
        new_client.in_memory = False
        bot_msg = await client.send_message(
            user_id,
            f"<b><blockquote>Tunggu proses selama 1-5 menit...\nKami sedang menghidupkan Userbot Anda.</blockquote></b>",
            disable_web_page_preview=True,
        )
        await asyncio.sleep(2)
        kn_client = UserBot(
            name=str(user_id),
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True,
        )
        try:
            await kn_client.start()
            for modul in _PLUGINS:
                importlib.reload(importlib.import_module(f"plugins.{modul}"))
        except Exception as e:
            logger.error(f"Error Client: {str(e)}")
        if not await dB.get_expired_date(kn_client.me.id):
            await setExpiredUser(kn_client.me.id)
        await dB.add_ubot(
            user_id=int(kn_client.me.id),
            session_string=session_string,
        )
        if not user_id == kn_client.me.id:
            session.remove_session(kn_client.me.id)
            await dB.remove_ubot(kn_client.me.id)
            await kn_client.log_out()
            return await bot_msg.edit(
                f"<blockquote><b>Gunakan akun anda sendiri, bukan orang lain!!</b></blockquote>"
            )
        user_token = await dB.generate_token(kn_client.me.id)
        await asyncio.sleep(1)
        seles = await dB.get_list_from_var(BOT_ID, "SELLER")
        if kn_client.me.id not in seles:
            try:
                AKSES_DEPLOY.remove(kn_client.me.id)
            except Exception:
                pass
        for chat in WAJIB_JOIN:
            try:
                await kn_client.join_chat(chat)
            except Exception:
                pass
        prefix = navy.get_prefix(kn_client.me.id)
        keyb = ButtonUtils.start_menu(is_admin=False)
        exp = await dB.get_expired_date(kn_client.me.id)
        PLAN = (
            "basic" if await dB.get_var(kn_client.me.id, "plan") == "basic" else "pro"
        )
        expir = exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        text_done = f"""
<blockquote expandable><b>🔥 {bot.me.mention} Berhasil Di Aktifkan
➡️ Akun: <a href=tg://openmessage?user_id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a>
➡️ ID: <code>{kn_client.me.id}</code>
➡️ Plan: <b>{PLAN}</b>
➡️ Prefixes: {' '.join(prefix)}
➡️ Token: <code>{user_token}</code>
➡️ Masa Aktif: {expir}</b></blockquote>

<blockquote expandable><b>Token kamu berfungsi untuk mengklaim garansi ubot, 
jika kamu ingin berpindah akun atau akunmu dibanned oleh pihak Telegram.
Mohon simpan Token kamu dengan aman.</b></blockquote>"""
        await bot_msg.edit(text_done, disable_web_page_preview=True, reply_markup=keyb)
        return await client.send_message(
            LOG_SELLER,
            f"""
<b>❏ Notifikasi Userbot Aktif</b>
<b>├ Akun :</b> <a href=tg://user?id={kn_client.me.id}>{kn_client.me.first_name} {kn_client.me.last_name or ''}</a> 
<b>├ ID :</b> <code>{kn_client.me.id}</code>""",
)
    except Exception:
        logger.error(f"ERROR Create Users: {traceback.format_exc()}")




