import os
import ssl

import certifi
import yaml
from imap_tools import MailBox

from .models import Filter, Settings


def make_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    context.load_verify_locations(
        cafile=os.path.relpath(certifi.where()), capath=None, cadata=None
    )
    return context


def make_mailbox(settings: Settings):
    context = make_context()
    return MailBox(settings.server, ssl_context=context).login(
        settings.username, settings.password
    )


def parse_config(config_raw: str):
    config_dict = yaml.safe_load(config_raw)
    filters = [Filter.parse_obj(filter_config) for filter_config in config_dict["filters"]]
    settings = Settings(**config_dict["settings"])
    return filters, settings
