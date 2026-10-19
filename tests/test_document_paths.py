"""Deep checkout paths must be read as files, never document content."""
from mdp.document import Document
from mdp.transformations import HeadingLevelTransformation, TransformationPipeline


def test_deep_checkout_and_pipeline_read_actual_content(tmp_path):
    parent = tmp_path / ("nested" * 20)
    parent.mkdir()
    source = parent / "source.md"
    source.write_text("# Heading\n\nBody.\n", encoding="utf-8")
    assert len(str(source)) > 100
    for file_path in (source, str(source)):
        document = Document(file_path=file_path)
        assert document.get_content() == source.read_text()
        target = parent / "output.md"
        TransformationPipeline([HeadingLevelTransformation(increment=1)]).apply(document, target)
        assert Document(file_path=target).get_content() == "## Heading\n\nBody.\n"


def test_legacy_positional_content_is_preserved():
    content = "# Heading\n\n" + "Very long content. " * 100
    assert Document(content).get_content() == content
