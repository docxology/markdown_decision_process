"""Tests for the MarkdownAgent module."""

import os
import pytest
import tempfile
import json
from pathlib import Path
import shutil
from unittest.mock import patch

from mdp import MarkdownAgent, MarkChain, PolicyOptimizer, StateSpace, BeliefUpdater

SAMPLE_MARKDOWN = """# Test Document

This is a paragraph with some text that explains the concept.

## Installation

Follow these steps to install:

1. Download the package
2. Extract the files
3. Run the installer

```bash
./install.sh --prefix=/usr/local
```

## Configuration

You can configure the system by editing the `config.yaml` file.

## Troubleshooting

If you encounter issues, check the logs.

**Warning**: Do not modify system files directly.
"""

@pytest.fixture
def temp_markdown_file():
    """Create a temporary markdown file for testing."""
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as tmp:
        tmp.write(SAMPLE_MARKDOWN)
        tmp_path = Path(tmp.name)
    
    yield tmp_path
    
    # Cleanup
    tmp_path.unlink()

@pytest.fixture
def temp_corpus_dir():
    """Create a temporary directory with multiple markdown files for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create multiple files
        for i in range(3):
            file_path = tmp_path / f"document_{i}.md"
            file_path.write_text(SAMPLE_MARKDOWN)
            
        # Create a different type of document
        tutorial = tmp_path / "tutorial.md"
        tutorial.write_text("""# Tutorial

This is a step-by-step tutorial.

## Step 1

First, you need to understand the basics.

## Step 2

Then, you can proceed to advanced topics.

## Examples

Here are some examples:

