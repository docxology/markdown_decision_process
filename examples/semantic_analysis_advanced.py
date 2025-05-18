#!/usr/bin/env python3
"""
Advanced Semantic Analysis Example

This script demonstrates advanced techniques for semantic analysis using the BeliefUpdater
class across different types of Markdown documents.
"""

import os
import sys
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Add the src directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mdp.belief_updater import BeliefUpdater
from mdp.markdown_document import MarkdownDocument

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_directories():
    """Set up the necessary directories for input and output."""
    # Get the directory of this script
    script_dir = Path(__file__).resolve().parent
    
    # Define directories
    sample_docs_dir = script_dir / "sample_docs"
    output_dir = script_dir / "outputs"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    return sample_docs_dir, output_dir

def analyze_document_semantics(doc_path, output_dir):
    """
    Analyze the semantics of a document using BeliefUpdater.
    
    Args:
        doc_path: Path to the document to analyze
        output_dir: Directory to save output files
    """
    logging.info(f"Analyzing semantics for: {doc_path}")
    
    # Create a BeliefUpdater with custom semantic classes
    updater = BeliefUpdater(
        semantic_classes=[
            "instruction", "explanation", "example", "reference", 
            "summary", "definition", "warning", "note",
            "research", "technical", "blog", "tutorial"
        ],
        noise_factor=0.1
    )
    
    # Set custom prior beliefs based on file type
    filename = doc_path.name.lower()
    if "research" in filename or "paper" in filename:
        updater.update_belief("research", 0.8)
        updater.update_belief("technical", 0.6)
    elif "tech" in filename or "doc" in filename:
        updater.update_belief("technical", 0.8)
        updater.update_belief("instruction", 0.5)
    elif "blog" in filename or "post" in filename:
        updater.update_belief("blog", 0.8)
        updater.update_belief("explanation", 0.6)
    
    # Analyze the document
    analysis = updater.analyze_document_file(doc_path)
    
    # Print the analysis
    updater.print_analysis(analysis)
    
    # Generate a semantic heatmap
    generate_semantic_heatmap(analysis, output_dir / f"{doc_path.stem}_heatmap.png")
    
    # Save the analysis to a file
    save_analysis(analysis, output_dir / f"{doc_path.stem}_analysis.json")
    
    return analysis

def generate_semantic_heatmap(analysis, output_path):
    """
    Generate a heatmap visualization of semantic beliefs across document elements.
    
    Args:
        analysis: Analysis results from BeliefUpdater
        output_path: Path to save the heatmap image
    """
    logging.info(f"Generating semantic heatmap: {output_path}")
    
    # Extract element-level semantics
    elements = analysis.get("elements", [])
    if not elements:
        logging.warning("No elements found in analysis, skipping heatmap generation")
        return
    
    # Prepare data for heatmap
    semantic_classes = list(elements[0].get("semantics", {}).keys())
    num_elements = len(elements)
    data = np.zeros((len(semantic_classes), num_elements))
    
    # Fill data matrix
    for i, element in enumerate(elements):
        for j, cls in enumerate(semantic_classes):
            data[j, i] = element.get("semantics", {}).get(cls, 0)
    
    # Create the heatmap
    plt.figure(figsize=(12, 8))
    plt.imshow(data, cmap="viridis", aspect="auto")
    plt.colorbar(label="Belief Strength")
    plt.xlabel("Document Elements")
    plt.ylabel("Semantic Classes")
    plt.title(f"Semantic Analysis Heatmap: {analysis.get('document_path', 'Unknown')}")
    
    # Add semantic class labels
    plt.yticks(range(len(semantic_classes)), semantic_classes)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    logging.info(f"Saved heatmap to {output_path}")

def save_analysis(analysis, output_path):
    """
    Save the analysis results to a JSON file.
    
    Args:
        analysis: Analysis results from BeliefUpdater
        output_path: Path to save the analysis
    """
    import json
    
    # Convert Path objects to strings
    def path_to_str(obj):
        if isinstance(obj, Path):
            return str(obj)
        return obj
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2, default=path_to_str)
    
    logging.info(f"Saved analysis to {output_path}")

