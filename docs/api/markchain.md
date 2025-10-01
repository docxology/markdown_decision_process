# MarkChain API Reference

The `MarkChain` class implements a Markov chain for generating Markdown content based on learned transition probabilities.

## Class Overview

```python
class MarkChain:
    """Markov chain for Markdown text generation."""

    def __init__(self, order: int = 1, smoothing: float = 0.01)
    def train(self, markdown_text: str) -> None
    def sample(self, start_state: str, length: int) -> str
    def generate(self, prompt: str, length: int) -> str
    def save(self, path: str) -> None
    def load(self, path: str) -> 'MarkChain'
```

## Constructor

### `__init__(order=1, smoothing=0.01)`

Initialize a MarkChain with specified order and smoothing.

**Parameters:**
- `order` (int): Markov chain order (1 = unigram, 2 = bigram, etc.)
- `smoothing` (float): Laplace smoothing factor for probability estimation

**Example:**
```python
from mdp import MarkChain

# Unigram model
chain = MarkChain(order=1)

# Bigram model with higher smoothing
chain = MarkChain(order=2, smoothing=0.1)
```

## Methods

### `train(markdown_text: str) -> None`

Train the Markov chain on markdown content.

**Parameters:**
- `markdown_text` (str): Markdown content to learn from

**Example:**
```python
chain = MarkChain()
corpus = "# Document\n\nContent here.\n\n## Section\n\nMore content."
chain.train(corpus)
```

### `sample(start_state: str, length: int) -> str`

Generate text starting from a specific state.

**Parameters:**
- `start_state` (str): State to start generation from
- `length` (int): Maximum length of generated text

**Returns:** Generated markdown text

**Example:**
```python
chain = MarkChain()
chain.train("# Header\n\nParagraph text.")

# Generate starting from header
text = chain.sample("header", length=200)
print(text)
```

### `generate(prompt: str, length: int) -> str`

Generate text based on a prompt.

**Parameters:**
- `prompt` (str): Initial text prompt
- `length` (int): Maximum length of generated text

**Returns:** Generated markdown text continuing from prompt

**Example:**
```python
chain = MarkChain()
chain.train(corpus)

prompt = "# My New Document"
generated = chain.generate(prompt, length=300)
print(generated)
```

### `save(path: str) -> None`

Save the trained model to disk.

**Parameters:**
- `path` (str): File path to save model

**Example:**
```python
chain.save("trained_model.pkl")
```

### `load(path: str) -> 'MarkChain'`

Load a trained model from disk.

**Parameters:**
- `path` (str): File path to load model from

**Returns:** Loaded MarkChain instance

**Example:**
```python
chain = MarkChain.load("trained_model.pkl")
```

## State Types

MarkChain recognizes these state types:

- `header`: Section headers (`#`, `##`, etc.)
- `paragraph`: Regular text paragraphs
- `list`: Both ordered and unordered lists
- `code`: Code blocks with optional language specification
- `blockquote`: Quoted text blocks
- `table`: Markdown tables
- `link`: Hyperlinks
- `image`: Image references
- `hr`: Horizontal rules

## Usage Examples

### Basic Training and Generation

```python
from mdp import MarkChain

# Create and train model
chain = MarkChain(order=2)
training_text = """
# Project Documentation

This project implements machine learning algorithms.

## Features

- Fast training
- Accurate predictions
- Easy integration

## Usage

```python
model = MLModel()
model.train(data)
predictions = model.predict(test_data)
```

## Results

The model achieved 95% accuracy on the test set.
"""

chain.train(training_text)

# Generate new content
prompt = "# New Project"
generated = chain.generate(prompt, length=400)
print(generated)
```

### State-Specific Generation

```python
from mdp import MarkChain

chain = MarkChain()
chain.train("""
# Chapter 1: Introduction

This chapter covers the basics.

## Section 1.1

Important concepts are explained here.

# Chapter 2: Advanced Topics

More complex material follows.
""")

# Generate starting from different states
header_text = chain.sample("header", length=100)
paragraph_text = chain.sample("paragraph", length=150)

print("Generated header section:")
print(header_text)
print("\nGenerated paragraph:")
print(paragraph_text)
```

### Model Persistence

