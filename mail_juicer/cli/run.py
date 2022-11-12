import typer
from imap_tools import AND

from ..config_state import state
from ..models.filter import apply_list

app = typer.Typer(
    name="run",
    callback=state.create_mailbox,
    no_args_is_help=True,
    short_help="Execute the configured filters.",
)


@app.command()
def single(
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Run once, on all messages of the INBOX (or the given folder)."""
    box = state.mailbox
    if folder is not None:
        box.folder.set(folder)
    counter = 0
    for msg in box.fetch(bulk=True):
        apply_list(state.filters, box, msg, dry_run)
        counter += 1
    print()
    print(f"{counter} messages parsed.")


@app.command()
def continuous(
    folder: str = typer.Option(None, help="Folder to fetch the messages from"),
    dry_run: bool = typer.Option(False, help="Print actions instead of running them"),
):
    """Run continuously, and apply filter on unseen messages"""
    box = state.mailbox
    if folder is not None:
        box.folder.set(folder)
    while True:
        responses = box.idle.wait(timeout=60)
        if responses:
            for msg in box.fetch(AND(seen=False), mark_seen=False):
                print(f"Found message [{{{msg.uid}}} {msg.from_} -> {msg.to} '{msg.subject}']")
                apply_list(state.filters, box, msg, dry_run)
