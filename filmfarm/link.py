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
        for movie_id, symlink_name in collections[collection]:
            (target / collection).mkdir(parents=True, exist_ok=True)
            relative_symlink(target / collection / symlink_name, blobs / movie_id)