```python
from mdp import MarkChain

# Train model
chain = MarkChain(order=3)
chain.train(large_corpus)

# Save for later use
chain.save("production_model.pkl")

# Load in production
production_chain = MarkChain.load("production_model.pkl")

# Generate content
content = production_chain.generate("# API Reference", length=500)
```

### Custom State Parsing

```python
from mdp import MarkChain

# The default state parser recognizes standard markdown elements
# For custom parsing, you can modify the internal state representation

chain = MarkChain()

# Access the state parser (for advanced usage)
parser = chain._state_parser

# Custom state types can be added by modifying parser logic
# This is advanced usage for specialized applications
```

## Advanced Features

### Smoothing and Probability Estimation

```python
# Higher smoothing reduces overfitting to training data
chain = MarkChain(order=2, smoothing=0.1)  # More exploration
strict_chain = MarkChain(order=2, smoothing=0.001)  # More conservative

# Train on same data
chain.train(text)
strict_chain.train(text)

# Generate - higher smoothing may produce more varied output
varied = chain.sample("header", length=200)
conservative = strict_chain.sample("header", length=200)
```

### Order Selection

```python
# Different orders capture different patterns:
# order=1: Simple frequency-based generation
# order=2: Captures pairwise transitions
# order=3: Captures longer-term dependencies

unigram = MarkChain(order=1)
bigram = MarkChain(order=2)
trigram = MarkChain(order=3)

# Train all on same corpus
for chain in [unigram, bigram, trigram]:
    chain.train(corpus)

# Generate - higher order models may produce more coherent text
u_text = unigram.sample("header", length=200)
b_text = bigram.sample("header", length=200)
t_text = trigram.sample("header", length=200)
```

## Integration with Other Components

### With StateSpace for Guided Generation

```python
from mdp import Document, StateSpace, MarkChain

doc = Document(content="# Guide\n\nInstructions.")
state_space = StateSpace(doc)

# Train chain on document
chain = MarkChain()
chain.train(doc.content)

# Use state space to guide generation
valid_states = list(state_space.graph.nodes)
start_state = valid_states[0] if valid_states else "header"

generated = chain.sample(start_state, length=300)
```

### With PolicyOptimizer for Quality Control

```python
from mdp import Document, StateSpace, MarkChain, PolicyOptimizer

doc = Document(content="# Document\n\nContent.")
state_space = StateSpace(doc)
chain = MarkChain()
chain.train(doc.content)

# Generate candidate content
candidates = [chain.sample("header", length=200) for _ in range(5)]

# Use policy optimizer to select best candidate
optimizer = PolicyOptimizer(state_space=state_space)

best_candidate = None
best_reward = -float('inf')

for candidate in candidates:
    candidate_doc = Document(content=candidate)
    reward = len(candidate_doc.get_structure())  # Simple reward function
    if reward > best_reward:
        best_reward = reward
        best_candidate = candidate

print(f"Selected candidate with reward: {best_reward}")
```

## Performance Considerations

- **Training Time**: Higher order models take longer to train
- **Memory Usage**: Transition matrices grow exponentially with order
- **Generation Speed**: Higher order models are slightly slower to generate
- **Model Size**: Saved models can be large for high-order, well-trained chains

## Best Practices

1. **Order Selection**: Start with order=2 for most applications
2. **Smoothing**: Use smoothing > 0 to avoid zero probabilities
3. **Training Data**: Use diverse, high-quality training data
4. **Generation Length**: Keep generation length reasonable (100-500 tokens)
5. **State Validation**: Verify start states exist in trained model
6. **Model Persistence**: Save trained models for reuse

## Common Patterns

### Document Extension

```python
# Extend existing document
existing = "# My Document\n\nCurrent content."
extended = chain.generate(existing, length=300)
```

### Section Generation

```python
# Generate specific section types
header_section = chain.sample("header", length=100)
code_section = chain.sample("code", length=150)
```

### Interactive Generation

```python
# Build documents incrementally
sections = []
current_prompt = "# Document"

for i in range(3):
    section = chain.generate(current_prompt, length=200)
    sections.append(section)
    current_prompt = section[-100:]  # Use end as next prompt

full_document = "\n\n".join(sections)
```


