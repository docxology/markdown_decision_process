# Test Suite - AI Agent Testing Guide

## Overview

This directory contains comprehensive tests for the Markdown Decision Process framework. Our testing philosophy emphasizes real data analysis over mocks, high coverage (80%+), and maintaining the MDP conceptual framework.

## Test Organization

- [conftest.py](conftest.py) defines shared Markdown inputs and temporary file fixtures.
- [fixtures/](fixtures/) contains the tracked Markdown inputs and expected transformation outputs.
- [snapshots/](snapshots/) holds the tracked JSON baselines for [test_snapshot.py](test_snapshot.py).
- [examples/sample_docs/](../examples/sample_docs/) contains the blog post, research paper and technical document examples.

## Testing Principles

### 1. Test-Driven Development (TDD)

Always write tests before implementation:

```python
# 1. Write failing test
def test_new_feature():
    """Test description of expected behavior."""
    result = new_feature(input_data)
    assert result == expected_output

# 2. Implement feature to make test pass
def new_feature(input_data):
    # Implementation
    return result

# 3. Refactor while keeping tests green
```

### 2. No Mock Methods - Real Data Analysis

**DON'T DO THIS**:
```python
def test_with_mocks():
    mock_document = Mock()
    mock_document.get_states.return_value = ["fake_state"]
    # This doesn't test real behavior!
```

**DO THIS**:
```python
def test_with_real_data(sample_document):
    """Use real documents and verify actual behavior."""
    state_space = StateSpace(sample_document)
    states = state_space.get_states()
    assert len(states) > 0
    assert all(isinstance(s, DocumentState) for s in states)
```

### 3. High Coverage Target (80%+)

```bash
# Check coverage
pytest tests/ --cov=src/mdp --cov-report=html --cov-report=term-missing

# Coverage report shows:
# - Line coverage
# - Branch coverage
# - Missing lines

# Aim for:
# - Overall: 80%+
# - Core modules: 90%+
# - Critical paths: 100%
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Example**: `test_markchain.py`
```python
class TestMarkChain:
    """Unit tests for Markov chain functionality."""
    
    def test_transition_probability_convergence(self, training_docs):
        """Verify transition probabilities sum to 1."""
        chain = MarkChain(order=1, smoothing=0.01)
        chain.train(training_docs)
        
        for state, transitions in chain.transition_matrix.items():
            total_prob = sum(transitions.values())
            assert abs(total_prob - 1.0) < 1e-6, \
                f"Probabilities for {state} don't sum to 1: {total_prob}"
    
    def test_smoothing_prevents_zero_probabilities(self):
        """Verify smoothing ensures non-zero probabilities."""
        chain = MarkChain(order=1, smoothing=0.01)
        chain.train(["# Header\n\nText"])
        
        # Even unseen transitions should have small non-zero probability
        for state, transitions in chain.transition_matrix.items():
            assert all(p > 0 for p in transitions.values())
    
    @pytest.mark.parametrize("order", [1, 2, 3])
    def test_higher_order_chains(self, training_docs, order):
        """Test Markov chains of different orders."""
        chain = MarkChain(order=order, smoothing=0.01)
        chain.train(training_docs)
        
        assert chain.is_trained
        assert len(chain.transitions) > 0
```

### Integration Tests

Test component interactions and workflows.

**Example**: `test_integration.py`
```python
class TestDocumentOptimizationPipeline:
    """Integration tests for complete optimization workflow."""
    
    def test_end_to_end_optimization(self, sample_document):
        """Test complete optimization pipeline."""
        # Parse document
        doc = Document(content=sample_document)
        assert doc.is_valid()
        
        # Build state space
        state_space = StateSpace(doc)
        assert len(state_space.states) > 0
        
        # Initialize belief updater
        belief_updater = BeliefUpdater(
            semantic_classes=["instruction", "explanation", "example"]
        )
        
        # Optimize
        optimizer = PolicyOptimizer(
            state_space=state_space,
            belief_updater=belief_updater,
            max_iterations=50
        )
        result = optimizer.optimize()
        
        # Verify results
        assert result.convergence_achieved
        assert result.quality_improvement >= 0
        assert len(result.applied_transformations) > 0
        
        # Verify document is still valid after optimization
        optimized_doc = result.optimized_document
        assert optimized_doc.is_valid()
