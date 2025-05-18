"""Tests for the Formatting Plugin."""

import os
import sys
import pytest

# Add the examples directory to the path so we can import the plugin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples')))

from plugins.formatting_plugin import FormattingPlugin


class TestFormattingPlugin:
    """Test suite for the Formatting Plugin."""

    def setup_method(self):
        """Set up the test environment."""
        self.plugin = FormattingPlugin()

    def test_metadata(self):
        """Test that the plugin metadata is correct."""
        metadata = self.plugin.get_metadata()
        assert "name" in metadata
        assert "version" in metadata
        assert "author" in metadata
        assert "description" in metadata

    def test_transformations(self):
        """Test that the plugin provides the expected transformations."""
        transformations = self.plugin.get_transformations()
        assert "fix_headings" in transformations
        assert "fix_lists" in transformations
        assert "standardize_links" in transformations

    def test_reward_functions(self):
        """Test that the plugin provides the expected reward functions."""
        reward_functions = self.plugin.get_reward_functions()
        assert "consistency_score" in reward_functions

    def test_configure(self):
        """Test that the plugin can be configured."""
        self.plugin.configure({
            "heading_style": "underline",
            "list_style": "*",
            "link_style": "reference"
        })
        assert self.plugin.config["heading_style"] == "underline"
        assert self.plugin.config["list_style"] == "*"
        assert self.plugin.config["link_style"] == "reference"

    def test_fix_headings_atx_to_underline(self):
        """Test converting ATX headings to underline style."""
        self.plugin.configure({"heading_style": "underline"})
        text = "# Heading 1\nSome text\n## Heading 2\nMore text"
        result = self.plugin._fix_headings(text)
        assert "Heading 1\n=========" in result
        assert "Heading 2\n---------" in result
        assert "# Heading" not in result

    def test_fix_headings_underline_to_atx(self):
        """Test converting underline headings to ATX style."""
        self.plugin.configure({"heading_style": "#"})
        text = "Heading 1\n=========\nSome text\nHeading 2\n---------\nMore text"
        result = self.plugin._fix_headings(text)
        assert "# Heading 1" in result
        assert "## Heading 2" in result
        assert "=========" not in result
        assert "---------" not in result

    def test_fix_lists(self):
        """Test standardizing list markers."""
        self.plugin.configure({"list_style": "-"})
        text = "* Item 1\n+ Item 2\n- Item 3"
        result = self.plugin._fix_lists(text)
        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

        # Test with a different style
        self.plugin.configure({"list_style": "*"})
        result = self.plugin._fix_lists(text)
        assert "* Item 1" in result
        assert "* Item 2" in result
        assert "* Item 3" in result

    def test_standardize_links_to_inline(self):
        """Test converting reference links to inline links."""
        self.plugin.configure({"link_style": "inline"})
        text = "This is a [link][ref1] and another [link][ref2].\n\n[ref1]: https://example.com\n[ref2]: https://example.org"
        result = self.plugin._standardize_links(text)
        assert "[link](https://example.com)" in result
        assert "[link](https://example.org)" in result
        assert "[ref1]:" not in result
        assert "[ref2]:" not in result

    def test_standardize_links_to_reference(self):
        """Test converting inline links to reference links."""
        self.plugin.configure({"link_style": "reference"})
        text = "This is a [link](https://example.com) and another [link](https://example.org)."
        result = self.plugin._standardize_links(text)
        assert "[link][link1]" in result
        assert "[link][link2]" in result
        assert "[link1]: https://example.com" in result
        assert "[link2]: https://example.org" in result

    def test_consistency_score_perfect(self):
        """Test consistency score calculation with perfect consistency."""
        text = "# Heading 1\n\n## Heading 2\n\n- Item 1\n- Item 2\n\nA [link](https://example.com) here."
        score = self.plugin._calculate_consistency_score(text)
        assert score == 1.0

    def test_consistency_score_mixed(self):
        """Test consistency score calculation with mixed styles."""
        text = """# Heading 1
        
Heading 2
---------

* Item 1
- Item 2
+ Item 3

A [link](https://example.com) and a [reference][ref] link.

[ref]: https://example.org
"""
        score = self.plugin._calculate_consistency_score(text)
        assert 0.0 <= score < 1.0 