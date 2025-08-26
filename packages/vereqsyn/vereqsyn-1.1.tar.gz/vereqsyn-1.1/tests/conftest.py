import pathlib

import pytest


@pytest.fixture(scope="session")
def fixtures() -> pathlib.Path:
    """Return a pathlib.Path to the fixtures directory."""
    return pathlib.Path(__file__).parent / "fixtures"
