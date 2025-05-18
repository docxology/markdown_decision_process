"""
BeliefUpdater: A module that handles the uncertainty in interpreting markdown semantics
from syntax, inspired by belief updates in Partially Observable Markov Decision Processes.
"""

import re
import numpy as np
import json
from typing import Dict, List, Tuple, Set, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)

class BeliefUpdater:
    """
    Updates beliefs about document states based on observations.
    
    This class manages a belief state (a probability distribution over possible states)
    and updates it based on observations from the document.
    """
    
    def __init__(self, semantic_classes: Optional[List[str]] = None, 
                 noise_factor: float = 0.2, prior_beliefs: Optional[Dict[str, float]] = None):
        """
        Initialize a BeliefUpdater instance.
        
        Args:
            semantic_classes: List of possible semantic meanings to track
            noise_factor: Factor controlling the amount of noise applied to beliefs (0-1)
            prior_beliefs: Dictionary of initial belief values
        """
        self.semantic_classes = semantic_classes or [
            "instruction", "explanation", "example", "reference", 
            "summary", "definition", "warning", "note"
        ]
        
        # Initialize belief distribution
        self.beliefs = {cls: 1.0 / len(self.semantic_classes) for cls in self.semantic_classes}
        
        # Add custom prior beliefs if provided
        if prior_beliefs:
            for key, value in prior_beliefs.items():
                self.beliefs[key] = value
                
        # Initialize confidence level
        self.confidence = 0.5
        
        # Set noise factor for belief updates
        self.noise_factor = min(max(noise_factor, 0.0), 1.0)  # Clamp between 0 and 1
        
        # Initialize observations storage
        self.observations = []
        
        # Create belief_state as property alias for beliefs
        self.belief_state = self.beliefs
        
        # Observation model: P(observation | semantic class)
        self._initialize_observation_model()
        
        # Transition model: P(semantic class' | semantic class)
        self._initialize_transition_model()
        
    def update_belief(self, key: str, value: float) -> None:
        """
        Update a specific belief value.
        
        Args:
            key: Belief identifier
            value: New belief value (0-1)
        """
        self.beliefs[key] = min(max(value, 0.0), 1.0)  # Clamp between 0 and 1
    
    def update_from_observation(self, observation: Dict[str, float]) -> None:
        """
        Update beliefs based on an observation dictionary.
        
        Args:
            observation: Dictionary mapping belief keys to observed values
        """
        # Store the observation
        self.observations.append(observation)
        
        for key, value in observation.items():
            if key in self.beliefs and isinstance(value, (int, float)):
                current = self.get_belief(key)
                # Simple Bayesian update
                updated = (current + value) / 2
                self.update_belief(key, updated)
        
        # Update confidence based on observation
        self._update_confidence(observation)
    
    def get_belief(self, key: str, default: float = 0.0) -> float:
        """
        Get the current value of a belief.
        
        Args:
            key: Belief identifier
            default: Default value if belief not found
            
        Returns:
            Current belief value
        """
        return self.beliefs.get(key, default)
    
    def get_all_beliefs(self) -> Dict[str, float]:
        """
        Get all current beliefs.
        
        Returns:
            Dictionary of all beliefs
        """
        return self.beliefs.copy()
    
    def get_noisy_belief(self, key: str) -> float:
        """
        Get a belief value with added noise.
        
        Args:
            key: Belief identifier
            
        Returns:
            Belief value with noise applied
        """
        value = self.get_belief(key)
        noise = np.random.normal(0, self.noise_factor * 0.1)
        noisy_value = value + noise
        return min(max(noisy_value, 0.0), 1.0)  # Clamp between 0 and 1
    
    def reset_beliefs(self) -> None:
        """Reset all beliefs to default values (zero)."""
        self.beliefs = {key: 0.0 for key in self.beliefs}
        self.confidence = 0.5
        self.observations = []
    
    def save_beliefs(self, filepath: str) -> None:
        """
        Save the current belief state to a file.
        
        Args:
            filepath: Path to save the belief state
        """
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'beliefs': self.beliefs,
                    'confidence': self.confidence,
                    'observations': self.observations
                }, f)
        except Exception as e:
            logger.error(f"Error saving beliefs to {filepath}: {e}")
            raise

    def load_beliefs(self, filepath: str) -> None:
        """
        Load beliefs from a file.
        
        Args:
            filepath: Path to load the belief state from
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.beliefs = data.get('beliefs', {})
                self.confidence = data.get('confidence', 0.0)
                self.observations = data.get('observations', [])
        except Exception as e:
            logger.error(f"Error loading beliefs from {filepath}: {e}")
            raise
    
    def combine_beliefs(self, other_beliefs: Dict[str, float], weight: float = 0.5) -> None:
        """
        Combine current beliefs with another set of beliefs.
        
        Args:
            other_beliefs: Dictionary of beliefs to combine with
            weight: Weight given to the other beliefs (0-1)
        """
        for key, value in other_beliefs.items():
            if key in self.beliefs:
                current = self.get_belief(key)
                combined = current * (1 - weight) + value * weight
                self.update_belief(key, combined)
            else:
                # If key doesn't exist in current beliefs, add it directly
                self.update_belief(key, value)
    
    def calculate_entropy(self) -> float:
        """
        Calculate the entropy of the current belief distribution.
        
        Returns:
            Entropy value
        """
        values = [v for v in self.beliefs.values() if v > 0]
        if not values:
            return 0.0
            
        # Normalize to ensure sum is 1
        total = sum(values)
        if total == 0:
            return 0.0
            
        normalized = [v / total for v in values]
        
        # Calculate entropy
        entropy = -sum(p * np.log2(p) for p in normalized if p > 0)
        return entropy
    
    def analyze_document(self, state_space: Any) -> Dict[str, float]:
        """
        Analyze a markdown document's state space to generate beliefs.
        
        Args:
            state_space: StateSpace object containing markdown structure
            
        Returns:
            Dictionary of beliefs about the document
        """
        beliefs = {}
        
        # Extract document properties from state space
        if hasattr(state_space, 'states'):
            # Count different types of states
            state_types = {}
            for state_id, state_data in state_space.states.items():
                state_type = state_data.get('type', 'unknown')
                state_types[state_type] = state_types.get(state_type, 0) + 1
            
            # Analyze structure based on state distributions
            total_states = len(state_space.states)
            if total_states > 0:
                # Calculate structure score based on heading hierarchy
                heading_ratio = state_types.get('heading', 0) / total_states
                beliefs['structure'] = min(heading_ratio * 5, 1.0)
                
                # Calculate readability based on paragraph to total ratio
                para_ratio = state_types.get('paragraph', 0) / total_states
                beliefs['readability'] = min(para_ratio * 2, 1.0)
                
                # Calculate consistency based on state transitions
                if hasattr(state_space, 'transitions') and state_space.transitions:
                    transition_consistency = len(state_space.transitions) / (total_states * 2)
                    beliefs['consistency'] = min(transition_consistency * 3, 1.0)
                elif hasattr(state_space, 'graph') and state_space.graph:
                    transition_consistency = len(state_space.graph) / (total_states * 2)
                    beliefs['consistency'] = min(transition_consistency * 3, 1.0)
                else:
                    # Default consistency if no graph data available
                    beliefs['consistency'] = 0.8
                
                # Add a few more belief values to ensure the dictionary is not empty
                beliefs['complexity'] = min(len(state_types) / 5, 1.0)
                beliefs['coherence'] = 0.5  # Default value
        
        # If no beliefs were generated, provide some default values
        if not beliefs:
            beliefs = {
                'structure': 0.5,
                'readability': 0.6,
                'consistency': 0.8,
                'complexity': 0.4,
                'coherence': 0.5
            }
                
        # Apply noise to beliefs
        if self.noise_factor > 0:
            for key in beliefs:
                noise = np.random.normal(0, self.noise_factor * 0.1)
                beliefs[key] = min(max(beliefs[key] + noise, 0.0), 1.0)
                
        return beliefs
    
    def _update_confidence(self, observation: Dict[str, float]) -> None:
        """
        Update confidence based on observations.
        
        Args:
            observation: Dictionary of observed features
        """
        # Calculate average certainty from observation
        # Only consider numeric values for certainty calculation
        numeric_values = [v for v in observation.values() if isinstance(v, (int, float))]
        if not numeric_values:
            avg_certainty = 0.0
        else:
            avg_certainty = sum(abs(v - 0.5) * 2 for v in numeric_values) / len(numeric_values)
            
        # Update confidence (simplified)
        confidence_boost = 0.05 * len(observation)
        
        # Update confidence
        self.confidence = min(self.confidence + confidence_boost * avg_certainty, 1.0)
    
    def update_belief_batch(self, observations: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Update belief distribution based on new markdown observations.
        
        Args:
            observations: List of observed markdown elements with features
            
        Returns:
            Updated belief distribution over semantic classes
        """
        for obs in observations:
            # Prediction step (temporal update)
            predicted_belief = self._predict_step()
            
            # Observation step (Bayesian update)
            self.beliefs = self._observation_step(predicted_belief, obs)
            
        return self.beliefs
    
    def get_most_likely_semantics(self) -> Tuple[str, float]:
        """
        Get the most likely semantic class based on current belief.
        
        Returns:
            Tuple of (most likely class, probability)
        """
        most_likely = max(self.beliefs.items(), key=lambda x: x[1])
        return most_likely
    
    def analyze_document_file(self, markdown_path: str) -> Dict[str, Any]:
        """
        Analyze a markdown document and infer its semantic structure.
        
        Args:
            markdown_path: Path to markdown file
            
        Returns:
            Dictionary containing semantic analysis
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse document into elements
        elements = self._parse_document(content)
        
        # Extract features from elements
        observations = [self._extract_features(elem) for elem in elements]
        
        # Initialize belief state
        self.beliefs = {cls: 1.0 / len(self.semantic_classes) for cls in self.semantic_classes}
        
        # Track section-level semantics
        section_semantics = []
        current_section = []
        current_belief = self.beliefs.copy()
        
        for i, obs in enumerate(observations):
            # Check if new section
            if i > 0 and obs.get('type') == 'header' and elements[i-1].get('type') != 'header':
                if current_section:
                    most_likely, prob = max(current_belief.items(), key=lambda x: x[1])
                    section_semantics.append({
                        'elements': current_section,
                        'semantic_class': most_likely,
                        'probability': prob,
                        'belief': current_belief.copy()
                    })
                
                current_section = [elements[i]]
                current_belief = self.beliefs.copy()
            else:
                current_section.append(elements[i])
                
            # Update belief
            current_belief = self.update_belief_batch([obs])
            
        # Add final section
        if current_section:
            most_likely, prob = max(current_belief.items(), key=lambda x: x[1])
            section_semantics.append({
                'elements': current_section,
                'semantic_class': most_likely,
                'probability': prob,
                'belief': current_belief.copy()
            })
            
        # Overall document semantics
        overall_belief = {}
        for cls in self.semantic_classes:
            overall_belief[cls] = np.mean([section['belief'].get(cls, 0.0) 
                                          for section in section_semantics])
            
        most_likely_overall, prob_overall = max(overall_belief.items(), key=lambda x: x[1])
        
        return {
            'sections': section_semantics,
            'overall_semantic_class': most_likely_overall,
            'overall_probability': prob_overall,
            'overall_belief': overall_belief
        }
    
    def print_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Print a human-readable version of the semantic analysis.
        
        Args:
            analysis: Document analysis from analyze_document
        """
        print(f"Document Semantic Analysis")
        print(f"==========================")
        print(f"Overall semantic class: {analysis['overall_semantic_class']} "
              f"(confidence: {analysis['overall_probability']:.2f})")
        
        print("\nBelief distribution:")
        for cls, prob in sorted(analysis['overall_belief'].items(), 
                                key=lambda x: x[1], reverse=True):
            print(f"  {cls}: {prob:.3f}")
            
        print("\nSection analysis:")
        for i, section in enumerate(analysis['sections']):
            print(f"\nSection {i+1}: {section['semantic_class']} "
                  f"(confidence: {section['probability']:.2f})")
            
            # Print first element of the section to identify it
            if section['elements']:
                first = section['elements'][0]
                if first.get('type') == 'header':
                    print(f"  {first.get('content', '')}")
                else:
                    content = first.get('content', '')
                    print(f"  {content[:50]}..." if len(content) > 50 else f"  {content}")
    
    def _initialize_observation_model(self) -> None:
        """Initialize the observation model relating markdown features to semantic classes."""
        # P(feature | semantic class)
        self.observation_model = {
            'header_level': {
                1: {'instruction': 0.1, 'explanation': 0.2, 'example': 0.1, 'reference': 0.1,
                    'summary': 0.3, 'definition': 0.05, 'warning': 0.05, 'note': 0.1},
                2: {'instruction': 0.2, 'explanation': 0.15, 'example': 0.15, 'reference': 0.1,
                    'summary': 0.1, 'definition': 0.2, 'warning': 0.05, 'note': 0.05},
                3: {'instruction': 0.15, 'explanation': 0.2, 'example': 0.1, 'reference': 0.05,
                    'summary': 0.05, 'definition': 0.3, 'warning': 0.1, 'note': 0.05},
            },
            'contains_code': {
                True: {'instruction': 0.3, 'explanation': 0.25, 'example': 0.3, 'reference': 0.05,
                       'summary': 0.05, 'definition': 0.03, 'warning': 0.01, 'note': 0.01},
                False: {'instruction': 0.1, 'explanation': 0.15, 'example': 0.05, 'reference': 0.2,
                        'summary': 0.2, 'definition': 0.1, 'warning': 0.1, 'note': 0.1},
            },
            'contains_list': {
                True: {'instruction': 0.4, 'explanation': 0.15, 'example': 0.15, 'reference': 0.1,
                       'summary': 0.1, 'definition': 0.05, 'warning': 0.03, 'note': 0.02},
                False: {'instruction': 0.05, 'explanation': 0.2, 'example': 0.15, 'reference': 0.15,
                        'summary': 0.15, 'definition': 0.1, 'warning': 0.1, 'note': 0.1},
            },
            'keyword_matches': {
                'instruction': {'instruction': 0.7, 'explanation': 0.1, 'example': 0.05, 'reference': 0.03,
                               'summary': 0.05, 'definition': 0.03, 'warning': 0.02, 'note': 0.02},
                'explanation': {'instruction': 0.1, 'explanation': 0.6, 'example': 0.1, 'reference': 0.05,
                               'summary': 0.05, 'definition': 0.05, 'warning': 0.03, 'note': 0.02},
                'example': {'instruction': 0.05, 'explanation': 0.1, 'example': 0.65, 'reference': 0.05,
                           'summary': 0.05, 'definition': 0.05, 'warning': 0.03, 'note': 0.02},
                'reference': {'instruction': 0.02, 'explanation': 0.05, 'example': 0.03, 'reference': 0.7,
                             'summary': 0.1, 'definition': 0.05, 'warning': 0.03, 'note': 0.02},
                'summary': {'instruction': 0.05, 'explanation': 0.1, 'example': 0.05, 'reference': 0.05,
                           'summary': 0.6, 'definition': 0.05, 'warning': 0.05, 'note': 0.05},
                'definition': {'instruction': 0.05, 'explanation': 0.1, 'example': 0.05, 'reference': 0.05,
                              'summary': 0.05, 'definition': 0.6, 'warning': 0.05, 'note': 0.05},
                'warning': {'instruction': 0.1, 'explanation': 0.05, 'example': 0.05, 'reference': 0.02,
                           'summary': 0.03, 'definition': 0.05, 'warning': 0.65, 'note': 0.05},
                'note': {'instruction': 0.05, 'explanation': 0.1, 'example': 0.05, 'reference': 0.05,
                        'summary': 0.05, 'definition': 0.05, 'warning': 0.05, 'note': 0.6},
                'none': {'instruction': 0.13, 'explanation': 0.14, 'example': 0.13, 'reference': 0.12,
                        'summary': 0.12, 'definition': 0.12, 'warning': 0.12, 'note': 0.12},
            }
        }
        
        # Keywords associated with each semantic class
        self.keywords = {
            'instruction': ['step', 'guide', 'how to', 'follow', 'instructions', 'tutorial', 
                           'steps', 'procedure', 'do', 'install', 'run', 'execute', 'setup'],
            'explanation': ['explain', 'because', 'due to', 'reason', 'why', 'how', 
                           'therefore', 'thus', 'hence', 'explainer', 'clarification'],
            'example': ['example', 'instance', 'e.g.', 'such as', 'illustration', 
                       'demonstrate', 'sample', 'for instance', 'case'],
            'reference': ['reference', 'citation', 'source', 'according to', 'cited', 
                         'link', 'url', 'refer', 'see', 'documentation', 'docs'],
            'summary': ['summary', 'overall', 'in conclusion', 'to sum up', 'in brief', 
                       'recap', 'in short', 'overview', 'tldr', 'tl;dr'],
            'definition': ['means', 'define', 'definition', 'is a', 'refers to', 'consists of', 
                          'is defined as', 'represents', 'stands for', 'term'],
            'warning': ['warning', 'caution', 'careful', 'danger', 'important', 'attention', 
                       'note', 'beware', 'avoid', 'prevent', 'problem', 'issue'],
            'note': ['note', 'notice', 'observe', 'point', 'remark', 'nb', 'n.b.', 
                    'reminder', 'side note', 'addendum', 'addition'],
        }
    
    def _initialize_transition_model(self) -> None:
        """Initialize the transition model between semantic classes."""
        # P(semantic class' | semantic class)
        self.transition_model = {
            'instruction': {'instruction': 0.7, 'explanation': 0.2, 'example': 0.05, 'reference': 0.01,
                           'summary': 0.01, 'definition': 0.01, 'warning': 0.01, 'note': 0.01},
            'explanation': {'instruction': 0.1, 'explanation': 0.6, 'example': 0.15, 'reference': 0.05,
                           'summary': 0.05, 'definition': 0.03, 'warning': 0.01, 'note': 0.01},
            'example': {'instruction': 0.05, 'explanation': 0.2, 'example': 0.6, 'reference': 0.05,
                       'summary': 0.05, 'definition': 0.01, 'warning': 0.02, 'note': 0.02},
            'reference': {'instruction': 0.02, 'explanation': 0.05, 'example': 0.03, 'reference': 0.7,
                         'summary': 0.1, 'definition': 0.05, 'warning': 0.02, 'note': 0.03},
            'summary': {'instruction': 0.15, 'explanation': 0.1, 'example': 0.05, 'reference': 0.05,
                       'summary': 0.6, 'definition': 0.02, 'warning': 0.01, 'note': 0.02},
            'definition': {'instruction': 0.05, 'explanation': 0.3, 'example': 0.1, 'reference': 0.05,
                          'summary': 0.05, 'definition': 0.4, 'warning': 0.02, 'note': 0.03},
            'warning': {'instruction': 0.2, 'explanation': 0.2, 'example': 0.1, 'reference': 0.05,
                       'summary': 0.05, 'definition': 0.05, 'warning': 0.3, 'note': 0.05},
            'note': {'instruction': 0.1, 'explanation': 0.2, 'example': 0.1, 'reference': 0.1,
                    'summary': 0.1, 'definition': 0.05, 'warning': 0.05, 'note': 0.3},
        }
    
    def _predict_step(self) -> Dict[str, float]:
        """
        Perform the prediction step of belief update.
        
        Returns:
            Predicted belief distribution
        """
        predicted = {}
        for next_class in self.semantic_classes:
            prob = 0
            for curr_class, curr_prob in self.beliefs.items():
                # Get probability of transitioning from curr_class to next_class
                trans_prob = self.transition_model.get(curr_class, {}).get(next_class, 0)
                prob += curr_prob * trans_prob
            predicted[next_class] = prob
            
        # Normalize
        total = sum(predicted.values())
        if total > 0:
            predicted = {k: v / total for k, v in predicted.items()}
            
        return predicted
    
    def _observation_step(self, prior: Dict[str, float], observation: Dict[str, Any]) -> Dict[str, float]:
        """
        Perform the observation step of belief update.
        
        Args:
            prior: Prior belief distribution
            observation: Observation with features
            
        Returns:
            Updated belief distribution
        """
        # Calculate likelihood of observation for each class
        likelihood = {cls: 1.0 for cls in self.semantic_classes}
        
        # Update for each feature in the observation
        for feature, model in self.observation_model.items():
            if feature == 'header_level' and 'header_level' in observation:
                level = observation['header_level']
                for cls in self.semantic_classes:
                    level_prob = model.get(level, {}).get(cls, 0.1)
                    likelihood[cls] *= level_prob
                    
            elif feature == 'contains_code' and 'contains_code' in observation:
                has_code = observation['contains_code']
                for cls in self.semantic_classes:
                    code_prob = model.get(has_code, {}).get(cls, 0.1)
                    likelihood[cls] *= code_prob
                    
            elif feature == 'contains_list' and 'contains_list' in observation:
                has_list = observation['contains_list']
                for cls in self.semantic_classes:
                    list_prob = model.get(has_list, {}).get(cls, 0.1)
                    likelihood[cls] *= list_prob
                    
            elif feature == 'keyword_matches' and 'keyword_matches' in observation:
                keywords = observation['keyword_matches']
                for cls in self.semantic_classes:
                    for keyword in keywords:
                        if keyword in model:
                            kw_prob = model.get(keyword, {}).get(cls, 0.1)
                            likelihood[cls] *= kw_prob
        
        # Calculate posterior using Bayes' rule
        posterior = {}
        for cls in self.semantic_classes:
            posterior[cls] = prior[cls] * likelihood[cls]
            
        # Normalize
        total = sum(posterior.values())
        if total > 0:
            posterior = {k: v / total for k, v in posterior.items()}
            
        return posterior
    
    def _parse_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse markdown content into elements.
        
        Args:
            content: Markdown content
            
        Returns:
            List of elements with their features
        """
        elements = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Parse headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2)
                elements.append({
                    'type': 'header',
                    'level': level,
                    'content': text
                })
                i += 1
                continue
                
            # Parse code blocks
            if line.startswith('```'):
                code_lines = []
                language = line[3:].strip()
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                    
                if i < len(lines):  # Skip closing ```
                    i += 1
                    
                elements.append({
                    'type': 'code',
                    'language': language,
                    'content': '\n'.join(code_lines)
                })
                continue
                
            # Parse lists
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1))
                bullet = list_match.group(2)
                text = list_match.group(3)
                list_type = 'ordered' if re.match(r'\d+\.', bullet) else 'unordered'
                
                # Get all list items at this level
                list_items = [text]
                i += 1
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    next_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', lines[i])
                    
                    if next_match and len(next_match.group(1)) == indent:
                        list_items.append(next_match.group(3))
                        i += 1
                    else:
                        break
                        
                elements.append({
                    'type': 'list',
                    'list_type': list_type,
                    'items': list_items
                })
                continue
                
            # Parse paragraphs
            if line:
                para_lines = [line]
                i += 1
                
                while i < len(lines) and lines[i].strip() and not (
                    re.match(r'^(#{1,6})\s+(.+)$', lines[i].strip()) or
                    re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', lines[i]) or
                    lines[i].strip().startswith('```')
                ):
                    para_lines.append(lines[i].strip())
                    i += 1
                    
                elements.append({
                    'type': 'paragraph',
                    'content': ' '.join(para_lines)
                })
                continue
                
            # Skip empty lines
            i += 1
                
        return elements
    
    def _extract_features(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from a markdown element.
        
        Args:
            element: Markdown element
            
        Returns:
            Dictionary of features
        """
        features = {'type': element['type']}
        
        if element['type'] == 'header':
            features['header_level'] = element['level']
            features['contains_code'] = False
            features['contains_list'] = False
            
            # Extract keywords
            keywords = []
            text = element['content'].lower()
            
            for cls in self.semantic_classes:
                if cls in text:
                    keywords.append(cls)
                    
            features['keyword_matches'] = keywords
            
        elif element['type'] == 'code':
            features['header_level'] = 0
            features['contains_code'] = True
            features['contains_list'] = False
            features['keyword_matches'] = []
            
        elif element['type'] == 'list':
            features['header_level'] = 0
            features['contains_code'] = False
            features['contains_list'] = True
            
            # Extract keywords from list items
            keywords = []
            for item in element['items']:
                text = item.lower()
                for cls in self.semantic_classes:
                    if cls in text and cls not in keywords:
                        keywords.append(cls)
                        
            features['keyword_matches'] = keywords
            
        elif element['type'] == 'paragraph':
            features['header_level'] = 0
            features['contains_code'] = '`' in element['content']
            features['contains_list'] = False
            
            # Extract keywords
            keywords = []
            text = element['content'].lower()
            
            for cls in self.semantic_classes:
                if cls in text:
                    keywords.append(cls)
                    
            features['keyword_matches'] = keywords
            
        return features 