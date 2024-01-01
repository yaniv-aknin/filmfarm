import typer

from . import scrape

app = typer.Typer()
app.add_typer(scrape.app, name="scrape")