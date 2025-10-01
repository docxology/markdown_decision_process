"""Tests for the PolicyOptimizer module."""

import pytest
import os
import tempfile
import re
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd

from mdp.policy_optimizer import PolicyOptimizer
from mdp.state_space import StateSpace
from mdp.document import Document
from mdp.transformations import (
    HeadingLevelTransformation,
    ListFormatTransformation,
    TextStyleTransformation,
    TransformationPipeline
)

# Sample markdown content for testing
SAMPLE_MARKDOWN = """# Test Document

This is a paragraph with some **important** information.

## Section 1
- Item 1
- Item 2

### Subsection
Some more text here.

```python
def test_function():
    return "Hello World"
```

## Section 2
This is another paragraph.
"""

@pytest.fixture
def state_space():
    """Fixture that creates a populated StateSpace instance."""
    space = StateSpace()
    space.parse_markdown(SAMPLE_MARKDOWN)
    return space

@pytest.fixture
def policy_optimizer(state_space):
    """Fixture that creates a PolicyOptimizer instance."""
    return PolicyOptimizer(state_space)

@pytest.fixture
def sample_markdown_file():
    """Create a temporary markdown file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as tmp:
        tmp.write(SAMPLE_MARKDOWN)
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

class TestPolicyOptimizer:
    """Tests for the PolicyOptimizer class."""
    
    def test_initialization(self, state_space):
        """Test basic initialization of PolicyOptimizer."""
        optimizer = PolicyOptimizer(state_space)
        
        # Should have initialized with the state space
        assert optimizer.state_space is state_space
        
        # Should have default parameters
        assert hasattr(optimizer, 'learning_rate')
        assert hasattr(optimizer, 'discount_factor')
        assert hasattr(optimizer, 'value_function')
        assert hasattr(optimizer, 'policy')
        
        # Value function should be initialized for all states
        assert set(optimizer.value_function.keys()) == set(state_space.states.keys())
        
        # Policy should be initialized for all states
        assert set(optimizer.policy.keys()) == set(state_space.states.keys())
    
    def test_initialization_with_parameters(self, state_space):
        """Test initialization with custom parameters."""
        learning_rate = 0.1
        discount_factor = 0.8
        
        optimizer = PolicyOptimizer(
            state_space,
            learning_rate=learning_rate,
            discount_factor=discount_factor
        )
        
        # Should have set the custom parameters
        assert optimizer.learning_rate == learning_rate
        assert optimizer.discount_factor == discount_factor
    
    def test_set_reward_function(self, policy_optimizer):
        """Test setting a custom reward function."""
        # Define a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.5
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Reward function should be set
        assert policy_optimizer.reward_function is not None
        
        # Test the reward function on a state
        for state_id, state in policy_optimizer.state_space.states.items():
            if state['type'] == 'header':
                assert policy_optimizer.reward_function(state) == 1.0
            else:
                assert policy_optimizer.reward_function(state) == 0.5
    
    def test_default_reward_function(self, policy_optimizer):
        """Test the default reward function."""
        # Default reward function should be set
        assert policy_optimizer.reward_function is not None
        
        # Test the default reward function on states
        for state_id, state in policy_optimizer.state_space.states.items():
            reward = policy_optimizer.reward_function(state)
            assert isinstance(reward, (int, float))
    
    def test_value_iteration(self, policy_optimizer):
        """Test the value iteration algorithm."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration
        policy_optimizer.value_iteration(max_iterations=10)
        
        # Value function should be updated
        for state_id in policy_optimizer.state_space.states:
            assert policy_optimizer.value_function[state_id] >= 0
            
        # Headers should generally have higher values
        header_values = []
        other_values = []
        
        for state_id, state in policy_optimizer.state_space.states.items():
            if state['type'] == 'header':
                header_values.append(policy_optimizer.value_function[state_id])
            else:
                other_values.append(policy_optimizer.value_function[state_id])
        
        # On average, header values should be higher
        if header_values and other_values:
            assert np.mean(header_values) > np.mean(other_values)
    
    def test_policy_improvement(self, policy_optimizer):
        """Test the policy improvement algorithm."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration first
        policy_optimizer.value_iteration(max_iterations=10)
        
        # Then improve the policy
        policy_optimizer.policy_improvement()
        
        # Policy should be updated for all states
        for state_id in policy_optimizer.state_space.states:
            # Only states with successors should have a policy
            if policy_optimizer.state_space.graph.out_degree(state_id) > 0:
                assert policy_optimizer.policy[state_id] is not None
                assert isinstance(policy_optimizer.policy[state_id], dict)
                
                # All probabilities should sum to approximately 1
                probs = list(policy_optimizer.policy[state_id].values())
                assert abs(sum(probs) - 1.0) < 1e-5
    
    def test_q_learning(self, policy_optimizer):
        """Test the Q-learning algorithm."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run Q-learning
        policy_optimizer.q_learning(episodes=5, max_steps=20)
        
        # Q-values should be initialized
        assert hasattr(policy_optimizer, 'q_values')
        assert len(policy_optimizer.q_values) > 0
        
        # Policy should be updated based on Q-values
        for state_id in policy_optimizer.state_space.states:
            if policy_optimizer.state_space.graph.out_degree(state_id) > 0:
                assert policy_optimizer.policy[state_id] is not None
    
    def test_generate_optimal_sequence(self, policy_optimizer):
        """Test generating an optimal sequence of states."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration
        policy_optimizer.value_iteration(max_iterations=10)
        policy_optimizer.policy_improvement()
        
        # Generate sequence
        sequence = policy_optimizer.generate_optimal_sequence(max_length=5)
        
        # Should return a sequence of state IDs
        assert isinstance(sequence, list)
        assert len(sequence) <= 5
        
        # Each state in the sequence should be a valid state
        for state_id in sequence:
            assert state_id in policy_optimizer.state_space.states
    
    def test_get_optimal_transitions(self, policy_optimizer):
        """Test getting optimal transitions for a state."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration
        policy_optimizer.value_iteration(max_iterations=10)
        policy_optimizer.policy_improvement()
        
        # Get a state with outgoing transitions
        for state_id in policy_optimizer.state_space.states:
            if policy_optimizer.state_space.graph.out_degree(state_id) > 0:
                # Get optimal transitions
                transitions = policy_optimizer.get_optimal_transitions(state_id)
                
                # Should return a dictionary mapping target states to probabilities
                assert isinstance(transitions, dict)
                assert len(transitions) > 0
                
                # Probabilities should sum to approximately 1
                probs = list(transitions.values())
                assert abs(sum(probs) - 1.0) < 1e-5
                break
    
    def test_get_best_action(self, policy_optimizer):
        """Test getting the best action for a state."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration
        policy_optimizer.value_iteration(max_iterations=10)
        policy_optimizer.policy_improvement()
        
        # Get a state with outgoing transitions
        for state_id in policy_optimizer.state_space.states:
            if policy_optimizer.state_space.graph.out_degree(state_id) > 0:
                # Get best action
                best_action = policy_optimizer.get_best_action(state_id)
                
                # Should return a valid state ID
                assert best_action in policy_optimizer.state_space.states
                break
    
    def test_evaluate_policy(self, policy_optimizer):
        """Test evaluating a policy."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Create a random policy
        random_policy = {}
        for state_id in policy_optimizer.state_space.states:
            successors = policy_optimizer.state_space.get_successor_states(state_id)
            if successors:
                # Equal probability for all successors
                probs = {s: 1.0 / len(successors) for s in successors}
                random_policy[state_id] = probs
            else:
                random_policy[state_id] = {}
        
        # Evaluate the policy
        value_function = policy_optimizer.evaluate_policy(random_policy)
        
        # Should return a value function
        assert isinstance(value_function, dict)
        assert len(value_function) == len(policy_optimizer.state_space.states)
        
        # Each state should have a value
        for state_id in policy_optimizer.state_space.states:
            assert state_id in value_function
            assert isinstance(value_function[state_id], (int, float))
    
    def test_save_and_load(self, policy_optimizer):
        """Test saving and loading the optimizer."""
        # Set a simple reward function
        def reward_fn(state):
            if state['type'] == 'header':
                return 1.0
            else:
                return 0.1
        
        policy_optimizer.set_reward_function(reward_fn)
        
        # Run value iteration
        policy_optimizer.value_iteration(max_iterations=10)
        policy_optimizer.policy_improvement()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.npz', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Save the optimizer
            policy_optimizer.save(tmp_path)
            
            # Create a new optimizer and load
            new_optimizer = PolicyOptimizer(policy_optimizer.state_space)
            new_optimizer.load(tmp_path)
            
            # Should have the same value function
            for state_id in policy_optimizer.state_space.states:
                assert abs(new_optimizer.value_function[state_id] - policy_optimizer.value_function[state_id]) < 1e-5
                
            # Should have the same policy
            for state_id in policy_optimizer.state_space.states:
                if policy_optimizer.policy[state_id]:
                    for next_state, prob in policy_optimizer.policy[state_id].items():
                        assert abs(new_optimizer.policy[state_id].get(next_state, 0) - prob) < 1e-5
        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()

    def test_parse_document(self, policy_optimizer):
        """Test the document parsing functionality."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        
        # Check overall structure
        assert len(document_structure) > 0
        
        # Verify header parsing
        headers = [el for el in document_structure if el['type'] == 'header']
        assert len(headers) >= 3  # Should have at least 3 headers
        assert headers[0]['level'] == 1
        assert headers[0]['text'] == 'Test Document'
        assert headers[1]['level'] == 2
        assert headers[1]['text'] == 'Section 1'
        
        # Verify paragraph parsing
        paragraphs = [el for el in document_structure if el['type'] == 'paragraph']
        assert len(paragraphs) >= 2
        assert "important" in paragraphs[0]['text']
        
        # Verify list parsing
        lists = [el for el in document_structure if el['type'] == 'list']
        assert len(lists) == 1
        assert len(lists[0]['items']) == 2
        assert lists[0]['list_type'] == 'unordered'
        
        # Verify code block parsing
        code_blocks = [el for el in document_structure if el['type'] == 'code']
        assert len(code_blocks) == 1
        assert code_blocks[0]['language'] == 'python'
        assert any('Hello World' in line for line in code_blocks[0]['lines'])
    
    def test_calculate_total_reward(self, policy_optimizer):
        """Test the reward calculation functionality."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        reward = policy_optimizer._calculate_total_reward(document_structure)
        
        # Reward should be a floating point number
        assert isinstance(reward, float)
        assert reward > 0
        
        # Test with custom reward function
        policy_optimizer.custom_rewards = {
            'test_reward': lambda doc: 42.0
        }
        policy_optimizer.reward_weights = {
            'test_reward': 1.0
        }
        
        custom_reward = policy_optimizer._calculate_total_reward(document_structure)
        assert custom_reward == 42.0
    
    def test_readability_reward(self, policy_optimizer):
        """Test the readability reward function."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        reward = policy_optimizer._readability_reward(document_structure)
        
        # Reward should be a floating point number
        assert isinstance(reward, float)
        
        # Create a document with long paragraphs that should be penalized
        long_paragraph = "This is a very long paragraph. " * 30
        long_doc = [{'type': 'paragraph', 'text': long_paragraph, 'content': long_paragraph}]
        long_reward = policy_optimizer._readability_reward(long_doc)
        
        # Document with long paragraphs should have lower readability reward
        assert long_reward < reward
    
    def test_information_density_reward(self, policy_optimizer):
        """Test the information density reward function."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        reward = policy_optimizer._information_density_reward(document_structure)
        
        # Reward should be a floating point number
        assert isinstance(reward, float)
        
        # Create a document with code blocks that should increase information density
        code_doc = [
            {'type': 'code', 'language': 'python', 'lines': ['def f(): pass'], 'content': '```python\ndef f(): pass\n```'},
            {'type': 'code', 'language': 'js', 'lines': ['function f() {}'], 'content': '```js\nfunction f() {}\n```'}
        ]
        code_reward = policy_optimizer._information_density_reward(code_doc)
        
        # Document with code blocks should have higher information density reward
        assert code_reward > 0
    
    def test_structure_clarity_reward(self, policy_optimizer):
        """Test the structure clarity reward function."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        reward = policy_optimizer._structure_clarity_reward(document_structure)
        
        # Reward should be a floating point number
        assert isinstance(reward, float)
        
        # Create a document with good structure
        good_structure = [
            {'type': 'header', 'level': 1, 'text': 'Title', 'content': '# Title'},
            {'type': 'paragraph', 'text': 'Intro', 'content': 'Intro'},
            {'type': 'header', 'level': 2, 'text': 'Section', 'content': '## Section'},
            {'type': 'paragraph', 'text': 'Content', 'content': 'Content'},
            {'type': 'list', 'list_type': 'unordered', 'items': ['- Item'], 'content': '- Item'}
        ]
        good_reward = policy_optimizer._structure_clarity_reward(good_structure)
        
        # Create a document with poor structure (skipping header levels)
        poor_structure = [
            {'type': 'header', 'level': 1, 'text': 'Title', 'content': '# Title'},
            {'type': 'header', 'level': 3, 'text': 'Subsection', 'content': '### Subsection'},
            {'type': 'paragraph', 'text': 'Content', 'content': 'Content'}
        ]
        poor_reward = policy_optimizer._structure_clarity_reward(poor_structure)
        
        # Document with good structure should have higher structure clarity reward
        assert good_reward > poor_reward
    
    def test_get_possible_transforms(self, policy_optimizer):
        """Test the transformation possibility detection."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        transforms = policy_optimizer._get_possible_transforms(document_structure)
        
        # Should return a list of possible transformations
        assert isinstance(transforms, list)
        
        # Create a document with a long paragraph
        long_paragraph = "This is a long paragraph. " * 20
        long_doc = [{'type': 'paragraph', 'text': long_paragraph, 'content': long_paragraph}]
        long_transforms = policy_optimizer._get_possible_transforms(long_doc)
        
        # Should suggest splitting the long paragraph
        assert any(t['type'] == 'split_paragraph' for t in long_transforms)
        
        # Create a document with list-like sentences in a paragraph
        list_like = "First item starts with first. Second item starts with second. Third item starts with third."
        list_like_doc = [{'type': 'paragraph', 'text': list_like, 'content': list_like}]
        list_transforms = policy_optimizer._get_possible_transforms(list_like_doc)
        
        # Should suggest converting to a list
        assert any(t['type'] == 'convert_to_list' for t in list_transforms)
    
    def test_apply_transform_split_paragraph(self, policy_optimizer):
        """Test applying a split paragraph transformation."""
        # Create a document with a paragraph to split
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        doc = [{'type': 'paragraph', 'text': text, 'content': text}]
        
        # Apply the split transformation
        transform = {'type': 'split_paragraph', 'index': 0}
        result = policy_optimizer._apply_transform(doc, transform)
        
        # Should now have two paragraphs
        assert len(result) == 2
        assert result[0]['type'] == 'paragraph'
        assert result[1]['type'] == 'paragraph'
        
        # Each paragraph should have some of the original content
        assert len(result[0]['text']) < len(text)
        assert len(result[1]['text']) < len(text)
        assert len(result[0]['text']) + len(result[1]['text']) > len(text) - 10  # Account for spaces
    
    def test_apply_transform_add_header(self, policy_optimizer):
        """Test applying an add header transformation."""
        # Create a document with paragraphs
        text = "This is a paragraph about an important topic."
        doc = [{'type': 'paragraph', 'text': text, 'content': text}]
        
        # Apply the add header transformation
        transform = {'type': 'add_header', 'index': 0}
        result = policy_optimizer._apply_transform(doc, transform)
        
        # Should now have a header and a paragraph
        assert len(result) == 2
        assert result[0]['type'] == 'header'
        assert result[1]['type'] == 'paragraph'
        
        # Header should contain words from the paragraph
        assert any(word in result[0]['text'] for word in text.split()[:5])
    
    def test_apply_transform_convert_to_list(self, policy_optimizer):
        """Test applying a convert to list transformation."""
        # Create a document with a list-like paragraph
        text = "First point. Second point. Third point."
        doc = [{'type': 'paragraph', 'text': text, 'content': text}]
        
        # Apply the convert to list transformation
        transform = {'type': 'convert_to_list', 'index': 0}
        result = policy_optimizer._apply_transform(doc, transform)
        
        # Should now have a list instead of a paragraph
        assert len(result) == 1
        assert result[0]['type'] == 'list'
        assert result[0]['list_type'] == 'unordered'
        
        # List should have items
        assert len(result[0]['items']) >= 3
        assert all(item.startswith('- ') for item in result[0]['items'])
    
    def test_structure_to_markdown(self, policy_optimizer):
        """Test converting a document structure back to markdown."""
        document_structure = policy_optimizer._parse_document(SAMPLE_MARKDOWN)
        markdown = policy_optimizer._structure_to_markdown(document_structure)
        
        # Should be a non-empty string
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        
        # Should contain key elements from the original markdown
        assert "# Test Document" in markdown
        assert "## Section 1" in markdown
        assert "- Item 1" in markdown
        assert "```python" in markdown
        assert "def test_function():" in markdown
    
    def test_transform(self, policy_optimizer, sample_markdown_file):
        """Test the full transformation process on a markdown file."""
        # Transform the sample file
        result = policy_optimizer.transform(sample_markdown_file)
        
        # Should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should contain key elements from the original markdown
        assert "# Test Document" in result
        assert "## Section" in result
        assert "Item" in result
        
        # Create a file with potential for optimization
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as tmp:
            long_paragraph = "This is a very long paragraph. " * 30
            tmp.write("# Document\n\n" + long_paragraph)
            tmp_path = tmp.name
        
        try:
            # Transform the file with long paragraphs
            optimized = policy_optimizer.transform(tmp_path)
            
            # Should have multiple paragraphs or other changes
            paragraph_count = len(re.findall(r'\n\n', optimized))
            assert paragraph_count > 0
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

