import typer
import os
import json
import shutil
from pathlib import Path
import json
import shutil

app = typer.Typer()

@app.command()
def movies(blobs_path: str, target_path: str):
    """
    Link movie directories by year and name.
    """
    target_dir = Path(target_path)
    if target_dir.exists():
        raise typer.Exit(f"{target_dir} already exists.")
    target_dir.mkdir(parents=True)

    blobs_dir = Path(blobs_path)
    for movie_id in blobs_dir.iterdir():
        movie_dir = blobs_dir / movie_id
        metadata_file = movie_dir / 'imdb.json'
        if not metadata_file.is_file():
            continue
        with open(metadata_file) as f:
            metadata = json.load(f)
        symlink_name = (
            f"{metadata['Title']} ({metadata['Year']})".replace('/', '_'))
        (target_dir / symlink_name).symlink_to(movie_dir)

@app.command()
def collections(imdb_dir: str, collections_dir: str):
    """
    Link movie directories by collection, year and name.
    """
    collections_dir_path = Path(collections_dir)
    imdb_path = Path(imdb_dir)
    if collections_dir_path.exists():
        raise typer.Exit(f"{collections_dir_path} already exists.")
    collections_dir_path.mkdir(parents=True)

    collections = {}
    for movie_id in os.listdir(imdb_path):
        movie_dir = Path(imdb_path) / movie_id
        metadata_file = movie_dir / 'tmdb.json'
        if not metadata_file.is_file():
            continue
        with open(metadata_file) as handle:
            metadata = json.load(handle)
        if not metadata['belongs_to_collection']:
            continue
        collection = metadata['belongs_to_collection']['name']
        if collection.endswith(" Collection"):
            collection = collection[:-len(" Collection")]
        collections.setdefault(collection, [])
        collection_path = collections_dir_path / collection
        title = metadata['title']
        year = metadata['release_date'].split('-')[0]
        symlink_name = f"{year}. {title}".replace('/', '_')
        symlink_path = collection_path / symlink_name
        collections[collection].append(
            (collection_path, movie_id, symlink_path))

    for collection in collections:
        if len(collections[collection]) <= 1:
            continue
        for collection_path, movie_id, symlink_path in collections[collection]:
            collection_path.mkdir(parents=True, exist_ok=True)
            symlink_path.symlink_to(imdb_path / movie_id)
