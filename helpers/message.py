from typing import Optional

from pytz import timezone
from clients import session
from config import BOT_ID, BOT_NAME, USENAME_OWNER
from database import dB
from logs import logger

def get_user_info(user_id: int):
    client = session.get_session(user_id)
    if client:
        return {
            "first_name": client.me.first_name,
            "last_name": client.me.last_name or "",
            "username": client.me.username or "",
        }
    return {"first_name": "User", "last_name": str(user_id), "username": ""}


class Message:
    """Enhanced message templates with modern formatting"""

    JAKARTA_TZ = timezone("Asia/Jakarta")
    USER_MENTION = "<a href=tg://user?id={id}>{name}</a>"
    CODE_BLOCK = "<code>{text}</code>"
    SECTION_START = "<b>❏ {title}</b>"
    SECTION_ITEM = "<b>├ {label}:</b> {value}"
    SECTION_END = "<b>╰ {label}</b> {value}"

    @staticmethod
    async def RESIKO_MENGGUNAKAN_USERBT():
        return """<blockquote expandable><b>💡 Catatan Untuk Pengguna.</b>
Gunakan userbot dengan bijak, Karena bisa menyebabkan pelanggaran akun.

<b>🤔 Apa Saja Penyebab Pelanggaran.</b>
      <b>1. Spam Berlebihan.</b>
Hampir <b>30,05% - 85,99%.</b> Rata-rata akun terkena pelanggaran akun dikarenakan spam tanpa jeda atau jeda terlalu cepat saat menggunakan fitur dspam ataupun spam.

<b>Saran:</b> Gunakanlah akal sehatmu, atur delay dengan sebijak mungkin, karena bisa menyebabkan akun telegram terkena pelanggaran.

      <b>2. Delay Jangka Pendek</b>
Apa benar, saat melakukan autofw, autobc, broadcast, ataupun forward dengan jeda jangka pendek akan menyebabkan akun terkena pelanggaran? Ya! benar, hal ini dikarenakan system menandai akun anda telah melakukan spam saat mengirim pesan.

<b>Saran: </b>Saat melakukan autobc/fw dengan jeda rounds jangka pendek, maka atur jeda groups 5-10 detik. karena dapat mengurangi resiko pelanggaran akun. Tidak sepenuhnya ter-atasi! tetapi hanya mengurangi saja.
   
      <b>3. Awalan ID Akun Telegram</b>
Kami sangat tidak menyarankan untuk pengguna userbot atau saat ingin membuat userbot dengan menggunakan akun awalan ID 7, 8, 9. Karena ini salah satu penyebab pelanggaran akun telegram.

<b>Saran: </b>Menggunakan awalan ID 1, 2, 3, 4, 5, 6, atau 7, 8, 9 dijit!

<b>👀 Apa Itu Pelanggaran Akun?</b>
Pelanggaran akun saat menggunakan userbot yaitu: Limit Trial/Permanent, Frozzen/Frezze, Banned/Deak, Logout.

<b>⚠️ Kami tidak akan bertanggung jawab saat akun telegram anda terkena pelanggaran. Karena itu sudah bagian dari resiko saat menggunakan userbot anda.</b></blockquote>"""

    @staticmethod
    async def cara_buat_userbot():
        return """📝 Langkah-Langkah, Cara memasang atau mengkaitkan akun kalian dengan Small Userbot. 

<b><blockquote>🚀 Mulai Membuat Userbot</blockquote>
      - Tekan tombol '🚀 Mulai Buat Userbot'.
      - Anda akan diminta untuk menyetujui kebijakan kami. tekan '📚Saya Setuju'.

<blockquote>📱 Kirim Nomor Telepon</blockquote>
      - Tekan tombol '📞 Kontak Saya' untuk mengirimkan nomor telepon akun Telegram yang akan dijadikan userbot. Pastikan nomor tersebut aktif.

<blockquote>🔐 Masukkan Kode OTP & Password</blockquote>
      - Periksa kode OTP yang masuk ke akun Telegram Anda dari akun resmi Telegram.
      - Masukkan kode tersebut ke bot.
      - Jika akun Anda memiliki verifikasi dua langkah (2FA), masukkan juga kata sandi Anda.

<blockquote>🎉  Small Userbot Aktif!</blockquote>
      - Jika semua langkah benar, Anda akan menerima pesan bahwa userbot berhasil diaktifkan.</b>"""
    @staticmethod
    def ReplyCheck(message):
        reply_id = None
        if message.reply_to_message:
            reply_id = message.reply_to_message.id
        elif not message.from_user:
            reply_id = message.id
        return reply_id

    @staticmethod
    async def _ads() -> str:
        txt = await dB.get_var(BOT_ID, "ads")
        if txt:
            msg = txt
        else:
            msg = f"Masih kosong, jika ingin promosi ads hubungi {USENAME_OWNER}"
        return msg

    @classmethod
    def _format_user_mention(
        cls, user_id: int, first_name: str, last_name: Optional[str] = None
    ) -> str:
        """Format user mention with full name"""
        full_name = f"{first_name} {last_name or ''}".strip()
        return cls.USER_MENTION.format(id=user_id, name=full_name)

    @classmethod
    def expired_message(cls, user_id: int) -> str:
        client = session.get_session(user_id)
        return f"""
{cls.SECTION_START.format(title="Notifikasi")}
{cls.SECTION_ITEM.format(
    label="Akun",
    value=cls._format_user_mention(client.me.id, client.me.first_name, client.me.last_name)
)}
{cls.SECTION_ITEM.format(label="ID", value=cls.CODE_BLOCK.format(text=client.me.id))}
{cls.SECTION_END.format(label="Status", value="Masa Aktif Telah Habis")}
"""

    @classmethod
    async def welcome_message(cls, client, message) -> str:
        """Generate personalized welcome message"""
        return f"""<b>👋🏻 hai, {cls._format_user_mention(
    message.from_user.id,
    message.from_user.first_name,
    message.from_user.last_name
)}!</b>"""
    @staticmethod
    async def userbot_list(start_index=0):
        user_list = session.get_list()
        total_users = len(user_list)
        end_index = min(start_index + 20, total_users)

        message_text = "<i><b>──── 🌵 Daftar Userbot 📚 ────</b></i>\n\n"

        for i in range(start_index, end_index):
            user_id = user_list[i]
            try:
                user_info = get_user_info(user_id)
                account_name = (
                    f"{user_info['first_name']} {user_info['last_name'] or ''}"
                )
                message_text += (
                    f"<b>{i+1}.</b> {account_name} - <code>{user_id}</code>\n"
                )
            except Exception as e:
                message_text += f"<b>{i+1}.</b> Unknown - <code>{user_id}</code>\n"

        message_text += f"\n<b>Menampilkan {start_index + 1}-{end_index} dari {total_users} userbot</b>"

        return message_text

    @staticmethod
    async def userbot_detail(count: int):
        try:
            user_id = session.get_list()[count]
            user_info = get_user_info(user_id)
            client = session.get_session(user_id)
            v2l = await dB.get_var(user_id, "PASSWORD") or "-"
            expired_date = await dB.get_expired_date(user_id)
            expir = (
                expired_date.astimezone(timezone("Asia/Jakarta")).strftime(
                    "%Y-%m-%d %H:%M"
                )
                if expired_date
                else "-"
            )
            return f"""
<b>❏ Userbot ke </b> <code>{count + 1}/{session.get_count()}</code>
<b> ├ Akun:</b> <a href='tg://user?id={user_id}'>{user_info['first_name']} {user_info['last_name'] or ''}</a> 
<b> ├ ID:</b> <code>{user_id}</code>
<b> ├ No. Hp:</b> <code>{client.me.phone_number}</code>
<b> ├ Expired:</b> <code>{expir}</code>
<b> ╰ V2L:</b> <code>{v2l}</code> 
"""
        except Exception as e:
            logger.error(f"Error in userbot method: {e}")
            return f"<b>❌ Error: {e}</b>"

    @staticmethod
    async def userbot(count: int):
        try:
            user_id = session.get_list()[count]
            user_info = get_user_info(user_id)
            expired_date = await dB.get_expired_date(user_id)

            if expired_date:
                expir = expired_date.astimezone(timezone("Asia/Jakarta")).strftime(
                    "%Y-%m-%d %H:%M"
                )
            else:
                expir = "Unknown"

            return f"""
    <b>❏ Userbot ke </b> <code>{count + 1}/{session.get_count()}</code>
    <b> ├ Akun:</b> <a href='tg://user?id={user_id}'>{user_info['first_name']} {user_info['last_name'] or ''}</a> 
    <b> ├ ID:</b> <code>{user_id}</code>
    <b> ├ Username:</b> @{user_info['username'] or 'None'}
    <b> ╰ Expired:</b> <code>{expir}</code>
    """
        except Exception as e:
            logger.error(f"Error in userbot method: {e}")
            return f"<b>❌ Error: {e}</b>"

    @staticmethod
    def deak(X):
        return f"""
<b>Attention !!</b>
<b>Akun:</b> <a href=tg://user?id={X.me.id}>{X.me.first_name} {X.me.last_name or ''}</a>
<b>ID:</b> <code>{X.me.id}</code>
<b>Reason:</b> <code>ᴅɪ ʜᴀᴘᴜs ᴅᴀʀɪ ᴛᴇʟᴇɢʀᴀᴍ</code>
"""

    @staticmethod
    async def policy_message() -> str:
        """Generate enhanced policy and terms message"""
        return f"<i><b>💡 Gunakan userbot ini sebijak mungkin. Agar akun telegram terkena pelanggaran.\n🌵 Harap untuk simpan [ TOKEN LOGIN ] Sebaik mungkin, Agar bisa klaim garansi userbot.</b></i>"

    @staticmethod
    def format_rupiah(angka):
        return f"Rp{angka:,}".replace(",", ".")

    @staticmethod
    def TEXT_PAYMENT(harga, total, bulan, plan, diskon=0):
        return f"""
<blockquote expandable><b>Sebelum melanjutkan pembayaran silahkan pilih durasi terlebih dahulu.

Harga per bulan: <code>{Message.format_rupiah(harga)}</code>

🎁 Diskon: <code>{Message.format_rupiah(diskon)}</code>
🔖 Total harga: <code>{Message.format_rupiah(total)}</code>
🗓️ Masa aktif: <code>{bulan} bulan</code>
🛒 Plan: <code>{plan}</code>

🎉 Diskon tersedia jika membeli:
   • 2 bulan atau lebih: Rp10.000 (hingga 25%)
   • 5 bulan atau lebih: Rp25.000 (hingga 25%)
   • 12 bulan atau lebih: Rp80.000 (hingga 33%)

✅ Klik tombol Konfirmasi dibawah untuk melakukan pembayaran.</b></blockquote>
"""

    @staticmethod
    def chosePlan():
        return """
    **⚡ Plan Lite**
        <blockquote expandable>
        Akses ke sekitar 20 fitur dasar yang ringan dan cocok untuk pemula.
        Cek detail fiturnya di tombol ⚡ Plan Lite.
        Jumlah fitur bisa berubah sesuai pengembangan dari developer.
        </blockquote>

    **🧩 Plan Basic**
        <blockquote expandable>
        Nikmati akses ke sekitar 50 fitur unggulan yang memenuhi kebutuhan standar.
        Cek semua fiturnya di tombol 🧩 Plan Basic.
        Fitur bisa bertambah atau berkurang sesuai pengembangan dari developer.
        </blockquote>

    **💎 Plan Pro**
        <blockquote expandable>
        Unlock semua kemampuan dengan sekitar 90 fitur premium yang sangat lengkap!
        Lihat daftar fitur lengkapnya di tombol 💎 Plan Pro.
        Fitur akan terus dikembangkan dan bisa berubah sesuai keputusan developer.
        </blockquote>

    **Silahkan pilih plan sebelum melakukan pembayaran!**
    """






















