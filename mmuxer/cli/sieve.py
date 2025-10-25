import logging
from pathlib import Path

import sievelib.managesieve
import typer
from rich import print

from mmuxer.config_state import state
from mmuxer.utils import config_file_typer_option

logger = logging.getLogger(__name__)


app = typer.Typer(
    name="sieve",
    no_args_is_help=True,
    help="Interract with managesieve server.",
)


@app.command()
def list(
    config_file: Path = config_file_typer_option,
):
    """List sieve scripts on the server."""
    state.load_config_file(config_file)
    settings = state.settings

    client = sievelib.managesieve.Client(settings.server, srvport=4190)
    client.connect(login=settings.username, password=settings.password, starttls=True)

    active_script, scripts = client.listscripts()

    if not scripts:
        print("[yellow]No scripts found on the server[/yellow]")
    else:
        if active_script:
            print("[bold green]Active script:[/bold green]")
            print(f"  {active_script}\n")
        else:
            print("[yellow]No active script set[/yellow]\n")

        other_scripts = [s for s in scripts if s != active_script]
        if other_scripts:
            print("[bold]Other scripts:[/bold]")
            for script in other_scripts:
                print(f"  {script}")
        elif active_script:
            print("[dim]No other scripts[/dim]")


@app.command()
def put(
    config_file: Path = config_file_typer_option,
    script_name: str | None = typer.Option(
        None, help="Name for the script on the server. Can also be set in the config file."
    ),
    set_active: bool = typer.Option(True, help="Set the created filter as the active one."),
):
    """Upload a sieve script generated from rules to the server."""
    state.load_config_file(config_file)
    settings = state.settings

    if not script_name:
        script_name = settings.sieve.name
    if not script_name:
        print("[bold red]script name must either be in config or passed as an option")
        raise typer.Exit(1)

    # Generate script content from rules
    rules_str = "\n".join(sieve_rule for rule in state.rules for sieve_rule in rule.to_sieve())
    sieve_extensions = ",".join(f'"{ext_name}"' for ext_name in settings.sieve.extensions)
    script_content = f"""require [{sieve_extensions}];
{rules_str}
"""

    client = sievelib.managesieve.Client(settings.server, srvport=4190)
    client.connect(login=settings.username, password=settings.password, starttls=True)

    print(f"[blue]Uploading script '{script_name}' to server...[/blue]")
    success = client.putscript(script_name, script_content)

    if success:
        print(f"[green]Success:[/green] Script '{script_name}' uploaded successfully")
    else:
        print(f"[red]Error:[/red] Failed _to upload script '{script_name}'")
        raise typer.Exit(1)

    if set_active:
        client.setactive(script_name)


@app.command()
def export(
    config_file: Path = config_file_typer_option,
    dest_file: Path | None = typer.Option(
        None, help="File to write. If not provided, write to stdout."
    ),
):
    """Convert the rules of the give config file to sieve format."""
    state.load_config_file(config_file)
    rules_str = "\n".join(sieve_rule for rule in state.rules for sieve_rule in rule.to_sieve())
    sieve_extensions = ",".join(f'"{ext_name}"' for ext_name in state.settings.sieve.extensions)
    output = f"""require [{sieve_extensions}];
{rules_str}
"""
    if dest_file is None:
        print(output)
    else:
        dest_file.write_text(output)
        logger.info(f"Rules written to '{dest_file.resolve()}'")
