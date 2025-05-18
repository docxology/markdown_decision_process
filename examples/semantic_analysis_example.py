#!/usr/bin/env python3
"""
Advanced semantic analysis example for the Markdown Decision Process package.

This example demonstrates:
1. Analyzing different document types (blog post, technical doc, research paper)
2. Comparing semantic analysis results across document types
3. Visualizing belief states and semantic classifications
4. Using belief updater for uncertain classifications
5. Generating semantic-aware content based on document type
"""

import sys
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import (
    BeliefUpdater,
    MarkdownDocument,
    StateSpace,
    MarkChain,
    DocumentQuality
)


def analyze_document_type(file_path: str) -> Dict[str, Any]:
    """
    Analyze a document and determine its semantic characteristics and document type.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Dictionary containing analysis results
    """
    print(f"\nAnalyzing document: {file_path}")
    
    # Create a belief updater with custom semantic classes for document types
    document_types = [
        "blog_post", "technical_documentation", 
        "research_paper", "tutorial", "reference"
    ]
    
    # Custom beliefs for different document types
    prior_beliefs = {
        # Technical documentation tends to have more structure and references
        "structure": 0.7,
        "consistency": 0.8,
        "reference": 0.6,
        
        # Research papers tend to have more complex language and citations
        "complexity": 0.5,
        "reference": 0.7,
        
        # Blog posts tend to be more narrative and approachable 
        "readability": 0.8,
        "coherence": 0.7
    }
    
    # Create belief updater for document analysis
    belief_updater = BeliefUpdater(
        semantic_classes=document_types,
        prior_beliefs=prior_beliefs,
        noise_factor=0.1  # Add some noise to simulate uncertainty
    )
    
    # Analyze document
    analysis = belief_updater.analyze_document_file(file_path)
    
    # Get document content for additional analysis
    doc = MarkdownDocument(file_path=file_path)
    content = doc.get_content()
    structure = doc.get_structure()
    
    # Run additional analysis with DocumentQuality
    quality = DocumentQuality()
    quality_metrics = quality.analyze_document(doc)
    
    # State space analysis for transition patterns
    state_space = StateSpace()
    state_space.parse_markdown_file(file_path)
    
    # Combine all analyses
    result = {
        "file_path": file_path,
        "semantic_analysis": analysis,
        "document_name": Path(file_path).stem,
        "word_count": len(content.split()),
        "structure_elements": len(structure),
        "quality_metrics": quality_metrics,
        "state_patterns": {
            "total_states": len(state_space.states),
            "total_transitions": sum(len(state_space.get_transitions(state_id)) for state_id in state_space.states),
            "state_types": _count_state_types(state_space)
        }
    }
    
    # Print a summary
    print(f"Document type: {analysis['overall_semantic_class']}")
    print(f"Confidence: {analysis['overall_probability']:.2f}")
    print(f"Word count: {result['word_count']}")
    print(f"Structure elements: {result['structure_elements']}")
    print(f"Reading ease: {quality_metrics.get('readability', {}).get('flesch_reading_ease', 0):.2f}")
    
    return result


def _count_state_types(state_space: StateSpace) -> Dict[str, int]:
    """Count the different types of states in a state space."""
    state_types = {}
    for state in state_space.states.values():
        state_type = state.get('type', 'unknown')
        state_types[state_type] = state_types.get(state_type, 0) + 1
    return state_types


