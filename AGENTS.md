# Markdown Decision Process - AI Agent Collaboration Guide

## Overview

This document provides comprehensive guidance for AI agents (like Claude, GPT-4, etc.) working on the Markdown Decision Process (MDP) framework. It describes the codebase architecture, development workflows, testing strategies, and best practices for effective collaboration.

## Repository Structure

```
markdown_decision_process/
├── src/mdp/              # Core framework implementation
│   ├── markchain.py      # Markov chain document generation
│   ├── state_space.py    # Graph-based document analysis
│   ├── policy_optimizer.py  # RL-based optimization
│   ├── belief_updater.py    # Semantic uncertainty management
│   ├── document.py       # Document representation
│   ├── transformations.py   # Document transformations
│   ├── visualization.py     # Plotting and visualization
│   ├── export.py         # Export functionality
│   ├── pandoc.py         # Pandoc integration
│   ├── quality.py        # Quality assessment
│   ├── markdown_agent.py    # Autonomous agent
│   ├── plugin_interface.py  # Plugin system interfaces
│   ├── plugin_manager.py    # Plugin management
│   ├── plugins.py        # Built-in plugins
│   └── animations.py     # Animation generation
├── tests/                # Comprehensive test suite
├── examples/             # Usage examples and demonstrations
├── docs/                 # Documentation and guides
├── paper/                # Academic paper and research
└── pyproject.toml        # Modern Python packaging
```

## Core Architecture Principles

### 1. MDP/POMDP Theoretical Foundation

The framework is built on rigorous decision-theoretic foundations:

- **States**: Markdown elements (headers, paragraphs, lists, code blocks, etc.)
- **Actions**: Document transformations (reordering, restructuring, rewording)
- **Transitions**: Probabilistic state-to-state movements
- **Rewards**: Document quality metrics (readability, structure, coherence)
- **Beliefs**: Probability distributions over semantic interpretations

### 2. Modular Design

Each module has a single responsibility and clear interfaces:

- **MarkChain**: Generative models for document creation
- **StateSpace**: Structural analysis and graph operations
- **PolicyOptimizer**: Reinforcement learning for optimization
- **BeliefUpdater**: Probabilistic semantic inference
- **Plugins**: Domain-specific extensions

### 3. The MDP Theme

**IMPORTANT**: This codebase maintains a playful but scientifically accurate theme where Markdown processing is reimagined through Markov Decision Process concepts. When writing code or documentation:

- Use terminology like "states", "transitions", "policies", "rewards", "beliefs"
- Frame document elements as states in a stochastic process
- Refer to document quality metrics as "reward functions"
- Call semantic interpretation "belief updating"
- Maintain scientific accuracy while keeping the conceptual joke alive

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/docxology/markdown_decision_process.git
cd markdown_decision_process

# Install in development mode
pip install -e ".[dev,docs,pandoc]"

# Run tests
pytest tests/ -v --cov=src/mdp --cov-report=html

# Build documentation
cd docs && python build_docs.py
```

### Code Style and Standards

**Python Code Style**:
- Line length: 88 characters (Black formatter)
- Docstring style: Google format
- Type hints: Required for all public functions
- Import sorting: isort

**Naming Conventions**:
- Modules: `snake_case`
- Classes: `PascalCase`
- Functions: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Comments**:
- Maintain the MDP theme in comments
- Each module should have at least one witty parallel to MDP/POMDP concepts
- Example: "The belief updater handles the partial observability of user intent"

### Testing Strategy

**Test-Driven Development**:
- Write tests before implementing features
- Aim for 80%+ code coverage
- Use pytest for all testing
- No mock methods - always use real data analysis

**Test Categories**:
1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Property-Based Tests**: Test invariants with hypothesis
4. **Performance Tests**: Benchmark critical paths
5. **Snapshot Tests**: Ensure output consistency

**Running Tests**:
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_markchain.py -v

# With coverage
pytest tests/ --cov=src/mdp --cov-report=term-missing

# Performance benchmarks
pytest tests/test_performance.py --benchmark-only
```

## Key Implementation Patterns

