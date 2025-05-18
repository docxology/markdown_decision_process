"""Tests for the BeliefUpdater module."""

import os
import pytest
import tempfile
from pathlib import Path
import numpy as np
import json

from mdp.belief_updater import BeliefUpdater
from mdp.state_space import StateSpace

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
    """Fixture that creates a pre-configured StateSpace."""
    space = StateSpace()
    space.parse_markdown(SAMPLE_MARKDOWN)
    return space

@pytest.fixture
def belief_updater():
    """Fixture that creates a BeliefUpdater with default settings."""
    return BeliefUpdater()

class TestBeliefUpdater:
    """Tests for the BeliefUpdater class."""
    
    def test_initialization(self):
        """Test basic initialization of BeliefUpdater."""
        updater = BeliefUpdater()
        assert hasattr(updater, 'belief_state')
        assert hasattr(updater, 'confidence')
        assert 0 <= updater.noise_factor <= 1
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        noise_factor = 0.1
        prior_beliefs = {'structure': 0.7, 'readability': 0.9}
        
        updater = BeliefUpdater(
            noise_factor=noise_factor,
            prior_beliefs=prior_beliefs
        )
        
        assert updater.noise_factor == noise_factor
        for belief, value in prior_beliefs.items():
            assert updater.belief_state.get(belief) == value
    
    def test_update_belief(self):
        """Test updating a single belief value."""
        updater = BeliefUpdater()
        belief_key = 'structure'
        belief_value = 0.8
        
        # Update the belief
        updater.update_belief(belief_key, belief_value)
        
        # Belief should be updated
        assert updater.belief_state.get(belief_key) == belief_value
        
    def test_update_from_observation(self):
        """Test updating beliefs from an observation."""
        updater = BeliefUpdater()
        observation = {
            'structure': 0.7,
            'readability': 0.8,
            'consistency': 0.6
        }
        
        # Record initial beliefs if any
        initial_beliefs = updater.belief_state.copy()
        
        # Update from observation
        updater.update_from_observation(observation)
        
        # Beliefs should be updated
        for key, value in observation.items():
            assert updater.belief_state.get(key) != initial_beliefs.get(key, 0)
    
    def test_get_belief(self):
        """Test getting a belief value."""
        updater = BeliefUpdater()
        belief_key = 'structure'
        belief_value = 0.8
        
        # Set the belief
        updater.update_belief(belief_key, belief_value)
        
        # Should return the set value
        assert updater.get_belief(belief_key) == belief_value
        
        # Should return default for unknown beliefs
        assert updater.get_belief('unknown_belief') == 0
    
    def test_get_all_beliefs(self):
        """Test getting all beliefs."""
        updater = BeliefUpdater()
        beliefs = {
            'structure': 0.7,
            'readability': 0.8,
            'consistency': 0.6
        }
        
        # Set beliefs
        for key, value in beliefs.items():
            updater.update_belief(key, value)
        
        # Get all beliefs
        all_beliefs = updater.get_all_beliefs()
        
        # Should return all set beliefs
        for key, value in beliefs.items():
            assert key in all_beliefs
            assert all_beliefs[key] == value
    
    def test_apply_noise(self):
        """Test applying noise to belief values."""
        updater = BeliefUpdater(noise_factor=0.5)
        belief_key = 'structure'
        belief_value = 0.8
        
        # Set the belief
        updater.update_belief(belief_key, belief_value)
        
        # Get noisy belief for multiple iterations
        np.random.seed(42)  # Set seed for reproducibility
        noisy_values = [updater.get_noisy_belief(belief_key) for _ in range(10)]
        
        # Should return different values due to noise
        assert len(set(noisy_values)) > 1
        
        # Values should be close to original but different
        for value in noisy_values:
            assert value != belief_value  # Different due to noise
            assert 0 <= value <= 1  # Within valid range
    
    def test_analyze_document(self, state_space):
        """Test analyzing a document to generate beliefs."""
        updater = BeliefUpdater()
        
        # Analyze the document
        beliefs = updater.analyze_document(state_space)
        
        # Should return a dictionary of beliefs
        assert isinstance(beliefs, dict)
        assert len(beliefs) > 0
        
        # Belief values should be between 0 and 1
        for value in beliefs.values():
            assert 0 <= value <= 1
    
    def test_update_confidence(self):
        """Test updating confidence based on observations."""
        updater = BeliefUpdater()
        initial_confidence = updater.confidence
        
        # Update from an observation
        updater.update_from_observation({'structure': 0.7})
        
        # Confidence should increase
        assert updater.confidence != initial_confidence
    
    def test_reset_beliefs(self):
        """Test resetting beliefs to default values."""
        updater = BeliefUpdater()
        
        # Set some beliefs
        updater.update_belief('structure', 0.7)
        updater.update_belief('readability', 0.8)
        
        # Reset beliefs
        updater.reset_beliefs()
        
        # Beliefs should be reset
        assert updater.get_belief('structure') == 0
        assert updater.get_belief('readability') == 0
    
    def test_save_and_load_beliefs(self):
        """Test saving and loading belief states."""
        updater = BeliefUpdater()
        
        # Set some beliefs
        test_beliefs = {
            'structure': 0.75,
            'readability': 0.82,
            'coherence': 0.67,
            'consistency': 0.91
        }
        
        for belief, value in test_beliefs.items():
            updater.update_belief(belief, value)
        
        # Save beliefs to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            updater.save_beliefs(tmp_path)
            
            # Save a copy to the outputs directory for inspection
            output_dir = Path('tests/outputs')
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / 'belief_states.json'
            
            # Generate the output file with detailed information
            with open(output_path, 'w') as f:
                # Save the original belief state for comparison
                output_data = {
                    'original_beliefs': updater.get_all_beliefs(),
                    'confidence': updater.confidence,
                    'timestamp': str(Path(tmp_path).stat().st_mtime)
                }
                
                # Create a new updater and load the beliefs
                new_updater = BeliefUpdater()
                new_updater.load_beliefs(tmp_path)
                
                # Add the loaded belief state to the output
                output_data['loaded_beliefs'] = new_updater.get_all_beliefs()
                output_data['loaded_confidence'] = new_updater.confidence
                
                # Check if beliefs were preserved
                output_data['beliefs_match'] = updater.get_all_beliefs() == new_updater.get_all_beliefs()
                output_data['confidence_match'] = updater.confidence == new_updater.confidence
                
                # Write the output
                json.dump(output_data, f, indent=2)
            
            # Now do the actual test assertions
            new_updater = BeliefUpdater()
            new_updater.load_beliefs(tmp_path)
            
            # Beliefs should be preserved
            assert new_updater.get_all_beliefs() == updater.get_all_beliefs()
            assert new_updater.confidence == updater.confidence
            
        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_combine_beliefs(self):
        """Test combining beliefs from multiple sources."""
        updater = BeliefUpdater()
        
        # Set initial beliefs
        updater.update_belief('structure', 0.5)
        updater.update_belief('readability', 0.6)
        
        # Combine with new beliefs
        new_beliefs = {
            'structure': 0.7,
            'consistency': 0.8
        }
        
        updater.combine_beliefs(new_beliefs)
        
        # Beliefs should be combined
        assert updater.get_belief('structure') != 0.5  # Changed
        assert updater.get_belief('readability') == 0.6  # Unchanged
        assert updater.get_belief('consistency') == 0.8  # Added
    
    def test_calculate_entropy(self):
        """Test calculating entropy of belief state."""
        updater = BeliefUpdater()
        
        # Set some beliefs
        updater.update_belief('structure', 0.5)  # Maximum uncertainty
        updater.update_belief('readability', 0.9)  # High confidence
        updater.update_belief('consistency', 0.1)  # High confidence
        
        # Calculate entropy
        entropy = updater.calculate_entropy()
        
        # Entropy should be a numeric value
        assert isinstance(entropy, float)
        
        # Entropy should be positive
        assert entropy >= 0

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 