"""
Formatting Plugin for Markdown Decision Process.

This plugin provides transformations and reward functions for standardizing
Markdown formatting elements like headings, lists, and links.
"""

import re
from typing import Dict, Any, Callable, List, Tuple

from mdp.plugins import MDPPlugin


class FormattingPlugin(MDPPlugin):
    """
    Plugin for standardizing Markdown formatting and measuring consistency.
    
    The plugin serves as a policy enforcer in the MDP, transitioning between
    different formatting states to maximize the reward of consistency.
    """
    
    def __init__(self):
        """Initialize the plugin with default configuration."""
        self.config = {
            "heading_style": "#",  # ATX style
            "list_style": "-",     # Dash style
            "link_style": "inline" # Inline style
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return plugin metadata.
        
        Returns:
            Dict[str, Any]: Dictionary containing plugin metadata
        """
        return {
            "name": "Formatting Plugin",
            "description": "Standardizes Markdown formatting and measures consistency",
            "version": "0.1.0",
            "author": "MDP Team"
        }
    
    def get_transformations(self) -> Dict[str, Callable]:
        """
        Return available transformations.
        
        Returns:
            Dict[str, Callable]: Dictionary mapping transformation names to functions
        """
        return {
            "fix_headings": self._fix_headings,
            "fix_lists": self._fix_lists,
            "standardize_links": self._standardize_links
        }
    
    def get_reward_functions(self) -> Dict[str, Callable]:
        """
        Return available reward functions.
        
        Returns:
            Dict[str, Callable]: Dictionary mapping reward function names to functions
        """
        return {
            "consistency_score": self._calculate_consistency_score
        }
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with user-defined settings.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        for key, value in config.items():
            if key in self.config:
                self.config[key] = value
    
    def initialize(self) -> None:
        """Initialize plugin resources."""
        # No initialization needed for this plugin
        pass
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        # No cleanup needed for this plugin
        pass
    
    def _fix_headings(self, text: str) -> str:
        """
        Convert headings to the configured style.
        
        Args:
            text (str): Markdown text
            
        Returns:
            str: Markdown text with standardized headings
        """
        if self.config["heading_style"] == "#":
            return self._convert_underline_to_atx(text)
        else:
            return self._convert_atx_to_underline(text)
    
    def _convert_atx_to_underline(self, text: str) -> str:
        """
        Convert ATX style headings to underline style.
        
        Args:
            text (str): Markdown text with ATX headings
            
        Returns:
            str: Markdown text with underline headings
        """
        lines = text.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            atx_match = re.match(r'^(#{1,2})\s+(.+)$', line)
            
            if atx_match:
                level, content = atx_match.groups()
                result.append(content)
                
                if len(level) == 1:  # h1 - use equals
                    result.append('=' * len(content))
                else:  # h2 - use dashes
                    result.append('-' * len(content))
            else:
                result.append(line)
            
            i += 1
        
        return '\n'.join(result)
    
    def _convert_underline_to_atx(self, text: str) -> str:
        """
        Convert underline style headings to ATX style.
        
        Args:
            text (str): Markdown text with underline headings
            
        Returns:
            str: Markdown text with ATX headings
        """
        lines = text.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if i < len(lines) - 1:
                next_line = lines[i + 1]
                
                # Check for equals underline (h1)
                if re.match(r'^=+$', next_line) and len(next_line) > 0:
                    result.append(f"# {line}")
                    i += 2
                    continue
                
                # Check for dash underline (h2)
                if re.match(r'^-+$', next_line) and len(next_line) > 0:
                    result.append(f"## {line}")
                    i += 2
                    continue
            
            result.append(line)
            i += 1
        
        return '\n'.join(result)
    
    def _fix_lists(self, text: str) -> str:
        """
        Standardize list markers to the configured style.
        
        Args:
            text (str): Markdown text
            
        Returns:
            str: Markdown text with standardized list markers
        """
        marker = self.config["list_style"]
        
        # Replace unordered list markers
        pattern = r'^(\s*)([*+-])(\s+)(.+)$'
        
        def replace_marker(match):
            indent, _, spacing, content = match.groups()
            return f"{indent}{marker}{spacing}{content}"
        
        lines = text.split('\n')
        result = []
        
        for line in lines:
            result.append(re.sub(pattern, replace_marker, line, flags=re.MULTILINE))
        
        return '\n'.join(result)
    
    def _standardize_links(self, text: str) -> str:
        """
        Standardize links to the configured style.
        
        Args:
            text (str): Markdown text
            
        Returns:
            str: Markdown text with standardized links
        """
        if self.config["link_style"] == "inline":
            return self._convert_reference_to_inline(text)
        else:
            return self._convert_inline_to_reference(text)
    
    def _convert_inline_to_reference(self, text: str) -> str:
        """
        Convert inline links to reference links.
        
        Args:
            text (str): Markdown text with inline links
            
        Returns:
            str: Markdown text with reference links
        """
        lines = text.split('\n')
        links = {}
        link_count = 1
        
        # First pass: gather links and replace with references
        for i, line in enumerate(lines):
            inline_links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line)
            for match in inline_links:
                text_part, url = match.groups()
                ref_id = f"link{link_count}"
                link_count += 1
                links[ref_id] = url
                lines[i] = lines[i].replace(match.group(0), f"[{text_part}][{ref_id}]")
        
        # Add reference definitions at the end
        if links:
            lines.append("")  # Empty line
            for ref_id, url in links.items():
                lines.append(f"[{ref_id}]: {url}")
        
        return '\n'.join(lines)
    
    def _convert_reference_to_inline(self, text: str) -> str:
        """
        Convert reference links to inline links.
        
        Args:
            text (str): Markdown text with reference links
            
        Returns:
            str: Markdown text with inline links
        """
        # Extract all reference definitions
        ref_links = {}
        ref_pattern = r'^\[([^\]]+)\]:\s*(.+)$'
        
        lines = text.split('\n')
        result_lines = []
        
        # First pass: collect all reference definitions
        for i, line in enumerate(lines):
            match = re.match(ref_pattern, line)
            if match:
                ref_id, url = match.groups()
                ref_links[ref_id] = url.strip()
            else:
                result_lines.append(line)
        
        # Second pass: replace references with inline links
        for i, line in enumerate(result_lines):
            ref_usages = re.finditer(r'\[([^\]]+)\]\[([^\]]+)\]', line)
            for match in ref_usages:
                text_part, ref_id = match.groups()
                if ref_id in ref_links:
                    url = ref_links[ref_id]
                    result_lines[i] = result_lines[i].replace(
                        match.group(0), f"[{text_part}]({url})"
                    )
        
        return '\n'.join(result_lines)
    
    def _calculate_consistency_score(self, text: str) -> float:
        """
        Calculate a consistency score based on formatting.
        
        Higher scores indicate more consistent formatting.
        
        Args:
            text (str): Markdown text
            
        Returns:
            float: Consistency score from 0.0 to 1.0
        """
        inconsistencies = 0
        total_elements = 0
        
        # Check heading styles
        h1_atx = len(re.findall(r'^#\s+.+$', text, re.MULTILINE))
        h1_underline = len(re.findall(r'^.+\n=+$', text, re.MULTILINE))
        h2_atx = len(re.findall(r'^##\s+.+$', text, re.MULTILINE))
        h2_underline = len(re.findall(r'^.+\n-+$', text, re.MULTILINE))
        
        total_h1 = h1_atx + h1_underline
        total_h2 = h2_atx + h2_underline
        
        if total_h1 > 0:
            inconsistencies += min(h1_atx, h1_underline)
            total_elements += total_h1
            
        if total_h2 > 0:
            inconsistencies += min(h2_atx, h2_underline)
            total_elements += total_h2
        
        # Check list markers
        dash_lists = len(re.findall(r'^\s*-\s+.+$', text, re.MULTILINE))
        star_lists = len(re.findall(r'^\s*\*\s+.+$', text, re.MULTILINE))
        plus_lists = len(re.findall(r'^\s*\+\s+.+$', text, re.MULTILINE))
        
        total_lists = dash_lists + star_lists + plus_lists
        
        if total_lists > 0:
            inconsistencies += total_lists - max(dash_lists, star_lists, plus_lists)
            total_elements += total_lists
        
        # Check link styles
        inline_links = len(re.findall(r'\[.+?\]\(.+?\)', text))
        reference_links = len(re.findall(r'\[.+?\]\[.+?\]', text))
        
        total_links = inline_links + reference_links
        
        if total_links > 0:
            inconsistencies += min(inline_links, reference_links)
            total_elements += total_links
        
        # Calculate score (0.0 to 1.0)
        if total_elements == 0:
            return 1.0  # Perfect score for empty document
        
        return 1.0 - (inconsistencies / total_elements)


# Plugin entry point for the plugin manager
def get_plugin_class():
    """Return the plugin class for this plugin."""
    return FormattingPlugin 