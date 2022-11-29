import enum
import logging
import os
from pathlib import Path

import typer
from rich.logging import RichHandler
from rich.pretty import pprint
from typer.core import TyperGroup

from .cli.folder import app as folder_app
from .cli.run import monitor as monitor_cmd
from .cli.run import tidy as tidy_cmd
from .config_state import state
from .utils import config_file_typer_option


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
    if os.isatty(0):
        handler = RichHandler(
            rich_tracebacks=True, show_time=False, show_path=(log_level == LogLevel.DEBUG)
        )
    else:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_level.name,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )


app = typer.Typer(no_args_is_help=True, cls=OrderCommands, callback=main_callback)


app.command(rich_help_panel="Main commands")(monitor_cmd)
app.command(rich_help_panel="Main commands")(tidy_cmd)


@app.command(rich_help_panel="Util commands")
def check(config_file: Path = config_file_typer_option):
    """Load the config and connect to the IMAP server."""
    state.load_config_file(config_file)
    state.create_mailbox()
    pprint(state.rules)


app.add_typer(folder_app, rich_help_panel="Util commands")

if __name__ == "__main__":
    app()
