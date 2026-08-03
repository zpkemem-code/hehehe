from command import autoshare_cmd
from helpers import CMD

__MODULES__ = "AutoShare"
__HELP__ = """**➕ Bantuan Module:** <u>Auto Share</u>
🧩 Utamakan membaca agar tidak ada kendala saat menggunakan auto promosi.

`{0}autoshare (bc/fw) (on/off)`
<blockquote expandable>✏️ Mengaktifkan atau menonaktifkan auto broadcast (bc) atau auto forward (fw).</blockquote>

`{0}autoshare (add/save) (bc/fw)`
<blockquote expandable>✏️ Menyimpan pesan balasan ke database Broadcast atau Forward.</blockquote>

`{0}autoshare (del/remove) (bc/fw)`
<blockquote expandable>✏️ Menghapus pesan yang tersimpan di database Broadcast atau Forward.</blockquote>

`{0}autoshare (bc/fw) (rounds/groups) (angka)`
<blockquote expandable>✏️ Mengatur delay.
• Rounds: Jeda menit per putaran.
• Groups: Jeda detik antar grup.</blockquote>

`{0}autoshare status`
<blockquote expandable>✏️ Melihat status konfigurasi Auto Broadcast dan Auto Forward secara bersamaan.</blockquote>"""

@CMD.UBOT("autoshare")
async def _(client, message):
    return await autoshare_cmd(client, message)
