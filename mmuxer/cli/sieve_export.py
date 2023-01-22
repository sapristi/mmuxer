import logging
from pathlib import Path
from typing import Optional

import typer

from mmuxer.config_state import state
from mmuxer.utils import config_file_typer_option

logger = logging.getLogger(__name__)


def sieve_export(
    config_file: Path = config_file_typer_option,
    dest_file: Optional[Path] = typer.Option(
        None, help="File to write. If not provided, write to stdout."
    ),
):
    """Convert the rules of the give config file to sieve format."""
    state.load_config_file(config_file)
    rules_str = "\n".join(sieve_rule for rule in state.rules for sieve_rule in rule.to_sieve())
    output = f"""require ["fileinto","imap4flags","regex"];
{rules_str}
    """
    if dest_file is None:
        print(output)
    else:
        dest_file.write_text(output)
        logger.info(f"Rules written to '{dest_file.resolve()}'")
