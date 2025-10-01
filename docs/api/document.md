# Document API Reference

The `Document` class is the core representation of a Markdown document in the MDP framework.

## Class Overview

```python
class Document:
    """Core Markdown document representation with structure analysis."""

    def __init__(self, file_path: Optional[Union[str, Path]] = None, content: Optional[str] = None)
    def get_structure(self) -> List[Dict[str, Any]]
    def update_content(self, content: str) -> None
    def save(self, path: Union[str, Path]) -> None
```

## Constructor

### `__init__(file_path=None, content=None)`

Initialize a Document instance from either a file path or content string.

**Parameters:**
- `file_path` (str | Path, optional): Path to a markdown file
- `content` (str, optional): String content of a markdown document

**Note:** Either `file_path` or `content` must be provided.

**Example:**
```python
from mdp import Document

# From content
doc = Document(content="# My Document\n\nThis is content.")

# From file
doc = Document(file_path="path/to/document.md")
```

## Methods

### `get_structure() -> List[Dict[str, Any]]`

Analyze and return the hierarchical structure of the document.

**Returns:** List of dictionaries representing document elements with keys:
- `type`: Element type (`header`, `paragraph`, `list`, `code`, etc.)
- `content`: Raw content of the element
- `level`: Nesting level (for headers and lists)
- `language`: Programming language (for code blocks)

**Example:**
```python
doc = Document(content="# Header\n\nParagraph text.\n\n## Subheader")
structure = doc.get_structure()
# Returns:
# [
#     {'type': 'header', 'content': '# Header', 'level': 1},
#     {'type': 'paragraph', 'content': 'Paragraph text.'},
#     {'type': 'header', 'content': '## Subheader', 'level': 2}
# ]
```

### `update_content(content: str) -> None`

Update the document content and re-parse the structure.

**Parameters:**
- `content` (str): New markdown content

**Example:**
```python
doc = Document(content="# Old Title")
doc.update_content("# New Title\n\nUpdated content.")
```

### `save(path: Union[str, Path]) -> None`

Save the document to a file.

**Parameters:**
- `path` (str | Path): Output file path

**Example:**
```python
doc.save("output.md")
doc.save(Path("docs/generated.md"))
```

## Usage Examples

### Basic Document Creation

```python
from mdp import Document

# Create from string content
content = """# Project Overview

This project implements a **Markdown Decision Process** framework.

## Features

- Document analysis
- Content optimization
- Format conversion

## Code Example

```python
def analyze_document(doc):
    return doc.get_structure()
```
"""

doc = Document(content=content)
print(f"Document has {len(doc.get_structure())} elements")
```

### Document Analysis

```python
from mdp import Document

doc = Document(content="# Report\n\n## Section 1\n\nContent here.\n\n## Section 2\n\nMore content.")

structure = doc.get_structure()

# Count element types
element_counts = {}
for element in structure:
    element_type = element['type']
    element_counts[element_type] = element_counts.get(element_type, 0) + 1

print(f"Headers: {element_counts.get('header', 0)}")
print(f"Paragraphs: {element_counts.get('paragraph', 0)}")
```

### Content Modification

```python
from mdp import Document

doc = Document(content="# Original Title\n\nOriginal content.")

# Update content
new_content = "# Updated Title\n\nModified content with improvements."
doc.update_content(new_content)

# Save changes
doc.save("updated_document.md")
```

## Integration with Other Components

The Document class serves as the foundation for other MDP components:

```python
from mdp import Document, StateSpace, MarkChain, PolicyOptimizer

# Create document
doc = Document(content="# Sample Document\n\nContent here.")

# Analyze structure
state_space = StateSpace(doc)

# Train generation model
chain = MarkChain()
chain.train(doc.content)

# Optimize content
optimizer = PolicyOptimizer(state_space=state_space)
result = optimizer.optimize(doc)
```

## Error Handling

```python
from mdp import Document

try:
    # Attempt to load non-existent file
    doc = Document(file_path="nonexistent.md")
except FileNotFoundError as e:
    print(f"File not found: {e}")

try:
    # Attempt to create document without content or file
    doc = Document()
except ValueError as e:
    print(f"Invalid arguments: {e}")
```

## Performance Considerations

- Document parsing is performed lazily on first `get_structure()` call
- Large documents (>100KB) may benefit from incremental processing
- Consider using `Path` objects for better cross-platform compatibility

## Best Practices

1. **Always provide either `file_path` or `content`**
2. **Use `Path` objects for file operations**
3. **Call `get_structure()` once and cache results for multiple analyses**
4. **Use `update_content()` for modifications rather than recreating objects**
5. **Save documents with appropriate `.md` extensions**


