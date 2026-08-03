import asyncio
import shlex
import subprocess

from typing import Optional

from pyrogram_styled import (
    Client,
    enums,
    errors,
    raw,
    filters,
)

from pyrogram_styled.methods.messages.send_rich_message import (
    SendRichMessage,
)

from database import dB


list_error = []



class BaseClient(
    Client,
    SendRichMessage
):


    def __init__(self, **kwargs):

        super().__init__(
            **kwargs
        )



    def user_prefix(
        self,
        command
    ):

        return filters.command(
            command,
            prefixes=[
                ".",
                "!",
                "/",
            ],
        )



    async def get_privileges(
        self,
        chat_id: int,
        user_id: int
    ):

        member = await self.get_chat_member(
            chat_id,
            user_id
        )

        return member.privileges



    async def parse_topic(
        self,
        chat_id: int
    ):

        data_forum = []

        title = (
            await self.get_chat(chat_id)
        ).title


        async for topic in self.get_forum_topics(
            chat_id
        ):

            data_forum.append(
                {
                    "id": topic.id,
                    "title": topic.title,
                }
            )


        return title, data_forum



    async def get_call(
        self,
        chat_id: int
    ) -> Optional[raw.types.InputGroupCall]:


        try:

            chat = await self.resolve_peer(
                chat_id
            )

        except (
            errors.PeerIdInvalid,
            errors.ChannelInvalid
        ):

            return None



        if isinstance(
            chat,
            raw.types.InputPeerChannel
        ):


            full_chat = await self.invoke(

                raw.functions.channels.GetFullChannel(

                    channel=raw.types.InputChannel(

                        channel_id=chat.channel_id,

                        access_hash=chat.access_hash,

                    )

                )

            )


        else:


            full_chat = await self.invoke(

                raw.functions.messages.GetFullChat(

                    chat_id=chat_id

                )

            )



        input_call = (
            full_chat.full_chat.call
        )



        if input_call:


            call_details = await self.invoke(

                raw.functions.phone.GetGroupCall(

                    call=input_call,

                    limit=-1

                )

            )


            call = call_details.call



            if (
                call
                and call.schedule_date
            ):

                return None



            return call



        return None




    async def admin_list(
        self,
        message
    ):


        return [

            member.user.id

            async for member in self.get_chat_members(

                message.chat.id,

                filter=enums.ChatMembersFilter.ADMINISTRATORS

            )

        ]




    async def get_chat_id(
        self,
        query
    ):


        chat_types = {


            "global":[

                enums.ChatType.CHANNEL,

                enums.ChatType.GROUP,

                enums.ChatType.SUPERGROUP,

            ],


            "all":[

                enums.ChatType.GROUP,

                enums.ChatType.SUPERGROUP,

                enums.ChatType.PRIVATE,

            ],


            "group":[

                enums.ChatType.GROUP,

                enums.ChatType.SUPERGROUP,

            ],


            "bot":[

                enums.ChatType.BOT,

            ],


            "usbot":[

                enums.ChatType.PRIVATE,

                enums.ChatType.BOT,

            ],


            "private":[

                enums.ChatType.PRIVATE,

            ],


            "channel":[

                enums.ChatType.CHANNEL,

            ],

        }



        if query not in chat_types:

            return []



        result = []



        try:


            async for dialog in self.get_dialogs():


                chat = dialog.chat


                if chat.type in chat_types[query]:

                    result.append(
                        chat.id
                    )


        except Exception:

            pass



        return result




    def extract_type_and_msg(
        self,
        message,
        is_reply_text=False
    ):


        args = message.text.split(
            None,
            2
        )


        if len(args) < 2:

            return None, None



        cmd_type = args[1]



        if is_reply_text:


            msg = (

                message.reply_to_message.text

                if message.reply_to_message

                else args[2]
                if len(args) > 2
                else None

            )


        else:


            msg = (

                message.reply_to_message

                if message.reply_to_message

                else args[2]
                if len(args) > 2
                else None

            )



        return cmd_type, msg




    async def get_translate(self):


        data = await dB.get_var(
            self.me.id,
            "_translate"
        )


        return data or "id"




    def get_message(
        self,
        message
    ):


        if message.reply_to_message:

            return message.reply_to_message


        if len(message.command) > 1:

            return " ".join(
                message.command[1:]
            )


        return ""




    async def run_cmd(
        self,
        cmd
    ):


        args = shlex.split(
            cmd
        )


        try:


            process = await asyncio.create_subprocess_exec(

                *args,

                stdout=asyncio.subprocess.PIPE,

                stderr=asyncio.subprocess.PIPE,

            )


            stdout, stderr = await process.communicate()



            return (

                stdout.decode(
                    "utf-8",
                    "replace"
                ).strip(),

                stderr.decode(
                    "utf-8",
                    "replace"
                ).strip(),

                process.returncode,

                process.pid,

            )



        except NotImplementedError:



            process = subprocess.Popen(

                cmd,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                shell=True,

            )


            stdout, stderr = process.communicate()



            return (

                stdout.decode(
                    "utf-8",
                    "replace"
                ).strip(),

                stderr.decode(
                    "utf-8",
                    "replace"
                ).strip(),

                process.returncode,

                process.pid,

            )