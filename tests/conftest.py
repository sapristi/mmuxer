import base64
import imaplib
import json
from pathlib import Path

import pytest

# from imap_tools import BaseMailBox
from mmuxer.mailbox import BaseMailBox


class UnsafeMailBox(BaseMailBox):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        super().__init__()

    def _get_mailbox_client(self) -> imaplib.IMAP4:
        return imaplib.IMAP4(self._host, self._port)


@pytest.fixture
def mailbox():
    box = UnsafeMailBox("localhost", 1143)
    yield UnsafeMailBox("localhost", 1143)
    box._get_mailbox_client().xatom("clear")


@pytest.fixture
def data():
    def inner(filename):
        return (Path(__file__).parent / "data" / filename).read_text()

    return inner


@pytest.fixture
def make_message(mailbox):
    def inner(user="u", box="INBOX", **kwargs):
        if "to" in kwargs:
            assert isinstance(kwargs["to"], list), "`to` must be a list"
        payload = (
            base64.b32encode(
                json.dumps(
                    {
                        **{
                            "to": ["to@ok.com"],
                            "from_": "from@ok.com",
                            "subject": "subject",
                        },
                        **kwargs,
                    }
                ).encode()
            )
            .replace(b"=", b"a")
            .decode()
        )
        mailbox._get_mailbox_client().xatom("receive", user, box, payload)

    return inner
