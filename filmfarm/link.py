import os
from pathlib import Path
import typing as t

import typer

from .models import Blob

app = typer.Typer()


def relative_symlink(source: Path, target: Path):
    common_path = os.path.commonpath([source, target])
    prefix = "../" * len(source.parent.relative_to(common_path).parts)
    relative_target = prefix / target.relative_to(common_path)
    source.symlink_to(relative_target)


def yield_symlink_pairs(blobs: Path):
    for blob in Blob.iterate_from_dir(blobs, predicate=lambda b: b.has("imdb.json")):
        metadata = blob.imdb
        symlink_name = f"{metadata['Title']} ({metadata['Year']})".replace("/", "_")
        yield blob.path, symlink_name


@app.command()
def movies(
    blobs: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
    target: t.Annotated[Path, typer.Argument(exists=False)],
):
    """
    Link movie directories by year and name.
    """
    target.mkdir(parents=True)

    for movie_dir, symlink_name in yield_symlink_pairs(Path(blobs)):
        relative_symlink(target / symlink_name, movie_dir)


def group_collections(blobs: Path) -> dict:
    collections = {}
    for blob in Blob.iterate_from_dir(blobs, predicate=lambda b: b.has("imdb.json")):
        metadata = blob.tmdb
        if not metadata["belongs_to_collection"]:
            continue
        collection = metadata["belongs_to_collection"]["name"]
        if collection.endswith(" Collection"):
            collection = collection[: -len(" Collection")]
        collections.setdefault(collection, [])
        title = metadata["title"]
        year = metadata["release_date"].split("-")[0]
        symlink_name = f"{year}. {title}".replace("/", "_")
        collections[collection].append((blob.id, symlink_name))
    return collections


def symlink_group(
    target: Path, blobs: Path, group: str, members: list[tuple[str, str]]
):
    for movie_id, name in members:
        (target / group).mkdir(parents=True, exist_ok=True)
        relative_symlink(target / group / name, blobs / movie_id)


@app.command()
def collections(
    blobs: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
    target: t.Annotated[Path, typer.Argument(exists=False)],
):
    """
    Link movie directories by collection, year and name.
    """
    target.mkdir(parents=True)

    collections = group_collections(blobs)

    for collection in collections:
        if len(collections[collection]) <= 1:
            continue
        symlink_group(target, blobs, collection, collections[collection])


@app.command()
def by_year(
    blobs: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
    target: t.Annotated[Path, typer.Argument(exists=False)],
):
    """
    Link movie directories by year, then name.
    """
    target.mkdir(parents=True)

    years = {}
    for blob in Blob.iterate_from_dir(
        blobs, predicate=lambda b: isinstance(b.imdb.get("Year"), int)
    ):
        metadata = blob.imdb
        symlink_name = f'{metadata["Title"]}'.replace("/", "_")
        years.setdefault(str(metadata["Year"]), []).append((blob.id, symlink_name))

    for year in years:
        symlink_group(target, blobs, year, years[year])


@app.command()
def by_rating(
    blobs: t.Annotated[
        Path, typer.Argument(exists=True, dir_okay=True, file_okay=False)
    ],
    target: t.Annotated[Path, typer.Argument(exists=False)],
):
    """
    Link movie directories by imdb rating, then year and name.
    """
    target.mkdir(parents=True)

    ratings = {}
    for blob in Blob.iterate_from_dir(
        blobs, predicate=lambda b: isinstance(b.imdb.get("imdbRating"), float)
    ):
        metadata = blob.imdb
        title = metadata["Title"]
        year = str(metadata["Year"])
        if not (len(year) == 4) and year.isdigit():
            continue
        symlink_name = f"{year}. {title}".replace("/", "_")
        ratings.setdefault(str(metadata["imdbRating"]), []).append(
            (blob.id, symlink_name)
        )

    for rating in ratings:
        symlink_group(target, blobs, rating, ratings[rating])
