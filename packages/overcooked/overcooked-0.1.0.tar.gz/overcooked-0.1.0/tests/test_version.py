import overcooked


def test_version_exists():
    assert hasattr(overcooked, "__version__")
    v = overcooked.__version__
    _major, _minor, _revision = v.split(".")
