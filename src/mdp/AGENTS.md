# MDP Core Modules - AI Agent Development Guide

## Module Overview

This directory contains the core implementation of the Markdown Decision Process framework. Each module implements a specific aspect of the MDP/POMDP paradigm applied to document processing.

## Module Architecture

```
src/mdp/
├── markchain.py         # Markov chain generation (generative model)
├── state_space.py       # Graph-based analysis (state representation)
├── policy_optimizer.py  # RL optimization (decision making)
├── belief_updater.py    # Semantic inference (partial observability)
├── document.py          # Document representation (environment)
├── transformations.py   # Document operations (actions)
├── visualization.py     # Plotting and analysis (observation)
├── export.py           # Multi-format export (output)
├── pandoc.py           # Format conversion (integration)
├── quality.py          # Quality assessment (reward functions)
├── markdown_agent.py   # Autonomous agent (policy execution)
├── plugin_interface.py # Plugin contracts (extensibility)
├── plugin_manager.py   # Plugin system (composition)
├── plugins.py          # Built-in plugins (specialization)
└── animations.py       # Evolution visualization (temporal analysis)
```

## Module Interdependencies

### Core Dependencies

```
Document → StateSpace → MarkChain
                     ↓
                 BeliefUpdater
                     ↓
              PolicyOptimizer
                     ↓
             Transformations
                     ↓
              Visualization
```

### Data Flow

1. **Input**: Markdown text → `Document` class
2. **Analysis**: Document → `StateSpace` graph representation
3. **Generation**: StateSpace → `MarkChain` probability models
4. **Inference**: StateSpace → `BeliefUpdater` semantic beliefs
5. **Optimization**: StateSpace + Beliefs → `PolicyOptimizer` improved structure
6. **Transformation**: Optimization → `Transformations` applied changes
7. **Output**: Results → `Export` / `Visualization`

## Module-Specific Guidance

### markchain.py - Markov Chain Generation

**Purpose**: Learn probabilistic transition models from document corpora and generate new documents.

**Key Classes**:
- `MarkChain`: Main Markov chain implementation
- `HigherOrderMarkChain`: Support for order > 1
- `AdaptiveMarkChain`: Dynamic order selection

**AI Agent Tasks**:
- Add new smoothing techniques (Kneser-Ney, Good-Turing)
- Implement context-dependent transitions
- Add domain adaptation capabilities
- Optimize probability computation for large vocabularies

**Testing Focus**:
- Transition probability convergence
- Generation diversity (distinct n-grams)
- Cross-domain generalization
- Memory efficiency for large corpora

### state_space.py - Graph-Based Analysis

**Purpose**: Represent document structure as directed graphs with rich metadata.

**Key Classes**:
- `StateSpace`: Main graph representation
- `StateNode`: Individual state with metadata
- `StateTransition`: Edge with transition properties

**AI Agent Tasks**:
- Add hierarchical state space support
- Implement graph clustering algorithms
- Add multi-level abstraction (sections → paragraphs → sentences)
- Optimize centrality computation for large graphs

**Testing Focus**:
- Graph construction correctness
- Centrality measure accuracy
- Subgraph extraction
- Community detection

### policy_optimizer.py - Reinforcement Learning

**Purpose**: Optimize document structure using RL algorithms.

**Key Classes**:
- `PolicyOptimizer`: Main optimization engine
- `ValueFunction`: State value estimates
- `QFunction`: State-action value estimates
- `Policy`: Learned decision strategy

**AI Agent Tasks**:
- Implement actor-critic methods
- Add multi-objective optimization (Pareto)
- Implement constrained optimization
- Add meta-learning for transfer

**Testing Focus**:
- Convergence properties
- Optimality of learned policies
- Constraint satisfaction
- Computational efficiency

### belief_updater.py - Semantic Inference

**Purpose**: Maintain probability distributions over semantic interpretations.

