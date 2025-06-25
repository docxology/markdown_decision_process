"""Manual test runner for the Transformations module."""

import tempfile
from pathlib import Path
import pytest
import os

from mdp.document import Document
from mdp.transformations import (
    HeadingLevelTransformation, 
    ListFormatTransformation,
    CodeBlockFormatTransformation,
    LinkFormatTransformation,
    TableFormatTransformation,
    TextStyleTransformation,
    TransformationPipeline
)
from mdp.state_space import StateSpace
from mdp.policy_optimizer import PolicyOptimizer

# Sample documents for testing
BASIC_MARKDOWN = """# Test Document
This is a paragraph.

## Section
- Item 1
- Item 2

```python
def hello():
    print("world")
```
"""

COMPLEX_MARKDOWN = """# Complex Document

## Section 1
This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
  - Nested item 1
  - Nested item 2

## Section 2
[Link text](https://example.com)

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

```javascript
function test() {
    return true;
}
```
"""

REF_LINK_MARKDOWN = """# Test Document

This is a [reference link][1] in a paragraph.

[1]: https://example.com
"""

@pytest.fixture
def basic_document():
    """Fixture that creates a Document with basic content."""
    return Document(content=BASIC_MARKDOWN)

@pytest.fixture
def complex_document():
    """Fixture that creates a Document with complex content."""
    return Document(content=COMPLEX_MARKDOWN)

@pytest.fixture
def ref_link_document():
    """Fixture that creates a Document with reference-style links."""
    return Document(content=REF_LINK_MARKDOWN)

@pytest.fixture
def temp_output_path():
    """Fixture that returns a temporary file path for output testing."""
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
        path = Path(tmp.name)
    
    yield path
    
    # Cleanup
    if path.exists():
        path.unlink()

# HeadingLevelTransformation tests
def test_apply_heading_transformation(basic_document, temp_output_path):
    """Test applying the heading level transformation."""
    # Increase heading levels by 1
    transform = HeadingLevelTransformation(min_level=1, increment=1)
    transform.apply(basic_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check headings were transformed correctly
    assert "## Test Document" in content  # Was # Test Document
    assert "### Section" in content  # Was ## Section
    
    # Check other content remains intact
    assert "This is a paragraph." in content
    assert "- Item 1" in content
    assert "- Item 2" in content
    assert "```python" in content
    assert "def hello():" in content

# ListFormatTransformation tests
def test_unordered_to_ordered(basic_document, temp_output_path):
    """Test converting unordered lists to ordered."""
    transform = ListFormatTransformation(target_type="ordered")
    transform.apply(basic_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check lists were transformed correctly
    assert "1. Item 1" in content
    assert "2. Item 2" in content

def test_bullet_style_change(basic_document, temp_output_path):
    """Test changing bullet style for unordered lists."""
    transform = ListFormatTransformation(target_type="unordered", bullet_style="*")
    transform.apply(basic_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check lists were transformed correctly
    assert "* Item 1" in content
    assert "* Item 2" in content

# CodeBlockFormatTransformation tests
def test_language_change(basic_document, temp_output_path):
    """Test changing code block language."""
    transform = CodeBlockFormatTransformation(
        target_language="python", 
        new_language="python3"
    )
    transform.apply(basic_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check code blocks were transformed correctly
    assert "```python3" in content
    assert "def hello():" in content
    assert 'print("world")' in content

# LinkFormatTransformation tests
def test_inline_to_reference(complex_document, temp_output_path):
    """Test converting inline links to reference style."""
    transform = LinkFormatTransformation(style="reference")
    transform.apply(complex_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check links were transformed correctly
    assert "[Link text][" in content
    assert "[Link text]:" in content or "[1]:" in content
    assert "https://example.com" in content

def test_reference_to_inline(ref_link_document, temp_output_path):
    """Test converting reference links to inline style."""
    transform = LinkFormatTransformation(style="inline")
    transform.apply(ref_link_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check links were transformed correctly
    assert "[reference link](https://example.com)" in content
    assert "[1]:" not in content

# TableFormatTransformation tests
def test_table_alignment(complex_document, temp_output_path):
    """Test aligning table contents."""
    transform = TableFormatTransformation(alignment="center")
    transform.apply(complex_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check tables were transformed correctly
    assert "|:----------:|:----------:|" in content  # Center alignment
    assert "| Column 1 | Column 2 |" in content
    assert "| Cell 1   | Cell 2   |" in content
    assert "| Cell 3   | Cell 4   |" in content

# TextStyleTransformation tests
def test_style_change(complex_document, temp_output_path):
    """Test changing text styling formats."""
    transform = TextStyleTransformation(bold_style="__", italic_style="*")
    transform.apply(complex_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check text styles were transformed correctly
    assert "paragraph with _*bold*_ and *italic* text" in content

# TransformationPipeline tests
def test_apply_pipeline(basic_document, temp_output_path):
    """Test applying multiple transformations in sequence."""
    # Create a pipeline with multiple transformations
    heading_transform = HeadingLevelTransformation(increment=1)
    list_transform = ListFormatTransformation(target_type="ordered")
    code_transform = CodeBlockFormatTransformation(
        target_language="python", 
        new_language="python3"
    )
    
    pipeline = TransformationPipeline([
        heading_transform, 
        list_transform, 
        code_transform
    ])
    
    # Apply the pipeline
    pipeline.apply(basic_document, temp_output_path)
    
    # Read the transformed document
    result_doc = Document(temp_output_path)
    content = result_doc.get_content()
    
    # Check all transformations were applied
    assert "## Test Document" in content  # Heading level increased
    assert "1. Item 1" in content  # List format changed
    assert "2. Item 2" in content
    assert "```python3" in content  # Code block language changed

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 