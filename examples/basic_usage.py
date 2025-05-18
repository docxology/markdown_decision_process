#!/usr/bin/env python3
"""
Basic usage examples for the Markdown Decision Process package.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import MarkChain, PolicyOptimizer, StateSpace, BeliefUpdater

def generate_markdown_example():
    """Example of generating markdown using MarkChain."""
    print("\n=== MarkChain Example ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Create a simple markdown sample to train on
    sample = """# Sample Document
    
This is a paragraph with some text. It demonstrates the basic structure of a markdown document.

## Section 1

- List item 1
- List item 2
- List item 3

Here's some code:

```python
def hello_world():
    print("Hello, world!")
```

## Section 2

This is another paragraph with different content.

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3
    """
    
    # Save the sample to a file
    sample_path = output_dir / "sample.md"
    with open(sample_path, "w") as f:
        f.write(sample)
    
    # Create and train a MarkChain model
    model = MarkChain(order=1)
    model.train(sample)
    
    # Generate new markdown
    generated = model.sample(length=15)
    print("\nGenerated Markdown:")
    print(generated)
    
    print(f"\nSample saved to: {sample_path}")
    print("\nYou can also train on multiple files:")
    print("model = MarkChain.from_corpus('path/to/docs/')")
    

def optimize_markdown_example():
    """Example of optimizing markdown using PolicyOptimizer."""
    print("\n=== PolicyOptimizer Example ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Create a sample to optimize
    sample = """# Unoptimized Document
    
This paragraph is very long and contains a lot of text without much structure. It goes on and on without giving the reader any breaks or clear organization. It mentions several different topics like installation, usage, and configuration all in one big block of text, which makes it hard to follow. Some readers will find this confusing because the information is all mixed together without clear separation between different ideas.

## Usage

Run the program and follow instructions.

## Reference

The API methods are: load(), save(), process(), analyze(), and export().
    """
    
    # Save the sample to a file
    unoptimized_path = output_dir / "unoptimized.md"
    with open(unoptimized_path, "w") as f:
        f.write(sample)
    
    # Create a PolicyOptimizer with custom weights
    optimizer = PolicyOptimizer(
        reward_weights={
            "readability": 0.8,
            "structure_clarity": 0.7,
            "information_density": 0.4
        }
    )
    
    # Optimize the document
    optimized = optimizer.transform(str(unoptimized_path))
    
    # Save the optimized version
    optimized_path = output_dir / "optimized.md"
    with open(optimized_path, "w") as f:
        f.write(optimized)
    
    print(f"\nOriginal document saved to '{unoptimized_path}'")
    print(f"Optimized document saved to '{optimized_path}'")
    print("\nThe optimizer breaks up long paragraphs, adds headers where needed,")
    print("and converts text to lists when appropriate.")


def visualize_state_space_example():
    """Example of visualizing markdown state space."""
    print("\n=== StateSpace Example ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    sample_path = output_dir / "sample.md"
    optimized_path = output_dir / "optimized.md"
    
    # Check if we have sample files
    if not sample_path.exists() or not optimized_path.exists():
        print("Please run the other examples first to generate sample files.")
        return
    
    # Create a StateSpace visualizer
    visualizer = StateSpace(simplify_states=True)
    
    # Analyze the markdown files
    visualizer.analyze(str(sample_path))
    visualizer.analyze(str(optimized_path))
    
    # Print statistics
    visualizer.print_statistics()
    
    # Generate visualization
    state_space_path = output_dir / "markdown_state_space.png"
    visualizer.visualize(str(state_space_path))
    
    print(f"\nState space visualization saved to '{state_space_path}'")


def analyze_semantics_example():
    """Example of analyzing markdown semantics using BeliefUpdater."""
    print("\n=== BeliefUpdater Example ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Create a sample with mixed semantic content
    sample = """# Installation Guide
    
Follow these steps to install the software:

1. Download the package
2. Run the installer
3. Configure settings

## Warning

**Important**: Make sure you backup your data before proceeding!

## Example Usage

Here's an example of how to use the API:

```python
from package import Client

client = Client()
client.connect()
result = client.query("data")
```

## Reference

For more information, see the [documentation](https://example.com/docs).
    """
    
    # Save the sample to a file
    semantic_path = output_dir / "semantic_sample.md"
    with open(semantic_path, "w") as f:
        f.write(sample)
    
    # Create a BeliefUpdater
    belief_updater = BeliefUpdater()
    
    # Analyze the document
    analysis = belief_updater.analyze_document_file(str(semantic_path))
    
    # Print the analysis
    belief_updater.print_analysis(analysis)
    
    print(f"\nSemantic sample saved to: {semantic_path}")
    print("The BeliefUpdater infers the semantic intent of different")
    print("sections in your markdown, accounting for uncertainty.")


def main():
    """Run the examples."""
    parser = argparse.ArgumentParser(description="MDP Examples")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--generate", action="store_true", help="Run MarkChain example")
    parser.add_argument("--optimize", action="store_true", help="Run PolicyOptimizer example")
    parser.add_argument("--visualize", action="store_true", help="Run StateSpace example")
    parser.add_argument("--analyze", action="store_true", help="Run BeliefUpdater example")
    
    args = parser.parse_args()
    
    # If no args or --all, run everything
    run_all = args.all or not (args.generate or args.optimize or args.visualize or args.analyze)
    
    if args.generate or run_all:
        generate_markdown_example()
        
    if args.optimize or run_all:
        optimize_markdown_example()
        
    if args.visualize or run_all:
        visualize_state_space_example()
        
    if args.analyze or run_all:
        analyze_semantics_example()


if __name__ == "__main__":
    main() 