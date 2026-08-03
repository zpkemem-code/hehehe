from command import addbl_cmd, delbl_cmd, listbl_cmd
from helpers import CMD

__MODULES__ = "Blacklist"
__HELP__ = """➕ **Bantuan Module:** <u>Blacklist</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan blacklist chat.

`{0}addbl (id group/users)`
<blockquote expandable>✏️ cmd di atas berguna untuk menambahkan chat ke dalam blacklist/daftar hitam, agar tidak terkirim saat kalian melakukan auto share dan broadcast.</blockquote>

`{0}addbl (id group/users)`
<blockquote expandable>✏️ cmd di atas berguna untuk mengeluarkan chat dari daftar hitam.</blockquote>

`{0}listbl〡{0}blacklist`
<blockquote expandable>✏️ cmd di atas berguna untuk melihat daftar hitam chat.</blockquote>"""

@CMD.UBOT("addbl")
@CMD.DEV_CMD("addbl")
async def _(client, message):
    return await addbl_cmd(client, message)

@CMD.UBOT("delbl")
@CMD.DEV_CMD("delbl")
async def _(client, message):
    return await delbl_cmd(client, message)

@CMD.UBOT("listbl|blacklist")
async def _(client, message):
    return await listbl_cmd(client, message)
