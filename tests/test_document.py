"""Tests for the Document module."""

import pytest
import tempfile
from pathlib import Path
import re
import os
import json
import matplotlib.pyplot as plt
import numpy as np

from mdp.document import Document

# Define sample Markdown content for tests
SAMPLE_MARKDOWN = """# Test Document

This is a paragraph with some **important** information.

Another paragraph with additional content.

## Section 1

- List item 1
- List item 2

### Subsection

Some more text here.

```python
def test():
    return "Hello World"
```

## Section 2

This is another paragraph with the word paragraph repeated.
"""

COMPLEX_MARKDOWN = """# Complex Document Analysis

## Introduction

This document contains a variety of markdown elements for testing document analysis metrics.

## Methods

The analysis is performed using several approaches:

1. First approach with detailed explanation
2. Second approach using alternative methodology
   - With sub-methodology A
   - With sub-methodology B
3. Third approach combining previous methods

### Data Collection

Data was collected from multiple sources:

* Primary sources (interviews)
* Secondary sources (literature)
* Tertiary sources (metadata analysis)

## Results

The results indicated several key findings:

| Metric | Value | Significance |
|--------|-------|--------------|
| Metric A | 85.2 | High |
| Metric B | 42.7 | Medium |
| Metric C | 93.1 | Very High |

### Statistical Analysis

```r
# Example R code
results <- analyze(data)
significance <- test_significance(results)
```

## Discussion

The findings suggest a strong correlation between variables X and Y, contrary to previous studies by Smith et al. (2018).

### Limitations

Several limitations must be acknowledged:

1. Sample size constraints
2. Geographical limitations
3. Temporal factors

## Conclusion

In conclusion, this analysis demonstrates the effectiveness of the proposed method and suggests directions for future research.

## References

1. Smith, J. (2018). Previous analysis methods. Journal of Analysis, 23(4), 45-67.
2. Johnson, A. (2020). Modern approaches to data collection. Research Methods Today, 15(2), 123-145.
"""

