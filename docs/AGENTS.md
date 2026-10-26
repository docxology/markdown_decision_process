# Documentation - AI Agent Documentation Guide

## Overview

This directory contains comprehensive documentation for the Markdown Decision Process framework, including API references, user guides, technical deep dives, and development processes.

## Documentation Structure

```
docs/
├── index.md                 # Main documentation index
├── README.md               # Documentation overview
├── API_COMPLETE.md         # Complete API reference
├── ROADMAP.md              # Development roadmap
├── DEVELOPMENT_PROCESS.md  # Development workflows
├── api/                    # API documentation by module
│   ├── markchain.md        # MarkChain API
│   ├── state_space.md      # StateSpace API
│   ├── policy_optimizer.md # PolicyOptimizer API
│   ├── belief_updater.rst  # BeliefUpdater API
│   ├── document.md         # Document API
│   └── ...                 # Other modules
├── guides/                 # User guides and tutorials
│   └── user_guide.md       # Comprehensive user guide
├── technical/              # Technical documentation
│   ├── markchain.md        # MarkChain technical details
│   ├── state_space.md      # StateSpace algorithms
│   ├── policy_optimization.md # Optimization theory
│   ├── belief_updater.md   # Belief update mathematics
│   └── README.md           # Technical docs index
├── examples/               # Documentation examples
│   ├── basic_usage.py      # Basic usage examples
│   └── advanced_usage.py   # Advanced examples
├── build_docs.py           # Documentation build script
├── conf.py                 # Sphinx configuration
└── versioning.py           # Version management
```

## Documentation Types

### 1. API Documentation

**Purpose**: Provide comprehensive reference for all public APIs.

**Files**:
- `api/markchain.md` - MarkChain class and methods
- `api/state_space.md` - StateSpace class and methods
- `api/policy_optimizer.md` - PolicyOptimizer class and methods
- `api/belief_updater.rst` - BeliefUpdater class and methods

**Format**: Markdown or ReStructuredText (for Sphinx)

**Example Structure**:
```markdown
# MarkChain API

## Class: MarkChain

Markov chain implementation for document generation.

### Constructor

```python
MarkChain(order: int = 1, smoothing: float = 0.01, min_transitions: int = 2)
```

**Parameters**:
- `order` (int): Markov chain order (1-3 recommended)
- `smoothing` (float): Additive smoothing parameter
- `min_transitions` (int): Minimum transition count threshold

**Returns**: MarkChain instance

### Methods

#### train(documents: List[str]) -> None

Train Markov chain on document corpus.

**Parameters**:
- `documents` (List[str]): List of markdown documents

**Raises**:
- `ValueError`: If documents list is empty
- `RuntimeError`: If training fails

**Example**:
```python
chain = MarkChain(order=2)
chain.train(["# Doc 1\n\nText", "# Doc 2\n\nMore text"])
```
```

### 2. User Guides

**Purpose**: Help users understand and effectively use the framework.

**Files**:
- `guides/user_guide.md` - Comprehensive tutorial
- `guides/quickstart.md` - Quick start guide
- `guides/best_practices.md` - Best practices

**Target Audience**: End users, developers using the framework

**Example Structure**:
```markdown
# User Guide

## Introduction

Welcome to the Markdown Decision Process framework...

## Getting Started

### Installation

```bash
pip install markdown-decision-process
```

### Your First Document Analysis

```python
from mdp import Document, StateSpace

doc = Document(content="# Title\n\nContent")
state_space = StateSpace(doc)
print(f"States: {len(state_space.states)}")
```

## Core Concepts

### 1. Documents as Markov Decision Processes

Documents are modeled as...

### 2. State Spaces and Transitions

State spaces represent...
```

### 3. Technical Documentation

**Purpose**: Explain algorithms, mathematics, and implementation details.

**Files**:
- `technical/markchain.md` - Markov chain theory
- `technical/policy_optimization.md` - RL algorithms
- `technical/belief_updater.md` - Bayesian inference

**Target Audience**: Advanced users, researchers, contributors

