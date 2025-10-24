from pathlib import Path

import sievelib.managesieve
import typer
from rich import print

from mmuxer.config_state import state
from mmuxer.utils import config_file_typer_option


def setup_callback(
    config_file: Path = config_file_typer_option,
):
    state.load_config_file(config_file)
    state.create_mailbox()


app = typer.Typer(
    name="managesieve",
    callback=setup_callback,
    no_args_is_help=True,
    help="Interract with managesieve server.",
)


@app.command()
def list():
    """List sieve scripts on the server."""
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
    script_name: str = typer.Argument(..., help="Name for the script on the server"),
):
    """Upload a sieve script generated from rules to the server."""
    settings = state.settings

    # Generate script content from rules
    rules_str = "\n".join(sieve_rule for rule in state.rules for sieve_rule in rule.to_sieve_str())
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
        print(f"[red]Error:[/red] Failed to upload script '{script_name}'")
        raise typer.Exit(1)
