from pathlib import Path
from filmfarm.link import group_collections, yield_symlink_pairs, relative_symlink


def test_relative_symlink(tmpdir):
    source = (Path(tmpdir) / "spam" / "eggs" / "bacon" / "source").resolve()
    target = (Path(tmpdir) / "foo" / "bar" / "baz" / "target").resolve()
    source.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    relative_symlink(source, target)
    assert source.is_symlink()
    assert source.resolve() == target
    assert str(source.readlink()) == "../../../foo/bar/baz/target"


def test_yield_symlink_pairs(tmpdir_with_blobs):
    symlinks = [
        (d.name, s) for d, s in yield_symlink_pairs(Path(tmpdir_with_blobs) / "blobs")
    ]
    assert symlinks == [
        ("tt0829150", "Dracula Untold (2014)"),
        ("tt0013442", "Nosferatu (1922)"),
        ("tt0080684", "Star Wars: Episode V - The Empire Strikes Back (1980)"),
        ("tt0076759", "Star Wars: Episode IV - A New Hope (1977)"),
        ("tt0021814", "Dracula (1931)"),
        ("tt0051554", "Horror of Dracula (1958)"),
        ("tt0086190", "Star Wars: Episode VI - Return of the Jedi (1983)"),
        ("tt0103874", "Bram Stoker's Dracula (1992)"),
    ]


def test_group_collections(tmpdir_with_blobs):
    groups = group_collections(Path(tmpdir_with_blobs) / "blobs")
    multi = {k: v for k, v in groups.items() if len(v) > 1}
    assert multi == {
        "Star Wars": [
            ("tt0080684", "1980. The Empire Strikes Back"),
            ("tt0076759", "1977. Star Wars"),
            ("tt0086190", "1983. Return of the Jedi"),
        ]
    }
