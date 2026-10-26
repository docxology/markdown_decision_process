# Markdown Decision Process - Quick Start Guide

## Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd markdown_decision_process

# Create virtual environment with uv
uv venv

# Activate the environment
source .venv/bin/activate

# Install the package in editable mode with the declared dev tooling
uv pip install -e ".[dev]"
```

## Basic Usage

### 1. Document Parsing

```python
from mdp import Document

# Load a markdown document
doc = Document(file_path="example.md")

# Or create from content
doc = Document(content="# Hello\n\nThis is a paragraph.")

# Access document elements
headings = doc.get_headings()
paragraphs = doc.get_paragraphs()
code_blocks = doc.get_code_blocks()

# Get statistics
stats = doc.get_statistics()
print(f"Word count: {stats['word_count']}")
```

### 2. Markov Chain Generation

```python
from mdp import MarkChain

# Train on existing markdown
chain = MarkChain()
chain.train("# Tutorial\n\nStep 1: Install\n\nStep 2: Configure")

# Generate new content
generated = chain.sample(length=10)
print(generated)

# Save/load models
chain.save_model("trained_model.json")
chain.load_model("trained_model.json")
```

### 3. State Space Analysis

```python
from mdp import StateSpace

# Analyze document structure
state_space = StateSpace()
state_space.analyze("document.md")

# Visualize the state space
state_space.visualize("structure.png", title="Document Structure")

# Get statistics
state_space.print_statistics()

# Calculate transition probabilities
probs = state_space.calculate_transition_probabilities()
```

### 4. Belief Updates (Semantic Analysis)

```python
from mdp import BeliefUpdater, StateSpace

# Create belief updater
updater = BeliefUpdater(
    semantic_classes=["tutorial", "reference", "explanation"],
    noise_factor=0.1
)

# Analyze a document
state_space = StateSpace()
state_space.analyze("document.md")

beliefs = updater.analyze_document(state_space)
print(f"Document beliefs: {beliefs}")

# Get most likely semantic class
semantic_class, probability = updater.get_most_likely_semantics()
print(f"Most likely: {semantic_class} ({probability:.2f})")
```

### 5. Document Transformation

```python
from mdp import Document
from mdp.transformations import (
    HeadingLevelTransformation,
    ListFormatTransformation,
    TransformationPipeline
)

# Create a document
doc = Document(file_path="input.md")

# Apply transformations
heading_transform = HeadingLevelTransformation(min_level=1, increment=1)
list_transform = ListFormatTransformation(target_type="unordered", bullet_style="-")

# Create a pipeline
pipeline = TransformationPipeline([
    heading_transform,
    list_transform
])

# Apply the pipeline
pipeline.apply(doc, "output.md")
```

### 6. Policy Optimization

```python
from mdp import PolicyOptimizer

# Create an optimizer (reward weights are fixed internally; supply your own
# scoring callable with optimizer.set_reward_function(fn) if needed)
optimizer = PolicyOptimizer(learning_rate=0.1, max_iterations=20)

# Optimize a document
optimized_content = optimizer.transform("document.md")

# Save optimized version
with open("optimized.md", "w") as f:
    f.write(optimized_content)
```

### 7. Visualization

```python
from mdp import plot_document_structure, plot_transitions
from mdp import Document, MarkChain
import matplotlib.pyplot as plt

# Visualize document structure
doc = Document(file_path="document.md")
fig = plot_document_structure(doc)
plt.savefig("structure.png")
plt.close()

# Visualize state transitions
chain = MarkChain()
chain.train(doc.get_content())
fig = plot_transitions(chain, top_n=10)
plt.savefig("transitions.png")
plt.close()
```

## Running Tests

```bash
# Activate environment
source .venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_document.py -v

# Run with coverage
python -m pytest tests/ --cov=mdp --cov-report=html

# Run benchmark tests
python -m pytest tests/test_performance.py --benchmark-only
```

## Common Issues

### Import Errors

If you get `ModuleNotFoundError: No module named 'mdp'`:
```bash
# Make sure you're in the activated environment
source .venv/bin/activate

# Reinstall in editable mode
uv pip install -e .
```

### Missing Dependencies

If you get import errors for specific packages:
```bash
# Install missing package
uv pip install <package-name>

# Or reinstall every declared dependency at once
uv pip install -e ".[dev]"
```

### Test Failures

If tests fail due to missing fixtures or data:
```bash
# Ensure test fixtures exist
ls tests/fixtures/

# Create outputs directory if needed
mkdir -p tests/outputs
```

## Project Structure

```
markdown_decision_process/
├── src/mdp/              # Main package source
│   ├── document.py       # Document parsing
│   ├── markchain.py      # Markov chain model
│   ├── state_space.py    # State space analysis
│   ├── belief_updater.py # Belief state management
│   ├── policy_optimizer.py # Document optimization
│   ├── transformations.py  # Document transformations
│   ├── visualization.py    # Visualization tools
│   └── ...
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
└── pyproject.toml        # Project configuration
```

## Next Steps

1. Explore the `examples/` directory for more detailed usage patterns
2. Read the technical documentation in `docs/technical/`
3. Check [TODO.md](TODO.md) — the single canonical backlog — for current work
4. Contribute improvements or report issues

## Getting Help

- Check the API documentation in `docs/api/`
- Look at working examples in `examples/`
- Review test files for usage patterns
- Read technical docs in `docs/technical/`

---
*For full documentation, see the `docs/` directory*
