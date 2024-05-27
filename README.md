# filmfarm

A toolkit to manage movie collections. It provides utilities to scrape metadata/posters and organize
movies into directories based on their metadata.

It's useful if you have a film collection in a directory where each film is in its own subdirectory
named after the [IMDB ID] of the film. This is easier to demonstrate than explain; in the demo
the directories are empty, but in real life they could contain video files from your DVD backups etc.

[![filmfarm demo](https://asciinema.org/a/osw3RpP45H6jlUc9YNYZ32om0.svg)](https://asciinema.org/a/osw3RpP45H6jlUc9YNYZ32om0)

[IMDB ID]: https://developer.imdb.com/documentation/key-concepts

## Installation

filmfarm is best installed using [pipx](https://pipx.pypa.io/stable/); `pipx install filmfarm`.

## Usage

filmfarm provides a command-line interface (CLI) using [Typer](https://typer.tiangolo.com/).
See `filmfarm --help` for details.

## Prerequisites

filmfarm requires API keys for [OMDB] and [TMDB], as of this writing these keys are freely
available. You must set `OMDB_API_KEY` and `TMDB_API_KEY` in your environment, or create a [dotenv]
file in the project's directory if you're running from source.

[OMDB]: https://www.omdbapi.com/
[TMDB]: https://www.themoviedb.org/
[dotenv]: https://stackoverflow.com/q/68267862

## Development

filmfarm is packaged with [Poetry](https://python-poetry.org/). Once Poetry is installed and you've
cloned the filmfarm source repo, run `poetry install` to install all dependencies. You can then run
`poetry run filmfarm` or use `poetry shell` (see Poetry docs for details).

To run the tests, use `pytest`. There's also `integration.sh`, a little shell script which sort of
does integration tests (it actually uses API keys to download and link some data).

## Attribution
This package uses the [TMDB](https://www.themoviedb.org/) API but is not endorsed or certified by
TMDB. It also uses the [OMDB](https://www.omdbapi.com/) API. A tiny sample of API results is
included as testdata.
