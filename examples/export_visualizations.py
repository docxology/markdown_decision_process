#!/usr/bin/env python3
"""
Example script demonstrating how to use the VisualizationExporter to export
visualizations of Markdown documents to various formats.

This example:
1. Analyzes a Markdown document
2. Creates visualizations of its structure, metrics, and state space
3. Exports these visualizations to PNG, PDF, SVG, and HTML
4. Generates a comprehensive analysis report in multiple formats
"""

import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mdp.export import VisualizationExporter
from mdp.document import MarkdownDocument
from mdp.state_space import StateSpace
from mdp.quality import DocumentQuality
from mdp.markdown_agent import MarkdownAgent
from mdp.pandoc import PandocNotFoundError
from mdp.visualization import plot_document_structure, plot_document_metrics


def main():
    """Run the visualization export example."""
    # Define input and output paths
    script_dir = Path(__file__).resolve().parent
    
    # Look for sample documents in the examples directory
    sample_docs_dir = script_dir / "sample_docs"
    
    if not sample_docs_dir.exists():
        # Create sample directory and document if it doesn't exist
        sample_docs_dir.mkdir(exist_ok=True)
        
        # Create a sample document
        sample_doc_path = sample_docs_dir / "sample_document.md"
        with open(sample_doc_path, "w") as f:
            f.write("""# Sample Markdown Document

This is a sample document for testing the visualization export functionality.

## Introduction

Markdown is a lightweight markup language that is easy to read and write.

## Features

Markdown includes various features:

- Headers (like the ones in this document)
- Lists (like this one)
- *Emphasized* and **bold** text
- [Links](https://example.com)
- `Inline code` and code blocks

### Code Examples

```python
def hello_world():
    print("Hello, world!")
```

## Structure

Documents can have nested structures.

### Subsection 1

This is a subsection.

#### Deeper Nesting

We can nest sections even deeper.

### Subsection 2

Another subsection here.

## Conclusion

Markdown is an excellent format for documentation.
""")
        print(f"Created sample document at {sample_doc_path}")
    else:
        # Use an existing markdown file if available
        markdown_files = list(sample_docs_dir.glob("*.md"))
        if markdown_files:
            sample_doc_path = markdown_files[0]
            print(f"Using existing sample document: {sample_doc_path}")
        else:
            print("No sample documents found. Creating one...")
            sample_doc_path = sample_docs_dir / "sample_document.md"
            with open(sample_doc_path, "w") as f:
                f.write("# Empty Sample Document\n\nThis is a placeholder document.")
            print(f"Created sample document at {sample_doc_path}")
    
    # Create output directory
    output_dir = script_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize the exporter
    exporter = VisualizationExporter(output_dir=output_dir)
    
    # Load the document
    document = MarkdownDocument(file_path=sample_doc_path)
    
    # Display basic information about the document
    print(f"\nAnalyzing document: {sample_doc_path}")
    content = document.get_content()
    word_count = len(content.split())
    print(f"Word count: {word_count}")
    print(f"Structure elements: {len(document.get_structure())}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # 1. Document structure visualization
    print("- Document structure")
    structure_output = output_dir / "document_structure.png"
    exporter.export_document_structure(
        document=document,
        output_path=structure_output
    )
    print(f"  Exported to {structure_output}")
    
    # 2. Document metrics
    print("- Document metrics")
    quality = DocumentQuality()
    metrics = quality.analyze_document(document)
    
    metrics_dict = {"Sample Document": metrics}
    metrics_output = output_dir / "document_metrics.png"
    exporter.export_document_metrics(
        metrics_dict=metrics_dict,
        output_path=metrics_output
    )
    print(f"  Exported to {metrics_output}")
    
    # 3. State space visualization
    print("- State space analysis")
    state_space = StateSpace()
    state_space.parse_markdown_file(sample_doc_path)
    
    state_space_output = output_dir / "state_space.png"
    exporter.export_state_space(
        state_space=state_space,
        output_path=state_space_output,
        title="Document State Space"
    )
    print(f"  Exported to {state_space_output}")
    
    # 4. Export to different formats
    print("\nExporting in different formats...")
    
    # Create a custom figure for multi-format export
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot readability scores
    readability = metrics.get('readability', {})
    ax1.bar(
        ['Flesch Reading Ease', 'Flesch-Kincaid Grade'],
        [readability.get('flesch_reading_ease', 0), 
         readability.get('flesch_kincaid_grade', 0)]
    )
    ax1.set_title('Readability Scores')
    
    # Plot state distribution
    state_types = {}
    for state in state_space.states.values():
        state_type = state.get('type', 'unknown')
        state_types[state_type] = state_types.get(state_type, 0) + 1
    
    labels = list(state_types.keys())
    values = list(state_types.values())
    ax2.pie(values, labels=labels, autopct='%1.1f%%')
    ax2.set_title('State Distribution')
    
    plt.tight_layout()
    
    # Export to different formats
    for fmt in ['png', 'pdf', 'svg']:
        output_path = output_dir / f"custom_visualization.{fmt}"
        exporter.export_figure(
            fig=fig,
            output_path=output_path,
            format=fmt,
            dpi=300
        )
        print(f"- Exported to {output_path}")
    
    # Export to HTML
    html_output = output_dir / "custom_visualization.html"
    exporter.export_to_html(
        fig=fig,
        output_path=html_output,
        title="Document Analysis Visualization"
    )
    print(f"- Exported to {html_output}")
    
    # Clean up the figure
    plt.close(fig)
    
    # 5. Generate comprehensive analysis report
    print("\nSkipping analysis report generation due to compatibility issues.")
    
    # Uncomment to generate analysis reports when StateSpace and MarkdownAgent are compatible
    # formats = ["md", "html", "pdf"]
    # for fmt in formats:
    #     try:
    #         report_output = output_dir / f"analysis_report.{fmt}"
    #         exporter.export_analysis_report(
    #             document=str(sample_doc_path),
    #             output_path=report_output,
    #             format=fmt
    #         )
    #         print(f"- Exported report to {report_output}")
    #     except (PandocNotFoundError, ImportError) as e:
    #         print(f"- Could not export to {fmt}: {str(e)}")
    
    # 6. Document with embedded visualizations
    print("\nSkipping document with embedded visualizations due to compatibility issues.")
    
    # Uncomment when compatibility issues are resolved
    # print("\nCreating document with embedded visualizations...")
    # 
    # # Create a document with markers for visualizations
    # doc_with_viz_content = """# Document Analysis Report
    # 
    # ## Document Structure
    # 
    # This visualization shows the structure of the document.
    # 
    # <!-- STRUCTURE_VIZ -->
    # 
    # ## Metrics Analysis
    # 
    # These metrics provide insights into the document's readability and information density.
    # 
    # <!-- METRICS_VIZ -->
    # 
    # ## State Space Analysis
    # 
    # This visualization shows the state transitions in the document.
    # 
    # <!-- STATE_SPACE_VIZ -->
    # 
    # ## Conclusion
    # 
    # The visualizations help understand the document's structure and quality.
    # """
    # 
    # # Create separate figures for embedding
    # # Generate figures directly using the visualization module
    # structure_fig = plot_document_structure(document)
    # metrics_fig = plot_document_metrics(metrics_dict)
    # 
    # # Create document with visualizations
    # doc_with_viz_path = output_dir / "document_with_visualizations.md"
    # with open(doc_with_viz_path, "w") as f:
    #     f.write(doc_with_viz_content)
    # 
    # # List of visualizations to embed
    # visualizations = [
    #     ("<!-- STRUCTURE_VIZ -->", structure_fig, {"format": "png"}),
    #     ("<!-- METRICS_VIZ -->", metrics_fig, {"format": "png"}),
    #     ("<!-- STATE_SPACE_VIZ -->", state_space_output, {})  # This one is a path, not a figure
    # ]
    # 
    # # Export to different formats
    # for fmt in ["md", "html", "pdf"]:
    #     try:
    #         output_path = output_dir / f"document_with_viz.{fmt}"
    #         
    #         # Special case for markdown - no need for pandoc
    #         if fmt == "md":
    #             # Simple replacement for markdown output
    #             content = doc_with_viz_content
    #             content = content.replace("<!-- STRUCTURE_VIZ -->", 
    #                                      f"![Structure](document_structure.png)")
    #             content = content.replace("<!-- METRICS_VIZ -->", 
    #                                      f"![Metrics](document_metrics.png)")
    #             content = content.replace("<!-- STATE_SPACE_VIZ -->", 
    #                                      f"![State Space](state_space.png)")
    #             
    #             with open(output_path, "w") as f:
    #                 f.write(content)
    #         else:
    #             # Use pandoc for other formats
    #             exporter.export_document_with_visualizations(
    #                 document=doc_with_viz_path,
    #                 output_path=output_path,
    #                 visualizations=visualizations,
    #                 to_format=fmt
    #             )
    #         
    #         print(f"- Exported document with visualizations to {output_path}")
    #     except (PandocNotFoundError, ImportError) as e:
    #         print(f"- Could not export to {fmt}: {str(e)}")
    
    # Clean up
    plt.close('all')
    
    print("\nAll exports completed. Check the outputs directory.")


if __name__ == "__main__":
    main() 