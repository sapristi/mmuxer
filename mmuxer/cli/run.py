import logging
from pathlib import Path
from typing import Union

import typer

from mmuxer.config_state import state
from mmuxer.models.rule import apply_list
from mmuxer.utils import config_file_typer_option, progress_when_tty
from mmuxer.workers import MonitorWorker, WatcherWorker

logger = logging.getLogger(__name__)


def _tidy(
    folder: Union[str, None],
    dry_run: bool,
):
    box = state.mailbox
    if folder is not None:
        box.folder.set(folder)
    counter = 0
    total_emails = len(box.numbers())
    with progress_when_tty() as progress:
        task = progress.add_task("[bold blue]Preparing to tidy emails...", total=total_emails)
        for msg in box.fetch(bulk=100, mark_seen=False):
            msg.associated_folder = folder
            apply_list(state.rules, box, msg, dry_run)
            for script in state.scripts:
                script.apply(msg, dry_run=dry_run)
            counter += 1
            progress.update(
                task,
                description=f"[bold blue]Tidied {counter}/{total_emails} emails...",
                advance=1,
            )
    logger.info(f"{counter} messages tidied.")


def tidy(
    config_file: Path = config_file_typer_option,
    folder: Union[str, None] = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Run once, on all messages of the INBOX (or the given folder)."""
    state.load_config_file(config_file)
    state.create_mailbox()
    _tidy(folder, dry_run)


def monitor(
    config_file: Path = config_file_typer_option,
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
    auto_reload: bool = typer.Option(
        False, help="Auto-reload config file on modification (EXPERIMENTAL)"
    ),
):
    """Monitor mailbox, and apply rules on unseen messages."""
    state.load_config_file(config_file)
    state.create_mailbox()

    if auto_reload:
        MonitorWorker(folder, dry_run).start()
        WatcherWorker().start()
    else:
        MonitorWorker(folder, dry_run).run()
