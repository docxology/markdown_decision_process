"""Metadata extraction is exercised against the actual local Pandoc CLI."""
import shutil

import pytest

from mdp.pandoc import extract_metadata

pytestmark = pytest.mark.skipif(shutil.which("pandoc") is None, reason="Pandoc is unavailable")


def test_real_pandoc_metadata_preserves_public_scalar_fields(tmp_path):
    source = tmp_path / "metadata.md"
    source.write_text(
        '---\ntitle: Test Document\nauthor: Test Author\ndate: "2026-11-05"\n---\n\nBody.\n',
        encoding="utf-8",
    )
    assert extract_metadata(source) == {
        "title": "Test Document", "author": "Test Author", "date": "2026-11-05"
    }


def test_real_pandoc_metadata_preserves_typed_nested_values_and_inline_text(tmp_path):
    source = tmp_path / "metadata.md"
    source.write_text(
        '---\ntitle: "A *marked* title"\n'
        'author:\n  - Ada Example\n  - Bob Example\n'
        'draft: true\nproject:\n  code: demo\n  enabled: false\n'
        'tags: [one, two]\n---\n\nBody.\n',
        encoding="utf-8",
    )
    assert extract_metadata(source, format="markdown+yaml_metadata_block") == {
        "title": "A marked title",
        "author": ["Ada Example", "Bob Example"],
        "draft": True,
        "project": {"code": "demo", "enabled": False},
        "tags": ["one", "two"],
    }


def test_real_pandoc_document_without_metadata_returns_an_empty_mapping(tmp_path):
    source = tmp_path / "plain.md"
    source.write_text("# A body heading\n\nBody.\n", encoding="utf-8")
    assert extract_metadata(source) == {}
