#!/usr/bin/env python3
"""
Document Comparison Example

This script demonstrates how to compare multiple Markdown documents
using the state space analysis and belief updater components.
"""

import os
import sys
import logging
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd  # Add pandas import for heat map generation

# Add the src directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mdp.state_space import StateSpace
from mdp.belief_updater import BeliefUpdater
from mdp.document import MarkdownDocument
from mdp.visualization import plot_transitions

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
    
    # Create a timestamped directory for this run
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    comparison_dir = output_dir / f"document_comparison_{timestamp}"
    comparison_dir.mkdir(exist_ok=True)
    
    return sample_docs_dir, comparison_dir

def analyze_document_state_space(doc_path):
    """
    Analyze the state space of a document.
    
    Args:
        doc_path: Path to the document to analyze
        
    Returns:
        StateSpace: The analyzed state space
    """
    logging.info(f"Analyzing state space of document: {doc_path}")
    
    state_space = StateSpace()
    state_space.analyze(doc_path)
    
    logging.info(f"State space analysis complete: {len(state_space.states)} states, "
                f"{sum(len(t) for t in state_space.transitions.values())} transitions")
    
    return state_space

def analyze_document_beliefs(doc_path):
    """
    Analyze the semantic beliefs of a document.
    
    Args:
        doc_path: Path to document to analyze
        
    Returns:
        BeliefUpdater with belief analysis
    """
    logging.info(f"Analyzing beliefs of document: {doc_path}")
    
    # Initialize belief updater
    belief_updater = BeliefUpdater()
    
    # Analyze document and get beliefs
    analysis = belief_updater.analyze_document_file(str(doc_path))
    
    # Store analysis in the belief updater for later use
    belief_updater.current_beliefs = analysis['overall_belief']
    belief_updater.element_beliefs = {}
    
    # Extract element beliefs from sections
    for section_idx, section in enumerate(analysis['sections']):
        for element_idx, element in enumerate(section['elements']):
            element_id = f"{section_idx}_{element_idx}"
            belief_updater.element_beliefs[element_id] = section['belief']
    
    return belief_updater

def visualize_state_space(state_space, output_path):
    """
    Visualize the state space of a document.
    
    Args:
        state_space: StateSpace object
        output_path: Path to save the visualization
    """
    logging.info(f"Generating state space visualization: {output_path}")
    
    state_space.visualize(output_path)
    
    logging.info(f"State space visualization saved to {output_path}")

def visualize_beliefs(belief_updater, output_path):
    """
    Visualize the beliefs of a document.
    
    Args:
        belief_updater: BeliefUpdater object
        output_path: Path to save the visualization
    """
    logging.info(f"Generating belief heatmap: {output_path}")
    
    # Extract belief data
    belief_data = []
    for element_id, element_beliefs in belief_updater.element_beliefs.items():
        for semantic_class, belief_value in element_beliefs.items():
            belief_data.append({
                "element": element_id,
                "semantic_class": semantic_class,
                "belief": belief_value
            })
    
    # Generate heatmap if we have data
    if belief_data:
        generate_heat_map(belief_data, output_path, 
                          x_key="element", 
                          y_key="semantic_class", 
                          value_key="belief",
                          title="Document Element Semantic Beliefs")
    else:
        logging.warning("No element belief data available for visualization")
    
    logging.info(f"Belief visualization saved to {output_path}")

