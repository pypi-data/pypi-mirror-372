from qqgjyx import __version__


def test_version_string():
    assert isinstance(__version__, str) and len(__version__) > 0


