import imaplib
import logging

import typer
from imap_tools import AND

from ..config_state import state
from ..models.rule import apply_list

logger = logging.getLogger(__name__)


def tidy(
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
    config_file: typer.FileText = typer.Option(...),
):
    """Run once, on all messages of the INBOX (or the given folder)."""
    state.parse_config(config_file)
    state.create_mailbox()
    box = state.mailbox
    if folder is not None:
        box.folder.set(folder)
    counter = 0
    for msg in box.fetch(bulk=True):
        apply_list(state.rules, box, msg, dry_run)
        counter += 1
    print()
    print(f"{counter} messages parsed.")


# @app.command()
def monitor(
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
    config_file: typer.FileText = typer.Option(...),
):
    """Monitor mailbox, and apply rules on unseen messages."""
    state.parse_config(config_file)
    state.create_mailbox()
    box = state.mailbox

    if folder is not None:
        box.folder.set(folder)
        logging.info(f"Starting monitoring {folder}")
    else:
        logging.info("Starting monitoring INBOX")
    while True:
        try:
            responses = box.idle.wait(timeout=60)
            if responses:
                for msg in box.fetch(AND(seen=False), mark_seen=False):
                    print(f"Found message [{{{msg.uid}}} {msg.from_} -> {msg.to} '{msg.subject}']")
                    apply_list(state.rules, box, msg, dry_run)
        except imaplib.IMAP4.abort:
            logger.warning("IMAP connection aborted, reconnecting ")
            state.create_mailbox()
            box = state.mailbox
        except Exception:
            logger.exception("An error occured, reconnecting...")
            state.create_mailbox()
            box = state.mailbox
