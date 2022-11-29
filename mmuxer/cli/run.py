import logging
from pathlib import Path

import typer

from ..config_state import state
from ..models.rule import apply_list
from ..workers import MonitorWorker, WatcherWorker

logger = logging.getLogger(__name__)


def tidy(
    config_file: Path = typer.Option(..., exists=True, dir_okay=False, readable=True),
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Run once, on all messages of the INBOX (or the given folder)."""
    state.load_config_file(config_file)
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


def monitor(
    config_file: Path = typer.Option(..., exists=True, dir_okay=False, readable=True),
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Monitor mailbox, and apply rules on unseen messages."""
    state.load_config_file(config_file)
    state.create_mailbox()

    MonitorWorker(folder, dry_run).start()
    WatcherWorker().start()
