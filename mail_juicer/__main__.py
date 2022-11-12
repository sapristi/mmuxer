import typer
from devtools import debug

from .cli.folder import app as folder_app
from .cli.run import app as run_app
from .config_state import state

app = typer.Typer(no_args_is_help=True)


@app.callback()
def common_parameters(
    config_file: typer.FileText = typer.Option(...),
):
    state.parse_config(config_file)


@app.command()
def check():
    """Load the config and connect to the IMAP server."""
    state.create_mailbox()
    debug(state.filters)


app.add_typer(folder_app)
app.add_typer(run_app)

if __name__ == "__main__":
    app()
