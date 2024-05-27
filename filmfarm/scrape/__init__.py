from collections import namedtuple
import re
import json
import os
from pathlib import Path
import dotenv

import typer
import requests
import tmdbsimple

from .omdb import parse_omdb_json
from .. import abort

app = typer.Typer()

IMDB = namedtuple("IMDB", ["path", "id"])


def get_env_key(name: str) -> str:
    """
    Get an API key from the environment or exit.
    """
    dotenv.load_dotenv()
    if name not in os.environ:
        abort(f"Missing environment variable {name}")
    return os.environ[name]


def valid_imdb(imdb_path: str | Path) -> IMDB:
    """
    Validate IMDb path and return a namedtuple with path and ID.
    """
    imdb_path = Path(imdb_path)
    if not imdb_path.is_dir():
        abort(f"{imdb_path} is not a valid directory path.")

    imdb_id = imdb_path.name
    if not re.match(r"tt[0-9]+", imdb_id):
        abort(f"{imdb_id} is not a valid IMDb ID.")

    return IMDB(imdb_path, imdb_id)


@app.command(name="omdb")
def omdb_(imdb_path: str):
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
        },
    )
    response.raise_for_status()
    if response.json()["Response"] == "False":
        abort(response.json()["Error"])

    doc = response.json()
    doc.pop("Response")
    try:
        processed = parse_omdb_json(doc)
    except ValueError as error:
        abort(str(error))

    with open(imdb.path / "imdb.json", "w") as handle:
        json.dump(processed, handle, indent=4)


@app.command()
def tmdb(imdb_path: str):
    """
    Scrape TMDB metadata for a movie, process it and store in tmdb.json.
    """
    tmdbsimple.API_KEY = get_env_key("TMDB_API_KEY")

    imdb = valid_imdb(imdb_path)
    if (imdb.path / "tmdb.json").is_file():
        return

    search = tmdbsimple.Find(imdb.id)
    results = search.info(external_source="imdb_id")["movie_results"]
    if not results:
        abort(f"No results found for IMDB ID {imdb.id}")
    if len(results) > 1:
        abort(f"Multiple results found for IMDB ID {imdb.id}")
    tmdb_id = results[0]["id"]
    processed = tmdbsimple.Movies(tmdb_id).info()

    with open(imdb.path / "tmdb.json", "w") as handle:
        json.dump(processed, handle, indent=4)


@app.command()
def poster(imdb_path: str):
    """
    Download the poster image for a movie.
    """
    imdb = valid_imdb(imdb_path)
    if (imdb.path / "poster.jpg").is_file():
        return

    if not (imdb.path / "imdb.json").is_file():
        abort(f"No imdb.json file found in {imdb.path}")
    with open(imdb.path / "imdb.json") as handle:
        imdb_json = json.load(handle)

    poster_url = imdb_json["Poster"]
    if poster_url == "N/A":
        abort(f"No poster available for {imdb.id}")
    response = requests.get(poster_url)
    response.raise_for_status()

    with open(imdb.path / "poster.jpg", "wb") as handle:
        handle.write(response.content)
