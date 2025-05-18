"""
Tests for the visualization exporter functionality.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest
import matplotlib.pyplot as plt
import numpy as np

from mdp.export import VisualizationExporter
from mdp.state_space import StateSpace
from mdp.document import Document
from mdp.markchain import MarkChain
from mdp.quality import DocumentQuality
from mdp.pandoc import PandocNotFoundError


SAMPLE_MARKDOWN = """# Test Document

This is a sample markdown document for testing export functionality.

## Introduction

Markdown is a lightweight markup language with plain text formatting syntax.

## Features

- Easy to learn
- Simple syntax
- Widely supported

### Code Blocks

```python
def hello_world():
    print("Hello, World!")
```

## Conclusion

Markdown is great for documentation.
"""


class TestVisualizationExporter(unittest.TestCase):
    """Test case for the VisualizationExporter class."""
    
    def setUp(self):
        """Set up test resources."""
        # Create a temporary directory for output files
        self.test_dir = tempfile.mkdtemp()
        self.exporter = VisualizationExporter(output_dir=self.test_dir)
        
        # Create a test document
        self.doc_path = os.path.join(self.test_dir, "test_document.md")
        with open(self.doc_path, "w") as f:
            f.write(SAMPLE_MARKDOWN)
        
        self.document = Document(file_path=self.doc_path)
        
        # Create a sample figure
        self.fig = plt.figure(figsize=(8, 6))
        ax = self.fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Sample Plot")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
    
    def tearDown(self):
        """Clean up test resources."""
        plt.close(self.fig)
        shutil.rmtree(self.test_dir)
    
    def test_export_figure(self):
        """Test exporting a matplotlib figure to various formats."""
        formats = ["png", "pdf", "svg"]
        
        for fmt in formats:
            output_path = os.path.join(self.test_dir, f"sample_figure.{fmt}")
            result = self.exporter.export_figure(
                fig=self.fig, 
                output_path=output_path,
                format=fmt
            )
            
            assert os.path.exists(result)
            assert str(result).endswith(f".{fmt}")
    
    def test_export_to_html(self):
        """Test exporting a figure to HTML."""
        output_path = os.path.join(self.test_dir, "sample_figure.html")
        result = self.exporter.export_to_html(
            fig=self.fig,
            output_path=output_path,
            title="Sample Figure HTML Export",
            include_interactive=False  # Use static for testing
        )
        
        assert os.path.exists(result)
        assert str(result).endswith(".html")
        
        # Check content
        with open(result, "r") as f:
            content = f.read()
            assert "<title>Sample Figure HTML Export</title>" in content
            assert "<img src=\"data:image/png;base64," in content
    
    def test_embed_in_markdown(self):
        """Test embedding a figure in a markdown document."""
        output_path = os.path.join(self.test_dir, "figure_markdown.md")
        result = self.exporter.embed_in_markdown(
            fig=self.fig,
            output_markdown_path=output_path,
            inline=True
        )
        
        assert os.path.exists(result)
        assert str(result).endswith(".md")
        
        # Check that the image file was created
        fig_path = str(result).replace(".md", ".png")
        assert os.path.exists(fig_path)
        
        # Check markdown content
        with open(result, "r") as f:
            content = f.read()
            assert "![Visualization]" in content
    
    def test_export_document_structure(self):
        """Test exporting document structure visualization."""
        output_path = os.path.join(self.test_dir, "document_structure.png")
        result = self.exporter.export_document_structure(
            document=self.document,
            output_path=output_path
        )
        
        assert os.path.exists(result)
        assert str(result).endswith(".png")
    
    def test_state_space_export(self):
        """Test exporting state space visualization."""
        # Create and populate a state space
        state_space = StateSpace()
        state_space.parse_markdown_file(self.doc_path)
        
        output_path = os.path.join(self.test_dir, "state_space.png")
        result = self.exporter.export_state_space(
            state_space=state_space,
            output_path=output_path,
            title="Test State Space"
        )
        
        assert os.path.exists(result)
        assert str(result).endswith(".png")
    
    def test_export_analysis_report(self):
        """Test exporting a comprehensive analysis report."""
        # Skip if pandoc is not available
        try:
            output_path = os.path.join(self.test_dir, "analysis_report.md")
            result = self.exporter.export_analysis_report(
                document=self.document,
                output_path=output_path,
                format="md"  # Use markdown for testing (doesn't require pandoc)
            )
            
            assert os.path.exists(result)
            assert str(result).endswith(".md")
            
            # Check report content
            with open(result, "r") as f:
                content = f.read()
                assert "# Analysis Report" in content
                assert "## Document Summary" in content
                assert "## Quality Metrics" in content
                assert "## Recommendations" in content
                
        except (ImportError, PandocNotFoundError):
            pytest.skip("Skipping test_export_analysis_report - pandoc or dependencies not available")
    
    @pytest.mark.skipif(shutil.which("pandoc") is None, 
                       reason="Pandoc not installed")
    def test_document_with_visualizations(self):
        """Test exporting a document with embedded visualizations."""
        # Create a document with visualization markers
        doc_content = """# Test Document with Visualizations
        
