from command import addsudo_cmd, delsudo_cmd, sudolist_cmd
from helpers import CMD

__MODULES__ = "Sudoers"
__HELP__ = """**➕ Bantuan Module:** <u>Sudoers</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan sudoers.

`{0}addsudo (username/balas user)`
<blockquote expandable>✏️ cmd di atas berguna untuk menambahkan users ke dalam list sudo, agar pengguna bisa mengontrol akun kalian.</blockquote>

`{0}delsudo (username/all/balas user)`
<blockquote expandable>✏️ cmd di atas berguna untuk menghapus users dari dalam list sudo, all untuk menghapus semua users dari list sudo.</blockquote>

`{0}listsudo〡{0}sudolist`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat semua users di dalam list sudo.</blockquote>"""


@CMD.UBOT("addsudo")
async def _(client, message):
    return await addsudo_cmd(client, message)

@CMD.UBOT("delsudo")
async def _(client, message):
    return await delsudo_cmd(client, message)

@CMD.UBOT("sudolist|listsudo")
async def _(client, message):
    return await sudolist_cmd(client, message)
