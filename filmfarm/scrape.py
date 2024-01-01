import re
import json
import datetime
import typing
import os
from pathlib import Path

import typer
import requests

app = typer.Typer()

def parse_year(f: str) -> int:
    return int(f.split('–')[0])

def parse_list(f: str) -> list[str]:
    return f.split(', ')

def parse_runtime(f: str) -> int:
    if f == '59S min':
        return 59 # hack for invalid entry tt0083437
    assert f.endswith(' min')
    return int(f.replace(' min', ''))

def parse_nullable(cast: callable) -> typing.Optional[str]:
    def parse(f: str):
        if f == 'N/A':
            return None
        return cast(f)
    return parse

def parse_human_integer(f: str) -> int:
    return int(f.replace('$', '').replace(',',  ''))

def parse_date(f: str) -> str:
    return datetime.datetime.strptime(f, '%d %b %Y').date().strftime('%Y-%m-%d')


def parse_rating(f: str) -> int:
    parsers = {
        'Internet Movie Database': lambda x: int(float(x.split('/')[0])*10),
        'Metacritic': lambda x: int(x.split('/')[0]),
        'Rotten Tomatoes': lambda x: int(x.replace('%', '')),
    }
    for r in f:
        r['Value'] = parsers[r['Source']](r['Value'])
    return f


def get_env_key(name: str) -> str:
    """
    Get an API key from the environment or exit.
    """
    if name not in os.environ:
        raise typer.Exit(f"Missing environment variable {name}")
    return os.environ[name]

def validate_omdb(response: requests.Response) -> None:
    """
    Validate an OMDB response or exit.
    """
    response.raise_for_status()
    if response.json()["Response"] == "False":
        raise typer.Exit(response.json()["Error"])

_omdb_spec = dict(
    Year = parse_year,
    Runtime = parse_runtime,
    Genre = parse_list,
    Director = parse_list,
    Writer = parse_list,
    Actors = parse_list,
    Country = parse_list,
    Language = parse_list,
    Metascore = parse_nullable(int),
    imdbRating = parse_nullable(float),
    imdbVotes = parse_nullable(parse_human_integer),
    BoxOffice = parse_nullable(parse_human_integer),
    Rated = parse_nullable(str),
    Awards = parse_nullable(str),
    Website = parse_nullable(str),
    Production = parse_nullable(str),
    Ratings = parse_rating,
    Released = parse_nullable(parse_date),
    DVD = parse_nullable(parse_date),
    Season = parse_nullable(int),
    Episode = parse_nullable(int),
    seriesID = parse_nullable(int),
)

def parse_omdb_json(doc: dict) -> dict:
    """
    Parse an OMDB JSON document.
    """
    for key, mutator in _omdb_spec.items():
        if key not in doc:
            continue
        try:
            doc[key] = mutator(doc[key])
        except Exception as error:
            raise ValueError(f"can't process {doc['imdbID']} key {key}: {error}\n")
    return doc

@app.command()
def omdb(imdb_path: str):
    """
    Scrape OMDB metadata for a movie, process it and store in imdb.json.
    """
    imdb_path = Path(imdb_path)
    if not imdb_path.is_dir():
        raise typer.Exit(f"{imdb_path} is not a valid directory path.")

    imdb_id = imdb_path.name
    if not re.match(r"tt[0-9]+", imdb_id):
        raise typer.Exit(f"{imdb_id} is not a valid IMDb ID.")

    if (imdb_path / "imdb.json").is_file():
        return

    response = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": get_env_key("OMDB_API_KEY"),
            "i": imdb_id,
        }
    )
    validate_omdb(response)
    doc = response.json()
    doc.pop('Response')
    try:
        processed = parse_omdb_json(doc)
    except ValueError as error:
        raise typer.Exit(str(error))
    with open(imdb_path / "imdb.json", "w") as handle:
        json.dump(processed, handle, indent=4)