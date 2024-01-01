from typing import Any
import pytest
from filmfarm.scrape import (
    parse_year,
    parse_list,
    parse_runtime,
    parse_nullable,
    parse_human_integer,
    parse_date,
    parse_rating,
    parse_omdb_json,
)


def test_parse_year():
    assert parse_year("2021") == 2021
    assert parse_year("1999") == 1999
    with pytest.raises(ValueError):
        parse_year("abcd")

def test_parse_list():
    assert parse_list("Action, Adventure, Sci-Fi") == ["Action", "Adventure", "Sci-Fi"]
    assert parse_list("Drama") == ["Drama"]

def test_parse_runtime():
    assert parse_runtime("120 min") == 120
    assert parse_runtime("90 min") == 90
    assert parse_runtime("59S min") == 59

def test_parse_nullable():
    assert parse_nullable(int)("123") == 123
    assert parse_nullable(int)("N/A") == None
    with pytest.raises(ValueError):
        parse_nullable(int)("Hello")
    assert parse_nullable(str)("Hello") == "Hello"

def test_parse_human_integer():
    assert parse_human_integer("1,234") == 1234
    assert parse_human_integer("10,000") == 10000

def test_parse_date():
    assert parse_date("23 Jun 2023") == "2023-06-23"

def test_parse_rating():
    fixture = [{'Source': 'Internet Movie Database', 'Value': '8.0/10'},
            {'Source': 'Metacritic', 'Value': '94/100'}]
    assert parse_rating(fixture) == [
        {'Source': 'Internet Movie Database', 'Value': 80},
        {'Source': 'Metacritic', 'Value': 94},
    ]

def test_parse_omdb_json(
        tt13238346_omdb_raw: dict, tt13238346_omdb_processed: dict):
    tt13238346_omdb_raw.pop('Response')
    assert parse_omdb_json(tt13238346_omdb_raw) == tt13238346_omdb_processed