#!/usr/bin/env python3
"""
Advanced MarkChain example for the Markdown Decision Process package.

This example demonstrates:
1. Training MarkChain models on different document types
2. Using higher-order Markov models for better context sensitivity
3. Generating document content in specific styles
4. Analyzing transition probabilities between markdown elements
5. Visualizing the learned state transition patterns
"""

import sys
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp import (
    MarkChain,
    MarkdownDocument,
    StateSpace,
    DocumentQuality
)


def train_specialized_models(docs_dir: Path) -> Dict[str, MarkChain]:
    """
    Train specialized MarkChain models on different document types.
    
    Args:
        docs_dir: Directory containing markdown documents
        
    Returns:
        Dictionary mapping document types to trained models
    """
    print("\nTraining specialized MarkChain models...")
    
    # Define document types and their file patterns
    document_types = {
        "blog_post": ["blog_*.md", "post_*.md"],
        "technical_doc": ["technical_*.md", "api_*.md", "reference_*.md"],
        "research_paper": ["research_*.md", "paper_*.md", "study_*.md"]
    }
    
    # Find all markdown files
    all_files = list(docs_dir.glob("*.md"))
    if not all_files:
        print(f"No markdown files found in {docs_dir}. Creating samples...")
        create_sample_documents(docs_dir)
        all_files = list(docs_dir.glob("*.md"))
    
    # Categorize files by document type
    categorized_files = {}
    for doc_type, patterns in document_types.items():
        files = []
        for pattern in patterns:
            files.extend(list(docs_dir.glob(pattern)))
        
        if files:
            categorized_files[doc_type] = files
        else:
            # Try to guess type from content
            for file in all_files:
                if file not in [f for sublist in categorized_files.values() for f in sublist]:
                    # Read the first few lines to guess document type
                    with open(file, 'r') as f:
                        content = f.read(1000)  # Read first 1000 chars
                        
                        if "abstract" in content.lower() or "methodology" in content.lower():
                            if "research_paper" not in categorized_files:
                                categorized_files["research_paper"] = []
                            categorized_files["research_paper"].append(file)
                        elif "api" in content.lower() or "function" in content.lower() or "method" in content.lower():
                            if "technical_doc" not in categorized_files:
                                categorized_files["technical_doc"] = []
                            categorized_files["technical_doc"].append(file)
                        else:
                            if "blog_post" not in categorized_files:
                                categorized_files["blog_post"] = []
                            categorized_files["blog_post"].append(file)
    
    # Train a model for each document type
    models = {}
    for doc_type, files in categorized_files.items():
        print(f"Training model for {doc_type} with {len(files)} files:")
        for file in files:
            print(f"  - {file.name}")
        
        # Create a model with higher order for better context
        model = MarkChain(order=2)
        
        # Train on all files of this type
        for file in files:
            with open(file, 'r') as f:
                content = f.read()
                model.train(content)
        
        models[doc_type] = model
    
    return models


def generate_specialized_content(models: Dict[str, MarkChain], output_dir: Path) -> Dict[str, Path]:
    """
    Generate content in different document styles using specialized models.
    
    Args:
        models: Dictionary of trained MarkChain models
        output_dir: Directory to save generated content
        
    Returns:
        Dictionary mapping document types to generated file paths
    """
    print("\nGenerating specialized content...")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Define seed content for each document type
    seeds = {
        "blog_post": """# My Thoughts on Markdown

## Introduction

""",
        "technical_doc": """# API Reference

## Overview

""",
        "research_paper": """# Research Findings

## Abstract

"""
    }
    
    # Generate content with each model
    generated_files = {}
    for doc_type, model in models.items():
        print(f"Generating {doc_type} content...")
        
        # Get seed text
        seed_text = seeds.get(doc_type, f"# Generated {doc_type.replace('_', ' ').title()}\n\n")
        
        # Generate content
        length = 50 if doc_type == "blog_post" else 75  # Research and technical docs longer
        generated = model.sample(length=length, seed_text=seed_text)
        
        # Save generated content
        output_path = output_dir / f"generated_{doc_type}.md"
        with open(output_path, 'w') as f:
            f.write(generated)
        
        print(f"  Saved to {output_path}")
        generated_files[doc_type] = output_path
    
    return generated_files


