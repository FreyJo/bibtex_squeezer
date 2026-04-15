"""Shared fixtures for bibtex_squeezer tests."""

from pathlib import Path

import pytest

# Directory containing .bib fixture files
BIB_DIR = Path(__file__).parent / "bib_files"


@pytest.fixture
def bib_path(request, tmp_path):
    """Copy a .bib fixture to a temp directory and return its path.

    Use via indirect parametrize::

        @pytest.mark.parametrize("bib_path", ["my_case.bib"], indirect=True)
        def test_something(bib_path):
            ...
    """
    src = BIB_DIR / request.param
    dst = tmp_path / src.name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst
