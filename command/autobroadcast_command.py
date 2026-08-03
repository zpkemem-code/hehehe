import asyncio
import pytz
from datetime import datetime, timedelta
from pytz import timezone

from database import dB
from helpers import (Emoji, StartAutoBC, StartAutoFW, add_auto_text,
                     add_auto_text_fw, animate_proses)

async def autoshare_cmd(client, message):
    user_id = message.from_user.id
    em = Emoji(client)
    await em.get()
    
    msg = await animate_proses(message, em.proses)
    
    if len(message.command) < 2:
        return await msg.edit(f"**{em.block} Gunakan format: .autoshare (bc/fw/add/del/status) ...**")

    arg1 = message.command[1].lower()
    arg2 = message.command[2].lower() if len(message.command) > 2 else None
    arg3 = message.command[3].lower() if len(message.command) > 3 else None

    if arg1 == "status":
        status_bc = await dB.get_var(client.me.id, "AUTOBC_STATUS")
        status_fw = await dB.get_var(client.me.id, "AUTOFW_STATUS")
        
        delay_bc = await dB.get_var(client.me.id, "DELAY_AUTOBC") or 60
        delay_fw = await dB.get_var(client.me.id, "DELAY_AUTOFW") or 60
        
        group_bc = await dB.get_var(client.me.id, "DELAY_AUTOBC_GROUP") or 3
        group_fw = await dB.get_var(client.me.id, "DELAY_AUTOFW_GROUP") or 3
        
        saved_bc = await dB.get_var(client.me.id, "MSG_AUTOBC")
        saved_fw = await dB.get_var(client.me.id, "MSG_AUTOFW")
        
        count_bc = len(saved_bc) if saved_bc else 0
        count_fw = len(saved_fw) if saved_fw else 0
        
        text_status = (
            f"**📊 AUTO SHARE STATUS**\n\n"
            f"**📢 Broadcast (BC)**\n"
            f"   • Status: `{'✅ On' if status_bc else '❌ Off'}`\n"
            f"   • Pesan Tersimpan: `{count_bc}`\n"
            f"   • Jeda Rounds: `{delay_bc} Menit`\n"
            f"   • Jeda Groups: `{group_bc} Detik`\n\n"
            f"**🔄 Forward (FW)**\n"
            f"   • Status: `{'✅ On' if status_fw else '❌ Off'}`\n"
            f"   • Pesan Tersimpan: `{count_fw}`\n"
            f"   • Jeda Rounds: `{delay_fw} Menit`\n"
            f"   • Jeda Groups: `{group_fw} Detik`"
        )
        return await msg.edit(text_status)

    elif arg1 in ["bc", "fw"]:
        mode = "AUTOBC" if arg1 == "bc" else "AUTOFW"
        task_func = StartAutoBC if arg1 == "bc" else StartAutoFW
        db_msg_key = "MSG_AUTOBC" if arg1 == "bc" else "MSG_AUTOFW"
        
        if not arg2:
            return await msg.edit(f"**{em.block} Mohon tentukan aksi: on, off, rounds, atau groups.**")

        if arg2 in ["on", "true"]:
            saved = await dB.get_var(client.me.id, db_msg_key)
            if not saved:
                return await msg.edit(f"**{em.gagal} Simpan pesan terlebih dahulu dengan `.autoshare add {arg1}`**")
            
            if await dB.get_var(client.me.id, f"{mode}_STATUS"):
                return await msg.edit(f"**{em.sukses} Auto {arg1.upper()} sudah aktif.**")
            else:
                await dB.set_var(client.me.id, f"{mode}_STATUS", True)
                await dB.set_var(client.me.id, f"{mode}_ROUNDS", 0)
                asyncio.create_task(task_func(client, client.me.id, 0))
                return await msg.edit(f"**{em.sukses} Auto {arg1.upper()} berhasil diaktifkan.**")

        elif arg2 in ["off", "false"]:
            if await dB.get_var(client.me.id, f"{mode}_STATUS"):
                await dB.set_var(client.me.id, f"{mode}_STATUS", False)
                return await msg.edit(f"**{em.sukses} Auto {arg1.upper()} berhasil dimatikan.**")
            else:
                return await msg.edit(f"**{em.sukses} Auto {arg1.upper()} sudah mati.**")

        elif arg2 in ["rounds", "round"]:
            if not arg3 or not arg3.isdigit():
                return await msg.edit(f"**{em.block} Gunakan angka valid. Contoh: `.autoshare {arg1} rounds 60`**")
            await dB.set_var(client.me.id, f"DELAY_{mode}", int(arg3))
            return await msg.edit(f"**{em.sukses} Jeda putaran {arg1.upper()} diatur ke {arg3} menit.**")

        elif arg2 in ["groups", "group"]:
            if not arg3 or not arg3.isdigit():
                return await msg.edit(f"**{em.block} Gunakan angka valid. Contoh: `.autoshare {arg1} groups 10`**")
            await dB.set_var(client.me.id, f"DELAY_{mode}_GROUP", int(arg3))
            return await msg.edit(f"**{em.sukses} Jeda antar grup {arg1.upper()} diatur ke {arg3} detik.**")
        
        else:
            return await msg.edit(f"**{em.block} Perintah tidak dikenali.**")

    elif arg1 in ["add", "save"]:
        if not message.reply_to_message:
            return await msg.edit(f"**{em.block} Balas pesan yang ingin disimpan.**")
        
        if arg2 == "bc":
            await add_auto_text(message)
            return await msg.edit(f"**{em.sukses} Pesan berhasil disimpan ke Auto BC.**")
        elif arg2 == "fw":
            if not (message.reply_to_message.forward_from or message.reply_to_message.forward_sender_name or message.reply_to_message.forward_from_chat):
                return await msg.edit(f"**{em.block} Pesan yang dibalas harus berupa forwardan untuk Auto FW.**")
            await add_auto_text_fw(message)
            return await msg.edit(f"**{em.sukses} Pesan berhasil disimpan ke Auto FW.**")
        else:
            return await msg.edit(f"**{em.block} Tentukan target simpan: bc atau fw.**")

    elif arg1 in ["del", "remove", "delete"]:
        if arg2 == "bc":
            saved = await dB.get_var(client.me.id, "MSG_AUTOBC")
            if not saved:
                return await msg.edit(f"**{em.block} Tidak ada pesan Auto BC yang tersimpan.**")
            await dB.remove_var(client.me.id, "MSG_AUTOBC")
            return await msg.edit(f"**{em.sukses} Pesan Auto BC berhasil dihapus.**")
        
        elif arg2 == "fw":
            saved = await dB.get_var(client.me.id, "MSG_AUTOFW")
            if not saved:
                return await msg.edit(f"**{em.block} Tidak ada pesan Auto FW yang tersimpan.**")
            await dB.remove_var(client.me.id, "MSG_AUTOFW")
            return await msg.edit(f"**{em.sukses} Pesan Auto FW berhasil dihapus.**")
        
        else:
            return await msg.edit(f"**{em.block} Tentukan target hapus: bc atau fw.**")

    else:
        return await msg.edit(f"**{em.block} Perintah salah. Ketik `.help autoshare` untuk bantuan.**")
