#!/usr/bin/env python3
"""
Debug script to investigate the state structure in MarkChain.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import MarkChain

def main():
    """Debug the MarkChain state structure."""
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
    
    # Print information about the trained chain
    print(f"Number of states: {len(model.transitions)}")
    
    print("\nFirst 10 states (type and value):")
    for i, state in enumerate(list(model.transitions.keys())[:10]):
        print(f"{i+1}. Type: {type(state)}, Value: {repr(state)}")
    
    print("\nTransition dictionary structure:")
    first_state = next(iter(model.transitions.keys()))
    print(f"First state type: {type(first_state)}")
    print(f"First state: {repr(first_state)}")
    
    transitions = model.transitions[first_state]
    print(f"Transitions type: {type(transitions)}")
    print(f"Number of transitions: {len(transitions)}")
    
    if transitions:
        first_target = next(iter(transitions.keys()))
        print(f"First target state type: {type(first_target)}")
        print(f"First target state: {repr(first_target)}")
        print(f"Transition probability: {transitions[first_target]}")
    
    print("\nFilter function test:")
    
    # Test different filter approaches
    print("\nTesting with string starts with filter:")
    hash_prefix_count = sum(1 for state in model.transitions if str(state).startswith('#'))
    print(f"States starting with '#': {hash_prefix_count}")
    
    print("\nTesting with string contains filter:")
    code_block_count = sum(1 for state in model.transitions if '```' in str(state))
    print(f"States containing '```': {code_block_count}")
    
    print("\nTesting with string regex filter:")
    import re
    link_count = sum(1 for state in model.transitions if re.search(r'\[.*?\]', str(state)))
    print(f"States containing link syntax: {link_count}")
    
    # Check if any states match our filters
    if hash_prefix_count > 0:
        print("\nExample of a state with '#':")
        for state in model.transitions:
            if str(state).startswith('#'):
                print(f"  {repr(state)}")
                break
    
    if code_block_count > 0:
        print("\nExample of a state with '```':")
        for state in model.transitions:
            if '```' in str(state):
                print(f"  {repr(state)}")
                break
    
    if link_count > 0:
        print("\nExample of a state with link syntax:")
        for state in model.transitions:
            if re.search(r'\[.*?\]', str(state)):
                print(f"  {repr(state)}")
                break

if __name__ == "__main__":
    main() 