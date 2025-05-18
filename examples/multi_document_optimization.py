#!/usr/bin/env python3
"""
Multi-Document Optimization Example

This script demonstrates how to apply consistent formatting and optimization
to multiple Markdown documents using the PolicyOptimizer.
"""

import os
import sys
import logging
from pathlib import Path
import json
from datetime import datetime

# Add the src directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mdp.policy_optimizer import PolicyOptimizer
from mdp.transformations import (
    HeadingLevelTransformation,
    ListFormatTransformation,
    CodeBlockFormatTransformation,
    LinkFormatTransformation,
    TableFormatTransformation,
    EmphasisStyleTransformation,
)
from mdp.markdown_document import MarkdownDocument
from mdp.metrics import (
    ReadabilityMetric,
    StructureMetric,
    ConsistencyMetric,
    InformationDensityMetric,
)

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
    batch_dir = output_dir / f"batch_optimization_{timestamp}"
    batch_dir.mkdir(exist_ok=True)
    
    return sample_docs_dir, batch_dir

def create_optimization_policy():
    """
    Create a policy optimizer with standard transformations.
    
    Returns:
        PolicyOptimizer: Configured optimizer with various transformations
    """
    # Create metrics
    metrics = [
        ReadabilityMetric(weight=0.3),
        StructureMetric(weight=0.3),
        ConsistencyMetric(weight=0.2),
        InformationDensityMetric(weight=0.2)
    ]
    
    # Create transformations
    transformations = [
        HeadingLevelTransformation(min_level=1, increment=0),
        ListFormatTransformation(target_type="unordered", bullet_style="-"),
        CodeBlockFormatTransformation(),
        LinkFormatTransformation(),
        TableFormatTransformation(alignment="default"),
        EmphasisStyleTransformation(bold_style="**", italic_style="*")
    ]
    
    # Create optimizer
    optimizer = PolicyOptimizer(
        metrics=metrics,
        transformations=transformations
    )
    
    return optimizer

def optimize_document(doc_path, optimizer, output_dir):
    """
    Optimize a single document using the provided optimizer.
    
    Args:
        doc_path: Path to the document to optimize
        optimizer: PolicyOptimizer to use
        output_dir: Directory to save optimized document
        
    Returns:
        tuple: Original score, optimized score, and path to optimized document
    """
    logging.info(f"Optimizing document: {doc_path}")
    
    # Read the document
    doc = MarkdownDocument(doc_path)
    original_content = doc.content
    
    # Analyze and score the original document
    original_analysis = optimizer.evaluate_markdown(original_content)
    original_score = original_analysis["overall_score"]
    
    logging.info(f"Original document score: {original_score:.2f}")
    
    # Optimize the document
    optimized_content = optimizer.optimize_markdown(original_content)
    
    # Score the optimized document
    optimized_analysis = optimizer.evaluate_markdown(optimized_content)
    optimized_score = optimized_analysis["overall_score"]
    
    logging.info(f"Optimized document score: {optimized_score:.2f}")
    
    # Save the optimized document
    output_path = output_dir / f"{doc_path.stem}_optimized.md"
    with open(output_path, "w") as f:
        f.write(optimized_content)
    
    # Save the analyses
    analysis_path = output_dir / f"{doc_path.stem}_analysis.json"
    with open(analysis_path, "w") as f:
        analysis = {
            "original": original_analysis,
            "optimized": optimized_analysis,
            "improvement": optimized_score - original_score
        }
        json.dump(analysis, f, indent=2)
    
    return original_score, optimized_score, output_path

def optimize_documents(doc_paths, output_dir):
    """
    Optimize multiple documents with the same policy.
    
    Args:
        doc_paths: List of paths to documents to optimize
        output_dir: Directory to save optimized documents
    """
    # Create the optimizer
    optimizer = create_optimization_policy()
    
    # Track results
    results = []
    
    # Process each document
    for doc_path in doc_paths:
        try:
            original_score, optimized_score, output_path = optimize_document(
                doc_path, optimizer, output_dir
            )
            
            results.append({
                "document": doc_path.name,
                "original_score": original_score,
                "optimized_score": optimized_score,
                "improvement": optimized_score - original_score,
                "output_path": str(output_path)
            })
        except Exception as e:
            logging.error(f"Error optimizing {doc_path}: {e}")
    
    # Save summary report
    summary_path = output_dir / "optimization_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate a human-readable report
    report_path = output_dir / "optimization_report.md"
    generate_report(results, report_path)
    
    return results

def generate_report(results, report_path):
    """
    Generate a human-readable report of optimization results.
    
    Args:
        results: List of optimization results
        report_path: Path to save the report
    """
    logging.info(f"Generating optimization report: {report_path}")
    
    # Calculate overall statistics
    total_docs = len(results)
    avg_original = sum(r["original_score"] for r in results) / total_docs if total_docs else 0
    avg_optimized = sum(r["optimized_score"] for r in results) / total_docs if total_docs else 0
    avg_improvement = sum(r["improvement"] for r in results) / total_docs if total_docs else 0
    
    # Create the report content
    report = f"""# Markdown Optimization Report

## Summary

- **Documents Processed**: {total_docs}
- **Average Original Score**: {avg_original:.2f}
- **Average Optimized Score**: {avg_optimized:.2f}
- **Average Improvement**: {avg_improvement:.2f} ({avg_improvement/avg_original*100 if avg_original else 0:.1f}%)

## Document Details

| Document | Original Score | Optimized Score | Improvement |
|----------|---------------|----------------|------------|
"""
    
    # Add rows for each document
    for result in sorted(results, key=lambda r: r["improvement"], reverse=True):
        doc_name = result["document"]
        original = result["original_score"]
        optimized = result["optimized_score"]
        improvement = result["improvement"]
        report += f"| {doc_name} | {original:.2f} | {optimized:.2f} | {improvement:.2f} |\n"
    
    # Add footer
    report += f"""
## Optimization Policy

The following transformations were applied to all documents:

- Consistent heading structure
- Unified list formatting with bullet style: "-"
- Standardized code block formatting
- Normalized link formatting
- Consistent table formatting
- Uniform emphasis styling (bold: "**", italic: "*")

*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    # Write the report
    with open(report_path, "w") as f:
        f.write(report)
    
    logging.info(f"Report saved to {report_path}")

def main():
    """Run the multi-document optimization example."""
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
    
    # Optimize all documents
    results = optimize_documents(markdown_files, output_dir)
    
    # Print summary
    logging.info(f"Optimization complete. Results saved to {output_dir}")
    
    # Find the document with the most improvement
    if results:
        best_result = max(results, key=lambda r: r["improvement"])
        logging.info(f"Best improvement: {best_result['document']} ({best_result['improvement']:.2f} increase)")

if __name__ == "__main__":
    main() 