def compare_document_semantics(doc_paths, output_dir):
    """
    Compare the semantics of multiple documents.
    
    Args:
        doc_paths: List of paths to documents to compare
        output_dir: Directory to save output files
    """
    logging.info(f"Comparing semantics for {len(doc_paths)} documents")
    
    # Analyze each document
    analyses = {}
    for doc_path in doc_paths:
        analyses[doc_path.stem] = analyze_document_semantics(doc_path, output_dir)
    
    # Extract overall semantic beliefs for each document
    semantic_comparison = {}
    for doc_name, analysis in analyses.items():
        semantic_comparison[doc_name] = analysis.get("overall_semantics", {})
    
    # Create comparison visualization
    generate_semantic_comparison(semantic_comparison, output_dir / "semantic_comparison.png")
    
    # Generate semantic similarity matrix
    generate_similarity_matrix(semantic_comparison, output_dir / "semantic_similarity.png")
    
    return analyses

def generate_semantic_comparison(comparison_data, output_path):
    """
    Generate a bar chart comparing document semantics.
    
    Args:
        comparison_data: Dictionary mapping document names to semantic beliefs
        output_path: Path to save the comparison image
    """
    logging.info(f"Generating semantic comparison: {output_path}")
    
    # Get all semantic classes
    all_classes = set()
    for doc_semantics in comparison_data.values():
        all_classes.update(doc_semantics.keys())
    all_classes = sorted(all_classes)
    
    # Prepare data for bar chart
    doc_names = list(comparison_data.keys())
    x = np.arange(len(all_classes))
    width = 0.8 / len(doc_names)
    
    # Create the bar chart
    plt.figure(figsize=(14, 8))
    
    for i, doc_name in enumerate(doc_names):
        doc_semantics = comparison_data[doc_name]
        values = [doc_semantics.get(cls, 0) for cls in all_classes]
        offset = width * i - width * len(doc_names) / 2 + width / 2
        plt.bar(x + offset, values, width, label=doc_name)
    
    plt.xlabel('Semantic Classes')
    plt.ylabel('Belief Strength')
    plt.title('Semantic Comparison Across Documents')
    plt.xticks(x, all_classes, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    logging.info(f"Saved semantic comparison to {output_path}")

def generate_similarity_matrix(comparison_data, output_path):
    """
    Generate a similarity matrix between documents based on semantic profiles.
    
    Args:
        comparison_data: Dictionary mapping document names to semantic beliefs
        output_path: Path to save the similarity matrix image
    """
    logging.info(f"Generating similarity matrix: {output_path}")
    
    # Get document names
    doc_names = list(comparison_data.keys())
    n_docs = len(doc_names)
    
    # Calculate similarity matrix
    similarity = np.zeros((n_docs, n_docs))
    
    for i, doc1 in enumerate(doc_names):
        for j, doc2 in enumerate(doc_names):
            # Calculate cosine similarity
            sem1 = comparison_data[doc1]
            sem2 = comparison_data[doc2]
            
            # Get all keys
            all_keys = set(sem1.keys()).union(set(sem2.keys()))
            
            # Calculate dot product and magnitudes
            dot_product = sum(sem1.get(k, 0) * sem2.get(k, 0) for k in all_keys)
            mag1 = sum(sem1.get(k, 0)**2 for k in all_keys) ** 0.5
            mag2 = sum(sem2.get(k, 0)**2 for k in all_keys) ** 0.5
            
            # Calculate similarity
            if mag1 and mag2:
                similarity[i, j] = dot_product / (mag1 * mag2)
            else:
                similarity[i, j] = 0
    
    # Create the heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(similarity, cmap="Blues", vmin=0, vmax=1)
    plt.colorbar(label="Semantic Similarity")
    plt.title("Document Semantic Similarity Matrix")
    
    # Add document name labels
    plt.xticks(range(n_docs), doc_names, rotation=45, ha='right')
    plt.yticks(range(n_docs), doc_names)
    
    # Add similarity values
    for i in range(n_docs):
        for j in range(n_docs):
            plt.text(j, i, f"{similarity[i, j]:.2f}", 
                     ha="center", va="center", 
                     color="w" if similarity[i, j] > 0.5 else "black")
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    logging.info(f"Saved similarity matrix to {output_path}")

def main():
    """Run the advanced semantic analysis example."""
    sample_docs_dir, output_dir = setup_directories()
    
    # Get all markdown files from sample_docs
    markdown_files = list(sample_docs_dir.glob("*.md"))
    
    if not markdown_files:
        logging.error(f"No markdown files found in {sample_docs_dir}")
        return
    
    # Print available documents
    logging.info("Found the following documents:")
    for i, doc_path in enumerate(markdown_files):
        logging.info(f"  [{i+1}] {doc_path.name}")
    
    # Analyze individual document (first as an example)
    analyze_document_semantics(markdown_files[0], output_dir)
    
    # Compare all documents
    compare_document_semantics(markdown_files, output_dir)
    
    logging.info(f"Analysis complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main() 