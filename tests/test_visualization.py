"""
Tests for the visualization module.
"""

import pytest
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import networkx as nx
from unittest.mock import patch
import tempfile
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud, STOPWORDS

from mdp.visualization import (
    plot_document_metrics,
    plot_transitions,
    plot_document_structure,
    plot_readability_comparison,
    plot_filtered_state_space
)
from mdp.document import Document
from mdp.markchain import MarkChain
from mdp.state_space import StateSpace
from mdp.quality import DocumentQuality

# Sample markdown for testing
SAMPLE_MARKDOWN = """# Test Document

This is a test document with some **important** content.

## Section 1

Here's a list:
* List item 1
* List item 2

```python
def test():
    print("Hello World")
    return True
```

## Section 2

Another paragraph with [a link](https://example.com).
"""

@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    return Document(content=SAMPLE_MARKDOWN)

@pytest.fixture
def sample_metrics_dict():
    """Create sample metrics dictionary for testing."""
    return {
        "Document 1": {
            "readability": {
                "flesch_reading_ease": 70.5,
                "flesch_kincaid_grade": 8.2
            },
            "information_density": {
                "lexical_diversity": 0.75,
                "entropy": 4.2
            },
            "structural_balance": {
                "heading_distribution": 0.85,
                "content_variety": 0.65
            }
        },
        "Document 2": {
            "readability": {
                "flesch_reading_ease": 65.0,
                "flesch_kincaid_grade": 9.5
            },
            "information_density": {
                "lexical_diversity": 0.68,
                "entropy": 3.9
            },
            "structural_balance": {
                "heading_distribution": 0.75,
                "content_variety": 0.70
            }
        }
    }

@pytest.fixture
def trained_chain():
    """Create a trained MarkChain for testing."""
    chain = MarkChain(order=1)
    chain.train(SAMPLE_MARKDOWN)
    return chain

@pytest.fixture
def multiple_documents():
    """Create a dictionary with multiple Document instances."""
    return {
        "Doc 1": Document(content=SAMPLE_MARKDOWN),
        "Doc 2": Document(content="""# Another Document
        
This is another document for testing comparison visualizations.

## Section A

* Bullet point 1
* Bullet point 2

## Section B

Final paragraph in the second document.
""")
    }

@pytest.fixture
def sample_markchain():
    """Create a sample trained MarkChain instance for testing."""
    # Create and train a simple model
    model = MarkChain(order=1)
    model.train("""# Sample Document
    
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
""")
    return model

@pytest.fixture
def metrics_dict():
    """Create a sample metrics dictionary for testing."""
    return {
        "doc1": {
            "readability": {
                "flesch_reading_ease": 65.0,
                "flesch_kincaid_grade": 8.5,
            },
            "information_density": {
                "lexical_diversity": 0.75,
                "entropy": 4.2,
            },
            "structural_balance": {
                "heading_distribution": 0.8,
                "content_variety": 0.6,
            }
        },
        "doc2": {
            "readability": {
                "flesch_reading_ease": 75.0,
                "flesch_kincaid_grade": 7.2,
            },
            "information_density": {
                "lexical_diversity": 0.65,
                "entropy": 3.8,
            },
            "structural_balance": {
                "heading_distribution": 0.7,
                "content_variety": 0.5,
            }
        }
    }

class TestVisualization:
    """Tests for the visualization module."""
    
    def test_plot_document_metrics(self, metrics_dict):
        """Test the plot_document_metrics function."""
        fig = plot_document_metrics(metrics_dict)
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 3
        plt.close(fig)
    
    def test_plot_transitions(self, sample_markchain):
        """Test the plot_transitions function."""
        fig = plot_transitions(sample_markchain, top_n=5)
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)
    
    def test_plot_document_structure(self):
        """Test the plot_document_structure function."""
        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as f:
            f.write("""# Test Document
            
## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection 2.1

More content.
""")
            temp_path = f.name
        
        try:
            fig = plot_document_structure(temp_path)
            assert isinstance(fig, plt.Figure)
            assert len(fig.axes) == 1
            plt.close(fig)
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_plot_readability_comparison(self):
        """Test the plot_readability_comparison function."""
        # Create temporary markdown files
        files = {}
        for name, content in [
            ("simple", """# Simple Document\n\nThis is easy to read. It has short sentences. The words are common.\n\n"""),
            ("complex", """# Complex Document\n\nThe utilization of multisyllabic lexicon in conjunction with intricate syntactical structures can significantly augment the perceived complexity of written communication.\n\n""")
        ]:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as f:
                f.write(content)
                files[name] = f.name
        
        try:
            fig = plot_readability_comparison(files)
            assert isinstance(fig, plt.Figure)
            assert len(fig.axes) == 4  # Function returns a figure with 4 readability metrics
            plt.close(fig)
        finally:
            # Clean up
            for path in files.values():
                os.unlink(path)
    
    def test_plot_filtered_state_space(self, sample_markchain):
        """Test the plot_filtered_state_space function."""
        # Test with heading filter
        def header_filter(state):
            if isinstance(state, tuple) and len(state) == 1:
                return state[0].startswith('#')
            return False
        
        fig = plot_filtered_state_space(
            sample_markchain,
            filter_func=header_filter
        )
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)
        
        # Test with list filter and highlighting
        def list_filter(state):
            if isinstance(state, tuple) and len(state) == 1:
                text = state[0].strip()
                return text.startswith(('-', '*'))
            return False
        
        def bullet_highlight(state):
            if isinstance(state, tuple) and len(state) == 1:
                text = state[0].strip()
                return text.startswith('-')
            return False
        
        fig = plot_filtered_state_space(
            sample_markchain,
            filter_func=list_filter,
            highlight_func=bullet_highlight
        )
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)
        
        # Test with code filter
        def code_filter(state):
            if isinstance(state, tuple) and len(state) == 1:
                return '```' in state[0]
            return False
        
        fig = plot_filtered_state_space(
            sample_markchain,
            filter_func=code_filter,
            include_isolated=True
        )
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        plt.close(fig)
    
    def test_plot_filtered_state_space_errors(self, sample_markchain):
        """Test error handling in plot_filtered_state_space function."""
        # Test with filter that matches no states
        def no_match_filter(state):
            return False
        
        with pytest.raises(ValueError, match="No states match the provided filter criteria"):
            plot_filtered_state_space(
                sample_markchain,
                filter_func=no_match_filter
            )
        
        # Test with untrained model
        untrained_model = MarkChain(order=1)
        
        with pytest.raises(ValueError, match="MarkChain must be trained before visualizing state space"):
            plot_filtered_state_space(untrained_model) 