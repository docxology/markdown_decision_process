#!/usr/bin/env python3
"""
Advanced usage examples for the Markdown Decision Process framework.

This script demonstrates sophisticated applications and custom configurations.
"""

import tempfile
from pathlib import Path
from mdp import (
    Document, StateSpace, MarkChain, PolicyOptimizer,
    MarkdownAgent, BeliefUpdater, TransformationPipeline,
    HeadingLevelTransformation, ListFormatTransformation
)


def custom_reward_functions():
    """Demonstrate custom reward function design."""
    print("=== Custom Reward Functions ===")

    content = """# Technical Documentation

This is a comprehensive guide to the system.

## Architecture Overview

The system consists of multiple components working together.

### Core Components

- Component A: Handles data processing
- Component B: Manages user interfaces
- Component C: Provides API endpoints

## Implementation Details

The implementation requires careful consideration of:

1. Performance optimization
2. Security considerations
3. Scalability requirements

```python
class System:
    def __init__(self):
        self.components = []
```

## Best Practices

Always follow these guidelines when using the system.
"""

    doc = Document(content=content)
    state_space = StateSpace(doc)

    # Custom reward functions
    def structure_reward(element):
        """Reward good document structure."""
        if element['type'] == 'header':
            # Higher reward for appropriate header levels
            level = element.get('level', 1)
            return 2.0 / level
        elif element['type'] == 'list':
            # Reward lists with good item counts
            item_count = element.get('item_count', 0)
            if 2 <= item_count <= 8:
                return 1.5
            return 0.5
        elif element['type'] == 'code':
            # Reward code blocks with language specification
            return 2.0 if element.get('language') else 1.0
        return 0.0

    def quality_reward(element):
        """Reward high-quality content indicators."""
        if element['type'] == 'paragraph':
            content = element['content']
            word_count = len(content.split())

            # Reward appropriate length
            if 30 <= word_count <= 100:
                return 1.0

            # Penalize extremes
            if word_count > 150 or word_count < 15:
                return -0.5

        return 0.0

    def combined_reward(element):
        """Combine multiple reward aspects."""
        return structure_reward(element) + quality_reward(element)

    # Test different optimizers
    optimizers = {
        'structure': PolicyOptimizer(state_space=state_space),
        'quality': PolicyOptimizer(state_space=state_space),
        'combined': PolicyOptimizer(state_space=state_space)
    }

    optimizers['structure'].set_reward_function(structure_reward)
    optimizers['quality'].set_reward_function(quality_reward)
    optimizers['combined'].set_reward_function(combined_reward)

    # Optimize and compare
    results = {}
    for name, optimizer in optimizers.items():
        result = optimizer.optimize(doc)
        results[name] = result['final_reward']
        print(f"{name.capitalize()} reward: {result['final_reward']}")

    best_approach = max(results, key=results.get)
    print(f"Best approach: {best_approach}")


def transformation_pipeline():
    """Demonstrate transformation pipeline usage."""
    print("\n=== Transformation Pipeline ===")

    content = """# original-title

This is some content.

## section-one

- item one
- item two
- item three

### subsection

More content here.
"""

    doc = Document(content=content)

    # Create transformation pipeline
    pipeline = TransformationPipeline([
        HeadingLevelTransformation(increment=1),  # Increase all heading levels
        ListFormatTransformation("ordered")      # Convert to ordered lists
    ])

    # Apply transformations
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pipeline.apply(doc, tmp_path)
        transformed_doc = Document(file_path=tmp_path)

        print("Original content:")
        print(content)
        print("\nTransformed content:")
        print(transformed_doc.content)
    finally:
        Path(tmp_path).unlink()


