"""
PolicyOptimizer: A module for transforming Markdown documents to optimize for 
specific reward functions, inspired by Markov Decision Process policies.
"""

import re
import math
import random
from typing import Dict, List, Callable, Optional, Union, Tuple, Any
from collections import defaultdict
from .document import Document

class PolicyOptimizer:
    """
    Optimizes Markdown documents according to specified reward functions
    and a stochastic policy that guides state transitions.
    """
    
    def __init__(
        self, 
        state_space=None,
        reward_function=None,
        transformation_pipeline=None,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        exploration_factor: float = 0.2,
        max_iterations: int = 100
    ):
        """
        Initialize a PolicyOptimizer instance.
        
        Args:
            state_space: The state space to optimize over
            reward_function: Custom reward function
            transformation_pipeline: Pipeline of transformations to apply
            learning_rate: Learning rate for policy optimization
            discount_factor: Discount factor for future rewards
            exploration_factor: Factor controlling exploration vs exploitation
            max_iterations: Maximum number of iterations for optimization
        """
        self.state_space = state_space
        self.reward_function = reward_function or self._default_reward_function
        self.transformation_pipeline = transformation_pipeline
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_factor = exploration_factor
        self.max_iterations = max_iterations
        
        # Initialize Q-table, policy, and value function
        self.q_table = {}
        self.q_values = {}  # Alias for q_table for compatibility
        self.policy = {}
        self.value_function = {}
        
        # Initialize value function and policy for all states if state_space is provided
        if state_space is not None:
            for state_id in state_space.states.keys():
                self.value_function[state_id] = 0.0
                # Initialize policy as uniform distribution over successors
                successors = state_space.get_successor_states(state_id)
                if successors:
                    uniform_prob = 1.0 / len(successors)
                    self.policy[state_id] = {s: uniform_prob for s in successors}
                else:
                    self.policy[state_id] = {}
        
        # Register default reward functions
        self.default_rewards = {
            "readability": self._readability_reward,
            "information_density": self._information_density_reward,
            "structure_clarity": self._structure_clarity_reward,
        }

        # Initialize reward weights
        self.reward_weights = {
            "readability": 1.0,
            "information_density": 1.0,
            "structure_clarity": 1.0
        }

        # Initialize custom rewards
        self.custom_rewards = {}
    
    def _default_reward_function(self, state):
        """
        Default reward function if no custom function is provided.
        
        Args:
            state: Current state of the document
        
        Returns:
            Reward value
        """
        # Simple default reward based on state type
        if state.get('type') == 'header':
            return 1.0
        elif state.get('type') == 'paragraph':
            return 0.5
        else:
            return 0.1
    
    def set_reward_function(self, reward_fn):
        """
        Set a custom reward function.
        
        Args:
            reward_fn: Callable reward function
        """
        self.reward_function = reward_fn
    
    def value_iteration(self, max_iterations: Optional[int] = None) -> Dict[str, float]:
        """
        Perform value iteration to compute optimal value function.
        
        Args:
            max_iterations: Maximum number of iterations (default: self.max_iterations)
            
        Returns:
            Dictionary mapping state IDs to values
        """
        if max_iterations is None:
            max_iterations = self.max_iterations
        
        if self.state_space is None:
            return {}
        
        # Initialize value function to zeros
        for state_id in self.state_space.states.keys():
            self.value_function[state_id] = 0.0
        
        # Iterate to convergence
        for _ in range(max_iterations):
            new_values = {}
            
            for state_id, state in self.state_space.states.items():
                # Get immediate reward
                reward = self.reward_function(state)
                
                # Get successor states
                successors = self.state_space.get_successor_states(state_id)
                
                # Calculate max expected value
                if successors:
                    max_value = max(
                        self.value_function.get(s, 0.0) 
                        for s in successors
                    )
                    new_values[state_id] = reward + self.discount_factor * max_value
                else:
                    new_values[state_id] = reward
            
            # Update value function
            self.value_function = new_values
        
        return self.value_function
    
    def policy_improvement(self) -> Dict[str, Dict[str, float]]:
        """
        Improve policy based on current value function.
        Creates a stochastic policy with probabilities.
        
        Returns:
            Dictionary mapping state IDs to action probability distributions
        """
        if self.state_space is None:
            return {}
        
        for state_id in self.state_space.states.keys():
            successors = self.state_space.get_successor_states(state_id)
            
            if successors:
                # Get values for all successors
                values = {s: self.value_function.get(s, 0.0) for s in successors}
                max_value = max(values.values())
                
                # Create softmax policy with temperature
                import math
                temperature = 0.1
                exp_values = {
                    s: math.exp((v - max_value) / temperature) 
                    for s, v in values.items()
                }
                total = sum(exp_values.values())
                
                # Normalize to get probabilities
                self.policy[state_id] = {
                    s: exp_val / total 
                    for s, exp_val in exp_values.items()
                }
            else:
                self.policy[state_id] = {}
        
        return self.policy
    
    def q_learning(self, episodes: int = 100, max_steps: int = 50) -> Dict[Tuple[str, str], float]:
        """
        Perform Q-learning to learn optimal Q-values.
        
        Args:
            episodes: Number of episodes to run
            max_steps: Maximum steps per episode
            
        Returns:
            Q-table dictionary
        """
        if self.state_space is None:
            return {}
        
        import random
        
        for episode in range(episodes):
            # Start from a random state
            state_ids = list(self.state_space.states.keys())
            if not state_ids:
                break
                
            current_state = random.choice(state_ids)
            
            for step in range(max_steps):
                # Get possible actions
                successors = self.state_space.get_successor_states(current_state)
                if not successors:
                    break
                
                # Epsilon-greedy action selection
                if random.random() < self.exploration_factor:
                    next_state = random.choice(successors)
                else:
                    # Choose best action
                    next_state = max(
                        successors,
                        key=lambda s: self.q_table.get((current_state, s), 0.0)
                    )
                
                # Get reward
                reward = self.reward_function(self.state_space.states[next_state])
                
                # Update Q-value
                current_q = self.q_table.get((current_state, next_state), 0.0)
                
                # Max Q-value for next state
                next_successors = self.state_space.get_successor_states(next_state)
                if next_successors:
                    max_next_q = max(
                        self.q_table.get((next_state, s), 0.0)
                        for s in next_successors
                    )
                else:
                    max_next_q = 0.0
                
                # Q-learning update
                new_q = current_q + self.learning_rate * (
                    reward + self.discount_factor * max_next_q - current_q
                )
                self.q_table[(current_state, next_state)] = new_q
                self.q_values[(current_state, next_state)] = new_q  # Keep q_values in sync
                
                current_state = next_state
        
        return self.q_table
    
    def optimize(self, document, output_path=None):
        """
        Optimize a document using the configured reward function and transformations.
        
        Args:
            document: Document to optimize (can be Document instance or path string)
            output_path: Optional path to save optimized document
        
        Returns:
            Optimized document content or Document instance
        """
        from .document import Document
        from pathlib import Path
        
        # Handle both Document objects and file paths
        if isinstance(document, Document):
            content = document.content
        elif isinstance(document, (str, Path)):
            with open(document, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = str(document)
        
        # Parse the document
        document_structure = self._parse_document(content)
        
        # Track reward history
        reward_history = []
        
        # Apply optimization iterations
        for iteration in range(self.max_iterations):
            current_reward = self._calculate_total_reward(document_structure)
            reward_history.append(current_reward)
            
            best_structure = document_structure
            best_reward = current_reward
            
            for transform in self._get_possible_transforms(document_structure):
                transformed = self._apply_transform(document_structure, transform)
                reward = self._calculate_total_reward(transformed)
                
                if reward > best_reward:
                    best_structure = transformed
                    best_reward = reward
            
            document_structure = best_structure
        
        # Reconstruct the markdown from optimized structure
        optimized_content = self._structure_to_markdown(document_structure)
        
        # Calculate final reward
        final_reward = self._calculate_total_reward(document_structure)
        
        # Save if output_path is provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
        
        return {
            "optimized_content": optimized_content,
            "final_reward": final_reward,
            "iterations": self.max_iterations,
            "reward_history": reward_history
        }
    
    def optimize_with_func(self, reward_fn):
        """
        Optimize the document using a specific reward function.
        
        Args:
            reward_fn: Reward function to use for optimization
        
        Returns:
            Optimized document
        """
        self.set_reward_function(reward_fn)
        return self.transform(self.state_space)
    
    def transform(self, markdown_path: str) -> str:
        """
        Transform a markdown document to optimize its reward.
        
        Args:
            markdown_path: Path to the markdown file
            
        Returns:
            Optimized markdown content
        """
        # Read the markdown file
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the document into a state structure
        document_structure = self._parse_document(content)
        
        # Apply optimizations iteratively
        for _ in range(self.max_iterations):
            # Calculate current reward
            current_reward = self._calculate_total_reward(document_structure)
            
            # Try possible transformations
            best_structure = document_structure
            best_reward = current_reward
            
            for transform in self._get_possible_transforms(document_structure):
                transformed = self._apply_transform(document_structure, transform)
                reward = self._calculate_total_reward(transformed)
                
                if reward > best_reward:
                    best_structure = transformed
                    best_reward = reward
            
            # If no improvement, stop
            if best_reward <= current_reward:
                break
                
            document_structure = best_structure
            
        # Convert optimized structure back to markdown
        return self._structure_to_markdown(document_structure)
    
    def _parse_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown document into a structured representation.
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of document elements with metadata
        """
        lines = content.split('\n')
        elements = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Headers
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line[level:].strip()
                elements.append({
                    'type': 'header',
                    'level': level,
                    'text': text,
                    'content': line
                })
                i += 1
                
            # Lists
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                list_items = []
                list_type = 'unordered' if line.startswith(('- ', '* ')) else 'ordered'
                
                while i < len(lines) and (
                    lines[i].strip().startswith('- ') or 
                    lines[i].strip().startswith('* ') or 
                    re.match(r'^\d+\.', lines[i].strip())
                ):
                    list_items.append(lines[i])
                    i += 1
                
                elements.append({
                    'type': 'list',
                    'list_type': list_type,
                    'items': list_items,
                    'content': '\n'.join(list_items)
                })
                
            # Code blocks
            elif line.startswith('```'):
                code_lines = [line]
                lang = line[3:].strip()
                i += 1
                
                while i < len(lines) and not lines[i].strip() == '```':
                    code_lines.append(lines[i])
                    i += 1
                    
                if i < len(lines):
                    code_lines.append(lines[i])
                    i += 1
                    
                elements.append({
                    'type': 'code',
                    'language': lang,
                    'lines': code_lines[1:-1] if len(code_lines) > 2 else [],
                    'content': '\n'.join(code_lines)
                })
                
            # Blank lines
            elif not line:
                elements.append({
                    'type': 'blank',
                    'content': ''
                })
                i += 1
                
            # Regular paragraphs
            else:
                paragraph_lines = [line]
                i += 1
                
                while i < len(lines) and lines[i].strip() and not (
                    lines[i].strip().startswith('#') or 
                    lines[i].strip().startswith('- ') or 
                    lines[i].strip().startswith('* ') or 
                    re.match(r'^\d+\.', lines[i].strip()) or
                    lines[i].strip().startswith('```')
                ):
                    paragraph_lines.append(lines[i])
                    i += 1
                    
                text = ' '.join([l.strip() for l in paragraph_lines])
                elements.append({
                    'type': 'paragraph',
                    'text': text,
                    'content': '\n'.join(paragraph_lines)
                })
                
        return elements
    
    def _calculate_total_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate the total reward for a document structure.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Total reward value
        """
        total_reward = 0.0
        
        # Apply all reward functions
        for reward_name, weight in self.reward_weights.items():
            # Use default or custom reward function
            reward_func = self.default_rewards.get(reward_name, self.custom_rewards.get(reward_name))
            if reward_func:
                total_reward += weight * reward_func(document_structure)
        
        return total_reward
    
    def _readability_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate readability reward based on sentence length, paragraph length,
        and structure clarity.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Readability reward value
        """
        reward = 0.0
        
        for element in document_structure:
            if element['type'] == 'paragraph':
                text = element['text']

                # Penalize long paragraphs (prefer shorter, focused paragraphs)
                paragraph_length = len(text.split())
                if paragraph_length > 100:
                    reward -= (paragraph_length - 100) * 0.05  # Stronger penalty
                elif paragraph_length <= 50:
                    reward += 0.5  # Reward concise paragraphs

                # Analyze sentences
                sentences = re.split(r'[.!?]+', text)
                for sentence in sentences:
                    words = sentence.strip().split()

                    # Reward moderately sized sentences
                    if 5 <= len(words) <= 20:
                        reward += 0.3
                    elif len(words) > 20:
                        reward -= (len(words) - 20) * 0.1
            
            # Reward appropriate header levels
            elif element['type'] == 'header':
                if element['level'] <= 3:
                    reward += 1.0
                    
            # Reward lists (easy to scan)
            elif element['type'] == 'list':
                reward += 0.5 * len(element['items'])
                
        return reward
    
    def _information_density_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate information density reward based on keyword concentration,
        code blocks, and substantive content.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Information density reward value
        """
        reward = 0.0
        total_content = ""
        
        # Collect all textual content
        for element in document_structure:
            if element['type'] in ('paragraph', 'header'):
                total_content += " " + element.get('text', '')

        # Reward code blocks (high information density)
        code_block_count = sum(1 for e in document_structure if e['type'] == 'code')
        reward += code_block_count * 2.0

        # Analyze keyword density only if we have textual content
        words = total_content.lower().split()
        word_count = len(words)

        if word_count == 0:
            # If we have no textual content but have code blocks, return the code block reward
            return reward if reward > 0 else 0.0
        
        # Calculate word frequency
        word_freq = {}
        for word in words:
            word = re.sub(r'[^\w]', '', word)
            if len(word) >= 4:  # Only count substantive words
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Reward for diverse vocabulary (higher information)
        unique_words = len(word_freq)
        diversity_ratio = unique_words / max(1, word_count)
        reward += diversity_ratio * 10
        
        return reward
    
    def _structure_clarity_reward(self, document_structure: List[Dict[str, Any]]) -> float:
        """
        Calculate structure clarity reward based on heading hierarchy,
        section balance, and overall organization.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Structure clarity reward value
        """
        reward = 0.0
        
        # Check for document title (h1)
        has_title = any(e['type'] == 'header' and e['level'] == 1 
                        for e in document_structure)
        if has_title:
            reward += 3.0
            
        # Track header levels to check hierarchy
        current_level = 0
        sections = []
        current_section = []
        
        for element in document_structure:
            if element['type'] == 'header':
                # New section encountered
                if current_section:
                    sections.append((current_level, current_section))
                    
                current_level = element['level']
                current_section = [element]
                
                # Penalize skipping header levels (e.g., h1 -> h3)
                if current_level > 1 and current_level - 1 > current_level:
                    reward -= 1.0
            else:
                current_section.append(element)
                
        # Add the last section
        if current_section:
            sections.append((current_level, current_section))
            
        # Reward balanced sections
        section_sizes = [len(s[1]) for s in sections]
        if section_sizes:
            avg_size = sum(section_sizes) / len(section_sizes)
            for size in section_sizes:
                balance = 1.0 - min(abs(size - avg_size) / max(avg_size, 1.0), 0.8)
                reward += balance
                
        # Reward logical grouping of elements
        for level, section in sections:
            # Reward paragraphs after headers
            for i in range(len(section) - 1):
                if section[i]['type'] == 'header' and section[i+1]['type'] == 'paragraph':
                    reward += 0.5
                    
            # Reward lists after introductory paragraphs
            for i in range(len(section) - 1):
                if section[i]['type'] == 'paragraph' and section[i+1]['type'] == 'list':
                    reward += 0.5
        
        return reward
    
    def _get_possible_transforms(self, document_structure: List[Dict[str, Any]]) -> List[Dict]:
        """
        Generate possible transformations of the document.
        
        Args:
            document_structure: Current document structure
            
        Returns:
            List of possible transformations
        """
        transforms = []
        
        # Split long paragraphs
        for i, element in enumerate(document_structure):
            if element['type'] == 'paragraph':
                text = element['text']
                words = text.split()
                
                if len(words) > 50:  # Lower threshold for testing
                    transforms.append({
                        'type': 'split_paragraph',
                        'index': i
                    })
        
        # Add section headers before long content blocks
        for i in range(1, len(document_structure)):
            if all(document_structure[j]['type'] not in ('header', 'blank') 
                   for j in range(max(0, i-5), i)):
                transforms.append({
                    'type': 'add_header',
                    'index': i
                })
        
        # Convert paragraphs to lists where appropriate
        for i, element in enumerate(document_structure):
            if element['type'] == 'paragraph':
                text = element['text']
                sentences = re.split(r'[.!?]+', text)
                
                # Check if paragraph has list-like sentences (check for ordinal patterns)
                valid_sentences = [s for s in sentences if s.strip()]
                if len(valid_sentences) >= 3 and all(len(s.strip()) > 0 for s in valid_sentences):
                    # Check for ordinal numbers (First, Second, Third, etc.)
                    ordinal_starts = 0
                    ordinal_words = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
                                   'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

                    for j in range(min(3, len(valid_sentences))):  # Check first few sentences
                        words = valid_sentences[j].strip().lower().split()
                        if words and words[0] in ordinal_words:
                            ordinal_starts += 1

                    # Also check for similar sentence structures
                    similar_structures = 0
                    for j in range(1, len(valid_sentences)):
                        words1 = valid_sentences[j-1].strip().lower().split()
                        words2 = valid_sentences[j].strip().lower().split()

                        if (words1 and words2 and
                            len(words1) > 2 and len(words2) > 2 and
                            words1[1] == words2[1]):  # Same second word
                            similar_structures += 1

                    if ordinal_starts >= 2 or similar_structures >= len(valid_sentences) // 2:
                        transforms.append({
                            'type': 'convert_to_list',
                            'index': i
                        })
        
        return transforms

    def save(self, filepath: str) -> None:
        """Save the optimizer state."""
        import pickle
        from pathlib import Path

        filepath = Path(filepath)
        state = {
            'q_table': dict(self.q_table),
            'policy': dict(self.policy),
            'value_function': dict(self.value_function),
            'reward_function_name': getattr(self.reward_function, '__name__', 'custom') if callable(self.reward_function) else None,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'exploration_factor': self.exploration_factor,
            'max_iterations': self.max_iterations,
            'reward_weights': self.reward_weights,
            'custom_rewards': self.custom_rewards
        }

        with open(filepath, 'wb') as f:
            pickle.dump(state, f)

    def load(self, filepath: str) -> None:
        """Load the optimizer state."""
        import pickle
        from pathlib import Path

        filepath = Path(filepath)
        with open(filepath, 'rb') as f:
            state = pickle.load(f)

        self.q_table = defaultdict(lambda: defaultdict(float), state['q_table'])
        self.policy = defaultdict(dict, state['policy'])
        self.value_function = state['value_function']

        # Restore reward function based on name
        reward_name = state.get('reward_function_name')
        if reward_name == '_default_reward_function':
            self.reward_function = self._default_reward_function
        elif reward_name in self.default_rewards:
            self.reward_function = self.default_rewards[reward_name]
        else:
            # Use default for unknown functions
            self.reward_function = self._default_reward_function

        self.learning_rate = state['learning_rate']
        self.discount_factor = state['discount_factor']
        self.exploration_factor = state['exploration_factor']
        self.max_iterations = state['max_iterations']
        self.reward_weights = state['reward_weights']
        self.custom_rewards = state['custom_rewards']

    def _apply_transform(
        self, document_structure: List[Dict[str, Any]], transform: Dict
    ) -> List[Dict[str, Any]]:
        """
        Apply a transformation to the document structure.
        
        Args:
            document_structure: Current document structure
            transform: Transformation to apply
            
        Returns:
            Transformed document structure
        """
        result = document_structure.copy()
        
        if transform['type'] == 'split_paragraph':
            idx = transform['index']
            element = result[idx]
            
            if element['type'] != 'paragraph':
                return result
                
            text = element['text']
            sentences = re.split(r'([.!?]+)', text)
            
            # Rejoin sentences with their punctuation
            if len(sentences) % 2 == 0:
                sentences.append('')
            
            complete_sentences = [''.join(sentences[i:i+2]).strip() 
                                  for i in range(0, len(sentences), 2)]
            
            # Find a good split point (around the middle)
            mid = len(complete_sentences) // 2
            
            first_half = ' '.join(complete_sentences[:mid])
            second_half = ' '.join(complete_sentences[mid:])
            
            # Create new paragraph elements
            first_element = {
                'type': 'paragraph',
                'text': first_half,
                'content': first_half
            }
            second_element = {
                'type': 'paragraph',
                'text': second_half,
                'content': second_half
            }
            
            # Replace original with split paragraphs
            result[idx] = first_element
            result.insert(idx + 1, second_element)
            
        elif transform['type'] == 'add_header':
            idx = transform['index']
            
            # Infer a header title from the following content
            title = 'Section'
            if idx < len(result):
                next_element = result[idx]
                if next_element['type'] == 'paragraph':
                    words = next_element['text'].split()[:5]
                    title = ' '.join(words) + '...'
                elif next_element['type'] == 'list':
                    if next_element['items']:
                        first_item = next_element['items'][0]
                        title = re.sub(r'^[-*\d.]\s+', '', first_item)[:20] + '...'
            
            # Determine appropriate heading level
            level = 2  # Default to h2
            for i in range(idx - 1, -1, -1):
                if result[i]['type'] == 'header':
                    # Use one level deeper than the previous header
                    level = min(result[i]['level'] + 1, 3)
                    break
            
            header_element = {
                'type': 'header',
                'level': level,
                'text': title,
                'content': '#' * level + ' ' + title
            }
            
            result.insert(idx, header_element)
            
        elif transform['type'] == 'convert_to_list':
            idx = transform['index']
            element = result[idx]
            
            if element['type'] != 'paragraph':
                return result
                
            text = element['text']
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            list_items = ['- ' + s for s in sentences]
            
            list_element = {
                'type': 'list',
                'list_type': 'unordered',
                'items': list_items,
                'content': '\n'.join(list_items)
            }
            
            result[idx] = list_element
            
        return result
    
    def _structure_to_markdown(self, document_structure: List[Dict[str, Any]]) -> str:
        """
        Convert a document structure back to markdown.
        
        Args:
            document_structure: Structured representation of the document
            
        Returns:
            Markdown content
        """
        markdown_lines = []
        
        for i, element in enumerate(document_structure):
            # Add spacing between elements
            if i > 0 and element['type'] != 'blank' and document_structure[i-1]['type'] != 'blank':
                markdown_lines.append('')
                
            markdown_lines.append(element['content'])
            
        return '\n'.join(markdown_lines)

    def generate_optimal_sequence(self, start_state: Optional[str] = None, max_length: int = 50) -> List[str]:
        """
        Generate an optimal sequence of states based on the learned policy.

        Args:
            start_state: Starting state (if None, choose random)
            max_length: Maximum sequence length

        Returns:
            List of state IDs in optimal sequence
        """
        if self.state_space is None or not self.policy:
            return []

        if start_state is None:
            # Choose a random start state
            start_state = random.choice(list(self.state_space.states.keys()))

        sequence = [start_state]
        current_state = start_state

        for _ in range(max_length - 1):
            if current_state not in self.policy:
                break

            # Get action probabilities
            action_probs = self.policy[current_state]

            if not action_probs:
                break

            # Choose next state based on policy
            next_states = list(action_probs.keys())
            probabilities = list(action_probs.values())

            next_state = random.choices(next_states, weights=probabilities, k=1)[0]
            sequence.append(next_state)
            current_state = next_state

        return sequence

    def get_optimal_transitions(self, state_id: str) -> Dict[str, float]:
        """
        Get the optimal transition states for a given state.

        Args:
            state_id: Source state ID

        Returns:
            Dictionary mapping next state IDs to probabilities
        """
        if state_id not in self.policy:
            return {}

        # Return the policy for this state
        return self.policy[state_id]

    def get_best_action(self, state_id: str) -> Optional[str]:
        """
        Get the best action (next state) for a given state.

        Args:
            state_id: Source state ID

        Returns:
            Best next state ID, or None if no actions available
        """
        if state_id not in self.policy:
            return None

        action_probs = self.policy[state_id]

        if not action_probs:
            return None

        # Return the action with highest probability
        return max(action_probs.items(), key=lambda x: x[1])[0]

    def evaluate_policy(self, test_document: Optional[Union[str, Dict]] = None) -> Dict[str, float]:
        """
        Evaluate the current policy on a test document.

        Args:
            test_document: Path to test document, or policy dict (optional)

        Returns:
            Dictionary with evaluation metrics
        """
        if self.state_space is None:
            return {"error": "No state space available"}

        # If test_document is a policy dict, use it directly
        if isinstance(test_document, dict):
            # Calculate value of the policy - return value function for each state
            state_values = {}
            for state_id, action_probs in test_document.items():
                if action_probs:
                    # Get average value of actions
                    action_values = []
                    for next_state, prob in action_probs.items():
                        if next_state in self.value_function:
                            action_values.append(self.value_function[next_state] * prob)
                    if action_values:
                        state_values[state_id] = sum(action_values)
                    else:
                        state_values[state_id] = 0.0
                else:
                    state_values[state_id] = 0.0

            return state_values

        # Use provided document or create a simple test document
        if test_document and isinstance(test_document, str):
            try:
                doc = Document(file_path=test_document)
            except:
                # If file doesn't exist, create from content
                doc = Document(content=test_document)
        else:
            doc = Document(content="# Test\n\nParagraph\n\n## Section\n\nContent")

        # Parse document into structure
        elements = []
        for state_id, state_data in self.state_space.states.items():
            element = {
                'type': state_data.get('type'),
                'content': state_data.get('content'),
                'state_id': state_id
            }
            elements.append(element)

        # Calculate rewards for each element
        total_reward = 0.0
        element_rewards = []

        for element in elements:
            reward = self.reward_function(element)
            total_reward += reward
            element_rewards.append(reward)

        return {
            "total_reward": total_reward,
            "average_reward": total_reward / len(elements) if elements else 0,
            "element_count": len(elements),
            "element_rewards": element_rewards
        }

    def parse_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse a document into structured elements.

        Args:
            content: Markdown content

        Returns:
            List of document elements
        """
        # Use StateSpace parsing
        temp_ss = StateSpace()
        temp_ss.parse_markdown(content)

        elements = []
        for state_id, state_data in temp_ss.states.items():
            element = {
                'type': state_data.get('type'),
                'content': state_data.get('content'),
                'state_id': state_id
            }
            # Add level and text for headers
            if state_data.get('type') == 'header':
                level = len(state_data.get('content', '')) - len(state_data.get('content', '').lstrip('#'))
                element['level'] = min(level, 6) if level > 0 else 1
                element['text'] = state_data.get('content', '').lstrip('#').strip()
            elements.append(element)

        return elements

    def get_possible_transforms(self, document_structure: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get possible transformations that could be applied to a document.

        Args:
            document_structure: Structured representation of the document

        Returns:
            List of possible transformation dictionaries
        """
        transforms = []

        # Analyze current structure to suggest improvements
        header_count = sum(1 for elem in document_structure if elem.get('type') == 'header')
        paragraph_count = sum(1 for elem in document_structure if elem.get('type') == 'paragraph')

        # Suggest adding headers if few exist
        if header_count < 2 and len(document_structure) > 5:
            transforms.append({
                'type': 'add_header',
                'description': 'Add section headers to improve structure',
                'priority': 'high'
            })

        # Suggest breaking up long paragraphs
        long_paragraphs = [elem for elem in document_structure
                          if elem.get('type') == 'paragraph' and len(elem.get('content', elem.get('text', ''))) > 50]  # Check both content and text
        if long_paragraphs:
            transforms.append({
                'type': 'split_paragraph',
                'description': 'Split long paragraphs for better readability',
                'priority': 'medium'
            })

        return transforms 