### 1. State Representation

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DocumentState:
    """Represents a document state with rich metadata."""
    state_id: str
    state_type: str  # header, paragraph, list, code, etc.
    content: str
    line_number: int
    metadata: Dict[str, Any]
    features: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary representation."""
        return {
            'state_id': self.state_id,
            'state_type': self.state_type,
            'content': self.content,
            'line_number': self.line_number,
            'metadata': self.metadata,
            'features': self.features
        }
```

### 2. Markov Chain Pattern

```python
class MarkChain:
    """Markov chain for document generation."""
    
    def __init__(self, order: int = 1, smoothing: float = 0.01):
        self.order = order
        self.smoothing = smoothing
        self.transitions = defaultdict(Counter)
        self.is_trained = False
    
    def train(self, documents: List[str]) -> None:
        """Train on document corpus."""
        # Extract states and build transition counts
        # Apply smoothing for unseen transitions
        # Estimate transition probabilities
        pass
    
    def generate(self, length: int = 100) -> str:
        """Generate document using learned model."""
        # Sample from transition distribution
        # Maintain state history for higher-order models
        # Apply temperature-based exploration
        pass
```

### 3. Policy Optimization Pattern

```python
class PolicyOptimizer:
    """RL-based document optimization."""
    
    def __init__(self, state_space, reward_function, algorithm='value_iteration'):
        self.state_space = state_space
        self.reward_function = reward_function
        self.algorithm = algorithm
        self.value_function = {}
        self.policy = {}
    
    def optimize(self) -> OptimizationResult:
        """Optimize document structure."""
        if self.algorithm == 'value_iteration':
            return self._value_iteration()
        elif self.algorithm == 'policy_iteration':
            return self._policy_iteration()
        else:
            return self._q_learning()
```

### 4. Belief Update Pattern

```python
class BeliefUpdater:
    """Bayesian belief updating for semantic inference."""
    
    def __init__(self, semantic_classes: List[str]):
        self.semantic_classes = semantic_classes
        self.beliefs = {cls: 1.0/len(semantic_classes) 
                       for cls in semantic_classes}
        self.observation_model = {}
    
    def update_beliefs(self, observation: Dict[str, float]) -> None:
        """Update beliefs given new observation."""
        # Compute likelihoods P(o|c) for each class c
        # Apply Bayes' rule: P(c|o) ∝ P(o|c) * P(c)
        # Normalize to get posterior distribution
        pass
```

## Plugin Development

### Creating Custom Plugins

```python
from mdp.plugin_interface import MDPPlugin, Transformation, RewardFunction

class AcademicWritingPlugin(MDPPlugin):
    """Plugin for academic document optimization."""
    
    def get_transformations(self) -> List[Transformation]:
        """Return custom transformation operations."""
        return [
            CitationReordering(),
            SectionStructuring(),
            MethodologyEnhancement()
        ]
    
    def get_reward_functions(self) -> Dict[str, RewardFunction]:
        """Return custom reward functions."""
        return {
            'citation_quality': CitationQualityReward(),
            'methodology_clarity': MethodologyClarityReward(),
            'contribution_emphasis': ContributionEmphasisReward()
        }
```

### Plugin Registration

```python
from mdp.plugin_manager import PluginManager

# Register plugin
manager = PluginManager()
manager.register_plugin('academic', AcademicWritingPlugin)

# Use plugin transformations
transformations = manager.get_transformations('academic')
rewards = manager.get_reward_functions('academic')
```

## Visualization Best Practices

### Creating Document Visualizations

```python
from mdp.visualization import DocumentVisualizer

# Visualize state space
visualizer = DocumentVisualizer(state_space)
visualizer.plot_state_graph(
    node_color='state_type',
    edge_width='weight',
    layout='spring'
)

# Plot transition probabilities
visualizer.plot_transition_heatmap(
    markchain.transition_matrix,
    title='State Transition Probabilities'
)

# Visualize optimization process
visualizer.plot_optimization_trajectory(
    optimization_history,
    metrics=['value_function', 'policy_entropy']
)
```

## Common Tasks for AI Agents

### Task 1: Adding New State Types

1. Update `state_space.py` with new state classification logic
2. Extend `markchain.py` to handle new state transitions
3. Add parsing logic in `document.py`
4. Update tests in `test_state_space.py`
5. Add visualization support in `visualization.py`

### Task 2: Implementing New Reward Functions

1. Create reward class inheriting from `RewardFunction`
2. Implement `compute()` method with state/action/next_state signature
3. Add to `quality.py` or create plugin
4. Write tests with edge cases
5. Document in API reference

### Task 3: Adding Optimization Algorithms

1. Implement algorithm in `policy_optimizer.py`
2. Follow naming convention: `_algorithm_name_optimization()`
3. Return `OptimizationResult` dataclass
4. Add convergence criteria and early stopping
5. Benchmark against existing algorithms
6. Document complexity and use cases

### Task 4: Extending Documentation

1. Use Google-style docstrings
2. Include examples in docstrings
3. Add type hints for all parameters
4. Link to related functions/classes
5. Update API documentation in `docs/api/`

## Troubleshooting Guide

### Common Issues

**Issue**: Markov chain not converging
- **Solution**: Increase smoothing parameter, check for state space connectivity

**Issue**: Policy optimization timeout
- **Solution**: Reduce max_iterations, simplify state space, use approximation

**Issue**: Belief updates producing uniform distributions
- **Solution**: Check observation model likelihoods, verify feature extraction

**Issue**: Visualization out of memory
- **Solution**: Filter states before plotting, use sparse graph representations

## Performance Optimization

### Profiling

```python
# Use built-in profiling
from mdp.utils.performance import profile_function

@profile_function
def expensive_operation():
    # Your code here
    pass

# Check performance metrics
metrics = expensive_operation.get_metrics()
print(f"Time: {metrics['time']:.2f}s, Memory: {metrics['memory']:.2f}MB")
```

### Optimization Checklist

- [ ] Use sparse matrices for large transition matrices
- [ ] Cache expensive computations (centrality, embeddings)
- [ ] Vectorize operations with NumPy where possible
- [ ] Use Numba JIT compilation for hot paths
- [ ] Implement incremental updates instead of recomputation
- [ ] Profile before optimizing - measure, don't guess

## Documentation Standards

### Module Documentation

```python
"""Module for Markov chain document generation.

