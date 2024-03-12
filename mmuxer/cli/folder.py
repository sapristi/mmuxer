from pathlib import Path

import typer
from rich import print
from rich.pretty import Node, pretty_repr

from mmuxer.config_state import state
from mmuxer.utils import config_file_typer_option


def setup_callback(
    config_file: Path = config_file_typer_option,
):
    state.load_config_file(config_file)
    state.create_mailbox()


app = typer.Typer(
    name="folder",
    callback=setup_callback,
    no_args_is_help=True,
    help="Various IMAP folder helpers.",
)


def render_with_name(name, value):
    value_repr = pretty_repr(value)
    return Node(key_repr=name, value_repr=value_repr).render()


def print_with_name(name, value):
    print(render_with_name(name, value))


@app.command(rich_help_panel="Generic commands")
def list():
    """List existing folders."""
    folder_names = sorted((f.name for f in state.mailbox.folder.list()))
    print_with_name("folder_names", folder_names)


@app.command(rich_help_panel="Generic commands")
def create(name: str):
    """Create a new folder."""
    state.mailbox.folder.create(name)


@app.command(rich_help_panel="Generic commands")
def delete(name: str):
    """Delete a folder."""
    state.mailbox.folder.delete(name)


@app.command(rich_help_panel="Generic commands")
def rename(old_name: str, new_name: str):
    """Rename a folder."""
    state.mailbox.folder.rename(old_name, new_name)


@app.command(rich_help_panel="Helper commands")
def show_destinations():
    """List destinations folders from your configuration."""
    destinations = sorted({dest for rule in state.rules for dest in rule.destinations()})
    print_with_name("[bold]destinations", destinations)


@app.command(rich_help_panel="Helper commands")
def compare_destinations():
    """Compare existing folders with destinations from the configuration"""
    destinations = {dest for rule in state.rules for dest in rule.destinations()}
    folder_names = {f.name for f in state.mailbox.folder.list()}
    folders_with_destination = sorted(destinations & folder_names)
    destinations_without_folder = sorted(destinations - folder_names)
    folders_without_destination = sorted(folder_names - destinations)
    print_with_name("[bold]folders_with_destination", folders_with_destination)
    print_with_name("[bold]folders_without_destination", folders_without_destination)
    print_with_name("[bold]destinations_without_folder", destinations_without_folder)


@app.command(rich_help_panel="Helper commands")
def create_missing_folders():
    """Create missing folders."""
    destinations = {dest for rule in state.rules for dest in rule.destinations()}
    folder_names = {f.name for f in state.mailbox.folder.list()}
    destinations_without_folder = sorted(destinations - folder_names)

    print_with_name("will_create_folders", destinations_without_folder)

    input("Will create the given folders, is that oK? (Ctrl-c to quit)")
    for folder in destinations_without_folder:
        state.mailbox.folder.create(folder)


@app.command(rich_help_panel="Bulk operations")
def move_emails(source_folder: str, dest_folder: str):
    """Move all emails in `source_folder` to `dest_folder`"""

    box = state.mailbox
    box.folder.set(source_folder)
    for msg in box.fetch(bulk=True):
        box.move(msg.uid, dest_folder)
