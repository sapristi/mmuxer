import enum
import logging

import typer
from rich.logging import RichHandler
from rich.pretty import pprint
from typer.core import TyperGroup

from .cli.folder import app as folder_app
from .cli.run import monitor as monitor_cmd
from .cli.run import tidy as tidy_cmd
from .config_state import state


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: typer.Context):
        """Return list of commands in the order they appear."""
        return list(self.commands)  # get commands using self.commands


class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


def main_callback(log_level: LogLevel = typer.Option("info", case_sensitive=False)):
    logging.basicConfig(
        level=log_level.name,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_time=False)],
    )


app = typer.Typer(no_args_is_help=True, cls=OrderCommands, callback=main_callback)


app.command(rich_help_panel="Main commands")(monitor_cmd)
app.command(rich_help_panel="Main commands")(tidy_cmd)


@app.command(rich_help_panel="Util commands")
def check(config_file: typer.FileText = typer.Option(...)):
    """Load the config and connect to the IMAP server."""
    state.parse_config(config_file)
    state.create_mailbox()
    pprint(state.rules)


app.add_typer(folder_app, rich_help_panel="Util commands")

if __name__ == "__main__":
    app()
