from filmfarm.models import Blob

import pytest


def test_bad_blob(tmpdir):
    blob = Blob("/i/do/not/exist")
    with pytest.raises(LookupError):
        blob.imdb
    with pytest.raises(LookupError):
        blob.poster
    with pytest.raises(OSError):
        Blob.from_dir("/i/do/not/exist")

    tmpdir.mkdir("not_a_blob")
    with pytest.raises(ValueError):
        Blob.from_dir(tmpdir / "not_a_blob")

    tmpdir.mkdir("tt123456")
    blob = Blob.from_dir(tmpdir / "tt123456")
    with pytest.raises(LookupError):
        blob.imdb


def test_good_blob(tmpdir_with_blobs):
    with pytest.raises(OSError):
        Blob.from_dir(tmpdir_with_blobs / "tt123456")
    blob = Blob.from_dir(tmpdir_with_blobs / "tt0013442")
    assert blob.id == "tt0013442"
    assert blob.imdb["Title"] == "Nosferatu"


def test_blob_iteration(tmpdir_with_blobs):
    titles = {b.imdb["Title"] for b in Blob.iterate_from_dir(tmpdir_with_blobs)}
    assert titles == {
        "Bram Stoker's Dracula",
        "Dracula",
        "Dracula Untold",
        "Horror of Dracula",
        "Nosferatu",
        "Star Wars: Episode IV - A New Hope",
        "Star Wars: Episode V - The Empire Strikes Back",
        "Star Wars: Episode VI - Return of the Jedi",
    }
