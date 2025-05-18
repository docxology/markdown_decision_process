#!/usr/bin/env python3
"""
Advanced document optimization pipeline example for the Markdown Decision Process package.

This example demonstrates:
1. Creating a multi-stage optimization pipeline for markdown documents
2. Using PolicyOptimizer with custom reward functions
3. Applying targeted transformations for different document elements
4. Measuring document quality before and after optimization
5. Visualizing the optimization results
"""

import sys
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import (
    MarkdownDocument,
    PolicyOptimizer,
    DocumentQuality,
    StateSpace,
    HeadingLevelTransformation,
    ListFormatTransformation,
    CodeBlockFormatTransformation,
    LinkFormatTransformation,
    TableFormatTransformation,
    TextStyleTransformation,
    TransformationPipeline
)


def create_optimization_pipeline() -> TransformationPipeline:
    """
    Create a comprehensive transformation pipeline for document optimization.
    
    Returns:
        Configured transformation pipeline
    """
    # Create individual transformations
    heading_transform = HeadingLevelTransformation(
        min_level=1,
        increment=0  # No change in levels, just normalize
    )
    
    list_transform = ListFormatTransformation(
        target_type="unordered",  # Use unordered lists
        bullet_style="-"     # Standardize on hyphen bullets
    )
    
    code_transform = CodeBlockFormatTransformation(
        target_language=None,  # Will be applied to all code blocks
        new_language=None      # No change to language specifier
    )
    
    link_transform = LinkFormatTransformation(
        style="reference"  # Convert to reference-style links for readability
    )
    
    table_transform = TableFormatTransformation(
        alignment="default"  # Use default alignment
    )
    
    text_transform = TextStyleTransformation(
        bold_style="**",  # Use double asterisks for bold
        italic_style="*"  # Use asterisks for italics
    )
    
    # Create a pipeline with all transformations
    pipeline = TransformationPipeline([
        heading_transform,
        list_transform,
        code_transform,
        link_transform,
        table_transform,
        text_transform
    ])
    
    return pipeline


