#!/usr/bin/env python3
"""
Example demonstrating the dynamic filtering of state space visualization.
"""

import os
import sys
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import re

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import MarkChain, plot_filtered_state_space

def main():
    """Run the filtered visualization example."""
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    # Create a sample markdown document to analyze
    sample = """# Dynamic Filtering Example

## Headings and Structure

This example demonstrates filtering the state space visualization based on different criteria.

### Headers are Important

Headers create the structure of your document.

## Lists and Code

- Item 1
- Item 2
- Item 3

Code examples:

```python
def example():
    return "This is code"
```

## Links and References

Check out [this link](https://example.com) for more information.

You can also refer to [internal sections](#headings-and-structure).

## Images and Tables

Images enhance content:

![Example image](example.jpg)

Tables organize data:

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
"""

    # Create and train a MarkChain model
    model = MarkChain(order=1)
    model.train(sample)
    
    # Print debug info
    print("Trained model with states: ")
    for i, state in enumerate(list(model.transitions.keys())[:5]):
        print(f"  {i+1}. {repr(state)}")
    print("  ...")
    
    # Example 1: Filter by headers only
    def header_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return state[0].startswith('#')
        return False
    
    fig = plot_filtered_state_space(
        model,
        filter_func=header_filter,
        figsize=(10, 8)
    )
    
    # Save the figure
    fig_path = output_dir / "filtered_headers.png"
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"Saved header-filtered visualization to {fig_path}")
    
    # Example 2: Filter by lists and highlight bullet lists
    def list_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0].strip()
            return text.startswith(('-', '*', '1.', '2.', '3.'))
        return False
    
    def bullet_highlight(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0].strip()
            return text.startswith(('-', '*'))
        return False
    
    fig = plot_filtered_state_space(
        model,
        filter_func=list_filter,
        highlight_func=bullet_highlight,
        figsize=(10, 8)
    )
    
    # Save the figure
    fig_path = output_dir / "filtered_lists.png"
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"Saved list-filtered visualization to {fig_path}")
    
    # Example 3: Filter by code-related states and highlight python code
    def code_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0]
            return '```' in text or text.strip() in ['def', 'class', 'return', 'import']
        return False
    
    def python_highlight(state):
        if isinstance(state, tuple) and len(state) == 1:
            return 'python' in state[0].lower()
        return False
    
    fig = plot_filtered_state_space(
        model,
        filter_func=code_filter,
        highlight_func=python_highlight,
        figsize=(10, 8)
    )
    
    # Save the figure
    fig_path = output_dir / "filtered_code.png"
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"Saved code-filtered visualization to {fig_path}")
    
    # Example 4: Advanced filtering with regex
    # Find states containing links or references
    def link_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return bool(re.search(r'\[.*?\]', state[0]))
        return False
    
    def external_link_highlight(state):
        if isinstance(state, tuple) and len(state) == 1:
            return bool(re.search(r'\[.*?\]\(https?://', state[0]))
        return False
    
    fig = plot_filtered_state_space(
        model,
        filter_func=link_filter,
        highlight_func=external_link_highlight,
        figsize=(10, 8)
    )
    
    # Save the figure
    fig_path = output_dir / "filtered_links.png"
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"Saved link-filtered visualization to {fig_path}")
    
    # Example 5: Combining multiple document samples
    # Create another sample with different characteristics
    technical_sample = """# Technical Documentation

## Installation

To install the package:

```bash
pip install markdown-decision-process
```

## API Reference

### `MarkChain` Class

The `MarkChain` class implements variable-order Markov models.

```python
from mdp import MarkChain

model = MarkChain(order=2)
model.train("your markdown here")
```

## Command Line Usage

Run the tool from the command line:

```
mdp optimize input.md --output optimized.md
```

See the [full documentation](https://mdp.example.com/docs) for more information.
"""
    
    # Train on the new sample as well
    model.train(technical_sample)
    
    # Example 6: Filter to show only code blocks across multiple documents
    def code_block_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return state[0].strip().startswith('```')
        return False
    
    def language_highlight(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0].strip()
            return text.startswith('```') and len(text) > 3
        return False
    
    fig = plot_filtered_state_space(
        model,
        filter_func=code_block_filter,
        highlight_func=language_highlight,
        figsize=(12, 10),
        node_size_factor=1500,
        edge_width_factor=5
    )
    
    # Save the figure
    fig_path = output_dir / "filtered_code_blocks.png"
    fig.savefig(fig_path)
    plt.close(fig)
    print(f"Saved code block visualization to {fig_path}")
    
    print("\nAll examples complete. The filtered visualizations demonstrate")
    print("how to focus on specific aspects of the document state space.")
    print("This enables deeper analysis of document structure and transitions.")

if __name__ == "__main__":
    main() 