
import datetime
import typing


def parse_year(f: str) -> int:
    return int(f.split('–')[0])

def parse_list(f: str) -> list[str]:
    return f.split(', ')

def parse_runtime(f: str) -> int:
    if f == '59S min':
        return 59 # hack for invalid entry tt0083437
    assert f.endswith(' min')
    return int(f.replace(' min', ''))

def parse_nullable(cast: callable) -> typing.Optional[str]:
    def parse(f: str):
        if f == 'N/A':
            return None
        return cast(f)
    return parse

def parse_human_integer(f: str) -> int:
    return int(f.replace('$', '').replace(',',  ''))

def parse_date(f: str) -> str:
    return datetime.datetime.strptime(f, '%d %b %Y').date().strftime('%Y-%m-%d')


def parse_rating(f: str) -> int:
    parsers = {
        'Internet Movie Database': lambda x: int(float(x.split('/')[0])*10),
        'Metacritic': lambda x: int(x.split('/')[0]),
        'Rotten Tomatoes': lambda x: int(x.replace('%', '')),
    }
    for r in f:
        r['Value'] = parsers[r['Source']](r['Value'])
    return f

_omdb_spec = dict(
    Year = parse_year,
    Runtime = parse_runtime,
    Genre = parse_list,
    Director = parse_list,
    Writer = parse_list,
    Actors = parse_list,
    Country = parse_list,
    Language = parse_list,
    Metascore = parse_nullable(int),
    imdbRating = parse_nullable(float),
    imdbVotes = parse_nullable(parse_human_integer),
    BoxOffice = parse_nullable(parse_human_integer),
    Rated = parse_nullable(str),
    Awards = parse_nullable(str),
    Website = parse_nullable(str),
    Production = parse_nullable(str),
    Ratings = parse_rating,
    Released = parse_nullable(parse_date),
    DVD = parse_nullable(parse_date),
    Season = parse_nullable(int),
    Episode = parse_nullable(int),
    seriesID = parse_nullable(int),
)

def parse_omdb_json(doc: dict) -> dict:
    for key, mutator in _omdb_spec.items():
        if key not in doc:
            continue
        try:
            doc[key] = mutator(doc[key])
        except Exception as error:
            raise ValueError(f"can't process {doc['imdbID']} key {key}: {error}\n")
    return doc