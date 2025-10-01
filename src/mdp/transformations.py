"""
Transformations: A module for applying transformations to Markdown documents.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Callable

from .document import Document


class Transformation(ABC):
    """
    Abstract base class for markdown transformations.
    """
    
    @abstractmethod
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply a transformation to a markdown document.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        pass


class HeadingLevelTransformation(Transformation):
    """
    Transformation that adjusts heading levels in a markdown document.
    """
    
    def __init__(self, min_level: int = 1, increment: int = 0):
        """
        Initialize a HeadingLevelTransformation.
        
        Args:
            min_level: Minimum heading level to transform (e.g., 1 for # headings)
            increment: Number of levels to adjust (positive or negative)
        """
        self.min_level = min_level
        self.increment = increment
    
    def apply(self, document: Document, output_path: Union[str, Path, None] = None) -> None:
        """
        Apply the heading level transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document (optional)
        """
        content = document.get_content()
        lines = content.split('\n')
        transformed_lines = []
        
        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                
                # Apply transformation if level meets minimum requirement
                if level >= self.min_level:
                    new_level = max(1, min(6, level + self.increment))
                    transformed_lines.append('#' * new_level + ' ' + text)
                else:
                    transformed_lines.append(line)
            else:
                transformed_lines.append(line)
        
        # Update document content in-place
        new_content = '\n'.join(transformed_lines)
        document.update_content(new_content)
        
        # Optionally save to file
        if output_path:
            document.save(output_path)

    def change_heading_level(self, document: Document, heading_text: str, new_level: int) -> str:
        """Changes the level of a specific heading."""
        lines = document.get_content().split('\n')
        new_lines = []
        found = False
        
        for line in lines:
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                
                if text == heading_text:
                    new_level = max(1, min(6, new_level))
                    new_lines.append('#' * new_level + ' ' + text)
                    found = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if not found:
            raise ValueError(f"Heading '{heading_text}' not found in document")
        
        return '\n'.join(new_lines)


class ListFormatTransformation(Transformation):
    """
    Transformation that converts between list formats (ordered/unordered) 
    and changes bullet styles.
    """
    
    def __init__(self, target_type: str = "unordered", bullet_style: str = "-"):
        """
        Initialize a ListFormatTransformation.
        
        Args:
            target_type: The target list type ("ordered" or "unordered")
            bullet_style: The bullet style for unordered lists ("-" or "*")
        """
        if target_type not in ["ordered", "unordered"]:
            raise ValueError("target_type must be 'ordered' or 'unordered'")
        if bullet_style not in ["-", "*"]:
            raise ValueError("bullet_style must be '-' or '*'")
        
        self.target_type = target_type
        self.bullet_style = bullet_style
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply the list format transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        content = document.get_content()
        
        # Process unordered lists
        if self.target_type == "ordered":
            # Convert unordered to ordered
            content = self._convert_unordered_to_ordered(content)
        else:
            # Change bullet style for unordered lists
            content = self._change_bullet_style(content)
        
        # Create a new document with transformed content
        transformed_doc = Document(content=content)
        transformed_doc.save(output_path)
    
    def _convert_unordered_to_ordered(self, content: str) -> str:
        """Convert unordered lists to ordered lists."""
        lines = content.split('\n')
        transformed_lines = []
        
        # Track list items and their nesting level
        in_list = False
        list_items = []
        list_indents = {}  # Maps indent level to current counter
        
        for line in lines:
            # Check for unordered list items
            list_match = re.match(r'^(\s*)[\*\-]\s+(.+)$', line)
            if list_match:
                indent = list_match.group(1)
                item_text = list_match.group(2)
                indent_level = len(indent)
                
                if not in_list:
                    in_list = True
                    list_indents = {indent_level: 1}
                elif indent_level not in list_indents:
                    list_indents[indent_level] = 1
                
                # Create ordered list item
                transformed_lines.append(f"{indent}{list_indents[indent_level]}. {item_text}")
                list_indents[indent_level] += 1
            else:
                # Check for ordered list items (to preserve them)
                ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
                if ol_match:
                    transformed_lines.append(line)
                else:
                    # Not a list item, reset tracking
                    in_list = False
                    list_indents = {}
                    transformed_lines.append(line)
        
        return '\n'.join(transformed_lines)
    
    def _change_bullet_style(self, content: str) -> str:
        """Change bullet style for unordered lists."""
        lines = content.split('\n')
        transformed_lines = []
        
        for line in lines:
            # Check for unordered list items
            list_match = re.match(r'^(\s*)[\*\-]\s+(.+)$', line)
            if list_match:
                indent = list_match.group(1)
                item_text = list_match.group(2)
                transformed_lines.append(f"{indent}{self.bullet_style} {item_text}")
            else:
                transformed_lines.append(line)
        
        return '\n'.join(transformed_lines)


class CodeBlockFormatTransformation(Transformation):
    """
    Transformation that changes the language specifier for code blocks.
    """
    
    def __init__(self, target_language: Optional[str] = None, new_language: Optional[str] = None):
        """
        Initialize a CodeBlockFormatTransformation.
        
        Args:
            target_language: The language to target for transformation (None for all)
            new_language: The new language specifier to use
        """
        self.target_language = target_language
        self.new_language = new_language
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply the code block format transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        content = document.get_content()
        
        if self.target_language is None or self.new_language is None:
            # Nothing to do
            document.save(output_path)
            return
        
        # Find and replace code block language specifiers
        pattern = f"```{self.target_language}(\\s*\\n)"
        replacement = f"```{self.new_language}\\1"
        
        transformed_content = re.sub(pattern, replacement, content)
        
        # Create a new document with transformed content
        transformed_doc = Document(content=transformed_content)
        transformed_doc.save(output_path)


class LinkFormatTransformation(Transformation):
    """
    Transformation that converts between inline and reference-style links.
    """
    
    def __init__(self, style: str = "reference"):
        """
        Initialize a LinkFormatTransformation.
        
        Args:
            style: The target link style ("reference" or "inline")
        """
        if style not in ["reference", "inline"]:
            raise ValueError("style must be 'reference' or 'inline'")
        
        self.style = style
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply the link format transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        content = document.get_content()
        
        if self.style == "reference":
            transformed_content = self._convert_to_reference(content)
        else:
            transformed_content = self._convert_to_inline(content)
        
        # Create a new document with transformed content
        transformed_doc = Document(content=transformed_content)
        transformed_doc.save(output_path)
    
    def _convert_to_reference(self, content: str) -> str:
        """Convert inline links to reference-style links."""
        # Find all inline links
        inline_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        if not inline_links:
            return content
        
        # Create reference links
        reference_definitions = []
        transformed_content = content
        
        for i, (text, url) in enumerate(inline_links, 1):
            ref_id = str(i)
            # Replace inline link with reference link
            transformed_content = transformed_content.replace(
                f"[{text}]({url})", 
                f"[{text}][{ref_id}]", 
                1
            )
            # Add reference definition
            reference_definitions.append(f"[{ref_id}]: {url}")
        
        # Append reference definitions at the end
        if reference_definitions:
            transformed_content += "\n\n" + "\n".join(reference_definitions)
        
        return transformed_content
    
    def _convert_to_inline(self, content: str) -> str:
        """Convert reference-style links to inline links."""
        # Find all reference links and their definitions
        reference_links = re.findall(r'\[([^\]]+)\]\[([^\]]+)\]', content)
        reference_defs = dict(re.findall(r'\[([^\]]+)\]:\s*([^\s]+)', content))
        
        transformed_content = content
        
        for text, ref_id in reference_links:
            if ref_id in reference_defs:
                url = reference_defs[ref_id]
                # Replace reference link with inline link
                transformed_content = transformed_content.replace(
                    f"[{text}][{ref_id}]", 
                    f"[{text}]({url})", 
                    1
                )
        
        # Remove reference definitions
        for ref_id in reference_defs:
            transformed_content = re.sub(
                r'\[' + re.escape(ref_id) + r'\]:\s*[^\s]+\s*\n?', 
                '', 
                transformed_content
            )
        
        return transformed_content


class TableFormatTransformation(Transformation):
    """
    Transformation that changes table alignment in markdown tables.
    """
    
    def __init__(self, alignment: str = "default"):
        """
        Initialize a TableFormatTransformation.
        
        Args:
            alignment: The target alignment ("default", "left", "center", "right")
        """
        if alignment not in ["default", "left", "center", "right"]:
            raise ValueError("alignment must be 'default', 'left', 'center', or 'right'")
        
        self.alignment = alignment
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply the table format transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        content = document.get_content()
        lines = content.split('\n')
        transformed_lines = []
        
        # Process each line
        i = 0
        while i < len(lines):
            current_line = lines[i]
            transformed_lines.append(current_line)
            
            # Check if this line starts a table header row
            if i + 1 < len(lines) and re.match(r'\|[^|]*\|', current_line) and re.match(r'\|\s*[-:]+\s*\|', lines[i + 1]):
                # This is a table header followed by a divider row
                divider_line = lines[i + 1]
                columns = divider_line.count('|') - 1
                
                # Create new divider line based on alignment
                if self.alignment == "left":
                    new_divider = '|' + '|'.join([':----------'] * columns) + '|'
                elif self.alignment == "center":
                    new_divider = '|' + '|'.join([':----------:'] * columns) + '|'
                elif self.alignment == "right":
                    new_divider = '|' + '|'.join(['----------:'] * columns) + '|'
                else:
                    # Default - preserve original
                    new_divider = divider_line
                
                # Replace the divider line
                transformed_lines.pop()  # Remove original header line
                transformed_lines.append(current_line)  # Add it back
                transformed_lines.append(new_divider)  # Add new divider
                i += 2  # Skip the original divider
            else:
                i += 1
        
        # Create a new document with transformed content
        transformed_doc = Document(content='\n'.join(transformed_lines))
        transformed_doc.save(output_path)


class TextStyleTransformation(Transformation):
    """
    Transformation that changes text styling formats (bold/italic) in markdown.
    """
    
    def __init__(self, bold_style: str = "**", italic_style: str = "_"):
        """
        Initialize a TextStyleTransformation.
        
        Args:
            bold_style: The style for bold text ("**" or "__")
            italic_style: The style for italic text ("*" or "_")
        """
        if bold_style not in ["**", "__"]:
            raise ValueError("bold_style must be '**' or '__'")
        if italic_style not in ["*", "_"]:
            raise ValueError("italic_style must be '*' or '_'")
        
        self.bold_style = bold_style
        self.italic_style = italic_style
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply the text style transformation.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        content = document.get_content()
        
        # Transform bold text
        if self.bold_style == "**":
            content = re.sub(r'__([^_]+)__', r'**\1**', content)
        else:
            content = re.sub(r'\*\*([^*]+)\*\*', r'__\1__', content)
        
        # Transform italic text
        if self.italic_style == "*":
            content = re.sub(r'_([^_]+)_', r'*\1*', content)
        else:
            content = re.sub(r'\*([^*]+)\*', r'_\1_', content)
        
        # Create a new document with transformed content
        transformed_doc = Document(content=content)
        transformed_doc.save(output_path)


class TransformationPipeline(Transformation):
    """
    Pipeline for applying multiple transformations in sequence.
    """
    
    def __init__(self, transformations: Optional[List[Transformation]] = None):
        """
        Initialize a TransformationPipeline.
        
        Args:
            transformations: List of transformations to apply
        """
        self.transformations = transformations or []
    
    def add_transformation(self, transformation: Transformation) -> None:
        """
        Add a transformation to the pipeline.
        
        Args:
            transformation: Transformation to add
        """
        self.transformations.append(transformation)
    
    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """
        Apply all transformations in the pipeline.
        
        Args:
            document: The MarkdownDocument to transform
            output_path: Path to save the transformed document
        """
        import tempfile
        from pathlib import Path
        
        if not self.transformations:
            # No transformations to apply
            document.save(output_path)
            return
        
        # Create a temporary directory for intermediate transformations
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Apply first transformation
            tmp_path = Path(tmp_dir) / "tmp_1.md"
            self.transformations[0].apply(document, tmp_path)
            
            # Apply remaining transformations
            for i, transform in enumerate(self.transformations[1:], 2):
                prev_path = Path(tmp_dir) / f"tmp_{i-1}.md"
                curr_path = Path(tmp_dir) / f"tmp_{i}.md"
                
                # Apply transformation
                prev_doc = Document(prev_path)
                transform.apply(prev_doc, curr_path)
                
                # Clean up previous temp file if needed
                if i > 2:
                    Path(tmp_dir, f"tmp_{i-2}.md").unlink(missing_ok=True)
            
            # Copy final transformed document to output path
            final_doc = Document(Path(tmp_dir) / f"tmp_{len(self.transformations)}.md")
            final_doc.save(output_path)


# Utility functions for standalone transformations

def split_paragraph(document: Document, paragraph_index: int, split_point: int) -> Document:
    """
    Split a paragraph at a specific point.

    Args:
        document: The document to modify
        paragraph_index: Index of the paragraph to split
        split_point: Character position to split at

    Returns:
        New document with the paragraph split
    """
    content = document.get_content()
    lines = content.split('\n')

    # Find the paragraph
    paragraphs = []
    current_paragraph = []

    for line in lines:
        if line.strip() == '':
            if current_paragraph:
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(line)

    if current_paragraph:
        paragraphs.append('\n'.join(current_paragraph))

    if paragraph_index >= len(paragraphs):
        return document

    # Split the paragraph
    paragraph = paragraphs[paragraph_index]
    if split_point >= len(paragraph):
        return document

    before = paragraph[:split_point].rstrip()
    after = paragraph[split_point:].lstrip()

    paragraphs[paragraph_index] = before
    paragraphs.insert(paragraph_index + 1, after)

    # Reconstruct content
    new_content = '\n\n'.join(paragraphs)

    return Document(content=new_content)


def merge_paragraphs(document: Document, para1_index: int, para2_index: int) -> Document:
    """
    Merge two adjacent paragraphs.

    Args:
        document: The document to modify
        para1_index: Index of the first paragraph
        para2_index: Index of the second paragraph

    Returns:
        New document with paragraphs merged
    """
    content = document.get_content()
    lines = content.split('\n')

    # Find paragraphs
    paragraphs = []
    current_paragraph = []

    for line in lines:
        if line.strip() == '':
            if current_paragraph:
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
        else:
            current_paragraph.append(line)

    if current_paragraph:
        paragraphs.append('\n'.join(current_paragraph))

    if para1_index >= len(paragraphs) or para2_index >= len(paragraphs) or para1_index == para2_index:
        return document

    # Merge paragraphs
    merged = paragraphs[para1_index] + '\n\n' + paragraphs[para2_index]
    paragraphs[para1_index] = merged

    # Remove the second paragraph
    del paragraphs[para2_index]

    # Reconstruct content
    new_content = '\n\n'.join(paragraphs)

    return Document(content=new_content)


def normalize_headings(document: Document) -> Document:
    """
    Normalize heading levels in a document.

    Args:
        document: The document to normalize

    Returns:
        New document with normalized headings
    """
    content = document.get_content()
    lines = content.split('\n')
    normalized_lines = []

    for line in lines:
        if line.strip().startswith('#'):
            # Count leading # symbols
            level = len(line) - len(line.lstrip('#'))
            # Normalize to reasonable levels (max 6)
            normalized_level = min(level, 6)
            normalized_line = '#' * normalized_level + line.lstrip('#')
            normalized_lines.append(normalized_line)
        else:
            normalized_lines.append(line)

    new_content = '\n'.join(normalized_lines)
    return Document(content=new_content)


def change_heading_level(document: Document, heading_index: int, new_level: int) -> Document:
    """
    Change the level of a specific heading.

    Args:
        document: The document to modify
        heading_index: Index of the heading to change
        new_level: New heading level (1-6)

    Returns:
        New document with the heading level changed
    """
    content = document.get_content()
    lines = content.split('\n')

    # Find headings
    headings = []
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            headings.append((i, line))

    if heading_index >= len(headings):
        return document

    # Change the heading level
    line_index, old_line = headings[heading_index]
    level = len(old_line) - len(old_line.lstrip('#'))
    new_level = max(1, min(6, new_level))  # Clamp to valid range

    if new_level != level:
        new_line = '#' * new_level + old_line.lstrip('#')
        lines[line_index] = new_line

    new_content = '\n'.join(lines)
    return Document(content=new_content) 