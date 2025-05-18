"""
MarkChain: A Markov chain-based markdown generator that models the stochastic
transitions between markdown elements.
"""

import os
import re
import random
import numpy as np
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set, Union, Iterator, Any, Callable

# Define standard decay functions
def linear_decay(distance: int) -> float:
    """Linear decay function: 1/distance"""
    return 1.0 / max(1, distance)

def exponential_decay(distance: int, base: float = 0.5) -> float:
    """Exponential decay function: base^(distance-1)"""
    return base ** (max(0, distance - 1))

def gaussian_decay(distance: int, sigma: float = 1.0) -> float:
    """Gaussian decay function: exp(-0.5 * (distance/sigma)^2)"""
    return np.exp(-0.5 * ((max(1, distance) - 1) / sigma) ** 2)

def constant_decay(distance: int) -> float:
    """Constant decay function: always returns 1.0"""
    return 1.0

class PositionalEncoder:
    """
    Transformer-style positional encoder for markdown elements.
    
    This encoder adds positional information to states based on their position in the document,
    enabling the model to capture structural patterns that depend on absolute or relative position.
    """
    
    def __init__(self, max_length: int = 1000, encoding_dim: int = 4):
        """
        Initialize a positional encoder.
        
        Args:
            max_length: Maximum document length to encode
            encoding_dim: Dimension of positional encoding vector
        """
        self.max_length = max_length
        self.encoding_dim = encoding_dim
        self.position_matrix = self._create_position_matrix()
        
    def _create_position_matrix(self) -> np.ndarray:
        """
        Create the positional encoding matrix.
        
        Returns:
            Matrix of shape (max_length, encoding_dim) with positional encodings
        """
        # Create an empty matrix
        pos_enc = np.zeros((self.max_length, self.encoding_dim))
        
        # Fill with sinusoidal position encodings, similar to transformer architecture
        for pos in range(self.max_length):
            for i in range(0, self.encoding_dim, 2):
                # Even dimensions use sine
                if i < self.encoding_dim:
                    pos_enc[pos, i] = math.sin(pos / (10000 ** (i / self.encoding_dim)))
                # Odd dimensions use cosine
                if i + 1 < self.encoding_dim:
                    pos_enc[pos, i + 1] = math.cos(pos / (10000 ** (i / self.encoding_dim)))
                    
        return pos_enc
    
    def encode(self, position: int) -> Tuple[float, ...]:
        """
        Get the positional encoding for a specific position.
        
        Args:
            position: Position in the document (0-indexed)
            
        Returns:
            Positional encoding vector as a tuple
        """
        if position >= self.max_length:
            position = self.max_length - 1
            
        return tuple(self.position_matrix[position])
    
    def encode_normalized(self, position: int, document_length: int) -> Tuple[float, ...]:
        """
        Get positional encoding based on relative position in the document.
        
        Args:
            position: Position in the document (0-indexed)
            document_length: Total length of the document
            
        Returns:
            Positional encoding vector as a tuple
        """
        if document_length <= 1:
            norm_position = 0
        else:
            norm_position = int((position / (document_length - 1)) * (self.max_length - 1))
            
        return self.encode(norm_position)