**Example Structure**:
```markdown
# Markov Chain Document Generation - Technical Details

## Theoretical Foundation

### Higher-Order Markov Models

A Markov chain of order $k$ models the probability:

$$P(s_t | s_{t-1}, s_{t-2}, \ldots, s_1) = P(s_t | s_{t-1}, \ldots, s_{t-k})$$

### Smoothing Techniques

We implement additive (Laplace) smoothing:

$$P(s' | s) = \frac{\text{count}(s, s') + \alpha}{\text{count}(s) + \alpha \cdot |S|}$$

## Implementation Details

### Efficient Probability Storage

We use nested dictionaries for $O(1)$ lookup:

```python
self.transitions = {
    ('state_1',): {'state_2': 10, 'state_3': 5},
    ('state_1', 'state_2'): {'state_3': 8, 'state_4': 2}
}
```

### Complexity Analysis

- **Training**: $O(n \cdot k)$ where $n$ = document length, $k$ = order
- **Generation**: $O(m \cdot k)$ where $m$ = target length
- **Memory**: $O(|V|^k)$ where $|V|$ = vocabulary size
```

### 4. Development Documentation

**Purpose**: Guide contributors and maintainers.

**Files**:
- `DEVELOPMENT_PROCESS.md` - Development workflow
- `ROADMAP.md` - Future plans
- `CONTRIBUTING.md` - Contribution guidelines

**Example Structure**:
```markdown
# Development Process

## Branching Strategy

- `main`: Stable releases
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Merge to main and tag
6. Deploy to PyPI
```

## Building Documentation

### Sphinx Documentation

```bash
# Install documentation dependencies
pip install -e ".[dev]"
pip install sphinx sphinx-rtd-theme myst-parser sphinx-markdown-tables

# Build HTML documentation
cd docs
python build_docs.py

# Or use Sphinx directly
sphinx-build -b html . _build/html

# View documentation
open _build/html/index.html
```

### Markdown Documentation

```bash
# Convert Markdown to HTML
python -c "
from pathlib import Path
import markdown

for md_file in Path('docs').rglob('*.md'):
    html = markdown.markdown(md_file.read_text())
    html_file = md_file.with_suffix('.html')
    html_file.write_text(html)
"
```

## Documentation Standards

### Writing Style

1. **Clear and Concise**: Use simple language
2. **Example-Driven**: Include code examples
3. **Maintain Theme**: Use MDP terminology appropriately
4. **Complete**: Cover all parameters, return values, exceptions

### Code Examples

```python
# Good: Complete, runnable example
from mdp import Document, StateSpace

doc = Document(content="# Title\n\nContent")
state_space = StateSpace(doc)
analysis = state_space.analyze_structure()
print(f"Document has {len(state_space.states)} states")

# Bad: Incomplete, vague example
doc = Document(...)  # What content?
state_space.do_something()  # What method?
```

### Docstring Standards

Use Google-style docstrings:

```python
def optimize_document(state_space: StateSpace,
                     reward_weights: Dict[str, float],
                     algorithm: str = 'value_iteration') -> OptimizationResult:
    """Optimize document structure using reinforcement learning.
    
    This function applies policy optimization to improve document quality
    according to user-specified reward functions. The optimization treats
    document editing as a Markov Decision Process.
    
    Args:
        state_space: Graph representation of document structure
        reward_weights: Dictionary mapping reward component names to weights.
            Must sum to 1.0.
        algorithm: Optimization algorithm to use. Options:
            - 'value_iteration': Standard value iteration (default)
            - 'policy_iteration': Policy iteration algorithm
            - 'q_learning': Q-learning for large state spaces
    
    Returns:
        OptimizationResult containing:
            - optimized_document: Improved document
            - quality_improvement: Percentage improvement
            - iterations: Number of iterations to convergence
            - transformations: List of applied transformations
    
    Raises:
        ValueError: If state_space is empty or reward_weights don't sum to 1
        ConvergenceError: If optimization fails to converge within max_iterations
    
    Example:
        >>> state_space = StateSpace(document)
        >>> rewards = {'readability': 0.5, 'structure': 0.3, 'coherence': 0.2}
        >>> result = optimize_document(state_space, rewards)
        >>> print(f"Improvement: {result.quality_improvement:.2%}")
        Improvement: 12.3%
    
    Note:
        Value iteration provides optimal policies but may be slow for large
        state spaces (>5000 states). Consider q_learning for faster results.
    
    See Also:
        PolicyOptimizer: For more control over optimization
        CompositeReward: For custom reward function composition
    """
    pass
```

## API Documentation Workflow

### 1. Update Module Docstrings

