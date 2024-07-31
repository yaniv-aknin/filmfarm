import os
import json
from pathlib import Path
import typing as t

import typer

app = typer.Typer()


def relative_symlink(source: Path, target: Path):
    common_path = os.path.commonpath([source, target])
    prefix = "../" * len(source.parent.relative_to(common_path).parts)
    relative_target = prefix / target.relative_to(common_path)
    source.symlink_to(relative_target)


def yield_symlink_pairs(blobs_path: Path):
    for movie_dir in blobs_path.iterdir():
        metadata_file = movie_dir / "imdb.json"
        if not metadata_file.is_file():
            continue
        with open(metadata_file) as f:
            metadata = json.load(f)
        symlink_name = f"{metadata['Title']} ({metadata['Year']})".replace("/", "_")
        yield movie_dir, symlink_name


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
    for movie_dir in blobs.iterdir():
        metadata_file = movie_dir / "tmdb.json"
        if not metadata_file.is_file():
            continue
        with open(metadata_file) as handle:
            metadata = json.load(handle)
        if not metadata["belongs_to_collection"]:
            continue
        collection = metadata["belongs_to_collection"]["name"]
        if collection.endswith(" Collection"):
            collection = collection[: -len(" Collection")]
        collections.setdefault(collection, [])
        title = metadata["title"]
        year = metadata["release_date"].split("-")[0]
        symlink_name = f"{year}. {title}".replace("/", "_")
        collections[collection].append((movie_dir.name, symlink_name))
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
