# Complete API Reference - Markdown Decision Process

## Core Modules

### Document (`mdp.document`)

**Class: `Document`**

Parse, analyze, and manipulate Markdown documents.

```python
from mdp import Document

# Create from file
doc = Document(file_path="document.md")

# Create from content
doc = Document(content="# Title\n\nContent")
```

**Methods:**

- `get_content() -> str`: Get raw markdown content
- `update_content(content: str) -> None`: Update document content
- `save(output_path: str) -> None`: Save to file
- `get_paragraphs() -> List[str]`: Extract all paragraphs
- `get_headings() -> List[Dict]`: Extract headings with levels
- `get_lists() -> List[Dict]`: Extract lists with items
- `get_code_blocks() -> List[Dict]`: Extract code blocks with language
- `get_statistics() -> Dict`: Get document statistics
- `get_structure() -> List[Dict]`: Get hierarchical structure
- `search(query: str, element_types: List[str]) -> List[Dict]`: Search content
- `evaluate_metrics() -> Dict[str, float]`: Calculate quality metrics
- `add_element(content: str, element_type: str) -> None`: Add element to document

**Example:**
```python
doc = Document(file_path="README.md")
stats = doc.get_statistics()
print(f"Words: {stats['word_count']}, Headings: {stats['heading_count']}")

headings = doc.get_headings()
for h in headings:
    print(f"Level {h['level']}: {h['text']}")
```

---

### MarkChain (`mdp.markchain`)

**Class: `MarkChain`**

Markov chain model for markdown state transitions and text generation.

```python
from mdp import MarkChain

chain = MarkChain(order=1, smoothing=0.01)
```

**Methods:**

- `train(markdown_text: str) -> None`: Train on markdown content
- `sample(length: int, start_state: str) -> str`: Generate markdown
- `generate(length: int, prompt: str, temperature: float) -> str`: Generate with options
- `get_transition_probabilities(state: str) -> Dict`: Get transition probs
- `save_model(filepath: str) -> None`: Save trained model
- `load_model(filepath: str) -> None`: Load trained model

**Example:**
```python
chain = MarkChain(order=2)
chain.train("# Tutorial\n\nStep 1: Install\n\nStep 2: Configure")
generated = chain.sample(length=10)
print(generated)
```

---

### StateSpace (`mdp.state_space`)

**Class: `StateSpace`**

Graph-based analysis of markdown document structure.

```python
from mdp import StateSpace

ss = StateSpace(simplify_states=True, min_count=2)
```

**Methods:**

- `parse_markdown(content: str) -> None`: Parse markdown into states
- `parse_markdown_file(filepath: str) -> None`: Parse from file
- `analyze(filepath: str) -> None`: Analyze file
- `add_state(state_data: Dict) -> str`: Add a state manually
- `add_transition(source: str, target: str, weight: float) -> None`: Add transition
- `get_state(state_id: str) -> Dict`: Get state data
- `get_transitions(state_id: str) -> Dict`: Get state transitions
- `get_successor_states(state_id: str) -> List[str]`: Get successors
- `get_features(state_id: str) -> Dict`: Extract state features
- `get_state_sequence(content: str) -> List[str]`: Get state sequence
- `calculate_transition_probabilities() -> Dict`: Calculate probabilities
- `extract_structure(content: str) -> Dict`: Extract document structure
- `visualize(output_path: str, title: str) -> None`: Create visualization
- `print_statistics() -> None`: Print statistics
- `save(filepath: str) -> None`: Save state space
- `load(filepath: str) -> None`: Load state space
- `calculate_pagerank() -> Dict[str, float]`: Calculate PageRank
- `get_markdown(state_sequence: List[str]) -> str`: Reconstruct markdown

**Example:**
```python
ss = StateSpace()
ss.parse_markdown("# Title\n\nContent\n\n## Section")
ss.visualize("structure.png", title="Document Structure")
probs = ss.calculate_transition_probabilities()
```

---

### BeliefUpdater (`mdp.belief_updater`)

**Class: `BeliefUpdater`**

POMDP-inspired belief state management for semantic analysis.

```python
from mdp import BeliefUpdater

updater = BeliefUpdater(
    semantic_classes=["tutorial", "reference", "explanation"],
    noise_factor=0.1
)
```

**Methods:**

- `update_belief(key: str, value: float) -> None`: Update belief
- `update_from_observation(observation: Dict) -> None`: Bayesian update
- `get_belief(key: str, default: float) -> float`: Get belief value
- `get_all_beliefs() -> Dict`: Get all beliefs
- `get_noisy_belief(key: str) -> float`: Get belief with noise
- `reset_beliefs() -> None`: Reset to defaults
- `save_beliefs(filepath: str) -> None`: Save beliefs
- `load_beliefs(filepath: str) -> None`: Load beliefs
- `combine_beliefs(other_beliefs: Dict, weight: float) -> None`: Combine beliefs
- `calculate_entropy() -> float`: Calculate belief entropy
- `analyze_document(state_space: StateSpace) -> Dict`: Analyze document
- `analyze_document_file(markdown_path: str) -> Dict`: Analyze from file
- `get_most_likely_semantics() -> Tuple[str, float]`: Get most likely class
- `print_analysis(analysis: Dict) -> None`: Print analysis

**Example:**
```python
updater = BeliefUpdater()
ss = StateSpace()
ss.analyze("document.md")
beliefs = updater.analyze_document(ss)
semantic, prob = updater.get_most_likely_semantics()
print(f"Type: {semantic} ({prob:.2f})")
```