def test_optimize_document():
    """Test that we can optimize a document using a policy optimizer."""
    # Create a basic reward function
    def reward_function(document):
        # Simple reward function - reward for having more sections
        heading_count = document.count_elements("heading")
        return {
            "reward": heading_count * 10,
            "explanation": f"Reward for {heading_count} headings"
        }
    
    # Create a transformation
    transformation = HeadingLevelTransformation(min_level=1, increment=0)
    pipeline = TransformationPipeline([transformation])
    
    # Create an optimizer
    optimizer = PolicyOptimizer(
        reward_function=reward_function,
        transformation_pipeline=pipeline,
        max_iterations=3,
        exploration_factor=0.2
    )
    
    # Create a document
    document = Document(content=SAMPLE_MARKDOWN)
    
    # Optimize the document
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        result = optimizer.optimize(document, output_path=tmp_path)
        
        # Check that we have a result
        assert "final_reward" in result
        assert "iterations" in result
        assert "reward_history" in result
        assert len(result["reward_history"]) <= 4  # Initial + max 3 iterations
        
        # Check that the output file exists
        assert os.path.exists(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_multiple_reward_functions_comparison():
    """Test different reward functions and compare their outcomes."""
    # Create a test document
    test_document = """# Test Document for Policy Optimization
    
This document will be optimized using different reward functions to see how they affect the outcome.

## Section 1: Readability Focus
Some text that could be improved in terms of readability.
A very long sentence with many complicated words and nested clauses that make it difficult to follow the main idea without getting lost in the details and confusing structure.

## Section 2: Structure Focus
- item 1
- item 2
* item 3
* item 4

### Subsection A
More content

### Subsection B
Even more content

## Section 3: Style Focus
This paragraph has *italicized* text and **bold** text with some _alternate_ styling.
    """
    
    document = Document(content=test_document)
    
    # Define different reward functions
    reward_functions = {
        "readability": lambda doc: {
            "reward": 100 * (1 / (1 + doc.calculate_readability_metrics().get("flesch_reading_ease", 0) / 100)),
            "explanation": "Optimize for lower Flesch reading ease (simpler text)"
        },
        "structure": lambda doc: {
            "reward": 10 * doc.count_elements("heading") - 5 * abs(3 - doc.count_elements("heading")),
            "explanation": "Optimize for around 3 headings with penalty for deviating"
        },
        "consistency": lambda doc: {
            "reward": -10 * (
                # Penalize mixed list styles
                (1 if "*" in doc.get_content() and "-" in doc.get_content() else 0) + 
                # Penalize mixed emphasis styles
                (1 if "*" in doc.get_content() and "_" in doc.get_content() else 0)
            ),
            "explanation": "Optimize for consistent list and emphasis styling"
        },
        "combined": lambda doc: (lambda readability, consistency, structure: {
            "reward": readability + consistency + structure,
            "explanation": "Combined reward function with weighted components"
        })(
            50 * (1 / (1 + doc.calculate_readability_metrics().get("flesch_reading_ease", 0) / 100)),
            -5 * (
                (1 if "*" in doc.get_content() and "-" in doc.get_content() else 0) + 
                (1 if "*" in doc.get_content() and "_" in doc.get_content() else 0)
            ),
            5 * doc.count_elements("heading") - 2 * abs(3 - doc.count_elements("heading"))
        )
    }
    
    # Create transformations to apply
    transformations = [
        HeadingLevelTransformation(min_level=1, increment=0),  # Can increase or decrease headings
        ListFormatTransformation(target_type="unordered", bullet_style="-"),  # Standardize lists
        TextStyleTransformation(bold_style="**", italic_style="_")  # Standardize text styling
    ]
    
    # Create a pipeline with these transformations
    pipeline = TransformationPipeline(transformations)
    
    # Optimize the document using each reward function
    results = {}
    for name, reward_function in reward_functions.items():
        # Create an optimizer with the current reward function
        optimizer = PolicyOptimizer(
            reward_function=reward_function,
            transformation_pipeline=pipeline,
            max_iterations=5,
            exploration_factor=0.3
        )
        
        # Run optimization
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Optimize the document
            optimization_result = optimizer.optimize(document, output_path=tmp_path)
            
            # Read the optimized document
            optimized_doc = Document(tmp_path)
            optimized_content = optimized_doc.get_content()
            
            # Store the results
            results[name] = {
                "content": optimized_content,
                "reward": optimization_result["final_reward"],
                "iterations": optimization_result["iterations"],
                "reward_history": optimization_result["reward_history"],
                "metrics": optimized_doc.evaluate_metrics()
            }
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    # Save the results to the outputs directory
    output_dir = Path("tests/outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Create a markdown report
    report_path = output_dir / "policy_optimization_comparison.md"
    with open(report_path, "w") as f:
        f.write("# Policy Optimization Comparison\n\n")
        f.write("This report compares the results of optimizing a document using different reward functions.\n\n")
        
        # Original document
        f.write("## Original Document\n\n")
        f.write("```markdown\n")
        f.write(test_document)
        f.write("\n```\n\n")
        
        # Write metrics for the original document
        original_metrics = document.evaluate_metrics()
        f.write("### Original Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        for metric, value in sorted(original_metrics.items()):
            f.write(f"| {metric} | {value} |\n")
        f.write("\n")
        
        # Write results for each optimization
        f.write("## Optimization Results\n\n")
        
        for name, result in results.items():
            f.write(f"### {name.capitalize()} Optimization\n\n")
            f.write(f"**Final Reward**: {result['reward']:.2f}\n\n")
            f.write(f"**Iterations**: {result['iterations']}\n\n")
            
            f.write("#### Optimized Document\n\n")
            f.write("```markdown\n")
            f.write(result["content"])
            f.write("\n```\n\n")
            
            f.write("#### Metrics\n\n")
            f.write("| Metric | Original | Optimized | Change |\n")
            f.write("|--------|----------|-----------|-------|\n")
            
            for metric, value in sorted(result["metrics"].items()):
                original_value = original_metrics.get(metric, 0)
                change = value - original_value
                change_str = f"{change:+g}" if isinstance(change, (int, float)) else "N/A"
                
                f.write(f"| {metric} | {original_value} | {value} | {change_str} |\n")
            
            f.write("\n#### Reward History\n\n")
            f.write("| Iteration | Reward |\n")
            f.write("|-----------|-------|\n")
            
            for i, reward in enumerate(result["reward_history"]):
                f.write(f"| {i} | {reward:.2f} |\n")
            
            f.write("\n")
    
    # Create visualization of the reward history
    plt.figure(figsize=(10, 6))
    
    for name, result in results.items():
        plt.plot(result["reward_history"], marker='o', linestyle='-', label=name.capitalize())
    
    plt.xlabel('Iteration')
    plt.ylabel('Reward')
    plt.title('Reward History for Different Optimization Strategies')
    plt.legend()
    plt.grid(True)
    
    viz_path = output_dir / "policy_optimization_rewards.png"
    plt.savefig(viz_path)
    plt.close()
    
    # Create a JSON file with detailed metrics
    json_path = output_dir / "policy_optimization_results.json"
    
    # Convert numpy arrays to lists for JSON serialization
    json_results = {}
    for name, result in results.items():
        json_results[name] = {
            "reward": float(result["reward"]),
            "iterations": result["iterations"],
            "reward_history": [float(r) for r in result["reward_history"]],
            "metrics": result["metrics"]
        }
    
    with open(json_path, "w") as f:
        json.dump({
            "original_metrics": original_metrics,
            "optimization_results": json_results
        }, f, indent=2)
    
    # Create a metrics comparison visualization
    common_metrics = ['word_count', 'sentence_count', 'average_sentence_length', 
                     'heading_count', 'list_count', 'code_block_count']
    
    # Prepare data for plotting
    metrics_data = {'Original': [original_metrics.get(m, 0) for m in common_metrics]}
    
    for name, result in results.items():
        metrics_data[name.capitalize()] = [result["metrics"].get(m, 0) for m in common_metrics]
    
    # Create DataFrame
    df = pd.DataFrame(metrics_data, index=common_metrics)
    
    # Plot
    ax = df.plot(kind='bar', figsize=(12, 6), width=0.8)
    plt.ylabel('Value')
    plt.title('Document Metrics Comparison Across Optimization Strategies')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    metrics_viz_path = output_dir / "policy_optimization_metrics.png"
    plt.savefig(metrics_viz_path)
    plt.close()
    
    # Add the visualizations to the report
    with open(report_path, "a") as f:
        f.write("## Visualizations\n\n")
        f.write("### Reward History\n\n")
        f.write("![Reward History](policy_optimization_rewards.png)\n\n")
        f.write("### Metrics Comparison\n\n")
        f.write("![Metrics Comparison](policy_optimization_metrics.png)\n\n")
        
        f.write("## Analysis\n\n")
        
        # Compare the effectiveness of different reward functions
        best_reward = max(results.items(), key=lambda x: x[1]["reward"])
        most_iterations = max(results.items(), key=lambda x: x[1]["iterations"])
        
        f.write(f"- The **{best_reward[0].capitalize()}** optimization achieved the highest reward ({best_reward[1]['reward']:.2f}).\n")
        f.write(f"- The **{most_iterations[0].capitalize()}** optimization required the most iterations ({most_iterations[1]['iterations']}).\n\n")
        
        # Analyze how different reward functions affected the document structure
        f.write("### Structural Changes\n\n")
        for name, result in results.items():
            heading_change = result["metrics"].get("heading_count", 0) - original_metrics.get("heading_count", 0)
            list_change = result["metrics"].get("list_count", 0) - original_metrics.get("list_count", 0)
            
            f.write(f"- **{name.capitalize()}**: Heading count {heading_change:+d}, List count {list_change:+d}\n")
    
    # Assertions for test verification
    assert os.path.exists(report_path)
    assert os.path.exists(viz_path)
    assert os.path.exists(json_path)
    assert os.path.exists(metrics_viz_path)
    assert len(results) == len(reward_functions)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 