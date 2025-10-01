"""
MarkChain: A Markov chain implementation for markdown state transitions.
"""

import re
import random
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from collections import Counter, defaultdict
from pathlib import Path


def default_state_parser(markdown_text: str) -> List[str]:
    """
    Parse markdown into states (elements).
    
    Args:
        markdown_text: Raw markdown content
        
    Returns:
        List of markdown states/elements
    """
    states = []
    lines = markdown_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Headers
        if line.startswith('#'):
            states.append(line)
            i += 1
            
        # Code blocks
        elif line.startswith('```'):
            code_block = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_block.append(lines[i])
                i += 1
            if i < len(lines):
                code_block.append(lines[i])
                i += 1
            states.append('\n'.join(code_block))
            
        # Lists
        elif line.startswith(('-', '*', '+')):
            states.append(line)
            i += 1
            
        # Numbered lists
        elif re.match(r'^\d+\.', line):
            states.append(line)
            i += 1
            
        # Paragraphs
        else:
            states.append(line)
            i += 1
            
    return states


class MarkChain:
    """
    A Markov chain model for markdown state transitions.
    """
    
    def __init__(self, order: int = 1, smoothing: float = 0.01):
        """
        Initialize a MarkChain.
        
        Args:
            order: The order of the Markov chain
            smoothing: Smoothing factor for unseen transitions
        """
        self.order = order
        self.smoothing = smoothing
        self.transitions = defaultdict(Counter)
        self.states = set()
        self.start_states = Counter()
        self.is_trained = False
        
    def train(self, markdown_text: str) -> None:
        """
        Train the model on markdown text.
        
        Args:
            markdown_text: Raw markdown content
        """
        states = default_state_parser(markdown_text)
        
        if not states:
            return
            
        # Track starting state
        self.start_states[states[0]] += 1
        self.states.add(states[0])
        
        # Learn transitions
        for i in range(len(states) - 1):
            current_state = states[i]
            next_state = states[i + 1]

            self.states.add(current_state)
            self.states.add(next_state)
            self.transitions[current_state][next_state] += 1

        self.is_trained = True
            
    def sample(self, length: int = 10, start_state: Optional[str] = None) -> str:
        """
        Generate a sample from the model.
        
        Args:
            length: Number of states to generate
            start_state: Starting state (if None, sample from start states)
            
        Returns:
            Generated markdown text
        """
        if not self.states:
            return ""
            
        # Choose starting state
        if start_state is None:
            if self.start_states:
                states_list = list(self.start_states.keys())
                weights = [self.start_states[s] for s in states_list]
                current = random.choices(states_list, weights=weights)[0]
            else:
                current = random.choice(list(self.states))
        else:
            current = start_state
            
        result = [current]
        
        # Generate sequence
        for _ in range(length - 1):
            if current not in self.transitions or not self.transitions[current]:
                # No transitions from current state, pick random state
                current = random.choice(list(self.states))
            else:
                # Sample next state
                next_states = list(self.transitions[current].keys())
                weights = [self.transitions[current][s] for s in next_states]
                current = random.choices(next_states, weights=weights)[0]
            result.append(current)
            
        return '\n\n'.join(result)
        
    def generate(self, length: int = 10, prompt: Optional[str] = None, 
                temperature: float = 1.0) -> str:
        """
        Generate markdown content.
        
        Args:
            length: Number of states to generate
            prompt: Starting prompt
            temperature: Temperature for sampling (higher = more random)
            
        Returns:
            Generated markdown
        """
        return self.sample(length=length, start_state=prompt)
        
    def get_transition_probabilities(self, state: str) -> Dict[str, float]:
        """
        Get transition probabilities from a state.
        
        Args:
            state: Source state
            
        Returns:
            Dictionary mapping next states to probabilities
        """
        if state not in self.transitions:
            return {}
            
        total = sum(self.transitions[state].values())
        if total == 0:
            return {}
            
        return {
            next_state: count / total
            for next_state, count in self.transitions[state].items()
        }
        
    def save_model(self, filepath: str) -> None:
        """Save model to file."""
        data = {
            'order': self.order,
            'smoothing': self.smoothing,
            'transitions': {k: dict(v) for k, v in self.transitions.items()},
            'states': list(self.states),
            'start_states': dict(self.start_states)
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    def load_model(self, filepath: str) -> None:
        """Load model from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.order = data['order']
        self.smoothing = data['smoothing']
        self.transitions = defaultdict(Counter, {
            k: Counter(v) for k, v in data['transitions'].items()
        })
        self.states = set(data['states'])
        self.start_states = Counter(data['start_states'])
