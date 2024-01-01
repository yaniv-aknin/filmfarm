from collections import namedtuple
import re
import json
import os
from pathlib import Path

import typer
import requests

from .omdb import parse_omdb_json

app = typer.Typer()

IMDB = namedtuple("IMDB", ["path", "id"])

def get_env_key(name: str) -> str:
    """
    Get an API key from the environment or exit.
    """
    if name not in os.environ:
        raise typer.Exit(f"Missing environment variable {name}")
    return os.environ[name]

def valid_imdb(imdb_path: str) -> IMDB:
    """
    Validate IMDb path and return a namedtuple with path and ID.
    """
    imdb_path = Path(imdb_path)
    if not imdb_path.is_dir():
        raise typer.Exit(f"{imdb_path} is not a valid directory path.")

    imdb_id = imdb_path.name
    if not re.match(r"tt[0-9]+", imdb_id):
        raise typer.Exit(f"{imdb_id} is not a valid IMDb ID.")

    return IMDB(imdb_path, imdb_id)

@app.command()
def omdb(imdb_path: str):
    """
    Scrape OMDB metadata for a movie, process it and store in imdb.json.
    """
    imdb = valid_imdb(imdb_path)
    if (imdb.path / "imdb.json").is_file():
        return

    response = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": get_env_key("OMDB_API_KEY"),
            "i": imdb.id,
        }
    )
    response.raise_for_status()
    if response.json()["Response"] == "False":
        raise typer.Exit(response.json()["Error"])

    doc = response.json()
    doc.pop('Response')
    try:
        processed = parse_omdb_json(doc)
    except ValueError as error:
        raise typer.Exit(str(error))
    
    with open(imdb.path / "imdb.json", "w") as handle:
        json.dump(processed, handle, indent=4)