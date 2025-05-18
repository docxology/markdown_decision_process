#!/usr/bin/env python3
"""
Debug script to test filter functions on MarkChain states.
"""

import sys
from pathlib import Path
import re

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import MarkChain

def main():
    """Debug the filter functions on MarkChain states."""
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
    
    # Print all states
    print("\nAll states:")
    for i, state in enumerate(model.transitions.keys()):
        print(f"{i+1}. {repr(state)}")
    
    print("\nTesting different filters:")
    
    # Define filter functions
    def header_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return state[0].startswith('#')
        return False
    
    def list_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0].strip()
            return text.startswith(('-', '*', '1.', '2.', '3.'))
        return False
    
    def code_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            text = state[0]
            return '```' in text or text.strip() in ['def', 'class', 'return', 'import']
        return False
    
    def link_filter(state):
        if isinstance(state, tuple) and len(state) == 1:
            return bool(re.search(r'\[.*?\]', state[0]))
        return False
    
    # Test each filter on each state
    filters = {
        "Header filter": header_filter,
        "List filter": list_filter,
        "Code filter": code_filter,
        "Link filter": link_filter
    }
    
    for filter_name, filter_func in filters.items():
        print(f"\n{filter_name} results:")
        matches = []
        for state in model.transitions.keys():
            if filter_func(state):
                matches.append(state)
        
        print(f"Matched {len(matches)} states:")
        for match in matches:
            print(f"  {repr(match)}")
    
    # Print some debug info about the first state with # to understand why it's not matching
    for state in model.transitions.keys():
        if isinstance(state, tuple) and len(state) == 1 and '#' in state[0]:
            print(f"\nDebug info for state with '#': {repr(state)}")
            print(f"Type: {type(state)}")
            print(f"Length of tuple: {len(state)}")
            print(f"First element type: {type(state[0])}")
            print(f"First element: {repr(state[0])}")
            print(f"Starts with #: {state[0].startswith('#')}")
            print(f"First few characters: {repr(state[0][:10])}")
            # Check the unicode values of the first few characters
            print(f"Unicode values: {[ord(c) for c in state[0][:10]]}")
            break

if __name__ == "__main__":
    main() 