def visualize_document_comparison(analyses: List[Dict[str, Any]]) -> None:
    """
    Visualize comparison between different document types.
    
    Args:
        analyses: List of document analyses to compare
    """
    print("\nGenerating visualizations...")
    
    # Create output directory
    output_dir = Path(__file__).parent / "visualization_output"
    output_dir.mkdir(exist_ok=True)
    
    # Get document names
    doc_names = [analysis["document_name"] for analysis in analyses]
    
    # 1. Plot document types as a bar chart of belief probabilities
    plt.figure(figsize=(12, 6))
    
    # For each document, plot the belief distribution
    for i, analysis in enumerate(analyses):
        # Get belief distribution
        belief_dist = analysis["semantic_analysis"]["overall_belief"]
        
        # Sort beliefs by probability
        sorted_beliefs = sorted(
            belief_dist.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Plot as grouped bar chart
        categories = [b[0] for b in sorted_beliefs]
        values = [b[1] for b in sorted_beliefs]
        x = np.arange(len(categories))
        
        # Plot with offset for grouped bars
        offset = 0.2 * (i - len(analyses)/2 + 0.5)
        plt.bar(x + offset, values, width=0.2, label=analysis["document_name"])
    
    plt.xlabel('Document Types')
    plt.ylabel('Probability')
    plt.title('Document Type Classification')
    plt.xticks(range(len(categories)), categories, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / "document_type_classification.png", dpi=300)
    print(f"Saved visualization to {output_dir / 'document_type_classification.png'}")
    
    # 2. Plot readability metrics comparison
    plt.figure(figsize=(10, 6))
    
    # Extract readability metrics
    metrics = ["flesch_reading_ease", "flesch_kincaid_grade"]
    metric_labels = ["Flesch Reading Ease", "Flesch-Kincaid Grade"]
    
    # Create data for plotting
    x = np.arange(len(metrics))
    width = 0.8 / len(analyses)
    
    for i, analysis in enumerate(analyses):
        readability = analysis["quality_metrics"].get("readability", {})
        values = [readability.get(m, 0) for m in metrics]
        offset = width * (i - len(analyses)/2 + 0.5)
        plt.bar(x + offset, values, width=width, label=analysis["document_name"])
    
    plt.xlabel('Metric')
    plt.ylabel('Score')
    plt.title('Readability Comparison')
    plt.xticks(x, metric_labels)
    plt.legend()
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / "readability_comparison.png", dpi=300)
    print(f"Saved visualization to {output_dir / 'readability_comparison.png'}")
    
    # 3. Plot state type distribution
    plt.figure(figsize=(12, 8))
    
    for i, analysis in enumerate(analyses):
        plt.subplot(1, len(analyses), i+1)
        
        state_types = analysis["state_patterns"]["state_types"]
        labels = list(state_types.keys())
        values = list(state_types.values())
        
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title(f"{analysis['document_name']} State Types")
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_dir / "state_type_distribution.png", dpi=300)
    print(f"Saved visualization to {output_dir / 'state_type_distribution.png'}")


def generate_semantic_aware_content(analyses: List[Dict[str, Any]]) -> None:
    """
    Generate new content based on semantic analysis of documents.
    
    This function demonstrates how the semantic understanding can be used
    to generate new content that matches the style and purpose of a document.
    
    Args:
        analyses: List of document analyses
    """
    print("\nGenerating semantic-aware content...")
    
    # Create output directory
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    for analysis in analyses:
        doc_name = analysis["document_name"]
        doc_path = analysis["file_path"]
        doc_type = analysis["semantic_analysis"]["overall_semantic_class"]
        
        print(f"\nGenerating content for {doc_name} (Type: {doc_type})")
        
        # Create a MarkChain model trained on the document
        chain = MarkChain(order=2)
        
        # Load document content
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Train the model
        chain.train(content)
        
        # Generate new content based on document type
        seed_text = f"# Generated {doc_type.replace('_', ' ').title()}\n\n"
        
        # Generate content
        generated = chain.sample(length=20, seed_text=seed_text)
        
        # Save generated content
        output_path = output_dir / f"{doc_name}_generated.md"
        with open(output_path, 'w') as f:
            f.write(generated)
        
        print(f"Generated content saved to {output_path}")


def main():
    """Run the semantic analysis example."""
    parser = argparse.ArgumentParser(description="Semantic Document Analysis")
    parser.add_argument("--docs", nargs='+', help="Paths to markdown documents to analyze")
    args = parser.parse_args()
    
    # Define paths to sample documents
    sample_docs_dir = Path(__file__).parent / "sample_docs"
    
    if args.docs:
        # Use provided document paths
        doc_paths = [Path(doc) for doc in args.docs]
    else:
        # Use default sample documents
        if not sample_docs_dir.exists():
            print(f"Sample documents directory not found: {sample_docs_dir}")
            print("Creating sample documents...")
            create_sample_documents()
        
        # Find markdown files in the sample docs directory
        doc_paths = list(sample_docs_dir.glob("*.md"))
    
    if not doc_paths:
        print("No documents found for analysis.")
        return
    
    print(f"Found {len(doc_paths)} documents for analysis.")
    
    # Analyze each document
    analyses = []
    for doc_path in doc_paths:
        analysis = analyze_document_type(str(doc_path))
        analyses.append(analysis)
    
    # Visualize comparison between documents
    visualize_document_comparison(analyses)
    
    # Generate content based on semantic analysis
    generate_semantic_aware_content(analyses)


