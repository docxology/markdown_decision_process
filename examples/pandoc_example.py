#!/usr/bin/env python3
"""
Pandoc integration examples for the Markdown Decision Process package.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import (
    MarkdownDocument,
    HeadingLevelTransformation,
    ListFormatTransformation,
    CodeBlockFormatTransformation,
    LinkFormatTransformation,
    PandocConverter,
    check_pandoc_installed,
    get_pandoc_version,
    get_supported_formats,
    convert_document,
    convert_with_transformations,
    extract_metadata,
    apply_template,
    PandocNotFoundError
)


def check_pandoc():
    """Check if Pandoc is installed and get version information."""
    print("\n=== Checking Pandoc Installation ===")
    
    try:
        # Check if Pandoc is installed
        pandoc_path = check_pandoc_installed()
        print(f"✅ Pandoc found at: {pandoc_path}")
        
        # Get Pandoc version
        version = get_pandoc_version()
        print(f"✅ Pandoc version: {version}")
        
        # Get supported formats
        formats = get_supported_formats()
        
        print("\nSupported input formats:")
        for fmt in formats["input"]:
            print(f"  - {fmt}")
        
        print("\nSupported output formats:")
        for fmt in formats["output"]:
            print(f"  - {fmt}")
        
        return True
    except PandocNotFoundError as e:
        print(f"❌ Pandoc not found: {e}")
        print("\nPlease install Pandoc to run these examples:")
        print("  - Download from: https://pandoc.org/installing.html")
        print("  - On Ubuntu/Debian: sudo apt-get install pandoc")
        print("  - On macOS with Homebrew: brew install pandoc")
        print("  - On Windows with Chocolatey: choco install pandoc")
        return False


def create_sample_document():
    """Create a sample markdown document for conversion examples."""
    print("\n=== Creating Sample Document ===")
    
    # Create directories for samples and output
    sample_dir = Path(__file__).parent / "pandoc_samples"
    sample_dir.mkdir(exist_ok=True)
    
    output_dir = Path(__file__).parent / "pandoc_output"
    output_dir.mkdir(exist_ok=True)
    
    # Sample document with YAML metadata
    sample_doc = """---
title: "Sample Document for Pandoc Conversion"
author: "MDP Framework"
date: "2023-07-10"
abstract: "This is a sample document demonstrating various markdown features for Pandoc conversion."
keywords: ["markdown", "pandoc", "conversion", "example"]
---

# Sample Document

## Introduction

This is a sample document demonstrating various markdown features. It includes:

- Code blocks
- Lists (ordered and unordered)
- Tables
- Links
- Blockquotes

## Code Example

```python
def fibonacci(n):
    \"\"\"Return the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Calculate the 10th Fibonacci number
result = fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")
```

## Lists

### Unordered List

- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered List

1. First item
2. Second item
   1. Nested item 2.1
   2. Nested item 2.2
3. Third item

## Table

| Feature | Description | Supported |
|---------|-------------|-----------|
| Tables | Markdown tables with formatting | Yes |
| Code Blocks | Syntax highlighted code | Yes |
| Math | LaTeX-style math formulas | Yes |
| Footnotes | Reference-style footnotes | Yes |

## Links and Images

Here's a [link to the Pandoc website](https://pandoc.org/).

## Blockquotes

> This is a blockquote.
> It can span multiple lines and contains emphasized text like *this* or **this**.

## Math Expressions

When rendered with Pandoc to formats like LaTeX or HTML with MathJax, you can include math expressions:

The Fibonacci sequence is defined as:

$$F_n = F_{n-1} + F_{n-2}$$

With initial conditions:

$$F_0 = 0, F_1 = 1$$

## Conclusion