def analyze_transitions(models: Dict[str, MarkChain]) -> Dict[str, Dict[str, float]]:
    """
    Analyze transition patterns in different document types.
    
    Args:
        models: Dictionary of trained MarkChain models
        
    Returns:
        Dictionary with transition analysis for each model
    """
    print("\nAnalyzing transition patterns...")
    
    analysis = {}
    for doc_type, model in models.items():
        print(f"Analyzing {doc_type} transitions...")
        
        # Get transition counts
        transitions = {}
        for history, counter in model.transitions.items():
            # For 2nd order models, we'll look at the last state in history
            from_state = history[-1] if isinstance(history, tuple) else history
            
            # Skip very long states for analysis clarity
            if len(from_state) > 100:
                from_state = from_state[:50] + "..."
            
            for to_state, count in counter.items():
                if len(to_state) > 100:
                    to_state = to_state[:50] + "..."
                
                # Categorize states
                from_category = categorize_state(from_state)
                to_category = categorize_state(to_state)
                
                transition_key = f"{from_category} → {to_category}"
                transitions[transition_key] = transitions.get(transition_key, 0) + count
        
        # Calculate probabilities
        total_transitions = sum(transitions.values())
        probabilities = {k: v / total_transitions for k, v in transitions.items()}
        
        # Keep only top transitions for simplicity
        top_transitions = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:10])
        
        analysis[doc_type] = top_transitions
        
        # Print top transitions
        print(f"Top transitions for {doc_type}:")
        for transition, prob in top_transitions.items():
            print(f"  {transition}: {prob:.3f}")
    
    return analysis


def categorize_state(state: str) -> str:
    """
    Categorize a markdown state into a simplified category.
    
    Args:
        state: Raw markdown state
        
    Returns:
        Simplified category name
    """
    state = state.strip()
    
    if state.startswith("#"):
        # Count the number of # to determine heading level
        level = 0
        for char in state:
            if char == '#':
                level += 1
            else:
                break
        return f"h{level}"
    
    if state.startswith("-") or state.startswith("*") or state.startswith("+"):
        return "list_item"
    
    if state.startswith("1.") or state.startswith("2."):
        return "ordered_item"
    
    if state.startswith("```"):
        return "code_block"
    
    if state.startswith(">"):
        return "blockquote"
    
    if "|" in state and "-|-" in state:
        return "table"
    
    if not state:
        return "blank"
    
    if len(state) < 40:
        return "short_text"
    
    return "paragraph"