@pytest.fixture
def sample_document():
    """Create a temporary markdown file and return a MarkdownDocument instance."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
        tmp.write(SAMPLE_MARKDOWN)
        tmp_path = Path(tmp.name)
    
    doc = Document(tmp_path)
    
    yield doc
    
    # Cleanup
    if tmp_path.exists():
        tmp_path.unlink()

def test_initialization():
    """Test that MarkdownDocument initializes correctly."""
    # Create from string content
    doc = Document(content=SAMPLE_MARKDOWN)
    assert doc.get_content() == SAMPLE_MARKDOWN
    
    # Create from file path
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
        tmp.write(SAMPLE_MARKDOWN)
        tmp_path = Path(tmp.name)
    
    try:
        doc = Document(tmp_path)
        assert doc.get_content() == SAMPLE_MARKDOWN
    finally:
        tmp_path.unlink()

def test_get_content(sample_document):
    """Test retrieving document content."""
    content = sample_document.get_content()
    assert isinstance(content, str)
    assert content == SAMPLE_MARKDOWN

def test_get_paragraphs(sample_document):
    """Test retrieving paragraphs from the document."""
    paragraphs = sample_document.get_paragraphs()
    assert isinstance(paragraphs, list)
    assert len(paragraphs) >= 2  # At least 2 paragraphs in SAMPLE_MARKDOWN
    
    # Check for paragraph content - use more general assertions
    paragraph_text = ' '.join(paragraphs)
    assert "paragraph" in paragraph_text
    assert "additional content" in paragraph_text

def test_get_headings(sample_document):
    """Test retrieving headings from the document."""
    headings = sample_document.get_headings()
    assert isinstance(headings, list)
    assert len(headings) >= 3  # At least 3 headings in SAMPLE_MARKDOWN
    
    # Check heading structure
    for heading in headings:
        assert "level" in heading
        assert "text" in heading
    
    # Verify specific headings
    h1 = [h for h in headings if h["level"] == 1]
    assert len(h1) == 1
    assert h1[0]["text"] == "Test Document"
    
    h2 = [h for h in headings if h["level"] == 2]
    assert len(h2) >= 2
    assert any(h["text"] == "Section 1" for h in h2)
    assert any(h["text"] == "Section 2" for h in h2)

def test_get_lists(sample_document):
    """Test retrieving lists from the document."""
    lists = sample_document.get_lists()
    assert isinstance(lists, list)
    assert len(lists) >= 1  # At least 1 list in SAMPLE_MARKDOWN
    
    # Check list structure
    for list_item in lists:
        assert "type" in list_item  # Should specify ordered/unordered
        assert "items" in list_item
        assert isinstance(list_item["items"], list)
    
    # Verify specific list
    unordered_lists = [l for l in lists if l["type"] == "unordered"]
    assert len(unordered_lists) >= 1
    
    # Check list items
    list_items = unordered_lists[0]["items"]
    assert len(list_items) >= 2
    assert any("List item 1" in item for item in list_items)
    assert any("List item 2" in item for item in list_items)

def test_get_code_blocks(sample_document):
    """Test retrieving code blocks from the document."""
    code_blocks = sample_document.get_code_blocks()
    assert isinstance(code_blocks, list)
    assert len(code_blocks) >= 1  # At least 1 code block in SAMPLE_MARKDOWN
    
    # Check code block structure
    for block in code_blocks:
        assert "language" in block
        assert "code" in block
    
    # Verify specific code block
    python_blocks = [b for b in code_blocks if b["language"] == "python"]
    assert len(python_blocks) >= 1
    assert "def test()" in python_blocks[0]["code"]

def test_save(sample_document, tmp_path):
    """Test saving a document to a file."""
    # Create a temporary file path
    output_path = tmp_path / "output.md"
    
    # Save the document
    sample_document.save(output_path)
    
    # Verify the file was created
    assert output_path.exists()
    
    # Verify the content is correct
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert content == sample_document.get_content()

def test_update_content(sample_document):
    """Test updating document content."""
    # Original content
    original_content = sample_document.get_content()
    
    # Update content
    new_content = "# New Title\n\nNew content."
    sample_document.update_content(new_content)
    
    # Verify content has been updated
    assert sample_document.get_content() == new_content
    assert sample_document.get_content() != original_content
    
    # Check that other properties are updated
    headings = sample_document.get_headings()
    assert len(headings) == 1
    assert headings[0]["text"] == "New Title"

def test_get_statistics(sample_document):
    """Test retrieving document statistics."""
    stats = sample_document.get_statistics()
    
    # Check for basic statistics
    assert "word_count" in stats
    assert "char_count" in stats
    assert "paragraph_count" in stats
    assert "heading_count" in stats
    assert "list_count" in stats
    assert "code_block_count" in stats
    
    # Check values
    assert stats["heading_count"] >= 3
    assert stats["paragraph_count"] >= 2

def test_get_structure(sample_document):
    """Test retrieving document structure."""
    structure = sample_document.get_structure()
    
    # Should be a list of elements
    assert isinstance(structure, list)
    assert len(structure) > 0
    
    # Each element should have a type and text
    for element in structure:
        assert "type" in element
        assert "text" in element or "children" in element  # Either text or children should be present

def test_search(sample_document):
    """Test searching for patterns in the document."""
    # Search for text
    results = sample_document.search("paragraph")
    assert len(results) >= 2  # Should find instances of "paragraph"
    
    # Search with regex
    regex_results = sample_document.search(r"List item \d+", use_regex=True)
    assert len(regex_results) >= 2  # Should find "List item 1" and "List item 2"

def test_invalid_file_path():
    """Test that an error is raised when an invalid file path is provided."""
    with pytest.raises(FileNotFoundError):
        Document("nonexistent_file.md")

def test_document_metrics_visualization():
    """Test evaluating document metrics and visualizing the results."""
    # Create documents
    simple_doc = Document(content=SAMPLE_MARKDOWN)
    complex_doc = Document(content=COMPLEX_MARKDOWN)
    
    # Evaluate metrics
    simple_metrics = simple_doc.evaluate_metrics()
    complex_metrics = complex_doc.evaluate_metrics()
    
    # Check metrics
    assert isinstance(simple_metrics, dict)
    assert isinstance(complex_metrics, dict)
    
    # Complex document should have higher complexity score
    assert complex_metrics["complexity_score"] > simple_metrics["complexity_score"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 