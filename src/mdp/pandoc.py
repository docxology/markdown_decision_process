"""
Pandoc: A module for integrating Pandoc with the Markdown Decision Process.
"""

import os
import subprocess
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple

from .document import Document
from .transformations import Transformation, TransformationPipeline
from .state_space import StateSpace


class PandocNotFoundError(Exception):
    """Exception raised when Pandoc is not found on the system."""
    pass


def check_pandoc_installed() -> str:
    """
    Check if Pandoc is installed and available on the system path.
    
    Returns:
        Path to pandoc executable
        
    Raises:
        PandocNotFoundError: If Pandoc is not installed or not found
    """
    pandoc_path = shutil.which("pandoc")
    if not pandoc_path:
        raise PandocNotFoundError(
            "Pandoc is not installed or not found in the system path. "
            "Please install Pandoc from https://pandoc.org/installing.html"
        )
    return pandoc_path


def get_pandoc_version() -> str:
    """
    Get the installed Pandoc version.
    
    Returns:
        Pandoc version string
        
    Raises:
        PandocNotFoundError: If Pandoc is not installed
    """
    try:
        pandoc_path = check_pandoc_installed()
        result = subprocess.run(
            [pandoc_path, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        # Extract version from the first line
        version_line = result.stdout.split("\n")[0]
        return version_line
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get Pandoc version: {e}")


def get_supported_formats() -> Dict[str, List[str]]:
    """
    Get the input and output formats supported by the installed Pandoc.
    
    Returns:
        Dictionary with 'input' and 'output' keys mapping to lists of supported formats
        
    Raises:
        PandocNotFoundError: If Pandoc is not installed
    """
    try:
        pandoc_path = check_pandoc_installed()
        
        # Get input formats
        input_result = subprocess.run(
            [pandoc_path, "--list-input-formats"],
            capture_output=True,
            text=True,
            check=True
        )
        input_formats = [fmt.strip() for fmt in input_result.stdout.split("\n") if fmt.strip()]
        
        # Get output formats
        output_result = subprocess.run(
            [pandoc_path, "--list-output-formats"],
            capture_output=True,
            text=True,
            check=True
        )
        output_formats = [fmt.strip() for fmt in output_result.stdout.split("\n") if fmt.strip()]
        
        return {
            "input": input_formats,
            "output": output_formats
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get Pandoc supported formats: {e}")


def convert_document(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    from_format: Optional[str] = None,
    to_format: Optional[str] = None,
    extra_args: Optional[List[str]] = None
) -> bool:
    """
    Convert a document from one format to another using Pandoc.
    
    Args:
        input_path: Path to the input file
        output_path: Path where the output file will be saved
        from_format: Input format (if None, inferred from file extension)
        to_format: Output format (if None, inferred from file extension)
        extra_args: Additional arguments to pass to Pandoc
        
    Returns:
        True if conversion was successful, False otherwise
        
    Raises:
        PandocNotFoundError: If Pandoc is not installed
    """
    try:
        pandoc_path = check_pandoc_installed()
        
        # Ensure paths are Path objects
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # Build command
        cmd = [pandoc_path]
        
        # Add input format if specified
        if from_format:
            cmd.extend(["--from", from_format])
        
        # Add output format if specified
        if to_format:
            cmd.extend(["--to", to_format])
        
        # Add extra arguments if provided
        if extra_args:
            cmd.extend(extra_args)
        
        # Add input and output files
        cmd.extend(["-o", str(output_path), str(input_path)])
        
        # Run the conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise an exception on non-zero return code
        )
        
        # Check if conversion was successful
        if result.returncode != 0:
            print(f"Pandoc conversion failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"Error during document conversion: {e}")
        return False


def convert_with_transformations(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    pre_transformations: Optional[List[Transformation]] = None,
    post_transformations: Optional[List[Transformation]] = None,
    from_format: Optional[str] = None,
    to_format: Optional[str] = None,
    pandoc_args: Optional[List[str]] = None
) -> bool:
    """
    Convert a document with transformations applied before and/or after Pandoc conversion.
    
    Args:
        input_path: Path to the input file
        output_path: Path where the output file will be saved
        pre_transformations: List of transformations to apply before Pandoc conversion
        post_transformations: List of transformations to apply after Pandoc conversion
        from_format: Input format (if None, inferred from file extension)
        to_format: Output format (if None, inferred from file extension)
        pandoc_args: Additional arguments to pass to Pandoc
        
    Returns:
        True if the entire process was successful, False otherwise
    """
    try:
        # Create temporary files for intermediate steps
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Step 1: Apply pre-transformations if specified
            if pre_transformations and len(pre_transformations) > 0:
                pre_transform_path = temp_dir_path / "pre_transformed.md"
                
                # Create a pipeline for pre-transformations
                pipeline = TransformationPipeline(pre_transformations)
                
                # Apply pre-transformations
                doc = Document(input_path)
                pipeline.apply(doc, pre_transform_path)
                
                # Update input path for Pandoc
                pandoc_input = pre_transform_path
            else:
                # Use original input
                pandoc_input = input_path
            
            # Step 2: Apply Pandoc conversion
            if to_format and to_format.lower() != "markdown":
                # If converting to a non-markdown format, use the final output path
                if post_transformations and len(post_transformations) > 0:
                    # Need an intermediate file for post-transformations
                    pandoc_output = temp_dir_path / "pandoc_output.md"
                else:
                    # Final output
                    pandoc_output = output_path
                
                # Run Pandoc
                conversion_success = convert_document(
                    input_path=pandoc_input,
                    output_path=pandoc_output,
                    from_format=from_format,
                    to_format=to_format,
                    extra_args=pandoc_args
                )
                
                if not conversion_success:
                    return False
                
                # If no post-transformations, we're done
                if not post_transformations or len(post_transformations) == 0:
                    return True
                
                # If the output is not markdown, we can't apply post-transformations
                if to_format.lower() != "markdown":
                    print("Warning: Cannot apply post-transformations to non-markdown output")
                    return True
            else:
                # Either markdown output or no format specified
                pandoc_output = temp_dir_path / "pandoc_output.md"
                conversion_success = convert_document(
                    input_path=pandoc_input,
                    output_path=pandoc_output,
                    from_format=from_format,
                    to_format=to_format or "markdown",
                    extra_args=pandoc_args
                )
                
                if not conversion_success:
                    return False
            
            # Step 3: Apply post-transformations if specified
            if post_transformations and len(post_transformations) > 0:
                # Create a pipeline for post-transformations
                pipeline = TransformationPipeline(post_transformations)
                
                # Apply post-transformations
                doc = Document(pandoc_output)
                pipeline.apply(doc, output_path)
            elif not (to_format and to_format.lower() != "markdown"):
                # Copy the Pandoc output to the final output path if we haven't already written to it
                with open(pandoc_output, "r", encoding="utf-8") as src:
                    with open(output_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
            
            return True
    except Exception as e:
        print(f"Error during conversion with transformations: {e}")
        return False


def extract_metadata(
    input_path: Union[str, Path],
    format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract metadata from a markdown document using Pandoc.
    
    Args:
        input_path: Path to the input file
        format: Input format (if None, inferred from file extension)
        
    Returns:
        Dictionary of metadata fields
        
    Raises:
        PandocNotFoundError: If Pandoc is not installed
    """
    try:
        pandoc_path = check_pandoc_installed()
        
        # Build command to extract metadata as JSON
        cmd = [
            pandoc_path, 
            "-s",  # Standalone document
            "--template={}",  # Empty template to only get metadata
            "-f", format or "markdown",  # Input format
            "-t", "plain",  # Output format 
            "--metadata-file=-"  # Output metadata to stdout
        ]
        
        # Add input file
        cmd.append(str(input_path))
        
        # Run the extraction
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the metadata
        try:
            # Pandoc might output an empty document if no metadata
            if result.stdout.strip():
                # Try to locate the YAML metadata block
                metadata_block = result.stdout
                
                # If it starts with ---, it's a YAML block
                if metadata_block.startswith("---"):
                    # Find the closing --- and extract the YAML
                    end_marker = metadata_block.find("---", 3)
                    if end_marker > 0:
                        metadata_block = metadata_block[3:end_marker].strip()
                
                # Parse the YAML
                import yaml
                return yaml.safe_load(metadata_block) or {}
            return {}
        except Exception as e:
            print(f"Error parsing metadata: {e}")
            return {}
    except subprocess.CalledProcessError as e:
        print(f"Pandoc metadata extraction failed: {e}")
        return {}
    except Exception as e:
        print(f"Error during metadata extraction: {e}")
        return {}


def apply_template(
    input_path: Union[str, Path],
    template_path: Union[str, Path],
    output_path: Union[str, Path],
    variables: Optional[Dict[str, str]] = None,
    from_format: Optional[str] = None,
    to_format: Optional[str] = None,
    extra_args: Optional[List[str]] = None
) -> bool:
    """
    Apply a Pandoc template to a markdown document.
    
    Args:
        input_path: Path to the input file
        template_path: Path to the Pandoc template file
        output_path: Path where the output file will be saved
        variables: Dictionary of variables to pass to Pandoc
        from_format: Input format (if None, inferred from file extension)
        to_format: Output format (if None, inferred from file extension)
        extra_args: Additional arguments to pass to Pandoc
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pandoc_path = check_pandoc_installed()
        
        # Build command
        cmd = [pandoc_path]
        
        # Add input format if specified
        if from_format:
            cmd.extend(["-f", from_format])
        
        # Add output format if specified
        if to_format:
            cmd.extend(["-t", to_format])
        
        # Add template
        cmd.extend(["--template", str(template_path)])
        
        # Add variables
        if variables:
            for key, value in variables.items():
                cmd.extend(["-V", f"{key}={value}"])
        
        # Add extra arguments if provided
        if extra_args:
            cmd.extend(extra_args)
        
        # Add standalone flag for complete documents
        cmd.append("-s")
        
        # Add input and output files
        cmd.extend(["-o", str(output_path), str(input_path)])
        
        # Run the template application
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if successful
        if result.returncode != 0:
            print(f"Pandoc template application failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"Error applying template: {e}")
        return False


class PandocConverter:
    """
    A wrapper class for Pandoc functionality, providing a convenient interface
    for document conversion and other Pandoc-related tasks.
    """
    
    def __init__(self, pandoc_path_override: Optional[str] = None):
        """
        Initialize the PandocConverter.

        Checks if Pandoc is installed and retrieves its path and supported formats.

        Args:
            pandoc_path_override: Optional path to override the system's Pandoc executable.

        Raises:
            PandocNotFoundError: If Pandoc is not found (and not overridden).
        """
        if pandoc_path_override:
            # Basic check for the overridden path
            if not (Path(pandoc_path_override).exists() and Path(pandoc_path_override).is_file()):
                raise PandocNotFoundError(f"Provided Pandoc path not valid or not a file: {pandoc_path_override}")
            self.pandoc_path = pandoc_path_override
        else:
            # This will raise PandocNotFoundError if pandoc is not found
            self.pandoc_path = check_pandoc_installed()
        
        try:
            # get_supported_formats uses check_pandoc_installed() internally, which is fine.
            self.supported_formats = get_supported_formats()
        except (PandocNotFoundError, RuntimeError) as e: 
            # PandocNotFoundError could happen if check_pandoc_installed inside get_supported_formats fails due to some edge case
            # RuntimeError if subprocess calls fail in get_supported_formats
            print(f"Warning: Could not retrieve Pandoc supported formats: {e}. Proceeding with empty formats.")
            self.supported_formats = {"input": [], "output": []}

    def is_pandoc_available(self) -> bool:
        """
        Check if Pandoc is available.
        
        Returns:
            True if Pandoc is available, False otherwise
        """
        try:
            if self.pandoc_path is None:
                self.pandoc_path = check_pandoc_installed()
            return True
        except PandocNotFoundError:
            return False
    
    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        from_format: Optional[str] = None,
        to_format: Optional[str] = None,
        transformations: Optional[List[Transformation]] = None,
        extra_args: Optional[List[str]] = None
    ) -> bool:
        """
        Convert a document using Pandoc with optional transformations.
        
        Args:
            input_path: Path to the input file
            output_path: Path where the output file will be saved
            from_format: Input format (if None, inferred from file extension)
            to_format: Output format (if None, inferred from file extension)
            transformations: List of transformations to apply after Pandoc conversion
            extra_args: Additional arguments to pass to Pandoc
            
        Returns:
            True if conversion was successful, False otherwise
        """
        if not self.is_pandoc_available():
            raise PandocNotFoundError(
                "Pandoc is not installed or not found in the system path."
            )
        
        # Determine if we're converting to a format that supports transformations
        supports_transformations = to_format is None or to_format.lower() == "markdown"
        
        if transformations and not supports_transformations:
            print("Warning: Transformations can only be applied when converting to markdown.")
            transformations = None
        
        # Apply the conversion with transformations if needed
        if transformations:
            return convert_with_transformations(
                input_path=input_path,
                output_path=output_path,
                pre_transformations=None,
                post_transformations=transformations,
                from_format=from_format,
                to_format=to_format,
                pandoc_args=extra_args
            )
        else:
            return convert_document(
                input_path=input_path,
                output_path=output_path,
                from_format=from_format,
                to_format=to_format,
                extra_args=extra_args
            )
    
    def batch_convert(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        from_format: Optional[str] = None,
        to_format: Optional[str] = None,
        file_pattern: str = "*.md",
        transformations: Optional[List[Transformation]] = None,
        extra_args: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Convert multiple documents in a directory using Pandoc.
        
        Args:
            input_dir: Directory containing input files
            output_dir: Directory where output files will be saved
            from_format: Input format (if None, inferred from file extension)
            to_format: Output format (if None, inferred from file extension)
            file_pattern: Glob pattern to match input files
            transformations: List of transformations to apply after Pandoc conversion
            extra_args: Additional arguments to pass to Pandoc
            
        Returns:
            Dictionary mapping filenames to conversion success status
        """
        if not self.is_pandoc_available():
            raise PandocNotFoundError(
                "Pandoc is not installed or not found in the system path."
            )
        
        # Ensure directories are Path objects
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find input files matching the pattern
        input_files = list(input_dir.glob(file_pattern))
        
        # Determine output extension
        if to_format:
            # Use standard extensions for common formats
            ext_map = {
                "html": ".html",
                "html5": ".html",
                "latex": ".tex",
                "beamer": ".tex",
                "docx": ".docx",
                "odt": ".odt",
                "pdf": ".pdf",
                "markdown": ".md",
                "gfm": ".md",
                "commonmark": ".md",
                "rst": ".rst",
                "asciidoc": ".adoc",
                "epub": ".epub",
                "epub3": ".epub"
            }
            output_ext = ext_map.get(to_format.lower(), f".{to_format}")
        else:
            # Keep the same extension
            output_ext = None
        
        # Convert each file
        results = {}
        for input_file in input_files:
            # Determine output filename
            if output_ext:
                output_name = input_file.stem + output_ext
            else:
                output_name = input_file.name
            
            output_path = output_dir / output_name
            
            # Convert the file
            success = self.convert(
                input_path=input_file,
                output_path=output_path,
                from_format=from_format,
                to_format=to_format,
                transformations=transformations,
                extra_args=extra_args
            )
            
            results[input_file.name] = success
        
        return results 