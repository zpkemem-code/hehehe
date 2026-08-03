from asyncio import sleep

from pyrogram_styled import raw
from pyrogram_styled.errors import FloodPremiumWait, FloodWait

from helpers import animate_proses, Emoji


async def spam_bot(client, message):

    await client.unblock_user("SpamBot")
    xin = await client.resolve_peer("SpamBot")
    em = Emoji(client)
    await em.get()
    msg = await animate_proses(message, em.proses)
    await client.send_message("SpamBot", "/start")
    await sleep(1)
    async for status in client.search_messages("SpamBot", limit=1):
        isdone = status.text
        break
    else:
        isdone = None
    if isdone:
        result = status.text
        await client.send_message(
            message.chat.id,
            f"**{result}**\n\n ~  **{client.me.first_name}**",
        )
        try:
            await client.invoke(
                raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True)
            )
        except (FloodWait, FloodPremiumWait) as e:
            await sleep(e.value)
            await client.invoke(
                raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True)
            )
    return await msg.delete()
