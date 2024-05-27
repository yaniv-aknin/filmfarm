import typer
import os
import json
from pathlib import Path
from . import abort

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
def movies(blobs_path: str, target_path: str):
    """
    Link movie directories by year and name.
    """
    target_dir = Path(target_path)
    if target_dir.exists():
        abort(f"{target_dir} already exists.")
    target_dir.mkdir(parents=True)

    for movie_dir, symlink_name in yield_symlink_pairs(Path(blobs_path)):
        relative_symlink(target_dir / symlink_name, movie_dir)


def group_collections(imdb_path: Path) -> dict:
    collections = {}
    for movie_id in os.listdir(imdb_path):
        movie_dir = Path(imdb_path) / movie_id
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
        collections[collection].append((movie_id, symlink_name))
    return collections


@app.command()
def collections(imdb_dir: str, collections_dir: str):
    """
    Link movie directories by collection, year and name.
    """
    collections_dir_path = Path(collections_dir)
    imdb_path = Path(imdb_dir)
    if collections_dir_path.exists():
        abort(f"{collections_dir_path} already exists.")
    collections_dir_path.mkdir(parents=True)

    collections = group_collections(imdb_path)

    for collection in collections:
        if len(collections[collection]) <= 1:
            continue
        for movie_id, symlink_name in collections[collection]:
            (collections_dir_path / collection).mkdir(parents=True, exist_ok=True)
            relative_symlink(
                collections_dir_path / collection / symlink_name, imdb_path / movie_id
            )
