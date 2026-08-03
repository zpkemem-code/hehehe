from command import spam_cmd, spamg_cmd
from helpers import CMD

__MODULES__ = "Spam"
__HELP__ = """➕ <b>Bantuan Module:</b> <u>Spam</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan spam.

`{0}dspam (balas teks/media) (jumlah) (delay)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengirim pesan spam dengan jumlah dan delay tertentu.</blockquote>

`{0}spamg (balas teks/media) (jumlah)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengirim pesan broadcast spam jumlah tertentu.</blockquote>

`{0}spam (balas teks/media) (jumlah)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengirim pesan spam jumlah tertentu.</blockquote>

`{0}cancel (task id)`
<blockquote expandable>✏️ cmd di atas berguna untuk membatalkan/menghentikan paksa spam yang sedang berjalan.</blockquote>"""


@CMD.UBOT("spam|dspam")
async def _(client, message):
    return await spam_cmd(client, message)


@CMD.UBOT("spamg")
async def _(client, message):
    return await spamg_cmd(client, message)
