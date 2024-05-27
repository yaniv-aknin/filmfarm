import typer

from . import scrape, link

app = typer.Typer()
app.add_typer(scrape.app, name="scrape")
app.add_typer(link.app, name="link")
