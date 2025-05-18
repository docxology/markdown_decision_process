#!/usr/bin/env python3
"""
Transformations examples for the Markdown Decision Process package.
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
    TableFormatTransformation,
    TextStyleTransformation,
    TransformationPipeline
)


def heading_transformation_example():
    """Example of heading level transformations."""
    print("\n=== Heading Level Transformation Example ===")
    
    # Create a sample markdown
    sample = """# Main Title

## Section 1

Some content here.

## Section 2

### Subsection 2.1

More content here.
    """
    
    # Save the sample to a file
    with open("tests/fixtures/headings_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Increase heading levels by 1
    transform = HeadingLevelTransformation(min_level=1, increment=1)
    transform.apply(doc, "tests/outputs/headings_increased.md")
    
    # Decrease heading levels for level 2+
    transform = HeadingLevelTransformation(min_level=2, increment=-1)
    transform.apply(doc, "tests/outputs/headings_decreased.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/headings_original.md (original)")
    print("  - tests/outputs/headings_increased.md (all headings increased by 1 level)")
    print("  - tests/outputs/headings_decreased.md (level 2+ headings decreased by 1 level)")


def list_transformation_example():
    """Example of list format transformations."""
    print("\n=== List Format Transformation Example ===")
    
    # Create a sample markdown
    sample = """# Lists Example

## Unordered List

- Item 1
- Item 2
  - Nested item 1
  - Nested item 2
- Item 3

## Ordered List

1. First item
2. Second item
   1. Nested first
   2. Nested second
3. Third item
    """
    
    # Save the sample to a file
    with open("tests/fixtures/lists_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Convert unordered lists to ordered
    transform = ListFormatTransformation(target_type="ordered")
    transform.apply(doc, "tests/outputs/lists_ordered.md")
    
    # Change bullet style to asterisks
    transform = ListFormatTransformation(target_type="unordered", bullet_style="*")
    transform.apply(doc, "tests/outputs/lists_asterisks.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/lists_original.md (original)")
    print("  - tests/outputs/lists_ordered.md (unordered lists converted to ordered)")
    print("  - tests/outputs/lists_asterisks.md (bullet style changed to asterisks)")


def code_block_transformation_example():
    """Example of code block transformations."""
    print("\n=== Code Block Transformation Example ===")
    
    # Create a sample markdown
    sample = """# Code Blocks Example

## Python Example

```python
def hello_world():
    print("Hello, world!")
```

## JavaScript Example

```javascript
function helloWorld() {
    console.log("Hello, world!");
}
```
    """
    
    # Save the sample to a file
    with open("tests/fixtures/code_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Change Python to Python3
    transform = CodeBlockFormatTransformation(
        target_language="python", 
        new_language="python3"
    )
    transform.apply(doc, "tests/outputs/code_python3.md")
    
    # Change JavaScript to JS
    transform = CodeBlockFormatTransformation(
        target_language="javascript", 
        new_language="js"
    )
    transform.apply(doc, "tests/outputs/code_js.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/code_original.md (original)")
    print("  - tests/outputs/code_python3.md (python changed to python3)")
    print("  - tests/outputs/code_js.md (javascript changed to js)")


def link_transformation_example():
    """Example of link format transformations."""
    print("\n=== Link Format Transformation Example ===")
    
    # Create a sample markdown with inline links
    inline_sample = """# Link Example