def belief_based_optimization():
    """Demonstrate belief-updater guided optimization."""
    print("\n=== Belief-Based Optimization ===")

    content = """# User Guide

This guide helps users understand the system.

## Getting Started

Follow these steps to begin.

## Troubleshooting

If you encounter issues, check the logs.
"""

    doc = Document(content=content)
    state_space = StateSpace(doc)

    # Set up belief tracking
    updater = BeliefUpdater([
        "instruction", "reference", "example", "troubleshooting"
    ])

    # Simulate reading through document
    structure = doc.get_structure()

    for element in structure:
        if element['type'] == 'header':
            # Headers provide context clues
            title = element['content'].lower()
            if 'guide' in title or 'getting started' in title:
                updater.update_from_observation({"instruction": 0.8, "reference": 0.2})
            elif 'troubleshoot' in title:
                updater.update_from_observation({"troubleshooting": 0.7, "reference": 0.3})

    beliefs = updater.get_all_beliefs()
    print(f"Document beliefs: {beliefs}")

    # Use beliefs to inform reward function
    def contextual_reward(element):
        if beliefs.get("instruction", 0) > 0.5:
            if element['type'] == 'paragraph':
                return 1.5  # Favor instructional content
        elif beliefs.get("troubleshooting", 0) > 0.5:
            if element['type'] == 'list':
                return 1.5  # Favor step-by-step troubleshooting

        return 0.5  # Default reward

    optimizer = PolicyOptimizer(state_space=state_space)
    optimizer.set_reward_function(contextual_reward)

    result = optimizer.optimize(doc)
    print(f"Contextual optimization reward: {result['final_reward']}")


def agent_training_and_generation():
    """Demonstrate agent training and autonomous operation."""
    print("\n=== Agent Training and Generation ===")

    # Training corpus
    corpus = """
# API Reference

This API provides programmatic access to the system.

## Authentication

Use API keys for authentication.

## Endpoints

### GET /api/data

Retrieve data from the system.

### POST /api/data

Submit new data to the system.

## Examples

```python
import requests

response = requests.get('/api/data')
data = response.json()
```

## Error Handling

Handle errors appropriately in your code.
"""

    agent = MarkdownAgent()

    # Train agent
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
        tmp.write(corpus)
        corpus_path = tmp.name

    try:
        training_stats = agent.train(corpus_path, iterations=20)
        print(f"Agent trained: {training_stats}")
    finally:
        Path(corpus_path).unlink()

    # Autonomous operation
    objectives = ["optimize", "extend", "summarize"]

    for objective in objectives:
        print(f"\n--- {objective.capitalize()} ---")

        if objective == "extend":
            # Extend with generated content
            result = agent.interact("# New API Endpoint", objective=objective)
        else:
            result = agent.interact(corpus, objective=objective)

        print(f"Actions taken: {len(result['actions_taken'])}")
        print(f"Content length: {len(result['modified_content'])}")


def performance_comparison():
    """Compare different MDP approaches."""
    print("\n=== Performance Comparison ===")

    # Test document
    test_content = """# Performance Test

This document tests different optimization approaches.

## Test Section

Content for testing purposes.

- Test item 1
- Test item 2

```python
def test_function():
    return "test"
```
"""

    doc = Document(content=test_content)
    state_space = StateSpace(doc)

    # Different optimization strategies
    strategies = {
        'structure_focused': lambda e: 2.0 if e['type'] == 'header' else 0.5,
        'content_focused': lambda e: 1.0 if e['type'] == 'paragraph' else 0.2,
        'balanced': lambda e: 1.0  # Simple baseline
    }

    results = {}

    for name, reward_fn in strategies.items():
        optimizer = PolicyOptimizer(state_space=state_space)
        optimizer.set_reward_function(reward_fn)

        result = optimizer.optimize(doc)
        results[name] = result['final_reward']

    print("Strategy comparison:")
    for strategy, reward in results.items():
        print(f"  {strategy}: {reward}")

    best_strategy = max(results, key=results.get)
    print(f"Best performing strategy: {best_strategy}")


def multi_document_processing():
    """Process multiple documents with consistency."""
    print("\n=== Multi-Document Processing ===")

    # Sample documents
    documents = [
        "# Document 1\n\nContent of document 1.",
        "# Document 2\n\nContent of document 2.",
        "# Document 3\n\nContent of document 3."
    ]

    # Build shared state space
    state_space = StateSpace()

    for content in documents:
        doc = Document(content=content)
        state_space.analyze(doc.file_path if hasattr(doc, 'file_path') and doc.file_path else None)

    print(f"Shared state space: {len(state_space.graph.nodes)} nodes")

    # Train shared generation model
    chain = MarkChain()
    combined_content = "\n\n".join(documents)
    chain.train(combined_content)

    # Generate consistent content across documents
    for i, doc_content in enumerate(documents, 1):
        extended = chain.generate(f"# Document {i} Extension", length=100)
        print(f"\nDocument {i} extension length: {len(extended)}")