def generate_heat_map(data, output_path, x_key, y_key, value_key, title="Heat Map"):
    """
    Generate a heat map visualization from tabular data.
    
    Args:
        data: List of dictionaries containing data points
        output_path: Path to save the visualization
        x_key: Dictionary key for x-axis values
        y_key: Dictionary key for y-axis values
        value_key: Dictionary key for cell values
        title: Title for the heat map
    """
    logging.info(f"Generating heat map: {output_path}")
    
    if not data:
        logging.warning("No data provided for heat map visualization")
        return
    
    # Convert data to DataFrame for easier pivoting
    df = pd.DataFrame(data)
    
    # Create pivot table for heatmap
    pivot_table = df.pivot_table(
        index=y_key, 
        columns=x_key, 
        values=value_key,
        aggfunc='mean',
        fill_value=0
    )
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    heatmap = plt.imshow(pivot_table.values, cmap='viridis', aspect='auto')
    plt.colorbar(heatmap, label='Belief Value')
    
    # Set labels
    plt.xticks(range(len(pivot_table.columns)), pivot_table.columns, rotation=45, ha='right')
    plt.yticks(range(len(pivot_table.index)), pivot_table.index)
    
    plt.title(title)
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_path)
    plt.close()
    
    logging.info(f"Heat map saved to {output_path}")

def compare_documents(doc_paths, output_dir):
    """
    Compare multiple documents using state space and belief analysis.
    
    Args:
        doc_paths: List of paths to documents to compare
        output_dir: Directory to save visualizations and results
    """
    logging.info(f"Comparing {len(doc_paths)} documents")
    
    # Track results
    results = {
        "state_spaces": {},
        "beliefs": {},
        "similarity": {}
    }
    
    # Analyze each document
    for doc_path in doc_paths:
        try:
            doc_name = doc_path.stem
            
            # Analyze state space
            state_space = analyze_document_state_space(doc_path)
            state_viz_path = output_dir / f"{doc_name}_state_space.png"
            visualize_state_space(state_space, state_viz_path)
            
            # Analyze beliefs
            belief_updater = analyze_document_beliefs(doc_path)
            belief_viz_path = output_dir / f"{doc_name}_beliefs.png"
            visualize_beliefs(belief_updater, belief_viz_path)
            
            # Store results
            results["state_spaces"][doc_name] = {
                "num_states": len(state_space.states),
                "num_transitions": sum(len(t) for t in state_space.transitions.values()),
                "visualization": str(state_viz_path.relative_to(output_dir.parent))
            }
            
            results["beliefs"][doc_name] = {
                "overall_beliefs": {k: float(v) for k, v in belief_updater.current_beliefs.items()},
                "visualization": str(belief_viz_path.relative_to(output_dir.parent))
            }
            
        except Exception as e:
            logging.error(f"Error analyzing {doc_path}: {e}")
    
    # Calculate similarity matrix
    document_names = list(results["beliefs"].keys())
    similarity_matrix = np.zeros((len(document_names), len(document_names)))
    
    for i, doc1 in enumerate(document_names):
        beliefs1 = results["beliefs"][doc1]["overall_beliefs"]
        for j, doc2 in enumerate(document_names):
            beliefs2 = results["beliefs"][doc2]["overall_beliefs"]
            
            # Calculate cosine similarity between belief vectors
            vec1 = np.array([beliefs1.get(c, 0) for c in set(beliefs1) | set(beliefs2)])
            vec2 = np.array([beliefs2.get(c, 0) for c in set(beliefs1) | set(beliefs2)])
            
            # Avoid division by zero
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 > 0 and norm2 > 0:
                similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            else:
                similarity = 0
            
            similarity_matrix[i, j] = similarity
    
    # Visualize similarity matrix
    plt.figure(figsize=(10, 8))
    plt.imshow(similarity_matrix, cmap="viridis", interpolation="nearest")
    plt.colorbar(label="Similarity")
    plt.xticks(range(len(document_names)), document_names, rotation=45, ha="right")
    plt.yticks(range(len(document_names)), document_names)
    plt.title("Document Similarity Matrix (Based on Semantic Beliefs)")
    plt.tight_layout()
    
    similarity_matrix_path = output_dir / "document_similarity_matrix.png"
    plt.savefig(similarity_matrix_path)
    plt.close()
    
    # Store similarity results
    results["similarity"] = {
        "matrix": similarity_matrix.tolist(),
        "visualization": str(similarity_matrix_path.relative_to(output_dir.parent))
    }
    
    # Save all results
    results_path = output_dir / "document_comparison_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate a human-readable report
    report_path = output_dir / "document_comparison_report.md"
    generate_report(results, document_names, report_path)
    
    return results

