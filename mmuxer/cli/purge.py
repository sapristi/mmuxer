from pathlib import Path

import typer
from imap_tools.query import AND
from rich import print

from mmuxer.config_state import state
from mmuxer.utils import config_file_typer_option


def purge(
    config_file: Path = config_file_typer_option,
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Purge specified emails. This is still alpha and may break at any time"""
    state.load_config_file(config_file)
    state.create_mailbox()
    box = state.mailbox

    for policy in state.purge_policies:
        box.folder.set(policy.folder)
        filters = {}
        if policy.flag:
            filters["keyword"] = policy.flag.imap
        if policy.custom_flag:
            filters["keyword"] = policy.custom_flag
        nb_messages = len(box.uids(AND(**filters)))
        print(f"[bold blue]{policy.display_name()}: {nb_messages} messages pending deletion.")
