#!/bin/bash

trap 'echo "❌ Error at line $LINENO"; exit 1' ERR
set -e

dracula="tt0013442 tt0021814 tt0051554 tt0103874 tt0829150"
star_wars="tt0076759 tt0080684 tt0086190"

echo "📋 Checking requirements"
[ -x "$(which filmfarm)" ] || { echo "  👉 filmfarm not installed" ; exit 1 ; }
if [ ! -f .env ]; then
    [ "$TMDB_API_KEY" ] || { echo "  👉 TMDB_API_KEY not set" && exit 1 ; }
    [ "$OMDB_API_KEY" ] || { echo "  👉 OMDB_API_KEY not set" && exit 1 ; }
fi

echo "🧪 Clearing old test data"
TEST_DIR="/tmp/filmfarm.test.d"
rm -fr "$TEST_DIR"

echo "🔍 Running tests"

echo -n "🎬 Scraping test films ["
for x in $dracula $star_wars; do
    echo -n "."
    mkdir -p "$TEST_DIR/blobs/$x"
    filmfarm scrape omdb "$TEST_DIR/blobs/$x" ; [ -f "$TEST_DIR/blobs/$x/imdb.json" ]
    filmfarm scrape tmdb "$TEST_DIR/blobs/$x" ; [ -f "$TEST_DIR/blobs/$x/tmdb.json" ]
done
echo "]"

echo "📸 Scraping a movie poster"
filmfarm scrape poster "$TEST_DIR/blobs/$x" ; [ -f "$TEST_DIR/blobs/$x/poster.jpg" ]

echo "🔗 Creating linkfarm"
filmfarm link movies "$TEST_DIR/blobs" "$TEST_DIR/movies"
[ $(find "$TEST_DIR/movies" -type l | wc -l) -eq 8 ]
[ -L "$TEST_DIR/movies/Nosferatu (1922)" ]
grep -q Nosferatu "$TEST_DIR/movies/Nosferatu (1922)/imdb.json"

filmfarm link collections "$TEST_DIR/blobs" "$TEST_DIR/collection"
[ -d "$TEST_DIR/collection/Star Wars" ]
[ $(find "$TEST_DIR/collection/Star Wars" -type l | wc -l) -eq 3 ]

echo "✅ All tests passed"