This document demonstrates various markdown features that can be processed by Pandoc for conversion to different formats.
"""
    
    # Save sample document
    sample_path = sample_dir / "sample.md"
    with open(sample_path, "w") as f:
        f.write(sample_doc)
    
    print(f"✅ Sample document created at: {sample_path}")
    return sample_dir, output_dir


def basic_conversion_example(sample_dir, output_dir):
    """Example of basic document conversion using Pandoc."""
    print("\n=== Basic Conversion Example ===")
    
    sample_path = sample_dir / "sample.md"
    
    # Convert to HTML
    html_output = output_dir / "sample.html"
    print(f"\nConverting markdown to HTML: {html_output}")
    success = convert_document(
        input_path=sample_path,
        output_path=html_output,
        to_format="html",
        extra_args=["--standalone", "--toc"]
    )
    
    if success:
        print(f"✅ Successfully converted to HTML: {html_output}")
    else:
        print("❌ HTML conversion failed")
    
    # Convert to LaTeX
    latex_output = output_dir / "sample.tex"
    print(f"\nConverting markdown to LaTeX: {latex_output}")
    success = convert_document(
        input_path=sample_path,
        output_path=latex_output,
        to_format="latex",
        extra_args=["--standalone"]
    )
    
    if success:
        print(f"✅ Successfully converted to LaTeX: {latex_output}")
    else:
        print("❌ LaTeX conversion failed")
    
    # Try PDF conversion if possible
    pdf_output = output_dir / "sample.pdf"
    print(f"\nConverting markdown to PDF: {pdf_output}")
    success = convert_document(
        input_path=sample_path,
        output_path=pdf_output,
        to_format="pdf",
        extra_args=["--toc"]
    )
    
    if success:
        print(f"✅ Successfully converted to PDF: {pdf_output}")
    else:
        print("❌ PDF conversion failed (LaTeX may not be installed)")
    
    # Convert to DOCX (Microsoft Word)
    docx_output = output_dir / "sample.docx"
    print(f"\nConverting markdown to DOCX: {docx_output}")
    success = convert_document(
        input_path=sample_path,
        output_path=docx_output,
        to_format="docx"
    )
    
    if success:
        print(f"✅ Successfully converted to DOCX: {docx_output}")
    else:
        print("❌ DOCX conversion failed")


def conversion_with_transformations(sample_dir, output_dir):
    """Example of document conversion with transformations."""
    print("\n=== Conversion with Transformations Example ===")
    
    sample_path = sample_dir / "sample.md"
    
    # Create transformations
    transformations = [
        # Decrease all heading levels by 1 (h1 -> h2, h2 -> h3, etc.)
        HeadingLevelTransformation(min_level=1, increment=1),
        
        # Convert unordered lists to ordered lists
        ListFormatTransformation(target_type="ordered"),
        
        # Change Python code blocks to Python3
        CodeBlockFormatTransformation(
            target_language="python", 
            new_language="python3"
        ),
        
        # Convert inline links to reference-style links
        LinkFormatTransformation(style="reference")
    ]
    
    # Convert to markdown with transformations
    transformed_md_output = output_dir / "sample_transformed.md"
    print(f"\nConverting with transformations to markdown: {transformed_md_output}")
    
    success = convert_with_transformations(
        input_path=sample_path,
        output_path=transformed_md_output,
        post_transformations=transformations,
        to_format="markdown"
    )
    
    if success:
        print(f"✅ Successfully converted with transformations: {transformed_md_output}")
        
        # Show diff summary
        original_doc = MarkdownDocument(sample_path)
        transformed_doc = MarkdownDocument(transformed_md_output)
        
        print("\nTransformation summary:")
        print(f"  - Original headings: {len(original_doc.get_headings())}")
        print(f"  - Transformed headings: {len(transformed_doc.get_headings())}")
        
        # Count unordered and ordered lists
        original_lists = original_doc.get_lists()
        transformed_lists = transformed_doc.get_lists()
        
        original_unordered = sum(1 for lst in original_lists if lst["type"] == "unordered")
        original_ordered = sum(1 for lst in original_lists if lst["type"] == "ordered")
        
        transformed_unordered = sum(1 for lst in transformed_lists if lst["type"] == "unordered")
        transformed_ordered = sum(1 for lst in transformed_lists if lst["type"] == "ordered")
        
        print(f"  - Original lists: {original_unordered} unordered, {original_ordered} ordered")
        print(f"  - Transformed lists: {transformed_unordered} unordered, {transformed_ordered} ordered")
        
        # Check code blocks
        original_code_blocks = original_doc.get_code_blocks()
        transformed_code_blocks = transformed_doc.get_code_blocks()
        
        print(f"  - Original code blocks: {len(original_code_blocks)}")
        for block in original_code_blocks:
            print(f"    - Language: {block['language']}")
        
        print(f"  - Transformed code blocks: {len(transformed_code_blocks)}")
        for block in transformed_code_blocks:
            print(f"    - Language: {block['language']}")
    else:
        print("❌ Transformation failed")


def metadata_extraction_example(sample_dir, output_dir):
    """Example of extracting metadata from a markdown document."""
    print("\n=== Metadata Extraction Example ===")
    
    sample_path = sample_dir / "sample.md"
    
    try:
        # Extract metadata
        metadata = extract_metadata(sample_path)
        
        # Print metadata
        print("\nExtracted metadata:")
        if metadata:
            for key, value in metadata.items():
                print(f"  - {key}: {value}")
        else:
            print("  No metadata found or extraction failed")
        
        # Save metadata as JSON
        import json
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nMetadata saved to: {metadata_path}")
    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")


def pandoc_converter_example(sample_dir, output_dir):
    """Example of using the PandocConverter class."""
    print("\n=== PandocConverter Class Example ===")
    
    # Create a PandocConverter
    converter = PandocConverter()
    
    if not converter.is_pandoc_available():
        print("❌ Pandoc is not available")
        return
    
    print("✅ Pandoc is available")
    
    # Create transformations
    transformations = [
        HeadingLevelTransformation(min_level=1, increment=-1),  # h2 -> h1, h3 -> h2, etc.
        CodeBlockFormatTransformation(
            target_language="python", 
            new_language="python3"
        )
    ]
    
    # Convert a single file
    sample_path = sample_dir / "sample.md"
    html_output = output_dir / "converter_sample.html"
    
    print(f"\nConverting markdown to HTML with PandocConverter: {html_output}")
    success = converter.convert(
        input_path=sample_path,
        output_path=html_output,
        to_format="html",
        extra_args=["--standalone", "--toc"]
    )
    
    if success:
        print(f"✅ Successfully converted to HTML: {html_output}")
    else:
        print("❌ HTML conversion failed")
    
    # Convert to markdown with transformations
    transformed_output = output_dir / "converter_transformed.md"
    
    print(f"\nConverting markdown to markdown with transformations: {transformed_output}")
    success = converter.convert(
        input_path=sample_path,
        output_path=transformed_output,
        to_format="markdown",
        transformations=transformations
    )
    
    if success:
        print(f"✅ Successfully transformed: {transformed_output}")
    else:
        print("❌ Transformation failed")
    
    # Batch conversion example
    print("\nPerforming batch conversion of all markdown files...")
    batch_results = converter.batch_convert(
        input_dir=sample_dir,
        output_dir=output_dir / "batch",
        to_format="html",
        file_pattern="*.md",
        extra_args=["--standalone"]
    )
    
    print("\nBatch conversion results:")
    for filename, success in batch_results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  - {filename}: {status}")


def main():
    """Run the Pandoc integration examples."""
    parser = argparse.ArgumentParser(description="Markdown Decision Process Pandoc Examples")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--check", action="store_true", help="Check Pandoc installation")
    parser.add_argument("--basic", action="store_true", help="Run basic conversion example")
    parser.add_argument("--transform", action="store_true", help="Run transformation example")
    parser.add_argument("--metadata", action="store_true", help="Run metadata extraction example")
    parser.add_argument("--converter", action="store_true", help="Run PandocConverter example")
    
    args = parser.parse_args()
    
    # If no args or --all, run everything
    run_all = args.all or not (args.check or args.basic or args.transform or 
                              args.metadata or args.converter)
    
    # Check Pandoc installation first
    if args.check or run_all:
        pandoc_available = check_pandoc()
        if not pandoc_available:
            print("\n❌ Pandoc is not available. Skipping examples.")
            return
    else:
        try:
            check_pandoc_installed()
        except PandocNotFoundError as e:
            print(f"\n❌ Pandoc is not available: {e}")
            print("Please install Pandoc to run these examples.")
            return
    
    # Create sample document
    sample_dir, output_dir = create_sample_document()
    
    # Run requested examples
    if args.basic or run_all:
        basic_conversion_example(sample_dir, output_dir)
        
    if args.transform or run_all:
        conversion_with_transformations(sample_dir, output_dir)
        
    if args.metadata or run_all:
        metadata_extraction_example(sample_dir, output_dir)
        
    if args.converter or run_all:
        pandoc_converter_example(sample_dir, output_dir)
    
    # Summary message
    print(f"\nAll Pandoc examples completed. Output files can be found in: {output_dir}")


if __name__ == "__main__":
    main() 