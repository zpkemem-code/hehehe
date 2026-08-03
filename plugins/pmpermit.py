from clients import navy
from command import AUTO_APPROVE, PMPERMIT, nopm_cmd, okpm_cmd, pmpermit_cmd
from helpers import CMD

__MODULES__ = "PMPermit"
__HELP__ = """➕ <b>Bantuan Module:</b> <u>PMPermit</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan pmpermit.

`{0}pmpermit set (on/off)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengaktifkan dan menonaktifkan pmpermit.</blockquote>

`{0}pmpermit media (balas media)`
<blockquote expandable>✏️ cmd di atas berguna untuk private chat otomatis mengirim media dan peringatan spam.</blockquote>

`{0}pmpermit teks (balas teks)`
<blockquote expandable>✏️ cmd di atas berguna untuk private chat otomatis mengirim pesan dan peringatan.</blockquote>

`{0}pmpermit warn (jumlah)`
<blockquote expandable>✏️ cmd di atas berguna untuk membatasi spam privatr chat dari pengguna lain.</blockquote>

`{0}pmpermit get (teks/media/warn/status)`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat teks, media, warn, dan status pmpermit.</blockquote>

`{0}ok〡{0}no`
<blockquote expandable>✏️ cmd di atas berguna untuk menerima atau menolak chat dari pengguna lain</blockquote>"""

@CMD.UBOT("pmpermit")
async def _(client, message):
    return await pmpermit_cmd(client, message)

@CMD.UBOT("ok")
@CMD.ONLY_PRIVATE
async def _(client, message):
    return await okpm_cmd(client, message)

@CMD.UBOT("no")
@CMD.ONLY_PRIVATE
async def _(client, message):
    return await nopm_cmd(client, message)

@CMD.NO_CMD("PMPERMIT", navy)
async def _(client, message):
    return await PMPERMIT(client, message)


@CMD.NO_CMD("AUTO_APPROVE", navy)
async def _(client, message):
    return await AUTO_APPROVE(client, message)