This module implements sophisticated Markov chain models for document
structure learning and generation. It treats Markdown elements as states
in a stochastic process, learning transition probabilities from training
corpora.

The MarkChain class supports:
- Higher-order Markov models (order 1-3)
- Additive smoothing for unseen transitions
- Temperature-based sampling for controlled randomness
- Domain adaptation through transfer learning

Example:
    >>> from mdp import MarkChain
    >>> chain = MarkChain(order=2, smoothing=0.01)
    >>> chain.train(documents)
    >>> generated = chain.generate(length=50)
    
The module maintains the MDP theme: documents are viewed as stochastic
processes where the "belief updater" would handle partial observability
of semantic intent.
"""
```

### Function Documentation

```python
def optimize_document(state_space: StateSpace,
                     reward_weights: Dict[str, float],
                     algorithm: str = 'value_iteration') -> OptimizedDocument:
    """Optimize document structure using reinforcement learning.
    
    Applies policy optimization to improve document quality according to
    user-specified reward functions. The optimization treats document
    editing as a Markov Decision Process where states are document
    configurations and actions are transformations.
    
    Args:
        state_space: Graph representation of document structure
        reward_weights: Dict mapping reward components to weights
        algorithm: Optimization algorithm ('value_iteration', 'policy_iteration', 'q_learning')
    
    Returns:
        OptimizedDocument containing improved structure and metadata
    
    Raises:
        ValueError: If state_space is empty or reward_weights don't sum to 1
        ConvergenceError: If optimization fails to converge within max_iterations
    
    Example:
        >>> state_space = StateSpace(document)
        >>> rewards = {'readability': 0.5, 'structure': 0.3, 'coherence': 0.2}
        >>> optimized = optimize_document(state_space, rewards)
        >>> print(f"Improvement: {optimized.quality_delta:.2%}")
    
    Note:
        The optimization uses value iteration by default, which provides
        optimal policies but may be slow for large state spaces (>5000 states).
        Consider 'q_learning' for faster but approximate results.
    """
    pass
```

## Contributing Guidelines

### Pull Request Process

1. **Branch Naming**: `feature/description` or `fix/description`
2. **Commit Messages**: Conventional commits format
3. **Tests**: All tests must pass, coverage must not decrease
4. **Documentation**: Update docstrings and API docs
5. **Review**: At least one maintainer approval required

### Code Review Checklist

- [ ] Follows MDP theme and terminology
- [ ] Includes comprehensive tests
- [ ] Has proper error handling
- [ ] Documented with examples
- [ ] Performance tested if applicable
- [ ] Backwards compatible (or documented breaking change)

## Research and Academic Use

### Citation

When using this framework in research:

```bibtex
@software{mdp_framework,
  title={Markdown Decision Process: A Framework for Probabilistic Document Analysis and Optimization},
  author={Friedman, Daniel Ari},
  year={2024},
  url={https://github.com/docxology/markdown_decision_process},
  doi={10.5281/zenodo.17244387}
}
```

### Paper Development

The `paper/` directory contains modular academic paper sections:
- Edit individual section files (`00_abstract.md` through `10_references.md`)
- Run `python paper/assemble_paper.py` to generate complete paper
- Output formats: Markdown, PDF, HTML, DOCX

## Contact and Support

- **Repository**: https://github.com/docxology/markdown_decision_process
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: daniel@activeinference.institute

## Version History

- **v0.1.0** (2023): Initial release with core MDP functionality
- **v0.2.0** (2024): Added POMDP belief updating and plugin system
- **v0.3.0** (2024): Enhanced visualization and multi-objective optimization

---

*Remember: When in doubt, think of documents as Markov Decision Processes. The partial observability of semantic intent is handled by the belief updater, and policy optimization maximizes expected reward (document quality). Keep the theme alive! 🎲📄*

