#!/usr/bin/env python3
"""
Example: Creating comprehensive animations of markdown document analysis.

This demonstrates the thin orchestrator pattern where simple function calls
coordinate complex visualizations across multiple components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdp import (
    Document,
    StateSpace,
    MarkChain,
    BeliefUpdater,
    DocumentEvolutionAnimator,
    StateSpaceEvolutionAnimator,
    MarkChainGenerationAnimator,
    BeliefStateAnimator,
    create_comprehensive_animation
)
from mdp.transformations import (
    HeadingLevelTransformation,
    ListFormatTransformation,
    TransformationPipeline
)


def example_document_transformation_animation():
    """Create an animation showing document transformations."""
    print("Creating document transformation animation...")
    
    # Create sample document
    sample_md = """# Original Document

This is the first paragraph with some content.

## Section 1
- Item 1
- Item 2
- Item 3

Some more text here.

### Subsection
More detailed content.
"""
    
    doc = Document(content=sample_md)
    
    # Create animator
    animator = DocumentEvolutionAnimator(figsize=(16, 10))
    
    # Apply transformations and record each step
    transformations = [
        ('Original', None),
        ('Heading Level +1', HeadingLevelTransformation(increment=1)),
        ('Lists to Unordered', ListFormatTransformation(target_type="unordered", bullet_style="-"))
    ]
    
    current_doc = doc
    for name, transform in transformations:
        if transform is None:
            # Initial state
            animator.add_transformation_step(
                current_doc,
                current_doc,
                name,
                current_doc.evaluate_metrics()
            )
        else:
            # Apply transformation
            before = current_doc
            after = Document(content=current_doc.get_content())
            transform.apply(after, None)
            
            animator.add_transformation_step(
                before,
                after,
                name,
                after.evaluate_metrics()
            )
            current_doc = after
    
    # Create animation
    output_path = "examples/visualization_output/document_transformation.gif"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    animator.create_animation(output_path, fps=0.5)
    print(f"✓ Created: {output_path}")


def example_state_space_evolution():
    """Create an animation showing state space evolution."""
    print("\nCreating state space evolution animation...")
    
    # Sample markdown with increasing complexity
    chunks = [
        "# Document Title",
        "# Document Title\n\nIntroduction paragraph.",
        "# Document Title\n\nIntroduction paragraph.\n\n## Section 1",
        "# Document Title\n\nIntroduction paragraph.\n\n## Section 1\n\n- Point 1\n- Point 2",
        "# Document Title\n\nIntroduction paragraph.\n\n## Section 1\n\n- Point 1\n- Point 2\n\n```python\ndef hello():\n    return 'world'\n```"
    ]
    
    animator = StateSpaceEvolutionAnimator(figsize=(14, 8))
    
    for i, chunk in enumerate(chunks):
        ss = StateSpace()
        ss.parse_markdown(chunk)
        animator.add_snapshot(ss, f"Stage {i+1}")
    
    output_path = "examples/visualization_output/state_space_evolution.gif"
    animator.create_animation(output_path, fps=1)
    print(f"✓ Created: {output_path}")


def example_markov_generation():
    """Create an animation of Markov chain generation."""
    print("\nCreating Markov chain generation animation...")
    
    # Train on sample markdown
    training_data = """# Introduction

This is a paragraph about the topic.

## Background

Some background information here.

### Details

More specific details.

## Implementation

Implementation details go here.

```python
def example():
    pass
```

## Conclusion

Final thoughts and summary.
"""
    
    chain = MarkChain()
    chain.train(training_data)
    
    animator = MarkChainGenerationAnimator(chain, figsize=(14, 10))
    
    output_path = "examples/visualization_output/markov_generation.gif"
    animator.animate_generation(output_path, steps=8, fps=0.5)
    print(f"✓ Created: {output_path}")


def example_belief_evolution():
    """Create an animation of belief state evolution."""
    print("\nCreating belief state evolution animation...")
    
    updater = BeliefUpdater(
        semantic_classes=["tutorial", "reference", "explanation", "example"],
        noise_factor=0.1
    )
    
    animator = BeliefStateAnimator(updater, figsize=(12, 8))
    
    # Simulate observations from document analysis
    observations = [
        ({'structure': 0.3, 'readability': 0.5, 'complexity': 0.2}, "Introduction"),
        ({'structure': 0.6, 'readability': 0.7, 'complexity': 0.4}, "Main Content"),
        ({'structure': 0.8, 'readability': 0.8, 'complexity': 0.6}, "Examples"),
        ({'structure': 0.9, 'readability': 0.9, 'complexity': 0.7}, "Conclusion")
    ]
    
    for obs, label in observations:
        animator.add_observation(obs, label)
    
    output_path = "examples/visualization_output/belief_evolution.gif"
    animator.create_animation(output_path, fps=1)
    print(f"✓ Created: {output_path}")


def example_comprehensive_animation():
    """Use the thin orchestrator to create all animations at once."""
    print("\nCreating comprehensive animation suite...")
    
    # Use an existing sample document
    sample_doc_path = "examples/sample_docs/technical_doc.md"
    
    if not Path(sample_doc_path).exists():
        print(f"⚠ Sample document not found: {sample_doc_path}")
        print("  Creating a temporary document instead...")
        
        # Create a temp document
        temp_path = "examples/sample_docs/temp_doc.md"
        Path(temp_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, 'w') as f:
            f.write("""# Technical Documentation

## Overview

This document provides technical details about the system.

### Architecture

The architecture consists of several components:

- Component A
- Component B
- Component C

### Implementation

Here's a code example:

```python
def process_data(input_data):
    # Process the input
    result = transform(input_data)
    return result
```

## Usage

To use the system, follow these steps:

1. Install dependencies
2. Configure settings
3. Run the application

## Troubleshooting

Common issues and solutions.
""")
        sample_doc_path = temp_path
    
    output_dir = "examples/visualization_output/comprehensive"
    outputs = create_comprehensive_animation(sample_doc_path, output_dir)
    
    print(f"\n✓ Created comprehensive animation suite in {output_dir}:")
    for anim_type, path in outputs.items():
        print(f"  - {anim_type}: {path}")


def main():
    """Run all animation examples."""
    print("=" * 70)
    print("MARKDOWN DECISION PROCESS - ANIMATION EXAMPLES")
    print("=" * 70)
    print()
    print("This demonstrates thin orchestrators that create vast visualizations")
    print("by coordinating Document, StateSpace, MarkChain, and BeliefUpdater.")
    print()
    
    try:
        example_document_transformation_animation()
        example_state_space_evolution()
        example_markov_generation()
        example_belief_evolution()
        example_comprehensive_animation()
        
        print()
        print("=" * 70)
        print("✅ ALL ANIMATIONS CREATED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("View animations in: examples/visualization_output/")
        print()
        
    except Exception as e:
        print(f"\n❌ Error creating animations: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


