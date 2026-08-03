import re

from pyrogram_styled import filters

from config import BOT_NAME
from database import dB

from .active import session
from .base import BaseClient
from .registry import HandlerRegistry


class UserBot(BaseClient):
    _prefix = {}
    _translate = {}
    _get_my_peer = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_version = "0.0.1.0.0"
        self.device_model = BOT_NAME
        self.system_version = "smallubot by @pakveno"
        self.in_memory = True
        self.sleep_threshold = 30
        self.plugins = {"root": "plugins"}

    def set_prefix(self, prefix):
        self._prefix[self.me.id] = prefix

    def get_prefix(self, user_id):
        return self._prefix.get(user_id, [".", ",", "?", "+", "!"])

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            HandlerRegistry.add_message_handler(filters, func, group)
            return func

        return decorator

    def on_edited_message(self, filters=None, group=-1):
        def decorator(func):
            HandlerRegistry.add_edited_message_handler(filters, func, group)
            return func

        return decorator

    def user_prefix(self, cmd):
        command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

        async def func(_, client, message):
            if message.text:
                text = message.text.strip().encode("utf-8").decode("utf-8")
                username = client.me.username or ""
                prefixes = self.get_prefix(client.me.id)

                if not text:
                    return False

                for prefix in prefixes:
                    if not text.startswith(prefix):
                        continue

                    without_prefix = text[len(prefix) :]

                    for command in cmd.split("|"):
                        if not re.match(
                            rf"^(?:{command}(?:@?{username})?)(?:\s|$)",
                            without_prefix,
                            flags=re.IGNORECASE | re.UNICODE,
                        ):
                            continue

                        without_command = re.sub(
                            rf"{command}(?:@?{username})?\s?",
                            "",
                            without_prefix,
                            count=1,
                            flags=re.IGNORECASE | re.UNICODE,
                        )
                        message.command = [command] + [
                            re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                            for m in command_re.finditer(without_command)
                        ]

                        return True

                return False

        return filters.create(func)

    async def start(self):
        await super().start()
        HandlerRegistry.apply_handlers(self)
        prefixes = await dB.get_pref(self.me.id)
        if prefixes:
            self._prefix[self.me.id] = prefixes
        else:
            self._prefix[self.me.id] = [".", ",", "?", "+", "!"]
        session.add_session(self.me.id, self)

    async def stop(self, *args, **kwargs):
        session.remove_session(self.me.id)
        await super().stop(*args, **kwargs)


navy = UserBot(name="clients")

