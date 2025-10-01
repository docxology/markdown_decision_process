"""
Tests for the notebook converter.
"""

import os
import sys
import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add the docs directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs')))

# Mock nbformat and nbconvert modules
sys.modules['nbformat'] = MagicMock()
sys.modules['nbconvert'] = MagicMock()
sys.modules['nbconvert.preprocessors'] = MagicMock()

# Import the notebook_converter module
import notebook_converter

# Create a sample notebook in JSON format
SAMPLE_NOTEBOOK = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Sample Notebook\n", "\n", "This is a sample notebook."]
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "source": ["import numpy as np\n", "import matplotlib.pyplot as plt"],
            "outputs": []
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {},
            "source": ["x = np.linspace(0, 10, 100)\n", "y = np.sin(x)\n", "plt.plot(x, y)"],
            "outputs": [
                {
                    "data": {
                        "image/png": "base64encodedimage=="
                    },
                    "metadata": {},
                    "output_type": "display_data"
                }
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

class TestNotebookConverter(unittest.TestCase):
    """Test the notebook converter functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.examples_dir = Path(self.temp_dir.name) / "examples"
        self.docs_dir = Path(self.temp_dir.name) / "docs"
        self.output_dir = Path(self.temp_dir.name) / "docs/user/examples"
        
        # Create necessary directories
        self.examples_dir.mkdir()
        self.docs_dir.mkdir()
        Path(self.docs_dir / "conf.py").write_text('project = "Test Project"\nextensions = []\nhtml_static_path = []')
        
        # Create a sample notebook file
        notebook_dir = self.examples_dir / "sample"
        notebook_dir.mkdir()
        self.notebook_path = notebook_dir / "sample_notebook.ipynb"
        with open(self.notebook_path, 'w') as f:
            json.dump(SAMPLE_NOTEBOOK, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_ensure_directory(self):
        """Test ensure_directory function."""
        test_dir = Path(self.temp_dir.name) / "test_dir"
        notebook_converter.ensure_directory(test_dir)
        self.assertTrue(test_dir.exists())
        self.assertTrue(test_dir.is_dir())

    @patch('subprocess.run')
    def test_run_command(self, mock_run):
        """Test run_command function."""
        # Setup mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Test output"
        mock_run.return_value = mock_process
        
        # Test
        result = notebook_converter.run_command(["test", "command"])
        
        # Assertions
        mock_run.assert_called_once()
        self.assertEqual(result, "Test output")

    @patch('glob.glob')
    def test_find_notebooks(self, mock_glob):
        """Test find_notebooks function."""
        # Setup mock
        mock_glob.return_value = [
            str(self.examples_dir / "sample/notebook1.ipynb"),
            str(self.examples_dir / "sample/notebook2.ipynb")
        ]
        
        # Test
        notebooks = notebook_converter.find_notebooks(self.examples_dir)
        
        # Assertions
        mock_glob.assert_called_once()
        self.assertEqual(len(notebooks), 2)

    @patch('docs.notebook_converter.MarkdownExporter')
    @patch('docs.notebook_converter.nbformat')
    def test_convert_notebook(self, mock_nbformat, mock_exporter):
        """Test convert_notebook function."""
        # Setup mocks
        mock_nb = MagicMock()
        mock_nbformat.read.return_value = mock_nb
        
        mock_exporter_instance = MagicMock()
        mock_exporter.return_value = mock_exporter_instance
        mock_exporter_instance.from_notebook_node.return_value = (
            "# Converted notebook content",
            {"outputs": {"image.png": b"image content"}}
        )
        
        # Set the global examples_dir
        notebook_converter.examples_dir = str(self.examples_dir)
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True)
        
        # Test
        result = notebook_converter.convert_notebook(
            str(self.notebook_path), 
            str(self.output_dir),
            execute=False
        )
        
        # Assertions
        mock_read.assert_called_once()
        mock_exporter_instance.from_notebook_node.assert_called_once_with(mock_nb)
        self.assertTrue(os.path.exists(result))

    @patch('builtins.open', new_callable=mock_open)
    def test_create_index_page(self, mock_file):
        """Test create_index_page function."""
        # Test data
        notebooks = [
            str(self.output_dir / "sample/notebook1.md"),
            str(self.output_dir / "sample/notebook2.md")
        ]
        
        # Test
        result = notebook_converter.create_index_page(str(self.output_dir), notebooks)
        
        # Assertions
        mock_file.assert_called_with(os.path.join(str(self.output_dir), "index.md"), 'w')
        write_calls = mock_file().write.call_args_list
        written_data = ''.join(call[0][0] for call in write_calls)
        self.assertIn("Example Notebooks", written_data)
        self.assertIn("```{toctree}", written_data)

    @patch('builtins.open', new_callable=mock_open, read_data='project = "Test"\nextensions = []\n')
    def test_update_sphinx_config(self, mock_file):
        """Test update_sphinx_config function."""
        # Test
        notebook_converter.update_sphinx_config(str(self.docs_dir))
        
        # Assertions
        read_path = os.path.join(str(self.docs_dir), "conf.py")
        mock_file.assert_any_call(read_path, 'r')
        write_path = os.path.join(str(self.docs_dir), "conf.py")
        mock_file.assert_any_call(write_path, 'a')
        
        # Check content written
        write_calls = mock_file().write.call_args_list
        written_data = ''.join(call[0][0] for call in write_calls if isinstance(call[0][0], str))
        self.assertIn("nbsphinx", written_data)
        self.assertIn("extensions.append", written_data)

    @patch('notebook_converter.convert_notebook')
    @patch('notebook_converter.find_notebooks')
    @patch('notebook_converter.create_index_page')
    def test_process_notebooks(self, mock_index, mock_find, mock_convert):
        """Test process_notebooks function."""
        # Setup mocks
        mock_find.return_value = [
            str(self.examples_dir / "sample/notebook1.ipynb"),
            str(self.examples_dir / "sample/notebook2.ipynb")
        ]
        mock_convert.side_effect = lambda nb, out, ex, to: f"{out}/converted_{os.path.basename(nb)}"
        mock_index.return_value = "index.md"
        
        # Test
        result = notebook_converter.process_notebooks(
            str(self.examples_dir), 
            str(self.output_dir),
            execute=False
        )
        
        # Assertions
        mock_find.assert_called_once()
        self.assertEqual(mock_convert.call_count, 2)
        mock_index.assert_called_once()
        self.assertEqual(len(result), 2)

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        """Test parse_args function."""
        # Setup mock
        mock_args = MagicMock()
        mock_args.examples_dir = "examples"
        mock_args.output_dir = "docs/user/examples"
        mock_args.docs_dir = "docs"
        mock_args.execute = True
        mock_args.timeout = 300
        mock_parse_args.return_value = mock_args
        
        # Test
        args = notebook_converter.parse_args()
        
        # Assertions
        self.assertEqual(args.examples_dir, "examples")
        self.assertEqual(args.output_dir, "docs/user/examples")
        self.assertEqual(args.docs_dir, "docs")
        self.assertTrue(args.execute)
        self.assertEqual(args.timeout, 300)

    @patch('notebook_converter.update_sphinx_config')
    @patch('notebook_converter.process_notebooks')
    @patch('notebook_converter.ensure_directory')
    @patch('notebook_converter.parse_args')
    def test_main(self, mock_parse_args, mock_ensure, mock_process, mock_update):
        """Test main function."""
        # Setup mock
        mock_args = MagicMock()
        mock_args.examples_dir = str(self.examples_dir)
        mock_args.output_dir = str(self.output_dir)
        mock_args.docs_dir = str(self.docs_dir)
        mock_args.execute = False
        mock_args.timeout = 600
        mock_parse_args.return_value = mock_args
        
        # Test
        notebook_converter.main()
        
        # Assertions
        self.assertEqual(mock_ensure.call_count, 2)  # output_dir and images_dir
        mock_process.assert_called_once_with(
            str(self.examples_dir), str(self.output_dir), False, 600
        )
        mock_update.assert_called_once_with(str(self.docs_dir))

if __name__ == '__main__':
    unittest.main() 