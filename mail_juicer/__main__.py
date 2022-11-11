import typer
from devtools import debug
from imap_tools import AND

from .misc import make_mailbox, parse_config
from .models import Filter

app = typer.Typer()


@app.command()
def check(config_file: typer.FileText = typer.Option(...)):
    filters, settings = parse_config(config_file)
    box = make_mailbox(settings)
    debug(filters)


@app.command()
def run_single(config_file: typer.FileText = typer.Option(...)):
    filters, settings = parse_config(config_file)
    box = make_mailbox(settings)
    for msg in box.fetch(bulk=True):
        print(msg.date, msg.subject, len(msg.text or msg.html))
        Filter.apply_list(filters, box, msg)


@app.command()
def run_continuous(config_file: typer.FileText = typer.Option(...)):
    filters, settings = parse_config(config_file)
    box = make_mailbox(settings)

    while True:
        responses = box.idle.wait(timeout=60)
        if responses:
            for msg in box.fetch(AND(seen=False), mark_seen=False):
                print(msg.uid, msg.date, msg.subject, len(msg.text or msg.html))
                Filter.apply_list(filters, box, msg)


if __name__ == "__main__":
    app()