```

### Property-Based Tests

Test invariants and properties using Hypothesis.

**Example**: `test_property_based.py`
```python
from hypothesis import given, strategies as st

class TestPropertyBasedInvariants:
    """Property-based tests for system invariants."""
    
    @given(st.text(min_size=10, max_size=1000))
    def test_document_parsing_idempotent(self, markdown_text):
        """Parsing a document twice should yield same result."""
        doc1 = Document(content=markdown_text)
        doc2 = Document(content=markdown_text)
        
        assert doc1.states == doc2.states
        assert doc1.metadata == doc2.metadata
    
    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=2, max_size=10))
    def test_belief_normalization(self, probabilities):
        """Beliefs should always form valid probability distribution."""
        # Normalize input
        total = sum(probabilities)
        if total > 0:
            normalized = [p/total for p in probabilities]
            
            belief_updater = BeliefUpdater(
                semantic_classes=[f"class_{i}" for i in range(len(normalized))]
            )
            belief_updater.beliefs = dict(zip(belief_updater.semantic_classes, normalized))
            
            # Verify normalization
            total_belief = sum(belief_updater.beliefs.values())
            assert abs(total_belief - 1.0) < 1e-6
```

### Performance Tests

Benchmark critical operations.

**Example**: `test_performance.py`
```python
import pytest
import time

class TestPerformance:
    """Performance benchmarks for critical operations."""
    
    @pytest.mark.benchmark
    def test_state_space_construction_performance(self, large_document, benchmark):
        """Benchmark state space construction."""
        def construct_state_space():
            return StateSpace(large_document)
        
        result = benchmark(construct_state_space)
        assert len(result.states) > 0
    
    @pytest.mark.benchmark
    def test_optimization_convergence_time(self, complex_state_space, benchmark):
        """Benchmark optimization convergence time."""
        optimizer = PolicyOptimizer(
            state_space=complex_state_space,
            max_iterations=100
        )
        
        result = benchmark(optimizer.optimize)
        assert result.convergence_achieved
    
    @pytest.mark.timeout(5)
    def test_large_document_processing_within_time_limit(self, very_large_document):
        """Ensure large documents process within reasonable time."""
        start = time.time()
        
        doc = Document(content=very_large_document)
        state_space = StateSpace(doc)
        analysis = state_space.analyze_structure()
        
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Processing took {elapsed:.2f}s, should be <5s"
```

### Snapshot Tests

Ensure output consistency across changes.

**Example**: `test_snapshot.py`
```python
class TestSnapshotConsistency:
    """Snapshot tests for output consistency."""
    
    def test_state_space_serialization_snapshot(self, snapshot, sample_document):
        """Verify state space serialization remains consistent."""
        state_space = StateSpace(sample_document)
        serialized = state_space.to_dict()
        
        snapshot.assert_match(serialized, 'state_space_snapshot.json')
    
    def test_visualization_output_snapshot(self, snapshot, sample_state_space):
        """Verify visualization output remains consistent."""
        visualizer = DocumentVisualizer(sample_state_space)
        plot_data = visualizer.get_plot_data()
        
        snapshot.assert_match(plot_data, 'visualization_snapshot.json')
```

## Fixtures and Test Data

Reuse `sample_markdown` and `complex_markdown` for inline content. Use
`sample_document_file` or `complex_document_file` when an API takes a file
path. Keep fixtures specific to one module near their tests.

Readability tests need a prepared CMU pronunciation dictionary. The [test
setup](README.md#setup) uses CI's checksum-verified script and shows how to set
`NLTK_DATA` for the test run.

## Running Tests

Use the environment and corpus from the [test setup](README.md#setup). The
`pytest` commands below assume an activated environment. They also work with
`uv run --locked --no-sync` before `pytest`.

### Basic Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_markchain.py -v

# Run specific test
pytest tests/test_markchain.py::test_generate_and_analyze_samples -v

# Run with coverage
pytest tests/ --cov=src/mdp --cov-report=html --cov-report=term-missing

# Run the suite without benchmark timing
pytest tests/ -v --benchmark-disable

# Run only benchmarks
pytest tests/ -v --benchmark-only
```

