#!/usr/bin/env python3
"""
Example showing how to use the Markdown Decision Process for document optimization.

This example demonstrates:
1. Loading a document
2. Analyzing document structure and quality
3. Optimizing the document using the PolicyOptimizer
4. Using MarkChain to generate complementary content
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from mdp.document import MarkdownDocument
from mdp.policy_optimizer import PolicyOptimizer
from mdp.markchain import MarkChain
from mdp.visualization import plot_document_metrics, plot_transitions
from mdp.quality import DocumentQuality


def main():
    """Run the document optimization example."""
    print("Markdown Decision Process - Document Optimization Example")
    print("=" * 60)

    # Load a sample document
    sample_path = Path(__file__).parent / "sample_document.md"
    
    # Create sample document if it doesn't exist
    if not sample_path.exists():
        print(f"Creating sample document at {sample_path}")
        create_sample_document(sample_path)
    
    document = MarkdownDocument(sample_path)
    print(f"Loaded document: {sample_path}")
    print(f"Document stats: {len(document.get_content())} characters, "
          f"{len(document.get_paragraphs())} paragraphs, "
          f"{len(document.get_headings())} headings")
    
    # Create a policy optimizer
    optimizer = PolicyOptimizer(
        reward_weights={
            "readability": 0.5,
            "information_density": 0.3,
            "structural_balance": 0.2
        }
    )
    
    # Create quality analyzer for metrics
    quality = DocumentQuality(
        readability_weight=0.5,
        information_density_weight=0.3,
        structural_balance_weight=0.2
    )
    
    # Analyze original document
    print("\nAnalyzing original document...")
    metrics = quality.analyze_document(document)
    print_metrics_summary(metrics)
    
    # Optimize document
    print("\nOptimizing document...")
    optimized_doc = optimizer.transform(sample_path)
    optimized_doc_obj = MarkdownDocument(content=optimized_doc)
    
    # Analyze optimized document
    print("\nAnalyzing optimized document...")
    optimized_metrics = quality.analyze_document(optimized_doc_obj)
    print_metrics_summary(optimized_metrics)
    
    # Compare metrics
    print("\nImprovement summary:")
    comparison = quality.compare_documents(document, optimized_doc_obj)
    differences = comparison["differences"]
    for category, diff in differences.items():
        print(f"  {category.replace('_diff', '').replace('_', ' ').title()}: "
              f"{diff:.2f} change")
    
    # Save optimized document
    optimized_path = sample_path.with_suffix(".optimized.md")
    with open(optimized_path, "w") as f:
        f.write(optimized_doc)
    print(f"\nOptimized document saved to: {optimized_path}")
    
    # Generate complementary content with MarkChain
    print("\nTraining MarkChain on document...")
    chain = MarkChain(order=2)
    chain.train(document.get_content())
    
    print("Generating complementary section...")
    generated = chain.sample(length=200)
    
    generated_path = sample_path.with_suffix(".generated.md")
    with open(generated_path, "w") as f:
        f.write(generated)
    print(f"Generated content saved to: {generated_path}")
    
    # Visualize document metrics if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        
        # Create output directory
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        print("\nGenerating visualizations...")
        # Visualize metrics comparison
        metrics_fig = plot_document_metrics(
            {"Original": metrics, "Optimized": optimized_metrics}
        )
        metrics_fig.savefig(output_dir / "document_metrics_comparison.png")
        
        # Visualize MarkChain transitions
        transitions_fig = plot_transitions(chain, top_n=8)
        transitions_fig.savefig(output_dir / "state_transitions.png")
        
        print("Visualizations saved to outputs directory")
    except ImportError:
        print("\nMatplotlib not available. Skipping visualizations.")


def print_metrics_summary(metrics):
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
    print(f"  Semantic Class: {metrics.get('overall_semantic_class', 'Unknown')}")


def create_sample_document(path):
    """Create a sample markdown document for testing."""
    content = """# Technical Documentation for Project XYZ

This document provides technical documentation for the XYZ system. The system is designed to process large amounts of data efficiently and provide insights through a user-friendly interface. The architecture is modular and extensible, with components that can be customized to meet specific needs.

## System Architecture

The XYZ system consists of the following components:

* Data Ingestion Layer
* Processing Engine
* Storage Layer
* API Layer
* User Interface

### Data Ingestion Layer

The data ingestion layer is responsible for collecting data from various sources, validating it, and preparing it for processing. It supports batch and streaming ingestion patterns.

### Processing Engine

The processing engine is the core of the system. It applies various algorithms to the data to extract insights and generate results. The processing engine is highly scalable and can be distributed across multiple nodes for improved performance.

#### Algorithms

The processing engine implements several algorithms:

1. Data normalization
2. Feature extraction
3. Pattern recognition
4. Anomaly detection

### Storage Layer

The storage layer manages the persistence of data throughout its lifecycle. It uses a combination of relational databases for structured data and document stores for unstructured data.

## API Reference

The API provides programmatic access to the system's functionality. It follows RESTful principles and uses JSON for data exchange.

### Authentication

All API requests require authentication using OAuth 2.0. Tokens can be obtained from the authentication endpoint.

### Endpoints

The following endpoints are available:

- `/api/v1/data` - Data management
- `/api/v1/process` - Processing operations
- `/api/v1/results` - Results retrieval

## Deployment Guide

Deployment can be performed using Docker containers or traditional installation on servers.

### Prerequisites

- Linux-based operating system
- At least 8GB RAM
- 50GB disk space
- Network connectivity

### Configuration

Configuration is done through a YAML file located at `/etc/xyz/config.yaml`. 

## Troubleshooting

Common issues and their solutions are documented in this section.

### Connectivity Issues

If you experience connectivity issues, check your network settings and firewall rules.

### Performance Problems

Performance issues are often related to insufficient resources or misconfiguration.
"""
    
    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main() 