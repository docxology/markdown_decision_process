"""
Notebook Converter for Markdown Decision Process.

This module provides utilities for converting between Jupyter notebooks
and Markdown documents, preserving code blocks, outputs, and text content.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import base64


class NotebookConverter:
    """Converter between Jupyter notebooks and Markdown documents."""
    
    def __init__(self, include_outputs: bool = True, include_cell_metadata: bool = False):
        """
        Initialize the notebook converter.
        
        Args:
            include_outputs: Whether to include cell outputs in the conversion
            include_cell_metadata: Whether to include cell metadata in the conversion
        """
        self.include_outputs = include_outputs
        self.include_cell_metadata = include_cell_metadata
    
    def notebook_to_markdown(self, notebook_path: Union[str, Path]) -> str:
        """
        Convert a Jupyter notebook to Markdown.
        
        Args:
            notebook_path: Path to the notebook file
            
        Returns:
            Markdown content as a string
        """
        notebook_path = Path(notebook_path)
        
        if not notebook_path.exists():
            raise FileNotFoundError(f"Notebook file not found: {notebook_path}")
        
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
        
        markdown_content = []
        
        # Add header with notebook metadata if available
        if "metadata" in notebook and self.include_cell_metadata:
            title = notebook.get("metadata", {}).get("title", notebook_path.stem)
            markdown_content.append(f"# {title}\n")
            
            # Add notebook metadata as YAML frontmatter
            markdown_content.append("---")
            for key, value in notebook.get("metadata", {}).items():
                if isinstance(value, (str, int, float, bool)):
                    markdown_content.append(f"{key}: {value}")
            markdown_content.append("---\n")
        
        # Process each cell
        for cell in notebook.get("cells", []):
            cell_type = cell.get("cell_type", "")
            
            # Add cell metadata if requested
            if self.include_cell_metadata and "metadata" in cell:
                markdown_content.append("<!-- Cell Metadata")
                for key, value in cell.get("metadata", {}).items():
                    if isinstance(value, (str, int, float, bool)):
                        markdown_content.append(f"{key}: {value}")
                markdown_content.append("-->\n")
            
            # Process by cell type
            if cell_type == "markdown":
                source = "".join(cell.get("source", []))
                markdown_content.append(source)
                markdown_content.append("")  # Empty line after markdown
                
            elif cell_type == "code":
                source = "".join(cell.get("source", []))
                language = notebook.get("metadata", {}).get("kernelspec", {}).get("language", "python")
                
                # Add code block
                markdown_content.append(f"```{language}")
                markdown_content.append(source.rstrip())
                markdown_content.append("```")
                
                # Add outputs if requested
                if self.include_outputs and "outputs" in cell and cell["outputs"]:
                    markdown_content.append("\nOutput:")
                    markdown_content.append("```")
                    
                    for output in cell["outputs"]:
                        output_type = output.get("output_type", "")
                        
                        if output_type == "stream":
                            stream_text = "".join(output.get("text", []))
                            markdown_content.append(stream_text.rstrip())
                            
                        elif output_type == "execute_result":
                            data = output.get("data", {})
                            if "text/plain" in data:
                                text = "".join(data["text/plain"])
                                markdown_content.append(text.rstrip())
                                
                        elif output_type == "display_data":
                            data = output.get("data", {})
                            if "text/plain" in data:
                                text = "".join(data["text/plain"])
                                markdown_content.append(text.rstrip())
                                
                        elif output_type == "error":
                            traceback = "\n".join(output.get("traceback", []))
                            # Remove ANSI color codes
                            traceback = re.sub(r'\x1b\[\d+m', '', traceback)
                            markdown_content.append(traceback.rstrip())
                    
                    markdown_content.append("```")
                
                markdown_content.append("")  # Empty line after code block
        
        return "\n".join(markdown_content)
    
    def markdown_to_notebook(self, markdown_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Convert a Markdown document to a Jupyter notebook.
        
        Args:
            markdown_path: Path to the Markdown file
            
        Returns:
            Notebook as a dictionary
        """
        markdown_path = Path(markdown_path)
        
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
        
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Initialize notebook structure
        notebook = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Extract YAML frontmatter if present
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', markdown_content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    notebook["metadata"][key.strip()] = value.strip()
            
            # Remove frontmatter from content
            markdown_content = markdown_content[len(frontmatter_match.group(0)):]
        
        # Split content into blocks
        blocks = []
        current_block = []
        in_code_block = False
        code_language = ""
        
        for line in markdown_content.split('\n'):
            code_block_start = re.match(r'```(\w*)', line)
            if code_block_start:
                if not in_code_block:
                    # Start of a code block
                    if current_block:
                        blocks.append(("markdown", "\n".join(current_block)))
                        current_block = []
                    in_code_block = True
                    code_language = code_block_start.group(1) or "python"
                else:
                    # End of a code block
                    blocks.append(("code", code_language, "\n".join(current_block)))
                    current_block = []
                    in_code_block = False
                    code_language = ""
            else:
                current_block.append(line)
        
        # Add the last block if any
        if current_block:
            if in_code_block:
                blocks.append(("code", code_language, "\n".join(current_block)))
            else:
                blocks.append(("markdown", "\n".join(current_block)))
        
        # Create cells from blocks
        for block in blocks:
            if block[0] == "markdown":
                cell = {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": block[1].split('\n')
                }
                notebook["cells"].append(cell)
            elif block[0] == "code":
                cell = {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": block[2].split('\n')
                }
                notebook["cells"].append(cell)
        
        return notebook
    
    def save_notebook(self, notebook: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """
        Save a notebook to a file.
        
        Args:
            notebook: Notebook as a dictionary
            output_path: Path to save the notebook to
        """
        output_path = Path(output_path)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2)


