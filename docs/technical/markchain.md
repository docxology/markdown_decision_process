# MarkChain Technical Documentation

The `MarkChain` component is the core Markov model implementation for the Markdown Decision Process (MDP) framework. It models transitions between markdown elements (states) to enable generation and transformation of markdown documents.

## Implementation Status

The following features from the roadmap have been implemented:

- ✅ Basic Markov model for markdown state transitions
- ✅ Variable-order Markov models for improved context awareness
- ✅ Weighted state transitions based on semantic importance
- ✅ Specialized generators for different markdown elements

Features still in development:
- Skip-gram models to capture non-adjacent dependencies
- Decay functions for distant state influences
- Positional encoding for structural awareness

## Core Concepts

### State Representation

In the MarkChain implementation, markdown elements are represented as discrete states. The state parsing system identifies the following primary states:

- Headings (with level tracking: H1, H2, H3, etc.)
- Paragraphs
- Lists (ordered and unordered)
- Code blocks (with language identification)
- Blockquotes
- Tables
- Horizontal rules
- YAML frontmatter
- Inline elements (as sub-states)

Each state includes metadata about its position, content characteristics, and relationships to other states.

### Transition Probability Matrix

The core of the MarkChain is a transition probability matrix that records the likelihood of transitioning from one state to another. This is implemented as a nested dictionary structure with optimized sparse matrix operations.

For a variable-order Markov model, the transition matrix accounts for sequences of states rather than just pairs:

```python
# Example representation of transition probabilities (pseudocode)
transitions = {
    ('heading_1', 'paragraph'): {
        'paragraph': 0.7,
        'heading_2': 0.2,
        'list_unordered': 0.1
    },
    ('heading_1', 'paragraph', 'paragraph'): {
        'paragraph': 0.4,
        'list_ordered': 0.3,
        'code_block': 0.2,
        'heading_2': 0.1
    }
}
```

### Training Process

The MarkChain's training process involves:

1. Parsing markdown documents into sequences of states
2. Computing transition frequencies between states
3. Normalizing frequencies into probabilities
4. Applying optional Bayesian smoothing to handle unseen transitions
5. Computing higher-order transitions for variable-order models

The implementation uses efficient incremental updates to allow for online learning from streaming documents.

## API Reference

### Initialization

```python
from mdp.markchain import MarkChain

# Create a basic MarkChain with default order
chain = MarkChain()

# Create a variable-order MarkChain
chain = MarkChain(order=3, smoothing=0.1)

# Create a MarkChain with custom state parser
from mdp.parsers import CustomMarkdownParser
chain = MarkChain(parser=CustomMarkdownParser())

# Create a MarkChain with semantic weighting
chain = MarkChain(semantic_weighting=True, embedding_model="sentence-transformers/all-mpnet-base-v2")
```

### Training

```python
# Train from a single document
chain.train("# Heading\n\nThis is a paragraph.\n\n* List item\n* Another item")

# Train from a file
chain.train_file("path/to/document.md")

# Train from a directory of files
chain.train_directory("path/to/docs/", pattern="*.md")

# Train with custom weights for document
chain.train_file("path/to/important.md", weight=2.0)

# Update with incremental learning
chain.update("New markdown content", learning_rate=0.1)
```

### Generation

```python
# Generate a complete document
document = chain.generate(length=100)

# Generate with a starting prompt
document = chain.generate(prompt="# Introduction", length=50)

# Generate with temperature control
document = chain.generate(prompt="# API Reference", length=100, temperature=0.8)

# Generate with state constraints
document = chain.generate(
    length=200,
    constraints={"max_heading_level": 3, "min_paragraphs_per_section": 2}
)
```

### Specialized Generators

The MarkChain implements specialized generators for different markdown elements:

```python
# Generate a heading that would naturally follow the given content
heading = chain.generate_heading(context="Previous markdown content")

# Generate a list based on context
list_items = chain.generate_list(context="Context for list", items=5, ordered=True)

# Generate a table with specified dimensions
table = chain.generate_table(context="Context for table", rows=4, columns=3)

# Generate a code block with appropriate language
code = chain.generate_code_block(context="Function description here", language="python")
```

## Performance Characteristics

The current implementation has the following performance characteristics:

- Training speed: ~10MB of markdown text per second on standard hardware
- Memory usage: Approximately 50MB base + 100MB per 1000 documents for a 3rd-order model
- Generation speed: ~1000 tokens per second

## Examples

### Creating a Technical Documentation Chain

```python
from mdp.markchain import MarkChain
from mdp.datasets import load_sample_docs

# Create a specialized chain for technical documentation
tech_docs = load_sample_docs("technical")
chain = MarkChain(order=3, semantic_weighting=True)
chain.train_corpus(tech_docs)

# Generate API documentation
api_doc = chain.generate(prompt="# API Reference\n\n", length=500)
print(api_doc)
```

### Analyzing State Transitions

```python
import matplotlib.pyplot as plt
from mdp.markchain import MarkChain
from mdp.visualization import plot_transitions

# Train the chain
chain = MarkChain()
chain.train_directory("docs/")

# Visualize common transitions
plt = plot_transitions(chain, top_n=10)
plt.savefig("transitions.png")
```

## Implementation Details

### Variable-Order Markov Model

The implementation uses a backoff model for variable-order Markov chains:

1. It first attempts to match the highest order context (e.g., the last 3 states)
2. If insufficient data exists, it backs off to a lower order (e.g., the last 2 states)
3. It continues backing off until it finds sufficient data or reaches order 1
4. Interpolation is applied between different orders based on confidence metrics

### Semantic Weighting

When semantic weighting is enabled:

1. Each markdown element is embedded using the specified language model
2. Transition probabilities are adjusted based on semantic similarity
3. This allows the model to generate more coherent transitions
4. Semantic neighborhoods are maintained to optimize performance

## Testing

The MarkChain implementation is tested with:

- Unit tests for each method and edge case
- Integration tests with real-world markdown documents
- Performance benchmarks for training and generation
- Comparison tests against reference Markov implementations

See the [test_markchain.py](../../tests/test_markchain.py) file for implementation details.

## Future Work

Upcoming improvements to the MarkChain component include:

1. Skip-gram models to better handle non-adjacent dependencies
2. Decay functions to model the influence of distant states
3. Positional encoding for structural awareness
4. Self-consistency validation during generation
5. Topic modeling integration for improved coherence

These features are tracked in the [project roadmap](../ROADMAP.md). 