def custom_state_analysis():
    """Demonstrate custom state analysis."""
    print("\n=== Custom State Analysis ===")

    content = """# Research Paper

## Abstract

This paper presents novel findings.

## Methodology

We used advanced techniques.

### Data Collection

- Collected data from multiple sources
- Applied rigorous validation

### Analysis

```python
import pandas as pd
df = pd.read_csv('data.csv')
results = df.analyze()
```

## Results

The results show significant improvements.

## Conclusion

This concludes our research.
"""

    doc = Document(content=content)
    state_space = StateSpace(doc)

    # Custom analysis functions
    def get_section_depths():
        """Get depth of each section."""
        depths = {}
        for node_id in state_space.graph.nodes:
            metadata = state_space.get_state_metadata(node_id)
            if metadata['type'] == 'header':
                depths[node_id] = metadata.get('level', 1)
        return depths

    def get_content_richness():
        """Calculate content richness by type."""
        richness = {}
        for node_id in state_space.graph.nodes:
            metadata = state_space.get_state_metadata(node_id)
            elem_type = metadata['type']

            if elem_type not in richness:
                richness[elem_type] = 0

            # Simple richness metric
            if elem_type == 'paragraph':
                word_count = len(metadata.get('content', '').split())
                richness[elem_type] += min(word_count / 100, 1.0)  # Normalize
            elif elem_type == 'code':
                richness[elem_type] += 1.0  # Code blocks add richness
            elif elem_type == 'list':
                item_count = metadata.get('item_count', 0)
                richness[elem_type] += min(item_count / 5, 1.0)  # Normalize

        return richness

    depths = get_section_depths()
    richness = get_content_richness()

    print(f"Section depths: {depths}")
    print(f"Content richness: {richness}")

    # Use in optimization
    def richness_reward(element):
        elem_type = element['type']
        base_reward = richness.get(elem_type, 0.5)

        # Boost reward for rich content types
        if elem_type in ['code', 'list']:
            return base_reward * 1.5
        return base_reward

    optimizer = PolicyOptimizer(state_space=state_space)
    optimizer.set_reward_function(richness_reward)

    result = optimizer.optimize(doc)
    print(f"Richness-optimized reward: {result['final_reward']}")


def error_handling_and_recovery():
    """Demonstrate robust error handling."""
    print("\n=== Error Handling and Recovery ===")

    # Test with various edge cases
    test_cases = [
        ("Empty document", ""),
        ("Single header", "# Header"),
        ("Malformed content", "# Header\n\n[unclosed link"),
        ("Very long content", "# Doc\n\n" + "Word " * 1000),
    ]

    for name, content in test_cases:
        print(f"\nTesting: {name}")

        try:
            if content.strip():  # Skip truly empty content
                doc = Document(content=content)
                state_space = StateSpace(doc)

                # Try basic operations
                structure = doc.get_structure()
                print(f"  ✓ Parsed {len(structure)} elements")

                if len(state_space.graph.nodes) > 0:
                    print(f"  ✓ Built state space with {len(state_space.graph.nodes)} nodes")

                    # Try optimization
                    optimizer = PolicyOptimizer(state_space=state_space)
                    def simple_reward(e):
                        return 0.5  # Neutral reward

                    optimizer.set_reward_function(simple_reward)
                    result = optimizer.optimize(doc)
                    print(f"  ✓ Optimized successfully (reward: {result['final_reward']})")
                else:
                    print("  ⚠ No states found (expected for simple documents)"
            else:
                print("  ⚠ Empty content (expected)")

        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")


def main():
    """Run all advanced examples."""
    custom_reward_functions()
    transformation_pipeline()
    belief_based_optimization()
    agent_training_and_generation()
    performance_comparison()
    multi_document_processing()
    custom_state_analysis()
    error_handling_and_recovery()


if __name__ == "__main__":
    main()