def convert_notebook_to_markdown(notebook_path: Union[str, Path], 
                               output_path: Optional[Union[str, Path]] = None,
                               include_outputs: bool = True) -> str:
    """
    Convert a Jupyter notebook to Markdown.
    
    Args:
        notebook_path: Path to the notebook file
        output_path: Path to save the Markdown file (optional)
        include_outputs: Whether to include cell outputs
        
    Returns:
        Markdown content as a string
    """
    converter = NotebookConverter(include_outputs=include_outputs)
    markdown = converter.notebook_to_markdown(notebook_path)
    
    if output_path:
        output_path = Path(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
    
    return markdown


def convert_markdown_to_notebook(markdown_path: Union[str, Path],
                               output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Convert a Markdown document to a Jupyter notebook.
    
    Args:
        markdown_path: Path to the Markdown file
        output_path: Path to save the notebook file (optional)
        
    Returns:
        Notebook as a dictionary
    """
    converter = NotebookConverter()
    notebook = converter.markdown_to_notebook(markdown_path)
    
    if output_path:
        converter.save_notebook(notebook, output_path)
    
    return notebook


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert between Jupyter notebooks and Markdown")
    parser.add_argument("input_path", help="Input file path (.ipynb or .md)")
    parser.add_argument("output_path", nargs="?", help="Output file path (.md or .ipynb)")
    parser.add_argument("--no-outputs", action="store_true", help="Exclude cell outputs from notebook conversion")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found.")
        exit(1)
    
    if input_path.suffix.lower() == ".ipynb":
        # Convert notebook to markdown
        output_path = args.output_path or input_path.with_suffix(".md")
        markdown = convert_notebook_to_markdown(
            input_path, 
            output_path,
            include_outputs=not args.no_outputs
        )
        print(f"Converted notebook to '{output_path}'")
    elif input_path.suffix.lower() == ".md":
        # Convert markdown to notebook
        output_path = args.output_path or input_path.with_suffix(".ipynb")
        notebook = convert_markdown_to_notebook(input_path, output_path)
        print(f"Converted markdown to '{output_path}'")
    else:
        print(f"Error: Unsupported file type: '{input_path.suffix}'")
        print("Supported file types: .ipynb, .md")
        exit(1) 