import typer


def abort(message: str):
    typer.echo(message, err=True)
    raise typer.Exit(1)
