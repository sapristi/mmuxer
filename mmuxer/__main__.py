import typer

from .cli.folder import app as folder_app
from .cli.run import app as run_app
from .config_state import state

app = typer.Typer(no_args_is_help=True)

import logging

from rich.logging import RichHandler
from rich.pretty import pprint

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_time=False)],
)


@app.callback()
def common_parameters(
    config_file: typer.FileText = typer.Option(...),
):
    state.parse_config(config_file)


@app.command()
def check():
    """Load the config and connect to the IMAP server."""
    state.create_mailbox()
    pprint(state.rules)


app.add_typer(folder_app)
app.add_typer(run_app)

if __name__ == "__main__":
    app()
