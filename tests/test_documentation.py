"""
Tests for the documentation build system.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the docs directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs')))

# Import the build_docs module
import build_docs

class TestDocumentationBuild(unittest.TestCase):
    """Test the documentation build functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.docs_dir = Path(self.temp_dir.name) / "docs"
        self.output_dir = Path(self.temp_dir.name) / "output"
        
        # Create necessary directories
        self.docs_dir.mkdir()
        (self.docs_dir / "api").mkdir()
        (self.docs_dir / "user").mkdir()
        (self.docs_dir / "dev").mkdir()
        (self.docs_dir / "_templates").mkdir()
        (self.docs_dir / "_static").mkdir()
        
        # Create a basic conf.py file
        with open(self.docs_dir / "conf.py", 'w') as f:
            f.write('project = "Test Project"\n')
            f.write('extensions = []\n')
        
        # Create a basic index.rst file
        with open(self.docs_dir / "index.rst", 'w') as f:
            f.write("Test Documentation\n")
            f.write("=================\n\n")
            f.write("Contents\n")
            f.write("--------\n\n")
            f.write(".. toctree::\n")
            f.write("   :maxdepth: 2\n\n")

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_ensure_directory(self):
        """Test ensure_directory function."""
        test_dir = Path(self.temp_dir.name) / "test_dir"
        build_docs.ensure_directory(test_dir)
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
        result = build_docs.run_command(["test", "command"])
        
        # Assertions
        mock_run.assert_called_once()
        self.assertEqual(result, "Test output")

    @patch('subprocess.run')
    def test_run_command_error(self, mock_run):
        """Test run_command function with error."""
        # Setup mock
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Error message"
        mock_run.return_value = mock_process
        
        # Test with expected exit
        with self.assertRaises(SystemExit):
            build_docs.run_command(["test", "command"])

    def test_generate_api_docs(self):
        """Test generate_api_docs function."""
        # Test
        api_dir = self.docs_dir / "api"
        build_docs.generate_api_docs(api_dir, "src_dir")
        
        # Check if files were created
        self.assertTrue((api_dir / "mdp.rst").exists())
        self.assertTrue((api_dir / "markchain.rst").exists())
        self.assertTrue((api_dir / "document.rst").exists())
        
        # Check content of one file
        with open(api_dir / "markchain.rst") as f:
            content = f.read()
            self.assertIn("Markchain", content)
            self.assertIn(".. automodule:: mdp.markchain", content)

    @patch('shutil.copy2')
    @patch('os.path.exists')
    def test_copy_markdown_files(self, mock_exists, mock_copy):
        """Test copy_markdown_files function."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Test
        build_docs.copy_markdown_files(self.docs_dir, self.docs_dir)
        
        # Assertions
        self.assertEqual(mock_copy.call_count, 3)  # Two technical guides are already in place

    @patch('build_docs.run_command')
    @patch('build_docs.generate_api_docs')
    @patch('build_docs.copy_markdown_files')
    def test_build_docs(self, mock_copy, mock_gen_api, mock_run):
        """Test build_docs function."""
        # Setup mock
        mock_run.return_value = "Build successful"
        
        # Test
        result = build_docs.build_docs(self.docs_dir, self.output_dir)
        
        # Assertions
        mock_gen_api.assert_called_once()
        mock_copy.assert_called_once()
        mock_run.assert_called_once()
        
        # Check output_dir is returned
        self.assertTrue(str(self.docs_dir) in str(result))

    @patch('shutil.rmtree')
    @patch('os.path.exists')
    def test_clean_docs(self, mock_exists, mock_rmtree):
        """Test clean_docs function."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Test
        build_docs.clean_docs(self.docs_dir)
        
        # Assertions
        mock_rmtree.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        """Test parse_args function."""
        # Setup mock
        mock_args = MagicMock()
        mock_args.clean = True
        mock_args.builder = "html"
        mock_args.output = None
        mock_parse_args.return_value = mock_args
        
        # Test
        args = build_docs.parse_args()
        
        # Assertions
        self.assertTrue(args.clean)
        self.assertEqual(args.builder, "html")
        self.assertIsNone(args.output)

    @patch('build_docs.build_docs')
    @patch('build_docs.clean_docs')
    @patch('build_docs.parse_args')
    def test_main(self, mock_parse_args, mock_clean, mock_build):
        """Test main function."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.clean = True
        mock_args.builder = "html"
        mock_args.output = str(self.output_dir)
        mock_parse_args.return_value = mock_args
        
        # Test
        build_docs.main()
        
        # Assertions
        mock_clean.assert_called_once()
        mock_build.assert_called_once()

if __name__ == '__main__':
    unittest.main() 