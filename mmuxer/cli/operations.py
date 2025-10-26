import logging
from pathlib import Path

import typer

from mmuxer.config_state import state
from mmuxer.service.operation import apply_operation
from mmuxer.utils import config_file_typer_option

logger = logging.getLogger(__name__)


app = typer.Typer(
    name="operation",
    no_args_is_help=True,
    help="Box operations",
)


@app.command()
def run(
    name: str,
    config_file: Path = config_file_typer_option,
):

    state.load_config_file(config_file)
    state.create_mailbox()
    operations_by_name = {operation.name: operation for operation in state.operations}
    apply_operation(
        operations_by_name[name],
        ask_confirmation=True,
    )
