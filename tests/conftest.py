from pathlib import Path
import pytest
import json

testdata = Path(__file__).resolve().parent / "testdata"


def load_json(name):
    with open(testdata / name) as handle:
        return json.load(handle)


@pytest.fixture
def tt13238346_omdb_raw():
    return load_json("tt13238346.omdb_raw.json")


@pytest.fixture
def tt13238346_omdb_processed():
    return load_json("tt13238346.omdb_processed.json")
