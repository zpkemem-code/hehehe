import re
from typing import List, Tuple
from uuid import uuid4

from pyrogram_styled.helpers import ikb, kb
from pyrogram_styled.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)

from database import dB, state
from clients import session


class EqInlineKeyboardButton(InlineKeyboardButton):

    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text


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
    def is_number(text):
        return text.isdigit()


    @staticmethod
    def is_copy(text):
        return text.startswith("copy:")


    @staticmethod
    async def create_button(
        text,
        data,
        suffix=""
    ):

        data = str(data).strip()


        # URL
        if ButtonUtils.is_url(data):

            return InlineKeyboardButton(
                text=text,
                url=data
            )


        # USER ID
        if ButtonUtils.is_number(data):

            return InlineKeyboardButton(
                text=text,
                user_id=int(data)
            )


        # COPY TEXT
        if ButtonUtils.is_copy(data):

            return InlineKeyboardButton(
                text=text,
                copy_text=data.replace(
                    "copy:",
                    ""
                )
            )


        # CALLBACK

        callback = (
            f"{data}_{suffix}"
            if suffix
            else data
        )


        return InlineKeyboardButton(
            text=text,
            callback_data=callback
        )


    @staticmethod
    async def create_inline_keyboard(
        buttons: List[List],
        suffix=""
    ):

        keyboard = []


        for row in buttons:

            keyboard_row = []

            for text, data in row:

                button = await ButtonUtils.create_button(
                    text,
                    data,
                    suffix
                )

                keyboard_row.append(button)


            keyboard.append(
                keyboard_row
            )


        return InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )



    @staticmethod
    def start_menu(
        is_admin=False
    ):


        if is_admin:

            menu = [

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
                ]

            ]


        else:

            menu = [

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
    def account_list(
        start_index=0
    ):

        users = session.get_list()

        buttons = []


        row = []


        for index,user_id in enumerate(users[start_index:start_index+20]):

            row.append(
                InlineKeyboardButton(
                    text=str(index+1),
                    callback_data=f"tools_acc {user_id}-{index}"
                )
            )


            if len(row)==5:

                buttons.append(row)
                row=[]


        if row:
            buttons.append(row)


        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Tutup",
                    callback_data="buttonclose"
                )
            ]
        )


        return InlineKeyboardMarkup(
            inline_keyboard=buttons
        )



    @staticmethod
    def build_buttons(
        data,
        uniq,
        callback,
        closed
    ):

        buttons=[]
        row=[]


        for idx,_ in enumerate(data):

            row.append(
                InlineKeyboardButton(
                    text=str(idx+1),
                    callback_data=f"{callback}{idx}_{uniq}"
                )
            )


            if len(row)==5:

                buttons.append(row)
                row=[]


        if row:
            buttons.append(row)


        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Close",
                    callback_data=f"close {closed} {uniq}"
                )
            ]
        )


        return InlineKeyboardMarkup(
            inline_keyboard=buttons
        )