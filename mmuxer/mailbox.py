"""
Code modified from https://github.com/ikvk/imap_tools/blob/master/imap_tools/mailbox.py
"""

import imaplib
import sys
from itertools import islice
from typing import Iterable

from imap_tools.mailbox import BaseMailBox, check_timeout_arg_support

PYTHON_VERSION_MINOR = sys.version_info.minor


def batched(iterable: Iterable, n: int):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


class MailBox(BaseMailBox):
    """Working with the email box through IMAP4 over SSL connection"""

    def __init__(
        self, host="", port=993, timeout=None, keyfile=None, certfile=None, ssl_context=None
    ):
        """
        :param host: host's name (default: localhost)
        :param port: port number
        :param timeout: timeout in seconds for the connection attempt, since python 3.9
        :param keyfile: PEM formatted file that contains your private key (deprecated)
        :param certfile: PEM formatted certificate chain file (deprecated)
        :param ssl_context: SSLContext object that contains your certificate chain and private key
        Since Python 3.9 timeout argument added
        Since Python 3.12 keyfile and certfile arguments are deprecated, ssl_context and timeout must be keyword args
        """
        check_timeout_arg_support(timeout)
        self._host = host
        self._port = port
        self._timeout = timeout
        self._keyfile = keyfile
        self._certfile = certfile
        self._ssl_context = ssl_context
        super().__init__()

    def _get_mailbox_client(self) -> imaplib.IMAP4:
        if PYTHON_VERSION_MINOR < 9:
            return imaplib.IMAP4_SSL(
                self._host, self._port, self._keyfile, self._certfile, self._ssl_context
            )
        elif PYTHON_VERSION_MINOR < 12:
            return imaplib.IMAP4_SSL(
                self._host,
                self._port,
                self._keyfile,
                self._certfile,
                self._ssl_context,
                self._timeout,
            )
        else:
            return imaplib.IMAP4_SSL(
                self._host, self._port, ssl_context=self._ssl_context, timeout=self._timeout
            )
