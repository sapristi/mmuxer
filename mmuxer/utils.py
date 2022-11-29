import typer

config_file_typer_option = typer.Option(
    ..., exists=True, dir_okay=False, readable=True, resolve_path=True
)
