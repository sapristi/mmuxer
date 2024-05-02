from pathlib import Path

from mmuxer.cli.run import _tidy
from mmuxer.config_state import state


def test_tidy(mailbox, make_message, tmp_path: Path):

    mailbox.login("u", "p")
    state._mailbox = mailbox

    _tidy(None, False)
