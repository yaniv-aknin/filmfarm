import json
import os
from pathlib import Path
import dotenv
import typing as t

import typer
import requests
import tmdbsimple

from .omdb import parse_omdb_json
from ..models import blob_or_abort
from .. import abort

app = typer.Typer()


def get_env_key(name: str) -> str:
    """
    Get an API key from the environment or exit.
    """
    dotenv.load_dotenv()
    if name not in os.environ:
        abort(f"Missing environment variable {name}")
    return os.environ[name]


@app.command(name="omdb")
def omdb_(
    imdb_path: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
):
    """
    Scrape OMDB metadata for a movie, process it and store in imdb.json.
    """
    imdb = blob_or_abort(imdb_path)
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
def tmdb(
    imdb_path: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
):
    """
    Scrape TMDB metadata for a movie, process it and store in tmdb.json.
    """
    tmdbsimple.API_KEY = get_env_key("TMDB_API_KEY")

    imdb = blob_or_abort(imdb_path)
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
def poster(
    imdb_path: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
):
    """
    Download the poster image for a movie.
    """
    imdb = blob_or_abort(imdb_path)
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
