from pathlib import Path

from mmuxer.cli.run import _tidy
from mmuxer.config_state import state

config = """
rules:
  - move_to: Trash
    condition:
      SUBJECT: spam
settings:
  server: localhost
  username: u
  password: p
"""


def test_tidy(mailbox, make_message, tmp_path: Path):
    """
    GIVEN a mailbox with messages
    WHEN running _tidy
    THEN messages are tidied up
    """
    config_file = tmp_path / "config.py"
    config_file.write_text(config)
    state.load_config_file(config_file)
    state._mailbox = mailbox

    mailbox.login("u", "p")

    make_message(user="u", box="INBOX", subject="spam", content_text="content")
    make_message(user="u", box="INBOX", subject="ok", content_text="content")

    _tidy(None, False)

    messages = list(mailbox.fetch())
    assert len(messages) == 1

    mailbox.folder.set("Trash")
    messages = list(mailbox.fetch())
    assert len(messages) == 1