### Advanced Test Options

```bash
# Run with detailed output
pytest tests/ -vv --tb=long

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

The coverage command above writes an HTML coverage report to `htmlcov/`.

## Writing Effective Tests

### Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected_result>

def test_markchain_training_with_empty_corpus_raises_error():
    """Test that training with empty corpus raises ValueError."""
    chain = MarkChain()
    with pytest.raises(ValueError, match="Corpus cannot be empty"):
        chain.train([])

def test_state_space_construction_from_valid_document_succeeds():
    """Test successful state space construction."""
    doc = Document(content="# Header\n\nParagraph")
    state_space = StateSpace(doc)
    assert len(state_space.states) > 0
```

### Assertion Best Practices

```python
# Use descriptive assertion messages
assert len(states) > 0, f"Expected non-empty states, got {len(states)}"

# Use pytest's rich assertion introspection
assert result == expected  # pytest will show diff automatically

# Use approximate equality for floats
import pytest
assert result == pytest.approx(expected, abs=1e-6)

# Use proper exception checking
with pytest.raises(ValueError, match="Invalid state"):
    invalid_operation()

# Check multiple conditions
assert all([
    result.is_valid(),
    result.quality_score > 0.5,
    len(result.transformations) > 0
]), "Result validation failed"
```

### Test Documentation

```python
def test_complex_scenario():
    """Test complex multi-step scenario.
    
    This test verifies that:
    1. Document parsing handles nested structures
    2. State space captures all hierarchical relationships
    3. Optimization preserves semantic meaning
    4. Output quality exceeds input quality
    
    The test uses a realistic technical document with:
    - Multiple heading levels (H1-H3)
    - Code blocks with syntax highlighting
    - Nested lists and tables
    - Cross-references and citations
    """
    # Test implementation
    pass
```

## Debugging Failed Tests

### Common Debugging Techniques

```bash
# Use pytest's debugging flag
pytest tests/test_markchain.py::test_generate_and_analyze_samples -vv --pdb
```

```python
# Add print statements (will show in -vv mode)
def test_something():
    result = function_under_test()
    print(f"DEBUG: result = {result}")  # Will show in verbose output
    assert result == expected

# Use logging for more control
import logging
logger = logging.getLogger(__name__)

def test_with_logging(caplog):
    with caplog.at_level(logging.DEBUG):
        result = function_under_test()
    
    # Check logs
    assert "Expected log message" in caplog.text
```

### Isolating Test Failures

```bash
pytest tests/test_markchain.py::test_generate_and_analyze_samples -vv --tb=long --showlocals
```

## Continuous Integration

The [test workflow](../.github/workflows/tests.yml) declares Python 3.11 and
3.15 on Ubuntu 24.04, macOS and Windows. Matrix jobs prepare the reviewed
readability data before running coverage and benchmarks. Linux on Python 3.11
also requires native Pandoc and PDF export checks. See the [GitHub Actions
workflow page](https://github.com/docxology/markdown_decision_process/actions/workflows/tests.yml)
for current enablement and run results.

## Test Maintenance

### Checking and Regenerating Snapshots

Run the snapshot tests from the repository root.

```bash
pytest tests/test_snapshot.py -q
```

To regenerate a snapshot, use a disposable checkout and move only the JSON file
you intend to refresh out of `tests/snapshots/`. For example, move
`tests/snapshots/normalize_headings.json` aside and run its test.

```bash
pytest tests/test_snapshot.py::TestDocumentTransformations::test_normalize_headings -q
```

The first run creates the missing snapshot and reports a skip. Review the new
JSON against the saved copy, then rerun the test to compare against the new
snapshot.

### Test Data Management

- Keep test fixtures minimal but realistic
- Version control small fixtures and baselines. Prepare the reviewed corpus through the test setup.
- Document test data sources
- Clean up generated test outputs

---

*Remember: Good tests are the belief updater for code correctness. They maintain our confidence (beliefs) that the system works as expected, even under partial observability (we can't test everything). Write tests that would make a POMDP proud!* 🧪