This is a [link to example](https://example.com) in a paragraph.

Here's another [link to GitHub](https://github.com).
    """
    
    # Create a sample markdown with reference links
    reference_sample = """# Reference Link Example

This is a [link to example][1] in a paragraph.

Here's another [link to GitHub][2].

[1]: https://example.com
[2]: https://github.com
    """
    
    # Save the samples to files
    with open("tests/fixtures/links_inline.md", "w") as f:
        f.write(inline_sample)
    
    with open("tests/fixtures/links_reference.md", "w") as f:
        f.write(reference_sample)
    
    # Create documents
    inline_doc = MarkdownDocument(content=inline_sample)
    reference_doc = MarkdownDocument(content=reference_sample)
    
    # Convert inline to reference
    transform = LinkFormatTransformation(style="reference")
    transform.apply(inline_doc, "tests/outputs/links_inline_to_reference.md")
    
    # Convert reference to inline
    transform = LinkFormatTransformation(style="inline")
    transform.apply(reference_doc, "tests/outputs/links_reference_to_inline.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/links_inline.md (original inline)")
    print("  - tests/fixtures/links_reference.md (original reference)")
    print("  - tests/outputs/links_inline_to_reference.md (inline converted to reference)")
    print("  - tests/outputs/links_reference_to_inline.md (reference converted to inline)")


def table_transformation_example():
    """Example of table format transformations."""
    print("\n=== Table Format Transformation Example ===")
    
    # Create a sample markdown with tables
    sample = """# Table Example

## Default Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
    """
    
    # Save the sample to a file
    with open("tests/fixtures/table_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Apply different alignments
    left_transform = TableFormatTransformation(alignment="left")
    left_transform.apply(doc, "tests/outputs/table_left.md")
    
    center_transform = TableFormatTransformation(alignment="center")
    center_transform.apply(doc, "tests/outputs/table_center.md")
    
    right_transform = TableFormatTransformation(alignment="right")
    right_transform.apply(doc, "tests/outputs/table_right.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/table_original.md (original)")
    print("  - tests/outputs/table_left.md (left-aligned)")
    print("  - tests/outputs/table_center.md (center-aligned)")
    print("  - tests/outputs/table_right.md (right-aligned)")


def text_style_transformation_example():
    """Example of text style transformations."""
    print("\n=== Text Style Transformation Example ===")
    
    # Create a sample markdown with styling
    sample = """# Text Style Example

This paragraph has **bold text** and *italic text*.

This paragraph uses __alternate bold__ and _alternate italic_.
    """
    
    # Save the sample to a file
    with open("tests/fixtures/style_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Change to alternate styles
    transform = TextStyleTransformation(bold_style="__", italic_style="*")
    transform.apply(doc, "tests/outputs/style_alternate.md")
    
    # Change to standard styles
    transform = TextStyleTransformation(bold_style="**", italic_style="_")
    transform.apply(doc, "tests/outputs/style_standard.md")
    
    print("\nTransformation applied. Check the following files:")
    print("  - tests/fixtures/style_original.md (original)")
    print("  - tests/outputs/style_alternate.md (using __ for bold and * for italic)")
    print("  - tests/outputs/style_standard.md (using ** for bold and _ for italic)")


def pipeline_example():
    """Example of transformation pipeline."""
    print("\n=== Transformation Pipeline Example ===")
    
    # Create a sample markdown
    sample = """# Pipeline Example

## Section 1

This paragraph has **bold text** and *italic text*.

- Item 1
- Item 2
- Item 3

```python
def example():
    return "Hello, world!"
```

## Section 2

This is a [link to example](https://example.com).

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
    """
    
    # Save the sample to a file
    with open("tests/fixtures/pipeline_original.md", "w") as f:
        f.write(sample)
    
    # Create document
    doc = MarkdownDocument(content=sample)
    
    # Create pipeline with multiple transformations
    pipeline = TransformationPipeline([
        HeadingLevelTransformation(min_level=2, increment=-1),
        ListFormatTransformation(target_type="ordered"),
        CodeBlockFormatTransformation(target_language="python", new_language="python3"),
        LinkFormatTransformation(style="reference"),
        TableFormatTransformation(alignment="center"),
        TextStyleTransformation(bold_style="__", italic_style="*")
    ])
    
    # Apply the pipeline
    pipeline.apply(doc, "tests/outputs/pipeline_result.md")
    
    print("\nPipeline applied. Check the following files:")
    print("  - tests/fixtures/pipeline_original.md (original)")
    print("  - tests/outputs/pipeline_result.md (combined transformations)")


def main():
    """Run the examples."""
    parser = argparse.ArgumentParser(description="Markdown Transformations Examples")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--headings", action="store_true", help="Run heading transformation example")
    parser.add_argument("--lists", action="store_true", help="Run list transformation example")
    parser.add_argument("--code", action="store_true", help="Run code block transformation example")
    parser.add_argument("--links", action="store_true", help="Run link transformation example")
    parser.add_argument("--tables", action="store_true", help="Run table transformation example")
    parser.add_argument("--styles", action="store_true", help="Run text style transformation example")
    parser.add_argument("--pipeline", action="store_true", help="Run pipeline example")
    
    args = parser.parse_args()
    
    # If no args or --all, run everything
    run_all = args.all or not (args.headings or args.lists or args.code or 
                               args.links or args.tables or args.styles or args.pipeline)
    
    if args.headings or run_all:
        heading_transformation_example()
        
    if args.lists or run_all:
        list_transformation_example()
        
    if args.code or run_all:
        code_block_transformation_example()
        
    if args.links or run_all:
        link_transformation_example()
        
    if args.tables or run_all:
        table_transformation_example()
        
    if args.styles or run_all:
        text_style_transformation_example()
        
    if args.pipeline or run_all:
        pipeline_example()
    
    print("\nAll examples completed. Check the generated .md files.")


if __name__ == "__main__":
    main() 