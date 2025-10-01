#!/usr/bin/env python3
"""
Basic usage examples for the Markdown Decision Process framework.

This script demonstrates fundamental operations with MDP components.
"""

from mdp import Document, StateSpace, MarkChain, PolicyOptimizer, MarkdownAgent


def basic_document_operations():
    """Demonstrate basic Document operations."""
    print("=== Basic Document Operations ===")

    # Create document from content
    content = """# Sample Document

This is a sample document demonstrating basic MDP operations.

## Section 1: Introduction

This section introduces the concept with some example content.

## Section 2: Implementation

Here's how to implement the solution:

```python
def example_function():
    return "Hello, World!"
```

## Conclusion

This concludes our sample document.
"""

    doc = Document(content=content)
    print(f"Document created with {len(doc.get_structure())} elements")

    # Analyze structure
    structure = doc.get_structure()
    print(f"Structure types: {[elem['type'] for elem in structure]}")

    # Save document
    doc.save("sample_output.md")
    print("Document saved to sample_output.md")


def state_space_analysis():
    """Demonstrate StateSpace analysis."""
    print("\n=== State Space Analysis ===")

    content = """# Document Title

Introduction paragraph here.

## Section Header

Content in section.

- List item 1
- List item 2

```python
code = "example"
```

Another paragraph.
"""

    doc = Document(content=content)
    state_space = StateSpace(doc)

    print(f"State space has {len(state_space.graph.nodes)} nodes")
    print(f"State space has {len(state_space.graph.edges)} edges")

    # Get metadata for specific states
    for node_id in list(state_space.graph.nodes)[:3]:
        metadata = state_space.get_state_metadata(node_id)
        print(f"Node {node_id}: {metadata['type']}")


def markov_chain_generation():
    """Demonstrate MarkChain text generation."""
    print("\n=== Markov Chain Generation ===")

    # Training corpus
    corpus = """# Project Documentation

This project implements advanced algorithms.

## Features

- Fast processing
- Accurate results
- Easy integration

## Usage

```python
model = Algorithm()
results = model.process(data)
```

## Examples

The algorithm performs well on various datasets.
"""

    # Create and train chain
    chain = MarkChain(order=2)
    chain.train(corpus)
    print(f"Chain trained with {len(chain.states)} states")

    # Generate content
    prompt = "# New Project"
    generated = chain.generate(prompt, length=200)
    print(f"Generated content:\n{generated}")


def policy_optimization():
    """Demonstrate PolicyOptimizer document optimization."""
    print("\n=== Policy Optimization ===")

    content = """# Document

This is a very long paragraph that contains many words and should probably be broken up into smaller paragraphs for better readability and comprehension.

## Section

Short content here.
"""

    doc = Document(content=content)
    state_space = StateSpace(doc)

    # Define reward function
    def readability_reward(element):
        if element['type'] == 'paragraph':
            word_count = len(element['content'].split())
            if word_count > 50:
                return -1.0  # Penalize long paragraphs
            elif word_count > 20:
                return 1.0   # Reward good length
            else:
                return -0.5  # Penalize too short
        return 0.0

    # Optimize
    optimizer = PolicyOptimizer(state_space=state_space)
    optimizer.set_reward_function(readability_reward)

    result = optimizer.optimize(doc)
    print(f"Original length: {len(doc.content)}")
    print(f"Optimized length: {len(result['optimized_content'])}")
    print(f"Final reward: {result['final_reward']}")


def agent_interaction():
    """Demonstrate MarkdownAgent interactive processing."""
    print("\n=== Agent Interaction ===")

    content = """# Sample Document

This document needs improvement and optimization for better structure and readability.
"""

    agent = MarkdownAgent()

    # Analyze document
    analysis = agent.analyze(content)
    print(f"Document analysis: {analysis['semantic_analysis']['overall_semantic_class']}")

    # Optimize document
    result = agent.interact(content, objective="optimize")
    print(f"Optimization completed with {len(result['actions_taken'])} actions")
    print(f"Modified content length: {len(result['modified_content'])}")


def comprehensive_workflow():
    """Demonstrate complete MDP workflow."""
    print("\n=== Comprehensive Workflow ===")

    # 1. Create and analyze document
    doc = Document(content="# Workflow Demo\n\nSample content for demonstration.")
    print(f"Step 1: Created document with {len(doc.get_structure())} elements")

    # 2. Build state space
    state_space = StateSpace(doc)
    print(f"Step 2: Built state space with {len(state_space.graph.nodes)} nodes")

    # 3. Train generation model
    chain = MarkChain()
    chain.train(doc.content)
    print(f"Step 3: Trained MarkChain with {len(chain.states)} states")

    # 4. Optimize content
    def simple_reward(element):
        return 1.0 if element['type'] in ['header', 'paragraph'] else 0.5

    optimizer = PolicyOptimizer(state_space=state_space)
    optimizer.set_reward_function(simple_reward)

    result = optimizer.optimize(doc)
    print(f"Step 4: Optimized document (reward: {result['final_reward']})")

    # 5. Generate additional content
    extended = chain.generate("# Additional Section", length=150)
    print(f"Step 5: Generated {len(extended)} characters of new content")

    print("Workflow completed successfully!")


if __name__ == "__main__":
    basic_document_operations()
    state_space_analysis()
    markov_chain_generation()
    policy_optimization()
    agent_interaction()
    comprehensive_workflow()


