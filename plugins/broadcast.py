from command import (addbcdb_cmd, bc_cmd, bcerror_cmd, cancel_cmd,
                     delbcdb_cmd, gcast_cmd, listbcdb_cmd, ucast_cmd)
from helpers import CMD

__MODULES__ = "Broadcast"
__HELP__ = """**➕ Bantuan Module:** <u>Broadcast</u>
🧩 utamakan membaca agar tidak ada kendala saat menggunakan broadcast.

`{0}gcast〡{0}ucast (teks/balas media&teks)`
<blockquote expandable>✏️ cmd di atas berguna untuk broadcast group dan private chat.</blockquote>

`{0}bc (db/group/private/all)`
<blockquote expandable>✏️ cmd di atas berguna untuk broadcast db, group, private, dan all untuk mengirim pesan bersamaan group dan private.</blockquote>

`{0}add-bcdb〡{0}del-bcdb (id group/users)`
<blockquote expandable>✏️ cmd di atas berguna untuk menambahkan atau menghapus chat daftar broadcast-db.</blockquote>

`{0}list-bcdb`
<blockquote expandable>✏️ cmd di atas berguna untuk menambahkan chat ke dalam daftar broadcast-db.</blockquote>

`{0}cancel (task id)`
<blockquote expandable>✏️ cmd di atas berguna untuk membatalkan/menghentikan paksa broadcast yang sedang berjalan.</blockquote>"""

@CMD.UBOT("bc")
async def _(client, message):
    return await bc_cmd(client, message)

@CMD.UBOT("gcast")
async def _(client, message):
    return await gcast_cmd(client, message)

@CMD.UBOT("ucast")
async def _(client, message):
    return await ucast_cmd(client, message)

@CMD.UBOT("bc-error")
async def _(client, message):
    return await bcerror_cmd(client, message)


@CMD.UBOT("cancel")
async def _(client, message):
    return await cancel_cmd(client, message)

@CMD.UBOT("add-bcdb")
async def _(client, message):
    return await addbcdb_cmd(client, message)

@CMD.UBOT("del-bcdb")
async def _(client, message):
    return await delbcdb_cmd(client, message)

@CMD.UBOT("list-bcdb")
async def _(client, message):
    return await listbcdb_cmd(client, message)


