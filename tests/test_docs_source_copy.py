"""The real docs build keeps in-place technical guides and copies external sources."""
from docs.build_docs import copy_markdown_files


def test_copy_sources_preserves_in_place_guides_and_is_repeatable(tmp_path):
    docs = tmp_path / "docs"
    technical = docs / "technical"
    technical.mkdir(parents=True)
    (tmp_path / "README.md").write_text("# Public overview\n")
    (tmp_path / "CONTRIBUTING.md").write_text("# Contribution process\n")
    (docs / "ROADMAP.md").write_text("# Future work\n")
    first = technical / "markchain.md"
    second = technical / "policy_optimization.md"
    first.write_text("# Markchain source\n")
    second.write_text("# Policy source\n")
    for _ in range(2):
        copy_markdown_files(str(docs), str(docs))
        assert first.read_text() == "# Markchain source\n"
        assert second.read_text() == "# Policy source\n"
        assert (docs / "index.md").read_text() == "# Public overview\n"
        assert (docs / "dev/contributing.md").read_text() == "# Contribution process\n"
        assert (docs / "dev/roadmap.md").read_text() == "# Future work\n"