class MarkChain:
    """
    A Markov chain model for generating markdown content based on transition probabilities
    learned from existing markdown documents.
    
    States in this model correspond to markdown elements (headers, paragraphs, lists, etc.),
    and transitions represent the probability of one element following another.
    """
    
    def __init__(self, order: int = 1, state_parser: Optional[callable] = None,
                 use_skipgrams: bool = False, skip_window: int = 2,
                 decay_function: Callable[[int], float] = linear_decay,
                 use_positional_encoding: bool = False, encoding_dim: int = 4):
        """
        Initialize a MarkChain instance.
        
        Args:
            order: The order of the Markov chain (how many previous states to consider)
            state_parser: Optional custom function to parse markdown into states
            use_skipgrams: Whether to use skip-gram models to capture non-adjacent dependencies
            skip_window: Maximum distance to consider for skip-grams (ignored if use_skipgrams is False)
            decay_function: Function to determine how influence decays with distance
            use_positional_encoding: Whether to incorporate positional information in the model
            encoding_dim: Dimension of positional encoding vectors (ignored if use_positional_encoding is False)
        """
        self.order = order
        self.state_parser = state_parser or self._default_state_parser
        self.transitions: Dict[Tuple, Counter] = defaultdict(Counter)
        self.start_states: List[Tuple] = []
        self.use_skipgrams = use_skipgrams
        self.skip_window = skip_window
        self.skipgram_transitions: Dict[Tuple, Dict[int, Counter]] = defaultdict(lambda: defaultdict(Counter))
        self.decay_function = decay_function
        
        # Positional encoding properties
        self.use_positional_encoding = use_positional_encoding
        self.positional_encoder = PositionalEncoder(encoding_dim=encoding_dim) if use_positional_encoding else None
        self.positional_transitions: Dict[Tuple, Dict[Tuple, Counter]] = defaultdict(lambda: defaultdict(Counter))
        
    @property
    def is_trained(self) -> bool:
        """
        Check if the model has been trained.
        
        Returns:
            True if the model has transitions recorded, False otherwise
        """
        return len(self.transitions) > 0
        
    @classmethod
    def from_corpus(cls, corpus_path: str, **kwargs) -> "MarkChain":
        """
        Create a MarkChain instance trained on a corpus of markdown files.
        
        Args:
            corpus_path: Path to a directory containing markdown files or a single file
            **kwargs: Additional arguments to pass to the constructor
            
        Returns:
            A trained MarkChain instance
        """
        instance = cls(**kwargs)
        
        if os.path.isdir(corpus_path):
            md_files = [os.path.join(corpus_path, f) for f in os.listdir(corpus_path)
                       if f.endswith('.md')]
        else:
            md_files = [corpus_path]
            
        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                instance.train(content)
                
        return instance
    
    def train(self, markdown_text: str) -> None:
        """
        Train the model on a markdown document.
        
        Args:
            markdown_text: The markdown content to learn from
        """
        states = list(self.state_parser(markdown_text))
        
        if len(states) <= self.order:
            return
            
        # Track possible start states
        history = tuple(states[:self.order])
        self.start_states.append(history)
        
        # Build transition probabilities
        for i in range(self.order, len(states)):
            next_state = states[i]
            self.transitions[history][next_state] += 1
            
            # Add skip-gram transitions if enabled
            if self.use_skipgrams:
                self._add_skipgram_transitions(states, i, history)
                
            # Add positional transitions if enabled
            if self.use_positional_encoding:
                self._add_positional_transitions(states, i, history)
                
            history = history[1:] + (next_state,)
    
    def _add_skipgram_transitions(self, states: List[Any], current_idx: int, history: Tuple) -> None:
        """
        Add skip-gram transitions to capture non-adjacent dependencies.
        
        Args:
            states: List of all states in the document
            current_idx: Current position in the states list
            history: Current history tuple used for the Markov chain
        """
        # Look ahead within the skip window
        for skip in range(2, min(self.skip_window + 1, len(states) - current_idx + 1)):
            if current_idx + skip - 1 < len(states):
                skip_state = states[current_idx + skip - 1]
                self.skipgram_transitions[history][skip][skip_state] += 1
    
    def _add_positional_transitions(self, states: List[Any], current_idx: int, history: Tuple) -> None:
        """
        Add positionally-aware transitions to capture structural patterns.
        
        Args:
            states: List of all states in the document
            current_idx: Current position in the states list
            history: Current history tuple used for the Markov chain
        """
        # Get positional encoding for current position
        pos_encoding = self.positional_encoder.encode_normalized(current_idx, len(states))
        
        # Add transition with positional information
        next_state = states[current_idx]
        self.positional_transitions[history][pos_encoding][next_state] += 1
    
    def sample(self, length: int = 100, seed_text: Optional[str] = None, 
               skipgram_weight: float = 0.3, positional_weight: float = 0.3) -> str:
        """
        Generate markdown text using the trained model.
        
        Args:
            length: Maximum number of states to generate
            seed_text: Optional markdown text to use as a starting point
            skipgram_weight: Weight given to skip-gram transitions (0-1, only used if use_skipgrams is True)
            positional_weight: Weight given to positional transitions (0-1, only used if use_positional_encoding is True)
            
        Returns:
            Generated markdown content
        """
        if not self.transitions:
            raise ValueError("Model has not been trained yet.")
            
        # Initialize history
        if seed_text:
            seed_states = list(self.state_parser(seed_text))
            if len(seed_states) < self.order:
                raise ValueError(f"Seed text too short for order {self.order} chain.")
            history = tuple(seed_states[-self.order:])
        else:
            history = random.choice(self.start_states)
            
        # Generate states
        result_states = list(history)
        for i in range(length - self.order):
            if history not in self.transitions or not self.transitions[history]:
                # No transitions found, pick a random start state
                history = random.choice(self.start_states)
                result_states.append(history[-1])
            else:
                # Sample next state based on transition probabilities
                position = self.order + i
                next_state = self._sample_next_state(history, position, len(result_states) + length - self.order,
                                                    skipgram_weight, positional_weight)
                result_states.append(next_state)
                history = history[1:] + (next_state,)
                
        # Convert states back to markdown
        return self._states_to_markdown(result_states)
    
    def _sample_next_state(self, history: Tuple, position: int, total_length: int,
                          skipgram_weight: float, positional_weight: float) -> Any:
        """
        Sample the next state using regular transitions, skip-gram transitions, and positional information.
        
        Args:
            history: Current history tuple
            position: Current position in the generated sequence
            total_length: Estimated total length of the final sequence
            skipgram_weight: Weight to give to skip-gram transitions (0-1)
            positional_weight: Weight to give to positional transitions (0-1)
            
        Returns:
            The next state
        """
        remaining_weight = 1.0
        
        # Start with regular transition probabilities
        counter = self.transitions[history]
        states = list(counter.keys())
        weights = np.array(list(counter.values()), dtype=float)
        
        # If skip-grams are enabled and we have skip-gram data, incorporate it
        if self.use_skipgrams and skipgram_weight > 0 and history in self.skipgram_transitions:
            # Combine probabilities from all skip distances
            skipgram_counter = Counter()
            
            # Add counts from each skip distance
            for skip, skip_counter in self.skipgram_transitions[history].items():
                # Apply the decay function based on skip distance
                decay = self.decay_function(skip)
                for state, count in skip_counter.items():
                    skipgram_counter[state] += count * decay
            
            # Merge skipgram probabilities if we have any
            if skipgram_counter:
                remaining_weight -= skipgram_weight
                # Get combined set of states
                all_states = set(states) | set(skipgram_counter.keys())
                
                # Create combined weights array
                combined_weights = np.zeros(len(all_states))
                all_states = list(all_states)
                
                # Fill in weights
                for i, state in enumerate(all_states):
                    regular_weight = remaining_weight * (counter[state] if state in counter else 0)
                    skip_weight = skipgram_weight * (skipgram_counter[state] if state in skipgram_counter else 0)
                    combined_weights[i] = regular_weight + skip_weight
                
                # If we have valid weights, update our sampling variables
                if combined_weights.sum() > 0:
                    states = all_states
                    weights = combined_weights
        
        # If positional encoding is enabled and we have positional data, incorporate it
        if self.use_positional_encoding and positional_weight > 0 and history in self.positional_transitions:
            # Get positional encoding for current position
            pos_encoding = self.positional_encoder.encode_normalized(position, total_length)
            
            # Find the closest position we have data for
            closest_encoding = None
            min_distance = float('inf')
            
            for enc in self.positional_transitions[history]:
                # Calculate Euclidean distance between encodings
                distance = sum((a - b) ** 2 for a, b in zip(pos_encoding, enc)) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_encoding = enc
            
            # If we found a close match, incorporate those transitions
            if closest_encoding is not None:
                pos_counter = self.positional_transitions[history][closest_encoding]
                
                if pos_counter:
                    remaining_weight -= positional_weight
                    # Get combined set of states
                    all_states = set(states) | set(pos_counter.keys())
                    
                    # Create combined weights array
                    combined_weights = np.zeros(len(all_states))
                    all_states = list(all_states)
                    
                    # Fill in weights
                    for i, state in enumerate(all_states):
                        # Scale weights from previous combinations
                        current_weight = weights[states.index(state)] if state in states else 0
                        
                        # Add positional weight
                        pos_value = pos_counter[state] if state in pos_counter else 0
                        combined_weights[i] = current_weight + positional_weight * pos_value
                    
                    # If we have valid weights, update our sampling variables
                    if combined_weights.sum() > 0:
                        states = all_states
                        weights = combined_weights
        
        # Normalize weights
        if weights.sum() > 0:
            weights = weights / weights.sum()
            
            # Sample the next state
            return np.random.choice(states, p=weights)
        else:
            # Fallback: return a random state from the original counter
            return random.choice(list(counter.keys())) if counter else None
    
    def set_decay_function(self, decay_function: Callable[[int], float]) -> None:
        """
        Set a new decay function for skip-gram transitions.
        
        Args:
            decay_function: Function that takes a distance parameter and returns a weight
        """
        self.decay_function = decay_function
    
    def _default_state_parser(self, markdown_text: str) -> Iterator[str]:
        """
        Default parser that breaks markdown into states.
        
        Args:
            markdown_text: Raw markdown content
            
        Returns:
            Iterator of markdown states
        """
        # Split by lines first
        lines = markdown_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Headers
            if line.startswith('#'):
                yield line
                i += 1
                
            # Lists
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                list_item = line
                i += 1
                while i < len(lines) and (lines[i].strip().startswith('- ') or 
                                          lines[i].strip().startswith('* ') or 
                                          re.match(r'^\d+\.', lines[i].strip())):
                    list_item += '\n' + lines[i]
                    i += 1
                yield list_item
                
            # Code blocks
            elif line.startswith('```'):
                code_block = line
                i += 1
                while i < len(lines) and not lines[i].strip() == '```':
                    code_block += '\n' + lines[i]
                    i += 1
                if i < len(lines):  # Add closing backticks if found
                    code_block += '\n' + lines[i]
                    i += 1
                yield code_block
                
            # Blank lines
            elif not line:
                yield line
                i += 1
                
            # Regular paragraphs
            else:
                paragraph = line
                i += 1
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().startswith('#') or 
                    lines[i].strip().startswith('- ') or 
                    lines[i].strip().startswith('* ') or 
                    re.match(r'^\d+\.', lines[i].strip()) or
                    lines[i].strip().startswith('```')
                ):
                    paragraph += '\n' + lines[i]
                    i += 1
                yield paragraph
    
    def _states_to_markdown(self, states: List[str]) -> str:
        """
        Convert a list of states back to markdown text.
        
        Args:
            states: List of markdown states
            
        Returns:
            Reconstructed markdown document
        """
        return '\n'.join(states) 