def optimize_document(input_path: str, output_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply a comprehensive optimization process to a markdown document.
    
    Args:
        input_path: Path to the input markdown document
        output_path: Path to save the optimized document
        
    Returns:
        Tuple of (original metrics, optimized metrics)
    """
    print(f"\nOptimizing document: {input_path}")
    print(f"Output will be saved to: {output_path}")
    
    # Create quality analyzer
    quality = DocumentQuality(
        readability_weight=0.5,
        information_density_weight=0.3,
        structural_balance_weight=0.2
    )
    
    # Load the original document
    original_doc = MarkdownDocument(file_path=input_path)
    
    # Analyze original document
    print("\nAnalyzing original document...")
    original_metrics = quality.analyze_document(original_doc)
    
    # First stage: Apply basic transformations pipeline
    print("\nStage 1: Applying basic transformations...")
    pipeline = create_optimization_pipeline()
    
    # Create intermediate file
    intermediate_path = Path(output_path).with_suffix(".intermediate.md")
    pipeline.apply(original_doc, str(intermediate_path))
    
    # Second stage: Apply policy optimization
    print("\nStage 2: Applying policy optimization...")
    optimizer = PolicyOptimizer(
        reward_weights={
            "readability": 0.6,
            "information_density": 0.2,
            "structural_balance": 0.2
        },
        custom_rewards={
            "paragraph_length": lambda doc: _calculate_paragraph_length_reward(doc),
            "heading_distribution": lambda doc: _calculate_heading_distribution_reward(doc),
            "list_to_paragraph_ratio": lambda doc: _calculate_list_ratio_reward(doc)
        },
        learning_rate=0.15,
        max_iterations=50
    )
    
    # Apply the policy optimizer to the intermediate document
    optimized_content = optimizer.transform(str(intermediate_path))
    
    # Save the optimized document
    with open(output_path, "w") as f:
        f.write(optimized_content)
    
    # Load the optimized document for analysis
    optimized_doc = MarkdownDocument(content=optimized_content)
    
    # Analyze optimized document
    print("\nAnalyzing optimized document...")
    optimized_metrics = quality.analyze_document(optimized_doc)
    
    # Clean up intermediate file
    intermediate_path.unlink(missing_ok=True)
    
    return original_metrics, optimized_metrics


def _calculate_paragraph_length_reward(doc: MarkdownDocument) -> float:
    """
    Calculate a reward based on paragraph length distribution.
    Favors paragraphs between 3-6 lines long.
    
    Args:
        doc: Markdown document
        
    Returns:
        Reward value between 0.0 and 1.0
    """
    paragraphs = doc.get_paragraphs()
    if not paragraphs:
        return 0.5  # Neutral reward if no paragraphs
    
    # Count lines in each paragraph
    paragraph_lines = [len(p.split("\n")) for p in paragraphs]
    
    # Calculate reward: higher for paragraphs with 3-6 lines
    good_length_count = sum(1 for length in paragraph_lines if 3 <= length <= 6)
    reward = good_length_count / len(paragraphs)
    
    return min(max(reward, 0.0), 1.0)  # Ensure reward is between 0 and 1


def _calculate_heading_distribution_reward(doc: MarkdownDocument) -> float:
    """
    Calculate a reward based on heading level distribution.
    Rewards more for proper hierarchical structure.
    
    Args:
        doc: Markdown document
        
    Returns:
        Reward value between 0.0 and 1.0
    """
    headings = doc.get_headings()
    if not headings:
        return 0.5  # Neutral reward if no headings
    
    # Count headings by level
    level_counts = {}
    for heading in headings:
        level = heading.get("level", 0)
        level_counts[level] = level_counts.get(level, 0) + 1
    
    # Reward based on decreasing count with increasing level
    levels = sorted(level_counts.keys())
    is_decreasing = all(level_counts.get(levels[i], 0) >= level_counts.get(levels[i+1], 0) 
                        for i in range(len(levels)-1))
    
    # Reward for hierarchy breadth (using levels 1-3)
    breadth_reward = len([l for l in level_counts if 1 <= l <= 3]) / 3
    
    # Reward for hierarchy depth
    depth_reward = min(len(level_counts) / 4, 1.0)
    
    # Combine rewards
    reward = (0.5 * breadth_reward + 0.3 * depth_reward + 0.2 * float(is_decreasing))
    
    return min(max(reward, 0.0), 1.0)  # Ensure reward is between 0 and 1


def _calculate_list_ratio_reward(doc: MarkdownDocument) -> float:
    """
    Calculate a reward based on the ratio of list items to paragraphs.
    Rewards documents with a balanced mix of lists and paragraphs.
    
    Args:
        doc: Markdown document
        
    Returns:
        Reward value between 0.0 and 1.0
    """
    paragraphs = doc.get_paragraphs()
    lists = doc.get_lists()
    
    if not paragraphs:
        return 0.5  # Neutral reward if no paragraphs
    
    # Calculate list item count
    list_item_count = sum(len(lst.get("items", [])) for lst in lists)
    
    # Calculate ratio of list items to paragraphs
    ratio = list_item_count / len(paragraphs)
    
    # Reward is highest when ratio is around 1.0 (balanced)
    if ratio <= 1.0:
        reward = ratio
    else:
        reward = 1.0 / ratio  # Decreases as ratio increases above 1.0
    
    return min(max(reward, 0.0), 1.0)  # Ensure reward is between 0 and 1


def visualize_optimization_results(
    original_metrics: Dict[str, Any], 
    optimized_metrics: Dict[str, Any],
    output_dir: Path
) -> None:
    """
    Visualize the results of document optimization.
    
    Args:
        original_metrics: Metrics for the original document
        optimized_metrics: Metrics for the optimized document
        output_dir: Directory to save visualizations
    """
    print("\nGenerating visualizations...")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # 1. Comparison of key metrics
    metrics_to_plot = [
        ("readability", "flesch_reading_ease", "Flesch Reading Ease"),
        ("readability", "flesch_kincaid_grade", "Flesch-Kincaid Grade"),
        ("information_density", "entropy", "Information Entropy"),
        ("structural_balance", "heading_balance", "Heading Balance"),
        ("overall_score", None, "Overall Score")
    ]
    
    # Setup the figure
    plt.figure(figsize=(12, 6))
    
    # Extract metrics for plotting
    metrics_values = []
    labels = []
    
    for category, name, label in metrics_to_plot:
        if name:
            original_value = original_metrics.get(category, {}).get(name, 0)
            optimized_value = optimized_metrics.get(category, {}).get(name, 0)
        else:
            original_value = original_metrics.get(category, 0)
            optimized_value = optimized_metrics.get(category, 0)
            
        metrics_values.append((original_value, optimized_value))
        labels.append(label)
    
    # Plot as a grouped bar chart
    x = np.arange(len(labels))
    width = 0.35
    
    plt.bar(x - width/2, [m[0] for m in metrics_values], width, label='Original')
    plt.bar(x + width/2, [m[1] for m in metrics_values], width, label='Optimized')
    
    plt.ylabel('Score')
    plt.title('Document Quality Metrics Comparison')
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / "quality_metrics_comparison.png", dpi=300)
    print(f"Saved metrics comparison to {output_dir / 'quality_metrics_comparison.png'}")
    
    # 2. Document structure comparison
    plt.figure(figsize=(12, 5))
    
    # Plot document structure elements
    structure_elements = ["paragraphs", "headings", "lists", "code_blocks", "tables"]
    element_labels = ["Paragraphs", "Headings", "Lists", "Code Blocks", "Tables"]
    
    original_counts = [
        len(original_metrics.get("structure", {}).get("paragraphs", [])),
        len(original_metrics.get("structure", {}).get("headings", [])),
        len(original_metrics.get("structure", {}).get("lists", [])),
        len(original_metrics.get("structure", {}).get("code_blocks", [])),
        len(original_metrics.get("structure", {}).get("tables", []))
    ]
    
    optimized_counts = [
        len(optimized_metrics.get("structure", {}).get("paragraphs", [])),
        len(optimized_metrics.get("structure", {}).get("headings", [])),
        len(optimized_metrics.get("structure", {}).get("lists", [])),
        len(optimized_metrics.get("structure", {}).get("code_blocks", [])),
        len(optimized_metrics.get("structure", {}).get("tables", []))
    ]
    
    x = np.arange(len(element_labels))
    width = 0.35
    
    plt.bar(x - width/2, original_counts, width, label='Original')
    plt.bar(x + width/2, optimized_counts, width, label='Optimized')
    
    plt.ylabel('Count')
    plt.title('Document Structure Element Comparison')
    plt.xticks(x, element_labels)
    plt.legend()
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / "structure_comparison.png", dpi=300)
    print(f"Saved structure comparison to {output_dir / 'structure_comparison.png'}")


def main():
    """Run the document optimization pipeline example."""
    parser = argparse.ArgumentParser(description="Document Optimization Pipeline")
    parser.add_argument("--input", help="Path to input markdown document")
    parser.add_argument("--output", help="Path to save optimized document")
    args = parser.parse_args()
    
    # Define paths for input/output
    script_dir = Path(__file__).parent
    sample_docs_dir = script_dir / "sample_docs"
    output_dir = script_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Determine input file
    if args.input:
        input_path = Path(args.input)
    else:
        # Use a sample document
        sample_docs_dir.mkdir(exist_ok=True)
        
        # Check if we already have a document for optimization
        existing_docs = list(sample_docs_dir.glob("*.md"))
        
        if existing_docs:
            input_path = existing_docs[0]
            print(f"Using existing document: {input_path}")
        else:
            # Create a sample document
            print("Creating a sample document for optimization...")
            input_path = create_sample_document(sample_docs_dir)
    
    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        # Create output path based on input filename
        output_filename = f"{input_path.stem}_optimized.md"
        output_path = output_dir / output_filename
    
    # Run the optimization pipeline
    original_metrics, optimized_metrics = optimize_document(
        str(input_path), 
        str(output_path)
    )
    
    # Print summary of metrics
    print("\nOriginal document metrics:")
    print_metrics_summary(original_metrics)
    
    print("\nOptimized document metrics:")
    print_metrics_summary(optimized_metrics)
    
    # Visualize the results
    visualize_optimization_results(original_metrics, optimized_metrics, output_dir)
    
    print(f"\nOptimization complete. Optimized document saved to: {output_path}")


def print_metrics_summary(metrics: Dict[str, Any]) -> None:
    """Print a summary of document metrics."""
    print("  Readability:")
    for metric, value in metrics.get('readability', {}).items():
        print(f"    {metric.replace('_', ' ').title()}: {value:.2f}")
    
    print("  Information Density:")
    for metric, value in metrics.get('information_density', {}).items():
        print(f"    {metric.replace('_', ' ').title()}: {value:.2f}")
    
    print("  Structural Balance:")
    for metric, value in metrics.get('structural_balance', {}).items():
        print(f"    {metric.replace('_', ' ').title()}: {value:.2f}")
    
    print(f"  Overall Score: {metrics.get('overall_score', 0):.2f}")


def create_sample_document(output_dir: Path) -> Path:
    """
    Create a sample markdown document that needs optimization.
    
    Args:
        output_dir: Directory to save the sample document
        
    Returns:
        Path to the created document
    """
    sample_path = output_dir / "sample_for_optimization.md"
    
    # Create a deliberately suboptimal document
    content = """# Markdown Optimization Example Document
    
This is a sample document that demonstrates various markdown features and formatting issues that could be optimized. This paragraph is intentionally quite long and could benefit from being broken up into smaller, more digestible chunks. It includes multiple thoughts and concepts without proper organization, which makes it harder to read and understand. The reader might get lost in the middle of this text without clear markers of where one idea ends and another begins.

## subsection one - inconsistent capitalization

this section has inconsistent capitalization in the heading and starts without proper capitalization in the text. it also uses dashes instead of spaces in the heading.

### Deep Nested Section Without Parent
This section skips a level in the heading hierarchy, which is not ideal for document structure.

## SECTION TWO - ALL CAPS
THIS SECTION USES ALL CAPS WHICH IS LIKE SHOUTING AND HARD TO READ. IT DOESN'T FOLLOW THE STYLE OF THE REST OF THE DOCUMENT.

Here's a poorly formatted list:
* Item one
+ Item two
- Item three with very long text that wraps around to multiple lines and doesn't have proper indentation which makes it hard to follow and understand the structure of the list items
* Item four

## Code Examples

Here's a code block without language specification:
```
function helloWorld() {
  console.log("Hello, world!");
}
```

## Information presentation

Here's a poorly formatted table:
|Column 1|Column 2|Column 3|
|-|-|-|
|Data|More data|Even more data that is quite long and makes the column width inconsistent|
|Short|medium length text|very long text that breaks formatting|

## Links Section

This section has both inline links like [example](https://example.com) and reference links like [another example][ref1], making the style inconsistent.

[ref1]: https://example.org

## Mixed Text Styles

This section uses _underscores_ for emphasis but also uses *asterisks* for the same purpose, creating inconsistency.

For strong emphasis, it uses both __double underscores__ and **double asterisks**.

# Inappropriately Large Heading
## For a subsection that should be better structured

## Final Thoughts

This document has poor structure, inconsistent formatting, and could benefit greatly from the optimization pipeline.
"""
    
    with open(sample_path, "w") as f:
        f.write(content)
    
    print(f"Created sample document at: {sample_path}")
    return sample_path


if __name__ == "__main__":
    main() 