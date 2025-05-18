#!/usr/bin/env python3
"""
Simple test for the filtered state space visualization.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import MarkChain, plot_filtered_state_space

def main():
    """Test the filtered state space visualization with a simple example."""
    print("Creating and training a MarkChain model...")
    
    # Create a sample markdown document to analyze
    sample = """# Sample Document
    
This is a paragraph with some text.

## Section 1

- Item 1
- Item 2

```python
def hello():
    print("Hello")
```

## Section 2

Check out [this link](https://example.com).
"""
    
    # Create and train a MarkChain model
    model = MarkChain(order=1)
    model.train(sample)
    
    # Define header filter
    def header_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return state[0].startswith('#')
        return False
    
    # Test the filter first to confirm it works
    headers = [state for state in model.transitions if header_filter(state)]
    print(f"Found {len(headers)} header states:")
    for header in headers:
        print(f"  {repr(header)}")
    
    # Plot the filtered state space
    print("\nCreating visualization...")
    
    try:
        fig = plot_filtered_state_space(
            model,
            filter_func=header_filter,
            figsize=(10, 8)
        )
        
        # Save the figure
        output_dir = Path(__file__).parent / "visualization_output"
        output_dir.mkdir(exist_ok=True)
        fig_path = output_dir / "simple_headers.png"
        fig.savefig(fig_path)
        plt.close(fig)
        print(f"Saved visualization to {fig_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 