---

### Transformations (`mdp.transformations`)

**Classes:**

- `Transformation` (abstract base)
- `HeadingLevelTransformation`
- `ListFormatTransformation`
- `CodeBlockFormatTransformation`
- `LinkFormatTransformation`
- `TableFormatTransformation`
- `TextStyleTransformation`
- `TransformationPipeline`

**Common Methods:**

- `apply(document: Document, output_path: str) -> None`: Apply transformation

**Example:**
```python
from mdp import Document
from mdp.transformations import (
    HeadingLevelTransformation,
    TransformationPipeline
)

doc = Document(file_path="input.md")
transform = HeadingLevelTransformation(increment=1)
transform.apply(doc, "output.md")

# Or use a pipeline
pipeline = TransformationPipeline([
    HeadingLevelTransformation(increment=1),
    ListFormatTransformation(target_type="unordered")
])
pipeline.apply(doc, "transformed.md")
```

---

### PolicyOptimizer (`mdp.policy_optimizer`)

**Class: `PolicyOptimizer`**

Optimize documents using reward functions and transformation strategies.

```python
from mdp import PolicyOptimizer

optimizer = PolicyOptimizer(
    reward_weights={
        "readability": 0.6,
        "information_density": 0.3,
        "structure_clarity": 0.1
    }
)
```

**Methods:**

- `set_reward_function(reward_fn: Callable) -> None`: Set custom reward
- `optimize_with_func(reward_fn: Callable) -> Document`: Optimize with function
- `transform(markdown_path: str) -> str`: Transform document

**Example:**
```python
optimizer = PolicyOptimizer()
optimized = optimizer.transform("document.md")
with open("optimized.md", "w") as f:
    f.write(optimized)
```

---

### Visualization (`mdp.visualization`)

**Functions:**

- `plot_document_metrics(metrics_dict: Dict, figsize: Tuple) -> Figure`
- `plot_transitions(chain: MarkChain, top_n: int, figsize: Tuple) -> Figure`
- `plot_document_structure(document: Document, figsize: Tuple) -> Figure`
- `plot_readability_comparison(documents: Dict, figsize: Tuple) -> Figure`
- `plot_filtered_state_space(chain: MarkChain, filter_func: Callable) -> Figure`

**Example:**
```python
from mdp import Document, plot_document_structure
import matplotlib.pyplot as plt

doc = Document(file_path="document.md")
fig = plot_document_structure(doc)
plt.savefig("structure.png")
```

---

### Animations (`mdp.animations`)

**Classes:**

- `DocumentEvolutionAnimator`: Animate transformations
- `StateSpaceEvolutionAnimator`: Animate state space growth
- `MarkChainGenerationAnimator`: Animate text generation
- `BeliefStateAnimator`: Animate belief updates

**Function:**

- `create_comprehensive_animation(document_path: str, output_dir: str) -> Dict`

**Example:**
```python
from mdp import create_comprehensive_animation

# One call creates all animations
outputs = create_comprehensive_animation(
    "document.md",
    "animations/"
)

print(f"Created: {outputs}")
```

---

### Quality (`mdp.quality`)

**Class: `DocumentQuality`**

Multi-dimensional quality assessment.

```python
from mdp import DocumentQuality

quality = DocumentQuality(
    readability_weight=0.4,
    information_density_weight=0.3,
    structural_balance_weight=0.3
)
```

**Methods:**

- `analyze_document(document: Document) -> Dict`: Analyze quality
- `compare_documents(doc1: Document, doc2: Document) -> Dict`: Compare

**Example:**
```python
quality = DocumentQuality()
doc = Document(file_path="document.md")
metrics = quality.analyze_document(doc)
print(f"Readability: {metrics['readability']}")
```

---

## Complete Usage Example

```python
from mdp import (
    Document,
    StateSpace,
    MarkChain,
    BeliefUpdater,
    DocumentQuality,
    create_comprehensive_animation
)
from mdp.transformations import HeadingLevelTransformation

# 1. Load and analyze document
doc = Document(file_path="document.md")
stats = doc.get_statistics()
print(f"Document has {stats['word_count']} words")

# 2. Analyze structure
ss = StateSpace()
ss.parse_markdown(doc.get_content())
ss.visualize("structure.png")

# 3. Semantic analysis
updater = BeliefUpdater()
beliefs = updater.analyze_document(ss)
semantic, prob = updater.get_most_likely_semantics()
print(f"Document type: {semantic} ({prob:.2f})")

# 4. Quality assessment
quality = DocumentQuality()
metrics = quality.analyze_document(doc)
print(f"Quality score: {metrics.get('overall_score', 0):.2f}")

# 5. Generate similar content
chain = MarkChain()
chain.train(doc.get_content())
generated = chain.sample(length=15)
print(f"Generated:\\n{generated}")

# 6. Transform document
transform = HeadingLevelTransformation(increment=1)
transform.apply(doc, "transformed.md")

# 7. Create comprehensive animations
outputs = create_comprehensive_animation(
    "document.md",
    "animations/"
)
print(f"Animations: {list(outputs.keys())}")
```

---

## Installation

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install package
uv pip install -e .

# Install dependencies
uv pip install textstat wordcloud numpy matplotlib networkx tqdm pytest
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_document.py -v

# With coverage
python -m pytest tests/ --cov=mdp --cov-report=html
```

---

*API Reference Complete - All methods documented and tested*
*Last Updated: 2025-09-29*


