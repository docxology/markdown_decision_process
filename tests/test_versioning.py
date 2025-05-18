"""
Tests for the versioned documentation deployment script.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add the docs directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs')))

# Import the versioning module
import versioning

class TestVersioning(unittest.TestCase):
    """Test the versioning functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "versioned_docs"
        self.output_dir.mkdir()

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_ensure_directory(self):
        """Test ensure_directory function."""
        test_dir = Path(self.temp_dir.name) / "test_ensure_dir"
        versioning.ensure_directory(test_dir)
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
        result = versioning.run_command(["test", "command"])
        
        # Assertions
        mock_run.assert_called_once()
        self.assertEqual(result, "Test output")

    @patch('builtins.open', new_callable=mock_open, read_data='version = "0.1.0"')
    def test_get_package_version(self, mock_file):
        """Test get_package_version function."""
        # Test
        version = versioning.get_package_version()
        
        # Assertions
        mock_file.assert_called_once_with("pyproject.toml", "r")
        self.assertEqual(version, "0.1.0")

    @patch('versioning.run_command')
    def test_get_git_tags(self, mock_run):
        """Test get_git_tags function."""
        # Setup mock
        mock_run.return_value = "v0.2.0\nv0.1.0\n"
        
        # Test
        tags = versioning.get_git_tags()
        
        # Assertions
        mock_run.assert_called_once_with(["git", "tag", "--sort=-v:refname"])
        self.assertEqual(tags, ["v0.2.0", "v0.1.0"])

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_version_json(self, mock_file, mock_dump):
        """Test create_version_json function."""
        # Test data
        versions_dir = self.output_dir
        current_version = "0.1.0"
        versions = ["latest", "v0.1.0"]
        
        # Test
        versioning.create_version_json(versions_dir, current_version, versions)
        
        # Assertions
        mock_file.assert_called_once()
        mock_dump.assert_called_once()
        args, _ = mock_dump.call_args
        self.assertEqual(args[0]["current"], current_version)
        self.assertEqual(args[0]["versions"], versions)

    @patch('versioning.build_docs')
    @patch('versioning.run_command')
    @patch('versioning.ensure_directory')
    def test_build_version_docs_latest(self, mock_ensure, mock_run, mock_build):
        """Test build_version_docs function with latest version."""
        # Test
        versioning.build_version_docs("latest", self.output_dir)
        
        # Assertions
        self.assertEqual(mock_ensure.call_count, 2)  # temp_dir and version_output
        mock_run.assert_not_called()  # Should not checkout for latest
        mock_build.assert_called_once()

    @patch('versioning.build_docs')
    @patch('versioning.run_command')
    @patch('versioning.ensure_directory')
    def test_build_version_docs_tag(self, mock_ensure, mock_run, mock_build):
        """Test build_version_docs function with a specific tag."""
        # Test
        versioning.build_version_docs("v0.1.0", self.output_dir)
        
        # Assertions
        self.assertEqual(mock_ensure.call_count, 2)  # temp_dir and version_output
        self.assertEqual(mock_run.call_count, 2)  # checkout and checkout back
        mock_build.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_create_redirect_index(self, mock_file):
        """Test create_redirect_index function."""
        # Test
        versioning.create_redirect_index(self.output_dir, "latest")
        
        # Assertions
        mock_file.assert_called_once()
        # Check that the HTML contains the right redirect
        write_calls = mock_file().write.call_args_list
        written_data = ''.join(call[0][0] for call in write_calls)
        self.assertIn("latest/index.html", written_data)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_version_selector(self, mock_file, mock_exists):
        """Test create_version_selector function."""
        # Setup mock
        mock_exists.return_value = True
        
        # Test
        versions = ["latest", "v0.1.0"]
        versioning.create_version_selector(self.output_dir, versions)
        
        # Assertions
        self.assertEqual(mock_file.call_count, 4)  # 2 version.js + 2 theme.js files
        # Check that the JS contains version information
        write_calls = mock_file().write.call_args_list
        written_data = ''.join(call[0][0] for call in write_calls if isinstance(call[0][0], str))
        self.assertIn("window.VERSION", written_data)
        self.assertIn("version-selector", written_data)

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        """Test parse_args function."""
        # Setup mock
        mock_args = MagicMock()
        mock_args.output = "test_output"
        mock_args.versions = ["latest", "v0.1.0"]
        mock_args.max_versions = 5
        mock_args.current = "0.1.0"
        mock_parse_args.return_value = mock_args
        
        # Test
        args = versioning.parse_args()
        
        # Assertions
        self.assertEqual(args.output, "test_output")
        self.assertEqual(args.versions, ["latest", "v0.1.0"])
        self.assertEqual(args.max_versions, 5)
        self.assertEqual(args.current, "0.1.0")

    @patch('versioning.create_version_selector')
    @patch('versioning.create_redirect_index')
    @patch('versioning.create_version_json')
    @patch('versioning.build_version_docs')
    @patch('versioning.get_git_tags')
    @patch('versioning.get_package_version')
    @patch('versioning.ensure_directory')
    @patch('versioning.parse_args')
    def test_main(self, mock_parse_args, mock_ensure, mock_version, mock_tags, 
                  mock_build, mock_json, mock_redirect, mock_selector):
        """Test main function."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.output = str(self.output_dir)
        mock_args.versions = None
        mock_args.max_versions = 3
        mock_args.current = None
        mock_parse_args.return_value = mock_args
        
        mock_version.return_value = "0.1.0"
        mock_tags.return_value = ["v0.1.0", "v0.0.9", "v0.0.8", "v0.0.7"]
        
        # Test
        versioning.main()
        
        # Assertions
        mock_ensure.assert_called_once()
        mock_version.assert_called_once()
        mock_tags.assert_called_once()
        self.assertEqual(mock_build.call_count, 3)  # latest + 2 versions
        mock_json.assert_called_once()
        mock_redirect.assert_called_once()
        mock_selector.assert_called_once()

if __name__ == '__main__':
    unittest.main() 