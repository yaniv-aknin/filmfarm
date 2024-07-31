import json
from pathlib import Path
import typing as t
import re

from . import abort


class Blob:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load_json(self, name: str) -> dict:
        try:
            return json.loads((self.path / name).read_text())
        except IOError as error:
            raise LookupError(f"no {name} for {self.path}") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid {name} for {self.path}") from error

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path}>"

    @property
    def id(self) -> str:
        return self.path.name

    @property
    def imdb(self) -> dict:
        return self.load_json("imdb.json")

    @property
    def tmdb(self) -> dict:
        return self.load_json("tmdb.json")

    @property
    def poster(self):
        if not (self.path / "poster.jpg").is_file():
            raise LookupError(f"no poster for {self.path}")
        return self.path / "poster.jpg"

    @classmethod
    def from_dir(cls, dir: Path | str) -> "Blob":
        dir = Path(dir)
        if not dir.is_dir():
            raise IOError(f"{dir} is not a valid directory path.")
        if not re.match(r"tt[0-9]+", dir.name):
            raise ValueError(f"{dir.name} is not a valid IMDb ID.")
        return cls(dir)

    @classmethod
    def iterate_from_dir(cls, dir: str | Path) -> t.Iterable["Blob"]:
        for blob_path in Path(dir).iterdir():
            try:
                yield cls.from_dir(blob_path)
            except (IOError, ValueError):
                continue


def blob_or_abort(imdb_path: Path) -> Blob:
    try:
        return Blob.from_dir(imdb_path)
    except (IOError, ValueError) as error:
        abort(str(error))
