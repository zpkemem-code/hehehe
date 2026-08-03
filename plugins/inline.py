from command import help_cmd, inline_cmd
from helpers import CMD

__MODULES__ = "Inline"
__HELP__ = """➕ <b>Bantuan Module:</b> <u>Inline</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan inline.

`{0}alive`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat masa aktif, kecepatan, status, dll. pada akun kalian.</blockquote>

`{0}help〡{0}help (nama module)`
<blockquote expandable>✏️ cmd di atas berguna untuk memunculkan menu dan menampilkan commands pada userbot.</blockquote>"""

@CMD.UBOT("alive")
async def _(client, message):
    return await inline_cmd(client, message)

@CMD.UBOT("help")
async def _(client, message):
    return await help_cmd(client, message)

