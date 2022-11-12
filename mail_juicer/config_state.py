import os
import ssl

import certifi
import yaml
from imap_tools import BaseMailBox, MailBox

from mail_juicer.models.filter import Filter, parse_filter

from .models import Filter, Settings


def make_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    context.load_verify_locations(
        cafile=os.path.relpath(certifi.where()), capath=None, cadata=None
    )
    return context


class State:
    def __init__(self):
        self._settings = None
        self._filters = None
        self._mailbox = None

    def create_mailbox(self):
        ssl_context = make_ssl_context()
        self._mailbox = MailBox(self.settings.server, ssl_context=ssl_context).login(
            self.settings.username, self.settings.password
        )

    def parse_config(self, config_raw):
        config_dict = yaml.safe_load(config_raw)
        self._settings = Settings(**config_dict["settings"])
        self._filters = [parse_filter(filter_config) for filter_config in config_dict["filters"]]

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            raise Exception("Uninitialized settings")
        return self._settings

    @property
    def filters(self) -> list[Filter]:
        if self._filters is None:
            raise Exception("Uninitialized filters")
        return self._filters

    @property
    def mailbox(self) -> BaseMailBox:
        if self._mailbox is None:
            raise Exception("Uninitialized mailbox")
        return self._mailbox


state = State()
