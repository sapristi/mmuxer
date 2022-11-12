import typer
from devtools import debug

from ..config_state import state

app = typer.Typer(name="folder", callback=state.create_mailbox, no_args_is_help=True)


@app.command()
def list():
    """List existing folders."""
    folder_names = sorted((f.name for f in state.mailbox.folder.list()))
    debug(folder_names)


@app.command()
def create(name: str):
    """Create a new folder."""
    state.mailbox.folder.create(name)


@app.command()
def delete(name: str):
    """Delete a folder."""
    state.mailbox.folder.delete(name)


@app.command()
def rename(old_name: str, new_name: str):
    """Rename a folder."""
    state.mailbox.folder.rename(old_name, new_name)


@app.command()
def show_destinations():
    """List destinations folders from your configuration."""
    destinations = sorted({dest for filter_ in state.filters for dest in filter_.destinations()})
    debug(destinations)


@app.command()
def compare_destinations():
    """Compare existing folders with destinations from the configuration"""
    destinations = {dest for filter_ in state.filters for dest in filter_.destinations()}
    folder_names = {f.name for f in state.mailbox.folder.list()}
    folders_with_destination = sorted(destinations & folder_names)
    destinations_without_folder = sorted(destinations - folder_names)
    folders_without_destination = sorted(folder_names - destinations)
    debug(
        folders_with_destination=folders_with_destination,
        destinations_without_folder=destinations_without_folder,
        folders_without_destination=folders_without_destination,
    )


@app.command()
def create_missing_folders():
    """Create missing folders."""
    destinations = {dest for filter_ in state.filters for dest in filter_.destinations()}
    folder_names = {f.name for f in state.mailbox.folder.list()}
    destinations_without_folder = sorted(destinations - folder_names)

    debug(will_create_folders=destinations_without_folder)

    input("Will create the given folders, is that oK? (Ctrl-c to quit)")
    for folder in destinations_without_folder:
        state.mailbox.folder.create(folder)
