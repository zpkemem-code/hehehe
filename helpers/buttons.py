import re
from math import ceil
from typing import List, Tuple
from uuid import uuid4

from pyrogram_styled.errors import QueryIdInvalid, RPCError
from pyrogram_styled.helpers import ikb, kb
from pyrogram_styled.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from clients import session
from database import dB, state


COLUMN_SIZE = 4
NUM_COLUMNS = 2


class EqInlineKeyboardButton(InlineKeyboardButton):

    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text



def paginate_modules(page_n, module_dict, prefix, chat=None):

    buttons = []

    for module in module_dict.values():

        name = module.__MODULES__

        if chat:
            data = f"{prefix}_module({chat},{name.lower()},{page_n})"
        else:
            data = f"{prefix}_module({name.lower()},{page_n})"

        buttons.append(
            EqInlineKeyboardButton(
                text=name,
                callback_data=data
            )
        )


    buttons = sorted(buttons)

    rows = [
        buttons[i:i+NUM_COLUMNS]
        for i in range(
            0,
            len(buttons),
            NUM_COLUMNS
        )
    ]


    max_page = ceil(len(rows)/COLUMN_SIZE) if rows else 1

    page = page_n % max_page


    if len(rows) > COLUMN_SIZE:

        rows = rows[
            page*COLUMN_SIZE:
            COLUMN_SIZE*(page+1)
        ]

        rows.append(
            [
                EqInlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"{prefix}_prev({page})"
                ),
                EqInlineKeyboardButton(
                    text="❌",
                    callback_data="buttonclose"
                ),
                EqInlineKeyboardButton(
                    text="➡️",
                    callback_data=f"{prefix}_next({page})"
                ),
            ]
        )


    else:

        rows.append(
            [
                EqInlineKeyboardButton(
                    text="➕ Owner Userbot ➕",
                    user_id=8333063872
                )
            ]
        )


    return rows




class ButtonUtils:


    URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )

    BUTTON_PATTERN = re.compile(
        r"\[(.*?)\|(.*?)\]"
    )



    @staticmethod
    def is_url(text):

        return bool(
            re.search(
                ButtonUtils.URL_PATTERN,
                text
            )
        )


    @staticmethod
    def parse_msg_buttons(texts):

        buttons=[]


        for text,url in ButtonUtils.BUTTON_PATTERN.findall(texts):

            if "|" in url:

                url=url.split("|")[0]


            buttons.append(
                [
                    [
                        text,
                        url
                    ]
                ]
            )


        clean=texts

        for x in re.findall(
            r"\[.+?\|.+?\]",
            texts
        ):
            clean=clean.replace(
                x,
                ""
            )


        return clean.strip(),buttons



    @staticmethod
    async def create_button(
        text,
        data,
        with_suffix=""
    ):


        data=data.strip()


        if ButtonUtils.is_url(data):

            return InlineKeyboardButton(
                text=text,
                url=data
            )


        if data.isdigit():

            return InlineKeyboardButton(
                text=text,
                user_id=int(data)
            )


        if data.startswith("copy:"):

            return InlineKeyboardButton(
                text=text,
                copy_text=data.replace(
                    "copy:",
                    ""
                )
            )


        return InlineKeyboardButton(
            text=text,
            callback_data=data
        )



    @staticmethod
    async def create_inline_keyboard(buttons,suffix=""):

        result=[]


        for row in buttons:

            temp=[]

            for text,data in row:

                temp.append(
                    await ButtonUtils.create_button(
                        text,
                        data,
                        suffix
                    )
                )


            result.append(temp)


        return InlineKeyboardMarkup(
            inline_keyboard=result
        )



    @staticmethod
    def start_menu(
        is_admin=False
    ):


        if is_admin:

            menu=[

                [
                    "🚀 Buat Userbot 🚀"
                ],

                [
                    "💎 Status 💎",
                    "🌐 Update 🌐",
                    "♻️ Restart ♻️"
                ],

                [
                    "📂 Cek Users 📂",
                    "📥 Backup DB 📥"
                ],

            ]

        else:

            menu=[

                [
                    "🚀 Buat Userbot 🚀",
                    "💎 Status 💎"
                ],

                [
                    "🔑 Token Login 🔑",
                    "📝 Cara Buat 📝"
                ]

            ]


        return kb(
            menu,
            resize_keyboard=True,
            one_time_keyboard=True
        )



    @staticmethod
    def account_list(start_index=0):

        users=session.get_list()

        keyboard=[]


        row=[]

        for i,user_id in enumerate(
            users[start_index:start_index+20],
            start=start_index
        ):

            row.append(
                InlineKeyboardButton(
                    text=str(i+1),
                    callback_data=f"tools_acc {user_id}-{i}"
                )
            )


            if len(row)==5:

                keyboard.append(row)
                row=[]


        if row:
            keyboard.append(row)



        keyboard.append(
            [
                InlineKeyboardButton(
                    text="❌ Tutup",
                    callback_data="buttonclose"
                )
            ]
        )


        return InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )