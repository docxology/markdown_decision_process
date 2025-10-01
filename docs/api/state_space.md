# StateSpace API Reference

The `StateSpace` class provides graph-based analysis of Markdown document structure, representing documents as networks of interconnected states.

## Class Overview

```python
class StateSpace:
    """Graph-based analysis of Markdown document structure."""

    def __init__(self, document: Optional[Document] = None)
    def analyze(self, filepath: Union[str, Path]) -> None
    def visualize(self, output_path: str, **kwargs) -> None
    def get_successor_states(self, state_id: str) -> List[str]
    def get_state_metadata(self, state_id: str) -> Dict[str, Any]
```

## Constructor

### `__init__(document=None)`

Initialize a StateSpace instance, optionally analyzing a document.

**Parameters:**
- `document` (Document, optional): Document to analyze immediately

**Example:**
```python
from mdp import Document, StateSpace

doc = Document(content="# Document\n\nContent.")
state_space = StateSpace(doc)  # Analyzes immediately
```

## Methods

### `analyze(filepath: Union[str, Path]) -> None`

Analyze a markdown file and build the state space graph.

**Parameters:**
- `filepath` (str | Path): Path to markdown file

**Example:**
```python
state_space = StateSpace()
state_space.analyze("document.md")
```

### `visualize(output_path: str, **kwargs) -> None`

Generate a visual representation of the state space.

**Parameters:**
- `output_path` (str): Output file path (e.g., "state_space.png")
- `**kwargs`: Additional arguments for visualization

**Example:**
```python
state_space.visualize("state_space.png", figsize=(12, 8))
```

### `get_successor_states(state_id: str) -> List[str]`

Get all states that can follow a given state.

**Parameters:**
- `state_id` (str): Source state identifier

**Returns:** List of state IDs that can follow the source state

**Example:**
```python
successors = state_space.get_successor_states("header")
# Returns: ["paragraph", "list", "code", ...]
```

### `get_state_metadata(state_id: str) -> Dict[str, Any]`

Get metadata for a specific state.

**Parameters:**
- `state_id` (str): State identifier

**Returns:** Dictionary with state metadata including type, level, etc.

**Example:**
```python
metadata = state_space.get_state_metadata("header_0")
# Returns: {"type": "header", "level": 1, "content": "# Title"}
```

## State Representation

States are represented as strings with the format `{type}_{index}`:

- `header_0`, `header_1`, ... for headers
- `paragraph_0`, `paragraph_1`, ... for paragraphs
- `list_0`, `list_1`, ... for lists
- `code_0`, `code_1`, ... for code blocks

## Usage Examples

### Basic State Space Analysis

```python
from mdp import Document, StateSpace

doc = Document(content="""
# Main Title

This is a paragraph.

## Section Header

- List item 1
- List item 2

```python
def example():
    return "code"
```
""")

state_space = StateSpace(doc)

print(f"Total states: {len(state_space.graph.nodes)}")
print(f"Total transitions: {len(state_space.graph.edges)}")

# Get metadata for first header
header_metadata = state_space.get_state_metadata("header_0")
print(f"Header level: {header_metadata['level']}")
```

### Transition Analysis

```python
from mdp import Document, StateSpace

doc = Document(content="# H1\n\nPara 1\n\n## H2\n\nPara 2")
state_space = StateSpace(doc)

# Get successors of first header
h1_successors = state_space.get_successor_states("header_0")
print(f"H1 can be followed by: {h1_successors}")

# Check if paragraph can follow header
para_successors = state_space.get_successor_states("paragraph_0")
print(f"Paragraph can be followed by: {para_successors}")
```

### Visualization

```python
from mdp import Document, StateSpace

doc = Document(content="# Document\n\nContent with sections.")
state_space = StateSpace(doc)

# Generate visualization
state_space.visualize(
    "state_space.png",
    title="Document State Space",
    node_color="lightblue",
    edge_color="gray"
)
```

### Large Document Analysis

```python
from mdp import StateSpace
from pathlib import Path

# Analyze entire directory
state_space = StateSpace()

# Analyze all markdown files in directory
for md_file in Path("docs").glob("*.md"):
    state_space.analyze(md_file)

print(f"Analyzed {len(state_space.graph.nodes)} total states")
print(f"Found {len(state_space.graph.edges)} transitions")

# Visualize the complete state space
state_space.visualize("complete_state_space.png", figsize=(20, 15))
```

## State Types and Metadata

### Header States
```python
# Metadata includes:
{
    "type": "header",
    "level": 1,  # Header level (1-6)
    "content": "# Main Title"
}
```

### Paragraph States
```python
# Metadata includes:
{
    "type": "paragraph",
    "content": "This is a paragraph of text.",
    "word_count": 7,
    "sentence_count": 1
}
```

### List States
```python
# Metadata includes:
{
    "type": "list",
    "list_type": "unordered",  # or "ordered"
    "item_count": 3
}
```

### Code Block States
```python
# Metadata includes:
{
    "type": "code",
    "language": "python",  # or None if not specified
    "content": "def function():\n    return True"
}
```

## Integration with Other Components

### With PolicyOptimizer

```python
from mdp import Document, StateSpace, PolicyOptimizer

doc = Document(content="# Document\n\nContent.")
state_space = StateSpace(doc)

optimizer = PolicyOptimizer(state_space=state_space)
optimizer.set_reward_function(lambda elem: 1.0 if elem['type'] == 'header' else 0.5)

result = optimizer.optimize(doc)
```

### With MarkChain

```python
from mdp import Document, StateSpace, MarkChain

doc = Document(content="# Doc\n\nText.")
state_space = StateSpace(doc)

chain = MarkChain()
chain.train(doc.content)

# Use state space to inform chain generation
start_state = list(state_space.graph.nodes)[0]
generated = chain.sample(start_state, length=100)
```

### With BeliefUpdater

```python
from mdp import Document, StateSpace, BeliefUpdater

doc = Document(content="# Guide\n\nInstructions here.")
state_space = StateSpace(doc)

# Extract semantic classes from state space
semantic_classes = list(set(
    state_space.get_state_metadata(node_id).get('type', 'unknown')
    for node_id in state_space.graph.nodes
))

updater = BeliefUpdater(semantic_classes)
updater.update_from_observation({"instruction": 0.8, "reference": 0.2})
```

## Performance Considerations

- **Memory Usage**: State space graphs scale with document complexity
- **Analysis Time**: Larger documents take longer to analyze
- **Visualization**: Complex graphs may require significant rendering time

## Best Practices

1. **Batch Analysis**: Analyze multiple related documents together for better state relationships
2. **State Filtering**: Use `get_state_metadata()` to filter states by type or properties
3. **Incremental Updates**: For large documents, consider analyzing sections separately
4. **Visualization Sizing**: Use appropriate figure sizes for complex state spaces
5. **Metadata Caching**: Cache frequently accessed metadata for performance