This document contains markers for visualizations.

## First Visualization

<!-- VISUALIZATION: FIG1 -->

## Second Visualization

<!-- VISUALIZATION: FIG2 -->

## Conclusion

The visualizations help understand the document structure.
"""
        test_doc_path = os.path.join(self.test_dir, "doc_with_viz.md")
        with open(test_doc_path, "w") as f:
            f.write(doc_content)
        
        # Create two different figures
        fig1 = plt.figure(figsize=(8, 6))
        ax1 = fig1.add_subplot(111)
        ax1.plot([1, 2, 3], [4, 5, 6])
        ax1.set_title("Figure 1")
        
        fig2 = plt.figure(figsize=(6, 4))
        ax2 = fig2.add_subplot(111)
        ax2.bar(["A", "B", "C"], [5, 7, 3])
        ax2.set_title("Figure 2")
        
        # List of visualizations (marker, figure, kwargs)
        visualizations = [
            ("<!-- VISUALIZATION: FIG1 -->", fig1, {"format": "png"}),
            ("<!-- VISUALIZATION: FIG2 -->", fig2, {"format": "png"})
        ]
        
        try:
            output_path = os.path.join(self.test_dir, "doc_with_viz")
            result = self.exporter.export_document_with_visualizations(
                document=test_doc_path,
                output_path=output_path,
                visualizations=visualizations,
                to_format="pdf"
            )
            
            assert os.path.exists(result)
            assert str(result).endswith(".pdf")
            
        except PandocNotFoundError:
            pytest.skip("Pandoc not installed, skipping PDF export test")
        finally:
            plt.close(fig1)
            plt.close(fig2)

class TestVisualizationExport(unittest.TestCase):
    """Test the export functionality."""
    
    def setUp(self):
        """Set up test resources."""
        # Create a temporary directory for output files
        self.test_dir = tempfile.mkdtemp()
        self.exporter = VisualizationExporter(output_dir=self.test_dir)
        
        # Create a test document
        self.doc_path = os.path.join(self.test_dir, "test_document.md")
        with open(self.doc_path, "w") as f:
            f.write("# Test Document\n\nThis is a test document.")
        
        self.document = Document(file_path=self.doc_path)
        
        # Create a sample figure
        self.fig = plt.figure(figsize=(8, 6))
        ax = self.fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_title("Sample Plot")
    
    def tearDown(self):
        """Clean up test resources."""
        plt.close(self.fig)
        shutil.rmtree(self.test_dir)
    
    def test_export_to_png(self):
        """Test exporting a figure to PNG."""
        output_path = os.path.join(self.test_dir, "sample_figure.png")
        result = self.exporter.export_figure(
            fig=self.fig,
            output_path=output_path,
            format="png"
        )
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(str(result).endswith(".png"))
    
    def test_export_to_pdf(self):
        """Test exporting a figure to PDF."""
        output_path = os.path.join(self.test_dir, "sample_figure.pdf")
        result = self.exporter.export_figure(
            fig=self.fig,
            output_path=output_path,
            format="pdf"
        )
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(str(result).endswith(".pdf"))
    
    def test_export_to_html(self):
        """Test exporting a figure to HTML."""
        output_path = os.path.join(self.test_dir, "sample_figure.html")
        result = self.exporter.export_to_html(
            fig=self.fig,
            output_path=output_path,
            title="Test HTML Export"
        )
        
        self.assertTrue(os.path.exists(result))
        self.assertTrue(str(result).endswith(".html"))
        
        # Check content
        with open(result, "r") as f:
            content = f.read()
            self.assertIn("<title>Test HTML Export</title>", content)
    
    @unittest.skipIf(shutil.which("pandoc") is None, "Pandoc not installed")
    def test_pandoc_export(self):
        """Test exporting to PDF with Pandoc if available."""
        try:
            # Create a document with a marker for visualization
            doc_content = "# Test Document\n\n<!-- TEST_VIZ -->\n\nThis is a test."
            test_doc_path = os.path.join(self.test_dir, "doc_with_viz.md")
            with open(test_doc_path, "w") as f:
                f.write(doc_content)
            
            # Export to PDF
            output_path = os.path.join(self.test_dir, "output.pdf")
            
            # Define visualization
            visualizations = [
                ("<!-- TEST_VIZ -->", self.fig, {"format": "png"})
            ]
            
            result = self.exporter.export_document_with_visualizations(
                document=test_doc_path,
                output_path=output_path,
                visualizations=visualizations,
                to_format="pdf"
            )
            
            self.assertTrue(os.path.exists(result))
            self.assertTrue(str(result).endswith(".pdf"))
            
        except PandocNotFoundError:
            self.skipTest("Pandoc not installed")
        except Exception as e:
            self.fail(f"Export failed: {e}") 