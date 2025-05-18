#!/usr/bin/env python3
"""
Visualization examples for the Markdown Decision Process package.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import (
    MarkdownDocument,
    MarkChain,
    PolicyOptimizer,
    plot_document_metrics,
    plot_transitions,
    plot_document_structure,
    plot_readability_comparison
)


def create_sample_documents():
    """Create sample markdown documents for visualization examples."""
    # Create directory for sample documents
    sample_dir = Path(__file__).parent / "sample_docs"
    sample_dir.mkdir(exist_ok=True)
    
    # Sample 1: Technical documentation
    technical_doc = """# Technical Documentation

## Introduction

This is a technical document demonstrating various markdown features. It includes code blocks, lists, and other elements.

## Code Example

```python
def hello_world():
    print("Hello, world!")
    return True
```

## Features

- Feature 1: Description of feature 1
- Feature 2: Description of feature 2
  - Sub-feature 2.1
  - Sub-feature 2.2
- Feature 3: Description of feature 3

## Advanced Usage

The library provides several advanced capabilities:

1. Capability one
2. Capability two
3. Capability three

## API Reference

| Method | Description | Return Type |
|--------|-------------|-------------|
| `method1()` | Does something | `void` |
| `method2(arg)` | Does something with arg | `boolean` |
| `method3(arg1, arg2)` | Complex operation | `Object` |

"""
    
    # Sample 2: Blog post
    blog_post = """# 10 Tips for Effective Writing

Writing effectively is crucial for clear communication. Here are 10 tips to improve your writing skills.

## 1. Know Your Audience

Always consider who will be reading your content. Tailor your tone, vocabulary, and examples to match their expectations and knowledge level.

## 2. Start with an Outline

Before diving into writing, create a rough outline of what you want to cover. This helps maintain structure and ensures you don't miss important points.

## 3. Be Concise

Avoid unnecessary words and phrases. Get to the point quickly to keep readers engaged.

## 4. Use Active Voice

Active voice makes your writing stronger and more direct. Instead of "The report was written," say "I wrote the report."

## 5. Edit Ruthlessly

Good writing comes from good editing. Cut anything that doesn't serve your purpose.

The remaining tips include proper grammar usage, incorporating examples, reading widely, seeking feedback, and practicing regularly.
"""
    
    # Sample 3: Research paper
    research_paper = """# Analysis of Performance Optimization Techniques

## Abstract

This paper presents an analysis of various performance optimization techniques applied to web applications. We compare different approaches and provide quantitative measurements of their effectiveness.

## 1. Introduction

Performance optimization remains a critical challenge in modern web development. As applications grow in complexity, ensuring fast load times and responsive interfaces becomes increasingly difficult.

## 2. Methodology

Our study evaluated 5 popular optimization techniques across 20 different web applications. Measurements were taken using standard performance metrics including:

- Time to First Byte (TTFB)
- First Contentful Paint (FCP)
- Time to Interactive (TTI)
- Total Blocking Time (TBT)

## 3. Results

The data collected shows significant variation in effectiveness depending on application architecture.

### 3.1 Caching Strategies

Implementing proper HTTP caching provided the most consistent benefits across all application types, with an average 47% improvement in load time.

### 3.2 Code Splitting

Applications utilizing modern JavaScript frameworks benefited significantly from code splitting, showing a 38% reduction in initial load time.

## 4. Conclusion

Our analysis demonstrates that no single optimization technique provides universal benefits. Developers should prioritize optimizations based on their specific application characteristics and user needs.

## References