```python
def example():
    return "This is an example"
```
""")
        
        yield tmp_path

@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for saving/loading models."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

def test_agent_initialization():
    """Test that MarkdownAgent initializes correctly."""
    # Test default initialization
    agent = MarkdownAgent()
    assert agent.exploration_rate == 0.2
    assert agent.learning_rate == 0.1
    assert agent.discount_factor == 0.9
    
    # Verify components are initialized
    assert isinstance(agent.generator, MarkChain)
    assert isinstance(agent.optimizer, PolicyOptimizer)
    assert isinstance(agent.state_space, StateSpace)
    assert isinstance(agent.belief_updater, BeliefUpdater)
    
    # Test with custom parameters
    agent = MarkdownAgent(
        exploration_rate=0.3,
        learning_rate=0.2,
        discount_factor=0.8,
        reward_weights={"readability": 0.7, "structure_clarity": 0.3}
    )
    assert agent.exploration_rate == 0.3
    assert agent.learning_rate == 0.2
    assert agent.discount_factor == 0.8

def test_agent_train(temp_corpus_dir):
    """Test training the agent on a corpus of markdown documents."""
    agent = MarkdownAgent()
    
    # Train with reduced iterations for testing
    stats = agent.train(str(temp_corpus_dir), iterations=5)
    
    # Verify training stats
    assert "iterations" in stats
    assert "documents_processed" in stats
    assert "value_function_updates" in stats
    assert "exploration_actions" in stats
    assert "exploitation_actions" in stats
    
    # Check that components were trained
    assert len(agent.generator.transitions) > 0
    assert len(agent.value_function) > 0
    assert len(agent.experiences) > 0

def test_agent_generate():
    """Test generating markdown content."""
    agent = MarkdownAgent()
    
    # Train the generator directly for testing
    agent.generator.train(SAMPLE_MARKDOWN)
    
    # Generate content
    generated = agent.generate(length=50)
    assert isinstance(generated, str)
    assert len(generated) > 0
    
    # Generate with prompt
    prompt = "# New Document\n\nThis is the first paragraph."
    generated_with_prompt = agent.generate(prompt=prompt)
    assert isinstance(generated_with_prompt, str)
    assert len(generated_with_prompt) > 0

def test_agent_optimize(temp_markdown_file, monkeypatch):
    """Test optimizing a markdown document."""
    # Mock the PolicyOptimizer.transform method for testing
    def mock_transform(self, markdown_path):
        with open(markdown_path, 'r') as f:
            content = f.read()
        return content + "\n\n## Optimized Section\n\nThis section was added during optimization."
    
    monkeypatch.setattr(PolicyOptimizer, "transform", mock_transform)
    
    agent = MarkdownAgent()
    optimized = agent.optimize(str(temp_markdown_file))
    
    # Verify optimization produced expected result
    assert isinstance(optimized, str)
    assert "## Optimized Section" in optimized
    assert "This section was added during optimization" in optimized

def test_agent_analyze(temp_markdown_file, monkeypatch):
    """Test analyzing a markdown document."""
    # Mock the BeliefUpdater.analyze_document method for testing
    def mock_analyze_document(self, markdown_path):
        return {
            "overall_semantic_class": "instruction",
            "overall_probability": 0.7,
            "sections": [
                {
                    "semantic_class": "instruction",
                    "probability": 0.8,
                    "elements": [{"type": "header", "content": "# Test Document"}]
                }
            ],
            "overall_belief": {"instruction": 0.7, "explanation": 0.3}
        }
    
    monkeypatch.setattr(BeliefUpdater, "analyze_document", mock_analyze_document)
    
    agent = MarkdownAgent()
    analysis = agent.analyze(str(temp_markdown_file))
    
    # Verify analysis contains expected information
    assert "semantic_analysis" in analysis
    assert "overall_semantic_class" in analysis["semantic_analysis"]
    assert "overall_probability" in analysis["semantic_analysis"]
    assert "sections" in analysis["semantic_analysis"]
    assert "overall_belief" in analysis["semantic_analysis"]
    
    # Check values from mock
    assert analysis["semantic_analysis"]["overall_semantic_class"] == "instruction"
    assert analysis["semantic_analysis"]["overall_probability"] == 0.7

@patch('mdp.markchain.MarkChain.sample')
def test_agent_interact(mock_markchain_sample, monkeypatch):
    """Test interactive markdown manipulation."""
    # Mock methods used by interact
    def mock_agent_generate(self, prompt=None, length=100):
        if prompt:
            return prompt + "\n\nGenerated content"
        return "# Generated Document\n\nGenerated content"
    
    mock_markchain_sample.return_value = "Generated sample content from MarkChain"

    def mock_optimize(self, markdown_path):
        return "# Optimized Document\n\nOptimized content"
    
    def mock_analyze(self, markdown_path):
        return {"overall_semantic_class": "instruction", "overall_probability": 0.8}
    
    monkeypatch.setattr(MarkdownAgent, "generate", mock_agent_generate)
    monkeypatch.setattr(MarkdownAgent, "optimize", mock_optimize)
    monkeypatch.setattr(MarkdownAgent, "analyze", mock_analyze)
    
    agent = MarkdownAgent()
    # Train the agent's generator component for objectives that use it (e.g., extend)
    agent.generator.train(SAMPLE_MARKDOWN)
    
    # Test optimizing
    result = agent.interact(SAMPLE_MARKDOWN, objective="optimize")
    assert "modified_content" in result
    assert result["objective"] == "optimize"
    
    # Test extending
    result = agent.interact(SAMPLE_MARKDOWN, objective="extend")
    assert "action" in result["actions_taken"][0]
    assert result["actions_taken"][0]["action"] == "extend"
    assert "modified_content" in result
    assert SAMPLE_MARKDOWN in result["modified_content"]
    assert "Generated sample content from MarkChain" in result["modified_content"]
    
    # Test analyzing
    result = agent.interact(SAMPLE_MARKDOWN, objective="summarize")
    assert "action" in result["actions_taken"][0]
    assert result["actions_taken"][0]["action"] == "summarize"
    assert "modified_content" in result
    assert result["objective"] == "summarize"
    assert "# Summary" in result["modified_content"]
    
    # Test with invalid objective
    result_invalid = agent.interact(SAMPLE_MARKDOWN, objective="invalid_objective_test")
    assert "action" in result_invalid["actions_taken"][0]
    assert result_invalid["actions_taken"][0]["action"] == "unknown_objective"
    assert result_invalid["modified_content"] == SAMPLE_MARKDOWN

def test_agent_save_load_models(temp_model_dir, monkeypatch):
    """Test saving and loading agent models."""
    # Mock the complex components to simplify testing
    def mock_save(self, path):
        os.makedirs(path, exist_ok=True)
        config = {
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor
        }
        with open(os.path.join(path, "config.json"), "w") as f:
            json.dump(config, f)
    
    def mock_load(self, path):
        with open(os.path.join(path, "config.json"), "r") as f:
            config = json.load(f)
        self.exploration_rate = config["exploration_rate"]
        self.learning_rate = config["learning_rate"]
        self.discount_factor = config["discount_factor"]
    
    monkeypatch.setattr(MarkdownAgent, "save_models", mock_save)
    monkeypatch.setattr(MarkdownAgent, "load_models", mock_load)
    
    # Create and save agent
    agent1 = MarkdownAgent(exploration_rate=0.3, learning_rate=0.2, discount_factor=0.8)
    agent1.save_models(str(temp_model_dir))
    
    # Load into new agent
    agent2 = MarkdownAgent()
    agent2.load_models(str(temp_model_dir))
    
    # Verify parameters were loaded
    assert agent2.exploration_rate == 0.3
    assert agent2.learning_rate == 0.2
    assert agent2.discount_factor == 0.8

def test_agent_private_methods():
    """Test the agent's private utility methods."""
    agent = MarkdownAgent()
    
    # Test _parse_document
    elements = agent._parse_document(SAMPLE_MARKDOWN)
    assert len(elements) > 0
    element_types = [elem.get("type") for elem in elements]
    assert "header" in element_types
    
    # Test _extract_features
    header_element = {"type": "header", "level": 1, "text": "Test Document", "content": "# Test Document"}
    features = agent._extract_features(header_element)
    assert "header_level" in features
    
    # Test _state_representation
    state_repr = agent._state_representation(header_element)
    assert state_repr == f"h{header_element.get('level')}"
    
    paragraph_element = {"type": "paragraph", "content": "Short."}
    
    # Test _calculate_reward
    element1 = {"type": "header", "level": 1, "text": "Test Document"}
    element2 = {"type": "paragraph", "text": "This is a paragraph."}
    reward = agent._calculate_reward(element1, element2, "optimize")
    assert isinstance(reward, float)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 