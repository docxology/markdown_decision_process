"""
MarkdownAgent: An autonomous agent that explores and exploits the Markdown state space,
combining the other MDP components to generate, analyze, and optimize markdown documents.
"""

import os
import random
import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from pathlib import Path
import tempfile

from .markchain import MarkChain
from .policy_optimizer import PolicyOptimizer
from .state_space import StateSpace
from .belief_updater import BeliefUpdater
from .document import Document

class MarkdownAgent:
    """
    An autonomous agent that explores and exploits the Markdown state space,
    optimizing for both user-defined rewards and its own exploration objectives.
    
    The agent combines generative models, policy optimization, state space understanding,
    and belief updating to create a comprehensive markdown assistant.
    """
    
    def __init__(
        self,
        exploration_rate: float = 0.2,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        reward_weights: Optional[Dict[str, float]] = None,
        model_path: Optional[str] = None
    ):
        """
        Initialize a MarkdownAgent.
        
        Args:
            exploration_rate: Probability of taking random actions for exploration
            learning_rate: Rate at which the agent learns from new experiences
            discount_factor: How much to value future rewards vs. immediate rewards
            reward_weights: Custom weights for different reward components
            model_path: Path to pre-trained models
        """
        self.exploration_rate = exploration_rate
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Initialize components
        self.generator = MarkChain(order=2)
        self.optimizer = PolicyOptimizer(
            reward_weights=reward_weights,
            learning_rate=learning_rate
        )
        self.state_space = StateSpace()
        self.belief_updater = BeliefUpdater()
        
        # Track experience
        self.experiences = []
        self.value_function = {}  # State -> value mapping
        
        # Load models if provided
        if model_path:
            self.load_models(model_path)
    
    def train(self, corpus_path: str, iterations: int = 100) -> Dict[str, Any]:
        """
        Train the agent on a corpus of markdown documents.
        
        Args:
            corpus_path: Path to a directory containing markdown files
            iterations: Number of training iterations
            
        Returns:
            Training statistics
        """
        # Analyze the corpus to build state space understanding
        self.state_space.analyze(corpus_path)
        
        # Train the generator on the corpus
        self.generator = MarkChain.from_corpus(corpus_path, order=2)
        
        # Collect markdown documents
        if os.path.isdir(corpus_path):
            md_files = [os.path.join(corpus_path, f) for f in os.listdir(corpus_path)
                       if f.endswith('.md')]
        else:
            md_files = [corpus_path]
            
        # Run training iterations
        stats = {
            "iterations": iterations,
            "documents_processed": len(md_files),
            "value_function_updates": 0,
            "exploration_actions": 0,
            "exploitation_actions": 0
        }
        
        for i in range(iterations):
            if i % 10 == 0:
                print(f"Training iteration {i}/{iterations}")
                
            # Select a random document to learn from
            doc_path = random.choice(md_files)
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the document
            elements = self._parse_document(content)
            
            # Extract features for belief updating
            observations = [self._extract_features(elem) for elem in elements]
            
            # Reset agent's belief state
            self.belief_updater = BeliefUpdater()
            
            # Simulate agent interactions with the document
            for j in range(len(observations) - 1):
                current_state = self._state_representation(elements[j])
                next_state = self._state_representation(elements[j+1])
                
                # Update belief based on observation
                self.belief_updater.update_from_observation(observations[j])
                
                # Determine action (exploration vs exploitation)
                if random.random() < self.exploration_rate:
                    # Exploration: try a random action
                    action = "explore"
                    stats["exploration_actions"] += 1
                else:
                    # Exploitation: try to optimize
                    action = "optimize"
                    stats["exploitation_actions"] += 1
                
                # Calculate reward for the transition
                reward = self._calculate_reward(elements[j], elements[j+1], action)
                
                # Store experience
                self.experiences.append({
                    "state": current_state,
                    "action": action,
                    "next_state": next_state,
                    "reward": reward,
                    "belief": self.belief_updater.belief_state.copy()
                })
                
                # Update value function (simplified Q-learning)
                if current_state not in self.value_function:
                    self.value_function[current_state] = 0.0
                    
                if next_state not in self.value_function:
                    self.value_function[next_state] = 0.0
                
                # Q-learning update
                current_value = self.value_function[current_state]
                next_value = self.value_function[next_state]
                
                # V(s) = V(s) + α[r + γV(s') - V(s)]
                self.value_function[current_state] = current_value + self.learning_rate * (
                    reward + self.discount_factor * next_value - current_value
                )
                
                stats["value_function_updates"] += 1
        
        # Update optimizer based on learned experiences
        self._update_optimizer_from_experiences()
        
        return stats
    
    def generate(self, prompt: Optional[str] = None, length: int = 100) -> str:
        """
        Generate markdown content, optionally starting from a prompt.
        
        Args:
            prompt: Optional starting markdown content
            length: Desired length of generated content
            
        Returns:
            Generated markdown content
        """
        return self.generator.sample(length=length, seed_text=prompt)
    
    def optimize(self, markdown_path: str) -> str:
        """
        Optimize an existing markdown document.
        
        Args:
            markdown_path: Path to the markdown file to optimize
            
        Returns:
            Optimized markdown content
        """
        return self.optimizer.transform(markdown_path)
    
    def analyze(self, markdown_input: Union[str, Document, Path]) -> Dict[str, Any]:
        """
        Analyze a markdown document to extract insights.
        
        Args:
            markdown_input: Path to the markdown file, Document object, or content string to analyze
        
        Returns:
            Analysis results
        """
        # Ensure we have a Document object to work with
        if isinstance(markdown_input, (str, Path)):
            # If it's a path, load the document
            if Path(markdown_input).exists() and Path(markdown_input).is_file():
                doc = Document(file_path=str(markdown_input))
                doc_content_for_belief = str(markdown_input) # Path for belief updater
            else:
                # Assume it's content string if not a valid file path
                doc = Document(content=str(markdown_input))
                # For belief updater, we might need to save temp content if it expects a path
                # This part of BeliefUpdater might need refactoring to accept content directly
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as tmp_f:
                    tmp_f.write(doc.get_content())
                    doc_content_for_belief = tmp_f.name
        elif isinstance(markdown_input, Document):
            doc = markdown_input
            # Similar to above, BeliefUpdater might need a path
            if doc.file_path and doc.file_path.exists():
                doc_content_for_belief = str(doc.file_path)
            else:
                with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as tmp_f:
                    tmp_f.write(doc.get_content())
                    doc_content_for_belief = tmp_f.name
        else:
            raise TypeError(f"Unsupported input type for analysis: {type(markdown_input)}. Expected str, Path, or Document.")

        # Use BeliefUpdater to analyze semantics
        # The belief_updater.analyze_document_file expects a path.
        semantic_analysis = self.belief_updater.analyze_document_file(doc_content_for_belief)
        if 'tmp_f' in locals() and Path(doc_content_for_belief).exists(): # Clean up temp file if created
            try:
                os.remove(doc_content_for_belief)
            except OSError:
                pass # Ignore if already deleted or other issue

        # Use StateSpace to analyze structure
        self.state_space = StateSpace()
        self.state_space.analyze(doc) # Pass the Document object to StateSpace.analyze
        
        # Read the content (already available in doc object)
        content = doc.get_content()
            
        elements = self._parse_document(content)
        
        # Calculate overall value based on value function
        total_value = 0.0
        state_values = []
        
        for elem in elements:
            state = self._state_representation(elem)
            value = self.value_function.get(state, 0.0)
            state_values.append({"state": state, "value": value})
            total_value += value
            
        avg_value = total_value / len(elements) if elements else 0.0
        
        # Combine analyses
        return {
            "semantic_analysis": semantic_analysis,
            "value_analysis": {
                "total_value": total_value,
                "average_value": avg_value,
                "state_values": state_values
            },
            "state_transitions": len(self.state_space.transitions),
            "unique_states": len(self.state_space.state_metadata)
        }
    
    def interact(
        self, 
        markdown_content: str, 
        objective: str = "optimize",
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interact with markdown content based on an objective.
        
        Args:
            markdown_content: Markdown content to interact with
            objective: The agent's objective ("optimize", "extend", "summarize", etc.)
            constraints: Optional constraints on the interaction
            
        Returns:
            Results of the interaction
        """
        constraints = constraints or {}
        elements = self._parse_document(markdown_content)
        observations = [self._extract_features(elem) for elem in elements]
        
        # Reset belief state
        self.belief_updater = BeliefUpdater()
        
        # Track actions and their effects
        actions_taken = []
        modified_content = markdown_content
        
        # Determine semantic intent
        self.belief_updater.update_belief_batch(observations)
        semantic_class, confidence = self.belief_updater.get_most_likely_semantics()
        
        # Determine high-value states based on value function
        element_values = []
        for elem in elements:
            state = self._state_representation(elem)
            value = self.value_function.get(state, 0.0)
            element_values.append((elem, value))
            
        # Sort by value
        element_values.sort(key=lambda x: x[1], reverse=True)
        
        # Take actions based on objective
        if objective == "optimize":
            # Directly use the optimizer
            with open("temp_interact.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            modified_content = self.optimizer.transform("temp_interact.md")
            os.remove("temp_interact.md")
            
            actions_taken.append({"action": "optimize", "result": "full_document"})
            
        elif objective == "extend":
            # Add content based on high-value states
            extension_point = None
            
            # Find a good extension point (preferably end of document)
            if elements:
                extension_point = len(elements) - 1
                
            if extension_point is not None:
                # Generate new content
                seed_text = elements[extension_point].get('content', '')
                new_content = self.generator.sample(length=20, seed_text=seed_text)
                
                # Add the new content
                modified_elements = elements.copy()
                
                # Create a new element with the generated content
                new_element = {
                    'type': 'paragraph',  # Default to paragraph
                    'content': new_content
                }
                
                # Insert at extension point
                modified_elements.insert(extension_point + 1, new_element)
                
                # Reconstruct content
                modified_content = '\n\n'.join(elem.get('content', '') for elem in modified_elements)
                
                actions_taken.append({"action": "extend", "position": extension_point})
                
        elif objective == "summarize":
            # Extract high-value elements for summary
            summary_elements = [elem for elem, value in element_values[:3]]
            
            # Start with a heading
            summary = "# Summary\n\n"
            
            # Add selected elements
            for elem in summary_elements:
                summary += elem.get('content', '') + "\n\n"
                
            modified_content = summary
            actions_taken.append({"action": "summarize", "elements_used": len(summary_elements)})
            
        else:
            # Unknown objective, just return original content
            actions_taken.append({"action": "unknown_objective", "result": "no_change"})
                
        return {
            "original_content": markdown_content,
            "modified_content": modified_content,
            "actions_taken": actions_taken,
            "semantic_class": semantic_class,
            "semantic_confidence": confidence,
            "objective": objective
        }
    
    def save_models(self, path: str) -> None:
        """
        Save trained models to a directory.
        
        Args:
            path: Directory to save models to
        """
        # Ensure directory exists
        os.makedirs(path, exist_ok=True)
        
        # Save value function
        np.save(os.path.join(path, "value_function.npy"), self.value_function)
        
        # Save experiences
        np.save(os.path.join(path, "experiences.npy"), self.experiences)
        
        # Note: For a real implementation, we would need to add proper
        # serialization for the component models
    
    def load_models(self, path: str) -> None:
        """
        Load trained models from a directory.
        
        Args:
            path: Directory to load models from
        """
        value_function_path = os.path.join(path, "value_function.npy")
        experiences_path = os.path.join(path, "experiences.npy")
        
        if os.path.exists(value_function_path):
            self.value_function = np.load(value_function_path, allow_pickle=True).item()
            
        if os.path.exists(experiences_path):
            self.experiences = np.load(experiences_path, allow_pickle=True).tolist()
            
        # Note: For a real implementation, we would need to add proper
        # deserialization for the component models
    
    def _parse_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown document into structured elements.
        
        Args:
            content: Markdown content
            
        Returns:
            List of document elements with metadata
        """
        # Reuse the parser from BeliefUpdater
        return self.belief_updater._parse_document(content)
    
    def _extract_features(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from a markdown element.
        
        Args:
            element: Parsed markdown element
            
        Returns:
            Dictionary of features
        """
        # Reuse the feature extractor from BeliefUpdater
        return self.belief_updater._extract_features(element)
    
    def _state_representation(self, element: Dict[str, Any]) -> str:
        """
        Create a string representation of an element's state.
        
        Args:
            element: Markdown element
            
        Returns:
            String representation of the state
        """
        element_type = element.get('type', 'unknown')
        
        if element_type == 'header':
            level = element.get('level', 1)
            return f"h{level}"
            
        elif element_type == 'list':
            list_type = element.get('list_type', 'unordered')
            return f"list_{list_type}"
            
        elif element_type == 'code':
            language = element.get('language', '')
            if language:
                return f"code_{language}"
            return "code"
            
        elif element_type == 'paragraph':
            # Simplify paragraphs based on length
            text = element.get('text', '')
            words = len(text.split())
            
            if words < 20:
                return "paragraph_short"
            elif words < 100:
                return "paragraph_medium"
            else:
                return "paragraph_long"
                
        elif element_type == 'blank':
            return "blank"
            
        return f"unknown_{element_type}"
    
    def _calculate_reward(
        self, 
        current_element: Dict[str, Any], 
        next_element: Dict[str, Any],
        action: str
    ) -> float:
        """
        Calculate the reward for a state transition.
        
        Args:
            current_element: Current markdown element
            next_element: Next markdown element
            action: Action taken
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Base reward for good transitions
        current_type = current_element.get('type', '')
        next_type = next_element.get('type', '')
        
        # Reward logical transitions
        if current_type == 'header' and next_type == 'paragraph':
            # Headers followed by explanatory paragraphs
            reward += 1.0
        elif current_type == 'paragraph' and next_type == 'list':
            # Paragraphs followed by supporting lists
            reward += 0.8
        elif current_type == 'paragraph' and next_type == 'code':
            # Paragraphs followed by illustrative code
            reward += 0.8
        elif current_type == 'list' and next_type == 'paragraph':
            # Lists followed by explanations
            reward += 0.5
            
        # Penalize undesirable transitions
        if current_type == 'header' and next_type == 'header':
            # Adjacent headers without content
            reward -= 0.5
        elif current_type == 'blank' and next_type == 'blank':
            # Multiple blank lines
            reward -= 0.3
            
        # Adjust based on action
        if action == "explore":
            # Encourage exploration of uncommon transitions
            state_pair = (self._state_representation(current_element),
                          self._state_representation(next_element))
            
            if state_pair not in self.value_function:
                # Reward for discovering new transitions
                reward += 0.5
                
        return reward
    
    def _update_optimizer_from_experiences(self) -> None:
        """
        Update the optimizer's reward functions based on agent experiences.
        """
        # This is a simplified implementation
        # In a real system, you would want to learn reward weights from experiences
        
        # Calculate average rewards for different transitions
        transition_rewards = defaultdict(list)
        
        for exp in self.experiences:
            transition = (exp["state"], exp["next_state"])
            transition_rewards[transition].append(exp["reward"])
            
        # Print top rewarding transitions
        avg_rewards = {t: sum(rewards)/len(rewards) 
                       for t, rewards in transition_rewards.items() 
                       if len(rewards) > 1}
        
        top_transitions = sorted(avg_rewards.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print("Top rewarding transitions learned:")
        for (s1, s2), reward in top_transitions:
            print(f"  {s1} → {s2}: {reward:.2f}") 