def generate_report(results, document_names, report_path):
    """
    Generate a human-readable report of document comparison results.
    
    Args:
        results: Comparison results dictionary
        document_names: List of document names
        report_path: Path to save the report
    """
    logging.info(f"Generating comparison report: {report_path}")
    
    # Create the report content
    report = f"""# Markdown Document Comparison Report

## Overview

This report compares {len(document_names)} Markdown documents based on their structure (state space) and semantic content (beliefs).

## Documents Analyzed

| Document | States | Transitions | Dominant Semantic Class |
|----------|--------|-------------|-------------------------|
"""
    
    # Add rows for each document
    for doc_name in document_names:
        state_space_info = results["state_spaces"][doc_name]
        belief_info = results["beliefs"][doc_name]
        
        # Find dominant semantic class
        dominant_class = max(belief_info["overall_beliefs"].items(), key=lambda x: x[1])
        
        report += f"| {doc_name} | {state_space_info['num_states']} | {state_space_info['num_transitions']} | {dominant_class[0]} ({dominant_class[1]:.2f}) |\n"
    
    # Add belief comparison
    report += """
## Semantic Beliefs Comparison

The following table shows the semantic belief values for each document:

| Document | Technical | Conceptual | Instructional | Informational | Persuasive |
|----------|-----------|------------|---------------|---------------|------------|
"""
    
    # Add rows for each document's beliefs
    for doc_name in document_names:
        beliefs = results["beliefs"][doc_name]["overall_beliefs"]
        report += f"| {doc_name} "
        for class_name in ["technical", "conceptual", "instructional", "informational", "persuasive"]:
            belief_value = beliefs.get(class_name, 0)
            report += f"| {belief_value:.2f} "
        report += "|\n"
    
    # Add similarity information
    report += """
## Document Similarity

The following pairs of documents have the highest semantic similarity:

"""
    
    # Extract similarity pairs
    similarity_matrix = np.array(results["similarity"]["matrix"])
    pairs = []
    
    for i in range(len(document_names)):
        for j in range(i+1, len(document_names)):
            pairs.append((document_names[i], document_names[j], similarity_matrix[i, j]))
    
    # Sort by similarity (descending)
    pairs.sort(key=lambda x: x[2], reverse=True)
    
    # Add top pairs
    for doc1, doc2, similarity in pairs[:5]:
        report += f"- **{doc1}** and **{doc2}**: {similarity:.2f}\n"
    
    # Add visualizations section
    report += """
## Visualizations

The following visualizations are available in the output directory:

"""
    
    # List visualizations
    for doc_name in document_names:
        state_viz = results["state_spaces"][doc_name]["visualization"]
        belief_viz = results["beliefs"][doc_name]["visualization"]
        
        report += f"- **{doc_name}**:\n"
        report += f"  - State Space: [{state_viz}]({state_viz})\n"
        report += f"  - Belief Heatmap: [{belief_viz}]({belief_viz})\n"
    
    # Add similarity matrix visualization
    similarity_viz = results["similarity"]["visualization"]
    report += f"- **Document Similarity Matrix**: [{similarity_viz}]({similarity_viz})\n"
    
    # Add footer
    report += f"""
## Analysis Methodology

This comparison uses two primary methods of analysis:

1. **State Space Analysis**: Represents the document structure as states and transitions between markdown elements.
2. **Belief Analysis**: Uses a belief updater to estimate the semantic content of each document based on predefined semantic classes.

*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    # Write the report
    with open(report_path, "w") as f:
        f.write(report)
    
    logging.info(f"Report saved to {report_path}")

def main():
    """Run the document comparison example."""
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
    
    # Compare all documents
    results = compare_documents(markdown_files, output_dir)
    
    # Print summary
    logging.info(f"Comparison complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main() 