"""Reject unreviewed corpus bytes before CI extraction without network access."""

from pathlib import Path
import runpy

import pytest


@pytest.mark.parametrize("size", [0, 896069, 896070])
def test_unreviewed_archive_is_rejected_without_creating_destination(tmp_path, size):
    script = Path(__file__).resolve().parents[1] / ".github/scripts/prepare_test_data.py"
    prepare = runpy.run_path(str(script))["prepare"]
    archive = tmp_path / "unreviewed.zip"
    archive.write_bytes(b"x" * size)
    destination = tmp_path / "nltk_data"
    with pytest.raises(ValueError, match="reviewed size/SHA-256"):
        prepare(destination, archive)
    assert not destination.exists()