**Key Classes**:
- `BeliefUpdater`: Bayesian belief updating
- `ObservationModel`: P(observation | semantic_class)
- `TransitionModel`: P(semantic' | semantic, action)

**AI Agent Tasks**:
- Add particle filtering for complex beliefs
- Implement active learning for observation models
- Add uncertainty quantification metrics
- Optimize belief update computation

**Testing Focus**:
- Belief update correctness (Bayes' rule)
- Calibration of confidence estimates
- Convergence to true semantics
- Computational efficiency

### document.py - Document Representation

**Purpose**: Parse and represent Markdown documents with rich metadata.

**Key Classes**:
- `Document`: Main document class
- `DocumentParser`: Markdown parsing
- `DocumentState`: State representation

**AI Agent Tasks**:
- Add incremental parsing
- Implement multi-format support (RST, AsciiDoc)
- Add metadata extraction (author, date, keywords)
- Optimize parsing for large documents

**Testing Focus**:
- Parsing accuracy across Markdown variants
- Metadata extraction correctness
- Edge case handling (malformed input)
- Performance on large files

### transformations.py - Document Operations

**Purpose**: Implement document transformation operations (actions in MDP).

**Key Classes**:
- `Transformation`: Abstract transformation
- `StructuralTransformation`: Structure changes
- `ContentTransformation`: Content modifications

**AI Agent Tasks**:
- Add composable transformations (pipelines)
- Implement reversible transformations
- Add constraint checking (preserve semantics)
- Optimize transformation application

**Testing Focus**:
- Transformation correctness
- Reversibility where applicable
- Constraint preservation
- Performance on complex documents

### visualization.py - Plotting and Analysis

**Purpose**: Visualize document structure, transitions, and optimization.

**Key Classes**:
- `DocumentVisualizer`: Main visualization class
- `StateSpacePlotter`: Graph visualization
- `TransitionPlotter`: Transition matrix plots

**AI Agent Tasks**:
- Add interactive visualizations (Plotly, Bokeh)
- Implement animation generation
- Add 3D state space visualization
- Optimize rendering for large graphs

**Testing Focus**:
- Plot generation correctness
- Layout quality for various graph types
- Performance on large visualizations
- Output format compatibility

### export.py - Multi-Format Export

**Purpose**: Export documents and analyses to multiple formats.

**Key Classes**:
- `DocumentExporter`: Main export class
- `FormatConverter`: Format-specific converters

**AI Agent Tasks**:
- Add more output formats
- Implement template-based export
- Add custom styling support
- Optimize export performance

**Testing Focus**:
- Format conversion accuracy
- Metadata preservation
- Style application correctness
- Cross-platform compatibility

### quality.py - Quality Assessment

**Purpose**: Implement reward functions for document quality.

**Key Classes**:
- `RewardFunction`: Abstract reward
- `ReadabilityReward`: Readability metrics
- `StructureReward`: Structure quality
- `SemanticReward`: Semantic coherence

**AI Agent Tasks**:
- Add learned reward functions
- Implement multi-dimensional quality
- Add domain-specific rewards
- Optimize reward computation

**Testing Focus**:
- Reward function correctness
- Correlation with human judgment
- Computational efficiency
- Robustness to edge cases

## Development Patterns

### Adding New Features

1. **Design Phase**:
   - Write design doc explaining MDP connection
   - Define interfaces following existing patterns
   - Plan test cases

2. **Implementation Phase**:
   - Write tests first (TDD)
   - Implement feature maintaining MDP theme
   - Add comprehensive docstrings

3. **Integration Phase**:
   - Update dependent modules
   - Add examples and documentation
   - Benchmark performance

### Code Quality Standards

**Type Hints** (Required):
```python
def optimize_policy(state_space: StateSpace,
                   reward_function: RewardFunction,
                   discount_factor: float = 0.9) -> Policy:
    """Optimize policy using value iteration."""
    pass
```

**Error Handling** (Required):
```python
def update_beliefs(self, observation: Dict[str, float]) -> None:
    """Update beliefs from observation."""
    if not observation:
        raise ValueError("Observation cannot be empty")
    
    if not self.is_initialized:
        raise RuntimeError("Belief updater not initialized")
    
    try:
        # Update logic
        pass
    except Exception as e:
        self.logger.error(f"Belief update failed: {e}")
        raise
```

**Logging** (Recommended):
```python
import logging

class PolicyOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize(self):
        self.logger.info("Starting optimization")
        self.logger.debug(f"State space size: {len(self.state_space)}")
        # ... optimization logic ...
        self.logger.info(f"Converged in {iterations} iterations")
```

## Performance Optimization

### Critical Paths

1. **Markov Chain Training**: O(n*k) where n=documents, k=avg length
   - Optimize: Use trie for prefix storage
   - Cache: Transition probabilities

2. **Policy Optimization**: O(|S|²*|A|*iterations)
   - Optimize: Sparse state spaces, approximate algorithms
   - Cache: Q-values between iterations

3. **Belief Updates**: O(|C|²) where C=semantic classes
   - Optimize: Prune unlikely classes
   - Cache: Observation likelihoods

### Memory Management

```python
# Use generators for large datasets
def iter_states(document: Document) -> Iterator[State]:
    """Yield states one at a time."""
    for line in document.lines:
        yield parse_state(line)

# Use sparse matrices for large transition tables
from scipy.sparse import csr_matrix

transition_matrix = csr_matrix((data, (rows, cols)), shape=(n_states, n_states))
```

## Testing Strategies

### Unit Test Template

```python
import pytest
from mdp.markchain import MarkChain

class TestMarkChain:
    """Test Markov chain functionality."""
    
    @pytest.fixture
    def sample_docs(self):
        """Provide sample documents."""
        return ["# Header\n\nParagraph", "# Another\n\nMore text"]
    
    def test_training_convergence(self, sample_docs):
        """Test that training converges to valid probabilities."""
        chain = MarkChain(order=1)
        chain.train(sample_docs)
        
        # Verify probabilities sum to 1
        for state, transitions in chain.transition_matrix.items():
            total = sum(transitions.values())
            assert abs(total - 1.0) < 1e-6
    
    def test_generation_diversity(self, sample_docs):
        """Test that generation produces diverse output."""
        chain = MarkChain(order=1)
        chain.train(sample_docs)
        
        generated = [chain.generate(length=50) for _ in range(10)]
        unique_docs = len(set(generated))
        
        assert unique_docs >= 7, "Generation should be diverse"
```

### Integration Test Template

```python
def test_optimization_pipeline():
    """Test complete optimization pipeline."""
    # Setup
    document = Document(content="# Test\n\nParagraph")
    state_space = StateSpace(document)
    belief_updater = BeliefUpdater()
    optimizer = PolicyOptimizer(state_space, belief_updater)
    
    # Execute
    result = optimizer.optimize()
    
    # Verify
    assert result.quality_improvement > 0
    assert result.convergence_achieved
    assert len(result.applied_transformations) > 0
```

## Debugging Tips

### Common Issues

**Issue**: Infinite loops in optimization
```python
# Add iteration limit and logging
for iteration in range(MAX_ITERATIONS):
    self.logger.debug(f"Iteration {iteration}, delta={delta}")
    if delta < threshold:
        break
else:
    self.logger.warning("Max iterations reached without convergence")
```

**Issue**: Memory errors with large documents
```python
# Use chunking and generators
def process_large_document(document: Document, chunk_size: int = 1000):
    for i in range(0, len(document.states), chunk_size):
        chunk = document.states[i:i+chunk_size]
        process_chunk(chunk)
```

**Issue**: Numerical instability in probabilities
```python
# Use log probabilities
import numpy as np

log_probs = np.log(probs + 1e-10)  # Add small constant to avoid log(0)
normalized_log_probs = log_probs - np.logaddexp.reduce(log_probs)
probs = np.exp(normalized_log_probs)
```

## Module Maintenance

### Backwards Compatibility

- Deprecated features should warn for 2 releases before removal
- Use `warnings.warn()` with `DeprecationWarning`
- Document breaking changes in CHANGELOG.md

### Version Numbering

- Major: Breaking changes to public API
- Minor: New features, backwards compatible
- Patch: Bug fixes, no API changes

## Resources

- **API Documentation**: `/docs/api/`
- **Technical Guides**: `/docs/technical/`
- **Examples**: `/examples/`
- **Tests**: `/tests/`

---

*Each module is a piece of the MDP puzzle. The state space represents our world, transitions capture dynamics, beliefs handle uncertainty, and policies guide us toward optimal documents. Code with this mindset!* 🧩

