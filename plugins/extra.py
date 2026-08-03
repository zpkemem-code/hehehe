from command import id_cmd, mping_cmd, setprefix_cmd, spam_bot
from helpers import CMD

__MODULES__ = "Extra"
__HELP__ = """➕ <b>Bantuan Module:</b> <u>PMPermit</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan pmpermit.

`{0}ping`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat kecepatan bot dan uptime.</blockquote>

`{0}pmpermit set (on/off)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengaktifkan dan menonaktifkan pmpermit.</blockquote>

`{0}limit〡{0}spambot`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat status akun kalian dari bot @SpamBot.</blockquote>

`{0}id (balas user/media/username)`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat id users atau media.</blockquote>

{0}setprefix (symbol/huruf)
<blockquote expandable>✏️ cmd di atas berguna untuk mengubah symbol/huruf pada awal commands.</blockquote>"""

@CMD.UBOT("limit|spambot")
async def _(client, message):
    return await spam_bot(client, message)
    
@CMD.UBOT("ping")
async def _(client, message):
    return await mping_cmd(client, message)

@CMD.UBOT("setprefix")
async def _(client, message):
    return await setprefix_cmd(client, message)

@CMD.UBOT("id")
async def _(client, message):
    return await id_cmd(client, message)

