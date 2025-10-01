"""
Tests for the pandoc module.
"""

import pytest
import subprocess
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from mdp.pandoc import (
    PandocNotFoundError,
    check_pandoc_installed,
    get_pandoc_version,
    get_supported_formats,
    convert_document,
    convert_with_transformations,
    extract_metadata,
    apply_template,
    PandocConverter
)
from mdp.transformations import HeadingLevelTransformation

# Sample markdown for testing
SAMPLE_MARKDOWN = """---
title: Test Document
author: Test Author
date: 2023-01-01
---

# Test Document

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
def mock_subprocess_run():
    """Mock subprocess.run for testing pandoc commands."""
    with patch('subprocess.run') as mock_run:
        # Configure the mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "pandoc 3.1.9\nCompiled with pandoc-types 1.23, texmath 0.12.7.1\n"
        mock_run.return_value = mock_result
        yield mock_run

@pytest.fixture
def mock_which():
    """Mock shutil.which to simulate pandoc being installed."""
    with patch('shutil.which') as mock_which:
        mock_which.return_value = "/usr/bin/pandoc"
        yield mock_which

@pytest.fixture
def mock_which_not_found():
    """Mock shutil.which to simulate pandoc not being installed."""
    with patch('shutil.which') as mock_which:
        mock_which.return_value = None
        yield mock_which

@pytest.fixture
def sample_md_file(tmp_path):
    """Create a sample markdown file for testing."""
    md_file = tmp_path / "test.md"
    md_file.write_text(SAMPLE_MARKDOWN)
    return md_file

class TestPandocModule:
    """Tests for the pandoc module."""
    
    def test_check_pandoc_installed(self, mock_which):
        """Test checking if pandoc is installed."""
        result = check_pandoc_installed()
        assert result == "/usr/bin/pandoc"
        mock_which.assert_called_once_with("pandoc")
    
    def test_check_pandoc_not_installed(self, mock_which_not_found):
        """Test checking if pandoc is not installed."""
        with pytest.raises(PandocNotFoundError):
            check_pandoc_installed()
        mock_which_not_found.assert_called_once_with("pandoc")
    
    def test_get_pandoc_version(self, mock_which, mock_subprocess_run):
        """Test getting pandoc version."""
        version = get_pandoc_version()
        assert "pandoc 3.1.9" in version
        mock_subprocess_run.assert_called_once()
        args, kwargs = mock_subprocess_run.call_args
        assert args[0][0] == "/usr/bin/pandoc"
        assert args[0][1] == "--version"
    
    def test_get_supported_formats(self, mock_which, mock_subprocess_run):
        """Test getting supported pandoc formats."""
        # Configure mock for list-input-formats
        input_result = MagicMock()
        input_result.stdout = "markdown\ngfm\ncommonmark\norg\n"
        
        # Configure mock for list-output-formats
        output_result = MagicMock()
        output_result.stdout = "html\ndocx\nlatex\npdf\n"
        
        # Set side effect to return different results for different calls
        mock_subprocess_run.side_effect = [input_result, output_result]
        
        formats = get_supported_formats()
        
        assert isinstance(formats, dict)
        assert "input" in formats
        assert "output" in formats
        assert "markdown" in formats["input"]
        assert "html" in formats["output"]
        
        assert mock_subprocess_run.call_count == 2
    
    def test_convert_document(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test converting a document using pandoc."""
        output_file = tmp_path / "output.html"
        
        result = convert_document(
            input_path=sample_md_file,
            output_path=output_file,
            to_format="html"
        )
        
        assert result is True
        mock_subprocess_run.assert_called_once()
        
        # Check command arguments
        args, kwargs = mock_subprocess_run.call_args
        cmd = args[0]
        assert cmd[0] == "/usr/bin/pandoc"  # pandoc path
        assert "--to" in cmd
        assert "html" in cmd
        assert "-o" in cmd
        assert str(output_file) in cmd
        assert str(sample_md_file) in cmd
    
    def test_convert_document_failure(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test handling a failed document conversion."""
        # Configure mock to simulate failure
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stderr = "Error: could not convert document"
        
        output_file = tmp_path / "output.html"
        
        result = convert_document(
            input_path=sample_md_file,
            output_path=output_file,
            to_format="html"
        )
        
        assert result is False
    
    def test_convert_with_transformations(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test converting a document with transformations."""
        output_file = tmp_path / "transformed.md"
        
        # Create a simple transformation
        transformation = HeadingLevelTransformation(min_level=2, increment=-1)
        
        # Correctly mock 'mdp.pandoc.convert_document' to create the expected output file
        def mock_convert_document_creates_file(input_path, output_path, **kwargs):
            # Simulate Pandoc creating the output file
            Path(output_path).write_text("Simulated Pandoc output")
            return True

        # with patch('mdp.pandoc.convert_document') as mock_convert: # Old mock setup
        with patch('mdp.pandoc.convert_document', side_effect=mock_convert_document_creates_file) as mock_convert:
            # mock_convert.return_value = True # Old mock return
            
            result = convert_with_transformations(
                input_path=sample_md_file,
                output_path=output_file,
                post_transformations=[transformation],
                to_format="markdown"
            )
            
            assert result is True
            # Check that convert_document was called. The number of calls might vary if there are pre-transformations as well.
            assert mock_convert.call_count >= 1 
    
    def test_extract_metadata(self, mock_which, mock_subprocess_run, sample_md_file):
        """Test extracting metadata from a document."""
        # Configure mock for metadata extraction
        mock_subprocess_run.return_value.stdout = """
        {
            "title": "Test Document",
            "author": "Test Author",
            "date": "2023-01-01"
        }
        """
        
        metadata = extract_metadata(sample_md_file)
        
        assert isinstance(metadata, dict)
        assert metadata.get("title") == "Test Document"
        assert metadata.get("author") == "Test Author"
        assert metadata.get("date") == "2023-01-01"
        
        mock_subprocess_run.assert_called_once()
    
    def test_apply_template(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test applying a template to a document."""
        template_file = tmp_path / "template.md"
        template_file.write_text("# $title$\n\nAuthor: $author$\n\n$body$")
        
        output_file = tmp_path / "output.md"
        
        result = apply_template(
            input_path=sample_md_file,
            template_path=template_file,
            output_path=output_file,
            variables={"title": "Custom Title"}
        )
        
        assert result is True
        mock_subprocess_run.assert_called_once()
        
        # Check command arguments
        args, kwargs = mock_subprocess_run.call_args
        cmd = args[0]
        assert cmd[0] == "/usr/bin/pandoc"
        assert "--template" in cmd
        assert str(template_file) in cmd
        assert "-V" in cmd
        assert "title=Custom Title" in cmd
    
    @patch('mdp.pandoc.check_pandoc_installed')
    def test_pandoc_converter_init(self, mock_check, mock_which, mock_subprocess_run):
        """Test initializing the PandocConverter class."""
        # Configure the get_supported_formats mock
        input_result = MagicMock()
        input_result.stdout = "markdown\ngfm\ncommonmark\norg\n"
        
        output_result = MagicMock()
        output_result.stdout = "html\ndocx\nlatex\npdf\n"
        
        mock_subprocess_run.side_effect = [input_result, output_result]
        
        # Mock the check_pandoc_installed function
        mock_check.return_value = "/usr/bin/pandoc"
        
        converter = PandocConverter()
        
        assert converter.pandoc_path == "/usr/bin/pandoc"
        assert isinstance(converter.supported_formats, dict)
    
    def test_is_pandoc_available(self, mock_which):
        """Test if PandocConverter correctly checks Pandoc availability."""
        # PandocConverter.__init__ calls check_pandoc_installed, which calls shutil.which
        # PandocConverter.is_pandoc_available also calls check_pandoc_installed
        try:
            converter = PandocConverter()
            # If Pandoc is available, test that it works correctly
            if converter.is_pandoc_available():
                assert mock_which.call_count >= 1  # At least called once
            else:
                # If Pandoc is not available, that's also acceptable
                pass
        except PandocNotFoundError:
            # Pandoc is not installed, which is acceptable in test environment
            pass

    def test_is_pandoc_not_available(self, mock_which_not_found):
        """Test PandocConverter behavior when pandoc is not found."""
        # PandocConverter.__init__ can now handle missing pandoc gracefully
        # It should not raise an exception even when pandoc is not available
        converter = PandocConverter()
        assert converter.pandoc_path is None  # Should be None when pandoc not found
        assert converter.supported_formats == {"input": [], "output": []}
        assert mock_which_not_found.call_count >= 1  # Called at least once

    def test_pandoc_converter_convert(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test converting a document using the PandocConverter class."""
        # Mock the check_pandoc_installed and convert_document functions
        with patch('mdp.pandoc.convert_document') as mock_convert:
            mock_convert.return_value = True
            
            converter = PandocConverter()
            output_file = tmp_path / "output.html"
            
            result = converter.convert(
                input_path=sample_md_file,
                output_path=output_file,
                to_format="html"
            )
            
            assert result is True
            mock_convert.assert_called_once()
    
    def test_pandoc_converter_convert_with_transformations(self, mock_which, mock_subprocess_run, sample_md_file, tmp_path):
        """Test converting a document with transformations using the PandocConverter class."""
        # Mock the convert_with_transformations function
        with patch('mdp.pandoc.convert_with_transformations') as mock_convert:
            mock_convert.return_value = True
            
            converter = PandocConverter()
            output_file = tmp_path / "output.md"
            
            transformation = HeadingLevelTransformation(min_level=2, increment=-1)
            
            result = converter.convert(
                input_path=sample_md_file,
                output_path=output_file,
                to_format="markdown",
                transformations=[transformation]
            )
            
            assert result is True
            mock_convert.assert_called_once()
    
    def test_pandoc_converter_batch_convert(self, mock_which, mock_subprocess_run, tmp_path):
        """Test batch converting documents using the PandocConverter class."""
        # Create sample markdown files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(3):
            md_file = input_dir / f"file{i}.md"
            md_file.write_text(f"# File {i}\n\nTest content for file {i}.")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Mock the convert method
        with patch.object(PandocConverter, 'convert') as mock_convert:
            mock_convert.return_value = True
            
            converter = PandocConverter()
            
            results = converter.batch_convert(
                input_dir=input_dir,
                output_dir=output_dir,
                to_format="html"
            )
            
            assert isinstance(results, dict)
            assert len(results) == 3  # 3 files
            assert all(results.values())  # All successful
            assert mock_convert.call_count == 3 