def visualize_transition_patterns(
    analysis: Dict[str, Dict[str, float]], 
    output_dir: Path
) -> None:
    """
    Visualize transition patterns between different document types.
    
    Args:
        analysis: Dictionary with transition analysis
        output_dir: Directory to save visualizations
    """
    print("\nVisualizing transition patterns...")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Create a figure for each document type
    for doc_type, transitions in analysis.items():
        plt.figure(figsize=(12, 8))
        
        # Extract categories and probabilities
        categories = list(transitions.keys())
        probs = list(transitions.values())
        
        # Sort by probability
        sorted_indices = np.argsort(probs)
        categories = [categories[i] for i in sorted_indices]
        probs = [probs[i] for i in sorted_indices]
        
        # Create horizontal bar chart
        y_pos = np.arange(len(categories))
        plt.barh(y_pos, probs, align='center')
        plt.yticks(y_pos, categories)
        
        plt.xlabel('Probability')
        plt.title(f'Transition Probabilities for {doc_type.replace("_", " ").title()}')
        plt.tight_layout()
        
        # Save the figure
        output_path = output_dir / f"{doc_type}_transitions.png"
        plt.savefig(output_path, dpi=300)
        print(f"  Saved to {output_path}")
    
    # Create a combined comparison figure
    plt.figure(figsize=(15, 10))
    
    # Find common transitions across all document types
    all_transitions = set()
    for transitions in analysis.values():
        all_transitions.update(transitions.keys())
    
    common_transitions = [t for t in all_transitions if all(t in analysis[dt] for dt in analysis)]
    
    if common_transitions:
        # If there are common transitions, create comparison chart
        x = np.arange(len(common_transitions))
        width = 0.8 / len(analysis)
        
        for i, (doc_type, transitions) in enumerate(analysis.items()):
            values = [transitions.get(t, 0) for t in common_transitions]
            offset = width * (i - len(analysis)/2 + 0.5)
            plt.bar(x + offset, values, width=width, label=doc_type.replace("_", " ").title())
        
        plt.xlabel('Transition')
        plt.ylabel('Probability')
        plt.title('Transition Probability Comparison')
        plt.xticks(x, common_transitions, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        # Save the figure
        output_path = output_dir / "transition_comparison.png"
        plt.savefig(output_path, dpi=300)
        print(f"  Saved comparison to {output_path}")
    
    # Create a heatmap visualization of state type transitions
    for doc_type, transitions in analysis.items():
        # Extract unique state types
        state_types = set()
        for transition in transitions.keys():
            from_state, to_state = transition.split(" → ")
            state_types.add(from_state)
            state_types.add(to_state)
        
        state_types = sorted(list(state_types))
        
        # Create a matrix for the heatmap
        matrix = np.zeros((len(state_types), len(state_types)))
        
        # Fill the matrix with transition probabilities
        for transition, prob in transitions.items():
            from_state, to_state = transition.split(" → ")
            if from_state in state_types and to_state in state_types:
                from_idx = state_types.index(from_state)
                to_idx = state_types.index(to_state)
                matrix[from_idx, to_idx] = prob
        
        # Create the heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(matrix, cmap='viridis')
        
        # Add labels
        plt.xticks(np.arange(len(state_types)), state_types, rotation=45, ha='right')
        plt.yticks(np.arange(len(state_types)), state_types)
        
        plt.colorbar(label='Transition Probability')
        plt.title(f'State Transition Heatmap for {doc_type.replace("_", " ").title()}')
        plt.tight_layout()
        
        # Save the figure
        output_path = output_dir / f"{doc_type}_heatmap.png"
        plt.savefig(output_path, dpi=300)
        print(f"  Saved heatmap to {output_path}")


def experiment_with_order(docs_dir: Path, output_dir: Path) -> None:
    """
    Experiment with different orders of Markov chains to demonstrate
    the impact on generated content quality.
    
    Args:
        docs_dir: Directory containing markdown documents
        output_dir: Directory to save results
    """
    print("\nExperimenting with different Markov chain orders...")
    
    # Find all markdown files
    md_files = list(docs_dir.glob("*.md"))
    if not md_files:
        print("No markdown files found for order experiment.")
        return
    
    # Concatenate all content
    content = ""
    for file in md_files:
        with open(file, 'r') as f:
            content += f.read() + "\n\n"
    
    # Create models with different orders
    orders = [1, 2, 3]
    models = {}
    for order in orders:
        print(f"Training order-{order} model...")
        model = MarkChain(order=order)
        model.train(content)
        models[order] = model
    
    # Generate content with each model using the same seed
    seed_text = "# Sample Document\n\n## Introduction\n\n"
    
    for order, model in models.items():
        print(f"Generating content with order-{order} model...")
        generated = model.sample(length=40, seed_text=seed_text)
        
        # Save generated content
        output_path = output_dir / f"order_{order}_sample.md"
        with open(output_path, 'w') as f:
            f.write(generated)
        
        print(f"  Saved to {output_path}")
    
    # Calculate coherence metrics for each generated sample
    print("\nAnalyzing coherence of generated content...")
    
    quality = DocumentQuality()
    coherence_metrics = {}
    
    for order in orders:
        file_path = output_dir / f"order_{order}_sample.md"
        doc = MarkdownDocument(file_path=str(file_path))
        
        metrics = quality.analyze_document(doc)
        coherence = metrics.get("coherence", 0.0)
        coherence_metrics[order] = coherence
        
        print(f"  Order {order} coherence: {coherence:.3f}")
    
    # Visualize coherence comparison
    plt.figure(figsize=(10, 6))
    
    orders_list = list(coherence_metrics.keys())
    values = list(coherence_metrics.values())
    
    plt.bar(orders_list, values)
    plt.xlabel('Markov Chain Order')
    plt.ylabel('Coherence Score')
    plt.title('Content Coherence by Markov Chain Order')
    plt.xticks(orders_list)
    plt.ylim(0, 1.0)
    
    # Save the figure
    output_path = output_dir / "order_comparison.png"
    plt.savefig(output_path, dpi=300)
    print(f"Saved coherence comparison to {output_path}")


def main():
    """Run the advanced MarkChain example."""
    parser = argparse.ArgumentParser(description="Advanced MarkChain Example")
    parser.add_argument("--docs", help="Path to directory containing markdown documents")
    args = parser.parse_args()
    
    # Define paths
    script_dir = Path(__file__).parent
    
    if args.docs:
        docs_dir = Path(args.docs)
    else:
        docs_dir = script_dir / "sample_docs"
        docs_dir.mkdir(exist_ok=True)
    
    output_dir = script_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Train specialized models
    models = train_specialized_models(docs_dir)
    
    # Generate specialized content
    generated_files = generate_specialized_content(models, output_dir)
    
    # Analyze transition patterns
    analysis = analyze_transitions(models)
    
    # Visualize transition patterns
    visualize_transition_patterns(analysis, output_dir)
    
    # Experiment with different orders
    experiment_with_order(docs_dir, output_dir)
    
    print("\nAdvanced MarkChain example completed!")
    print(f"All outputs saved to: {output_dir}")


def create_sample_documents(output_dir: Path) -> None:
    """
    Create sample documents of different types for training.
    
    Args:
        output_dir: Directory to save sample documents
    """
    print("Creating sample documents...")
    
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
    
    # Create another blog post sample for variety
    blog_post2 = """# 5 Essential Markdown Tips for Bloggers

Are you a blogger looking to streamline your writing process? Markdown might be just what you need!

## What is Markdown?

Markdown is a lightweight markup language created by John Gruber in 2004. It lets you format text using simple, readable syntax that converts to properly formatted HTML.

## Tip 1: Start with Headers

Headers are essential for organizing your content:

# H1 for your title
## H2 for main sections
### H3 for subsections

Using proper heading hierarchy improves readability and SEO.

## Tip 2: Master List Formatting

Lists make your content scannable:

* Unordered lists use asterisks
* Or you can use hyphens
* Perfect for feature lists

And for step-by-step instructions:

1. First step
2. Second step
3. Third step

## Tip 3: Emphasis Matters

Emphasize your text with *italics* or make it stand out with **bold**. Use it to highlight important points, but don't overdo it!

## Tip 4: Add Links Seamlessly

Link to other content [like this](https://example.com). You can also use reference-style links for cleaner markdown.

## Tip 5: Include Images

Images work similarly to links:

![Alt text for image](https://example.com/image.jpg)

## Conclusion

Markdown makes blogging faster and more consistent. Give these tips a try on your next post!
"""
    
    # Create another technical doc
    technical_doc2 = """# Markdown Parser Library

## Installation

```bash
npm install markdown-parser
# or
yarn add markdown-parser
```

## Usage

The library provides a simple API for parsing Markdown into various formats.

```javascript
const { parse } = require('markdown-parser');

// Parse to HTML
const html = parse('# Hello world', { format: 'html' });
console.log(html); // <h1>Hello world</h1>
```

## API Reference

### parse(input, options)

The main parsing function.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| input | string | Markdown input text |
| options | object | Parsing options |

**Options:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| format | string | 'html' | Output format ('html', 'json', 'ast') |
| sanitize | boolean | true | Whether to sanitize HTML |
| highlight | boolean | false | Enable syntax highlighting |

**Returns:**

Parsed output in the specified format.

## Extensions

The library supports several Markdown extensions:

- Tables
- Fenced code blocks
- Footnotes
- Strikethrough
- Task lists

To enable all extensions:

```javascript
const html = parse(markdown, { 
  extensions: ['all'] 
});
```

Or enable specific extensions:

```javascript
const html = parse(markdown, { 
  extensions: ['tables', 'code'] 
});
```

## Error Handling

The parser throws typed errors for various issues:

```javascript
try {
  const result = parse(invalidMarkdown);
} catch (error) {
  if (error instanceof ParseError) {
    console.error(`Parse error at line ${error.line}: ${error.message}`);
  }
}
```
"""

    # Save sample documents with appropriate filenames for detection
    with open(output_dir / "blog_post.md", "w") as f:
        f.write(blog_post)
    
    with open(output_dir / "technical_doc.md", "w") as f:
        f.write(technical_doc)
    
    with open(output_dir / "research_paper.md", "w") as f:
        f.write(research_paper)
        
    with open(output_dir / "blog_tips.md", "w") as f:
        f.write(blog_post2)
        
    with open(output_dir / "api_reference.md", "w") as f:
        f.write(technical_doc2)
    
    print(f"Created sample documents in: {output_dir}")


if __name__ == "__main__":
    main() 