[1] Smith, J. (2022). Web Performance Optimization.
[2] Jones, A. et al. (2021). Modern Techniques for Web Speed.
"""
    
    # Save sample documents
    with open(sample_dir / "technical_doc.md", "w") as f:
        f.write(technical_doc)
    
    with open(sample_dir / "blog_post.md", "w") as f:
        f.write(blog_post)
    
    with open(sample_dir / "research_paper.md", "w") as f:
        f.write(research_paper)
    
    return sample_dir


def document_structure_visualization(sample_dir):
    """Example of document structure visualization."""
    print("\n=== Document Structure Visualization Example ===")
    
    # Load sample documents
    docs = {
        "Technical Doc": MarkdownDocument(sample_dir / "technical_doc.md"),
        "Blog Post": MarkdownDocument(sample_dir / "blog_post.md"),
        "Research Paper": MarkdownDocument(sample_dir / "research_paper.md")
    }
    
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    # Visualize the structure of each document
    for doc_name, doc in docs.items():
        print(f"\nVisualizing structure of {doc_name}...")
        fig = plot_document_structure(doc)
        output_path = output_dir / f"{doc_name.lower().replace(' ', '_')}_structure.png"
        fig.savefig(output_path)
        print(f"Structure visualization saved to {output_path}")


def document_metrics_visualization(sample_dir):
    """Example of document metrics visualization."""
    print("\n=== Document Metrics Visualization Example ===")
    
    # Load sample documents
    docs = {
        "Technical Doc": sample_dir / "technical_doc.md",
        "Blog Post": sample_dir / "blog_post.md",
        "Research Paper": sample_dir / "research_paper.md"
    }
    
    # Create a document quality analyzer
    from mdp.quality import DocumentQuality
    quality = DocumentQuality()
    
    # Calculate metrics for each document
    metrics = {}
    for doc_name, doc_path in docs.items():
        print(f"\nCalculating metrics for {doc_name}...")
        doc = MarkdownDocument(doc_path)
        metrics[doc_name] = quality.analyze_document(doc)
    
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    # Visualize metrics comparison
    print("\nCreating metrics comparison visualization...")
    fig = plot_document_metrics(metrics)
    output_path = output_dir / "document_metrics_comparison.png"
    fig.savefig(output_path)
    print(f"Metrics visualization saved to {output_path}")


def transitions_visualization(sample_dir):
    """Example of MarkChain transitions visualization."""
    print("\n=== MarkChain Transitions Visualization Example ===")
    
    # Load and combine sample documents for training
    all_content = ""
    for doc_path in sample_dir.glob("*.md"):
        with open(doc_path, "r") as f:
            all_content += f.read() + "\n\n"
    
    # Train a MarkChain model
    print("\nTraining MarkChain on sample documents...")
    chain = MarkChain(order=2)
    chain.train(all_content)
    
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    # Visualize transitions
    print("\nVisualizing state transitions...")
    fig = plot_transitions(chain, top_n=10)
    output_path = output_dir / "markchain_transitions.png"
    fig.savefig(output_path)
    print(f"Transitions visualization saved to {output_path}")


def readability_comparison(sample_dir):
    """Example of readability comparison visualization."""
    print("\n=== Readability Comparison Visualization Example ===")
    
    # Load sample documents
    docs = {
        "Technical Doc": sample_dir / "technical_doc.md",
        "Blog Post": sample_dir / "blog_post.md",
        "Research Paper": sample_dir / "research_paper.md"
    }
    
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Import textstat to check availability
        import textstat
        
        # Visualize readability comparison
        print("\nComparing document readability...")
        fig = plot_readability_comparison(docs)
        output_path = output_dir / "readability_comparison.png"
        fig.savefig(output_path)
        print(f"Readability comparison saved to {output_path}")
    except ImportError:
        print("\nTextstat package not found. To run readability comparison, install with:")
        print("pip install textstat")


def main():
    """Run the visualization examples."""
    parser = argparse.ArgumentParser(description="Markdown Decision Process Visualization Examples")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    parser.add_argument("--structure", action="store_true", help="Run document structure visualization")
    parser.add_argument("--metrics", action="store_true", help="Run document metrics visualization")
    parser.add_argument("--transitions", action="store_true", help="Run transitions visualization")
    parser.add_argument("--readability", action="store_true", help="Run readability comparison")
    
    args = parser.parse_args()
    
    # If no args or --all, run everything
    run_all = args.all or not (args.structure or args.metrics or args.transitions or args.readability)
    
    # Create sample documents for examples
    sample_dir = create_sample_documents()
    print(f"Created sample documents in {sample_dir}")
    
    # Run requested examples
    if args.structure or run_all:
        document_structure_visualization(sample_dir)
        
    if args.metrics or run_all:
        document_metrics_visualization(sample_dir)
        
    if args.transitions or run_all:
        transitions_visualization(sample_dir)
        
    if args.readability or run_all:
        readability_comparison(sample_dir)
    
    # Show output location
    output_dir = Path(__file__).parent / "visualization_output"
    print(f"\nAll visualizations have been saved to {output_dir}")
    print("You can view the PNG files to see the visualization results.")


if __name__ == "__main__":
    main() 