"""Heading membership must follow real sections rather than fenced examples."""

import pytest

from mdp.document import Document
from mdp.transformations import HeadingLevelTransformation, change_heading_level


@pytest.mark.parametrize("level", [2, 3, 6])
def test_structure_keeps_leading_subheading(level):
    document = Document(content="#" * level + " Lead")
    assert document.get_structure() == [
        {"type": "heading", "level": level, "text": "Lead", "children": []}
    ]


def test_structure_attaches_skipped_levels_to_nearest_real_parent():
    document = Document(
        content="# Root\n### Deep\n##### Deeper\n## Peer\n#### Child\n# Next"
    )
    structure = document.get_structure()
    assert [node["text"] for node in structure] == ["Root", "Next"]
    root = structure[0]
    assert [node["text"] for node in root["children"]] == ["Deep", "Peer"]
    assert root["children"][0]["children"][0]["text"] == "Deeper"
    assert root["children"][1]["children"][0]["text"] == "Child"
    assert root["children"][1]["children"][0]["level"] == 4
    document.update_content("### Replacement")
    assert document.get_structure()[0]["text"] == "Replacement"
    assert document.get_headings() == [{"level": 3, "text": "Replacement"}]


FENCED_EXAMPLES = [
    "```python\n# code comment\n```",
    "~~~shell\n# code comment\n~~~",
    "````python\n```\n# code comment\n`````",
    "~~~~lang\n~~~\n# code comment\n~~~~~",
    "   ```python\n# code comment\n  ```  ",
    "```python\n~~~\n# code comment\n``` trailing\n```",
]


@pytest.mark.parametrize("code", FENCED_EXAMPLES)
def test_headings_ignore_fenced_examples_and_resume_after_close(code):
    document = Document(content="# Before\n" + code + "\n## After")
    assert document.get_headings() == [
        {"level": 1, "text": "Before"},
        {"level": 2, "text": "After"},
    ]
    assert document.get_structure()[0]["children"][0]["text"] == "After"


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_unclosed_fence_hides_remaining_heading_lines(fence):
    document = Document(content="# Before\n" + fence + "\n## Code forever")
    assert document.get_headings() == [{"level": 1, "text": "Before"}]


@pytest.mark.parametrize("code", FENCED_EXAMPLES)
def test_bulk_heading_transform_preserves_code_bytes(code):
    document = Document(content="# Before\n" + code + "\n## After\n")
    HeadingLevelTransformation(increment=1).apply(document)
    assert document.get_content() == "## Before\n" + code + "\n### After\n"


def test_named_heading_transform_ignores_code_only_match():
    document = Document(content="```sh\n# Inside\n```\n# Outside")
    transform = HeadingLevelTransformation()
    with pytest.raises(ValueError, match="not found"):
        transform.change_heading_level(document, "Inside", 3)
    result = transform.change_heading_level(document, "Outside", 3)
    assert result == "```sh\n# Inside\n```\n### Outside"
    assert document.get_content().endswith("# Outside")


def test_indexed_heading_transform_uses_real_heading_membership():
    source = "# Before\n~~~shell\n# Inside\n~~~\n## After"
    document = Document(content=source)
    changed = change_heading_level(document, 1, 4)
    assert changed.get_content() == source.removesuffix("## After") + "#### After"
    assert document.get_content() == source
    assert change_heading_level(document, 2, 4) is document


def test_invalid_fence_openers_do_not_hide_real_heading():
    # Four-space indentation and a backtick in a backtick info string are not
    # fenced-block openers. Inline code likewise does not open a block.
    for line in ["    ```", "```invalid`info", "Text with ``` inline"]:
        assert Document(content=line + "\n# Real").get_headings() == [
            {"level": 1, "text": "Real"}
        ]


@pytest.mark.parametrize("fence", ["```", "~~~"])
def test_bulk_transform_preserves_unclosed_code_through_end(fence):
    source = "# Before\n" + fence + "\n# Code\n"
    document = Document(content=source)
    HeadingLevelTransformation(increment=1).apply(document)
    assert document.get_content() == "#" + source


def test_transform_preserves_crlf_inside_fenced_code():
    source = "# Before\r\n```sh\r\n# Code\r\n```\r\n## After\r\n"
    document = Document(content=source)
    HeadingLevelTransformation(increment=1).apply(document)
    assert document.get_content() == (
        "## Before\r\n```sh\r\n# Code\r\n```\r\n### After\r\n"
    )