```python
# In src/mdp/markchain.py

"""Markov chain document generation module.

This module implements sophisticated Markov chain models for learning
document structure patterns and generating new documents. It supports:

- Higher-order Markov chains (order 1-3)
- Multiple smoothing techniques
- Temperature-based sampling
- Domain adaptation

The module maintains the MDP theme by treating documents as stochastic
processes where state transitions follow learned probability distributions.

Example:
    >>> from mdp import MarkChain
    >>> chain = MarkChain(order=2, smoothing=0.01)
    >>> chain.train(documents)
    >>> generated = chain.generate(length=100)
"""
```

### 2. Generate API Documentation

```bash
# Auto-generate API docs from docstrings
python docs/generate_api_docs.py

# This creates/updates files in docs/api/
```

### 3. Review and Enhance

- Add conceptual explanations
- Include diagrams and visualizations
- Add cross-references
- Include performance notes

### 4. Build and Test

```bash
# Build documentation
python docs/build_docs.py

# Check for broken links
python docs/check_links.py

# Verify examples run
python docs/test_examples.py
```

## Version Management

### Versioning Documentation

```python
# In docs/versioning.py

def get_version_info():
    """Get current version information."""
    return {
        'version': '0.3.0',
        'release_date': '2024-01-15',
        'status': 'stable'
    }

def update_version_refs(new_version: str):
    """Update version references in documentation."""
    files_to_update = [
        'docs/index.md',
        'docs/README.md',
        'docs/api/index.md'
    ]
    
    for file_path in files_to_update:
        update_file_version(file_path, new_version)
```

### Changelog Maintenance

```markdown
# CHANGELOG.md

## [0.3.0] - 2024-01-15

### Added
- Multi-objective optimization support
- Interactive visualizations with Plotly
- Advanced belief calibration metrics

### Changed
- Improved state space construction performance (2x faster)
- Enhanced error messages and validation

### Fixed
- Memory leak in large document processing
- Visualization rendering on macOS

### Deprecated
- `StateSpace.build()` - use `StateSpace(document)` instead
```

## Documentation Testing

### Test Code Examples

```python
# docs/test_examples.py

import doctest
import importlib

def test_documentation_examples():
    """Test all code examples in documentation."""
    doc_modules = [
        'docs.api.markchain',
        'docs.api.state_space',
        'docs.guides.user_guide'
    ]
    
    for module_name in doc_modules:
        module = importlib.import_module(module_name)
        results = doctest.testmod(module)
        
        if results.failed > 0:
            print(f"FAILED: {module_name}")
            print(f"  {results.failed} failures")
        else:
            print(f"PASSED: {module_name}")
```

### Link Checking

```bash
# Check for broken links
python docs/check_links.py

# Output:
# Checking docs/index.md... OK
# Checking docs/api/markchain.md... OK
# Checking docs/guides/user_guide.md... BROKEN LINK: /api/nonexistent
```

## Documentation Deployment

### GitHub Pages

```yaml
# .github/workflows/docs.yml

name: Documentation

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install sphinx sphinx-rtd-theme myst-parser sphinx-markdown-tables
      
      - name: Build documentation
        run: |
          cd docs
          python build_docs.py
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5
        with:
          path: docs/_build/html
```

Deployment is opt-in through the `DOCS_PAGES_ENABLED` repository variable; the
authoritative description is [PUBLISHING.md](PUBLISHING.md).

### ReadTheDocs

Not configured for this repository: there is no `.readthedocs.yml` and no
hosted `markdown-decision-process.readthedocs.io` site. Build the HTML locally
("Local build" in [PUBLISHING.md](PUBLISHING.md)) or use the GitHub Pages flow
above.

## Contribution Guidelines

### Adding New Documentation

1. **Create Document**:
   ```bash
   # For API docs
   touch docs/api/new_module.md
   
   # For guides
   touch docs/guides/new_guide.md
   ```

2. **Follow Template**:
   - Use existing docs as templates
   - Include all required sections
   - Add code examples

3. **Update Index**:
   ```markdown
   # In docs/index.md
   - [New Guide](guides/new_guide.md)
   ```

4. **Test Documentation**:
   ```bash
   python docs/test_examples.py
   python docs/check_links.py
   ```

5. **Submit PR**:
   - Title: "docs: Add guide for X"
   - Include screenshots if relevant
   - Link to related issues

### Maintaining Documentation

- Review quarterly for accuracy
- Update examples when API changes
- Add deprecation notices before removal
- Keep screenshots current
- Monitor user feedback

---

*Documentation is our observation model - it helps users build correct beliefs about the framework's capabilities. Well-calibrated documentation (accurate and complete) leads to confident, correct usage!* 📖