def create_sample_documents():
    """Create sample documents for analysis if they don't exist."""
    sample_docs_dir = Path(__file__).parent / "sample_docs"
    sample_docs_dir.mkdir(exist_ok=True)
    
    # Create a blog post sample
    blog_post = """# My Journey with Markdown
    
Writing in Markdown has been a game-changer for my productivity. It's simple, intuitive, and incredibly versatile.

## The Beginning

I first discovered Markdown when I started using GitHub for my coding projects. It seemed like a simple way to format README files, but I quickly realized it was so much more.

## Why I Love Markdown

Here are a few reasons why I've fallen in love with Markdown:

- **Simplicity**: The syntax is straightforward and easy to learn
- **Portability**: My documents can be viewed anywhere
- **Flexibility**: I can convert to HTML, PDF, and many other formats
- **Focus**: I can concentrate on writing rather than formatting

## My Favorite Tools

1. VS Code with Markdown extensions
2. Typora for distraction-free writing
3. Pandoc for conversions to other formats

If you haven't tried Markdown yet, give it a shot! You might be surprised at how it transforms your writing workflow.
"""
    
    # Create a technical documentation sample
    technical_doc = """# API Documentation

## Overview

This API provides access to the customer database and related services.

## Authentication

Authentication uses OAuth 2.0 with JWT tokens.

```
POST /auth/token
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

## Endpoints

### GET /customers

Returns a list of all customers.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| page | int | Page number |
| limit | int | Items per page |

**Response:**

```json
{
  "customers": [
    {
      "id": 1,
      "name": "Acme Inc.",
      "created_at": "2023-01-15T14:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

## Error Handling

All errors return appropriate HTTP status codes and a JSON body with details.
"""
    
    # Create a research paper sample
    research_paper = """# Analysis of Markdown Usage in Technical Documentation

## Abstract

This paper presents an analysis of Markdown adoption in technical documentation across various industries. We examined over 500 documentation repositories to understand patterns of Markdown usage, extensions employed, and correlation with documentation quality metrics.

## Introduction

Technical documentation has evolved significantly with the advent of lightweight markup languages. Markdown, created by John Gruber in 2004, has emerged as a popular choice due to its simplicity and readability.

## Methodology

Our research methodology involved the following components:

1. Collection of documentation repositories from GitHub, GitLab, and Bitbucket
2. Analysis of Markdown feature usage using custom parsing tools
3. Survey of 150 technical writers regarding their Markdown workflows
4. Evaluation of documentation quality using established metrics

## Results

The analysis revealed several key findings:

| Industry | Markdown Adoption | Primary Extensions |
|----------|------------------|-------------------|
| Software | 78.3% | GFM, Math |
| Healthcare | 42.1% | Tables, Footnotes |
| Finance | 35.7% | Tables, Warnings |
| Education | 61.2% | Math, Diagrams |

Figure 1 illustrates the correlation between Markdown adoption and documentation quality scores.

## Discussion

Our findings suggest that Markdown adoption correlates positively with several quality metrics, particularly readability and maintenance frequency. However, complex documentation requirements often necessitate extensions beyond standard Markdown.

## Conclusion

Markdown has established itself as a valuable tool in technical documentation workflows, particularly in software development. Future research should examine the emergence of Markdown-inspired formats and their impact on documentation practices.

## References

1. Gruber, J. (2004). Markdown. Retrieved from https://daringfireball.net/projects/markdown/
2. Smith, J. et al. (2021). Comparative Analysis of Lightweight Markup Languages. Journal of Technical Communication, 45(3), 112-128.
3. Zhang, L. (2022). Documentation Quality Metrics: A Systematic Review. Technical Communication Quarterly, 31(2), 78-95.
"""
    
    # Save sample documents
    with open(sample_docs_dir / "blog_post.md", "w") as f:
        f.write(blog_post)
    
    with open(sample_docs_dir / "technical_doc.md", "w") as f:
        f.write(technical_doc)
    
    with open(sample_docs_dir / "research_paper.md", "w") as f:
        f.write(research_paper)
    
    print("Created sample documents in:", sample_docs_dir)


if __name__ == "__main__":
    main() 