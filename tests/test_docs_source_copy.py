"""The Sphinx build preserves maintained navigation and technical guides."""

from pathlib import Path

from docs.build_docs import build_docs


def test_build_preserves_sources_and_is_repeatable(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    technical = docs / "technical"
    technical.mkdir(parents=True)
    (tmp_path / "README.md").write_text("# Repository overview\n")
    index = docs / "index.md"
    guide = technical / "markchain.md"
    index.write_text("# Documentation index\n")
    guide.write_text("# Markchain guide\n")
    reference = docs / "reference"
    reference.mkdir()
    stub = reference / "markchain.rst"
    stub.write_text(".. automodule:: mdp.markchain\n")
    invocations = []

    def run_sphinx(command):
        invocations.append(command)

    monkeypatch.setattr("docs.build_docs.run_command", run_sphinx)
    for _ in range(2):
        build_docs(str(docs), str(docs / "_build/html"))
        assert index.read_text() == "# Documentation index\n"
        assert guide.read_text() == "# Markchain guide\n"
        assert stub.read_text() == ".. automodule:: mdp.markchain\n"
        assert not (docs / "api").exists()

    assert len(invocations) == 2
    assert Path(invocations[0][-2]) == docs
