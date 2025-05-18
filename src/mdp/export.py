"""
Export: A module for exporting visualizations and documents to various formats.
"""

import os
import io
import json
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
import base64
from datetime import datetime
import tempfile

from .state_space import StateSpace
from .visualization import (
    plot_document_metrics,
    plot_transitions,
    plot_document_structure,
    plot_readability_comparison
)
from .document import Document
from .markchain import MarkChain
from .pandoc import PandocConverter, check_pandoc_installed, PandocNotFoundError
from .quality import DocumentQuality


def _ensure_document(input_val: Union[Document, str, Path]) -> Document:
    if isinstance(input_val, Document):
        return input_val
    elif isinstance(input_val, (str, Path)):
        return Document(file_path=str(input_val))
    else:
        raise TypeError(f"Unsupported document input type: {type(input_val)}. Expected Document, str, or Path.")


class VisualizationExporter:
    """
    A class for exporting visualizations and integrating them with documents.
    
    This exporter can:
    1. Save visualizations in various formats (PNG, PDF, SVG)
    2. Export visualizations to standalone HTML
    3. Embed visualizations in markdown documents
    4. Convert documents with integrated visualizations to other formats
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize a VisualizationExporter.
        
        Args:
            output_dir: Directory to save exports to. If None, use current directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to initialize Pandoc
        self.pandoc = None
        try:
            self.pandoc = PandocConverter()
        except PandocNotFoundError:
            # Pandoc not available, but we'll continue without it
            pass
    
    def export_figure(
        self,
        fig: plt.Figure,
        output_path: Union[str, Path],
        format: str = "png",
        dpi: int = 300,
        transparent: bool = False,
        **kwargs
    ) -> Path:
        """
        Export a matplotlib figure to a file.
        
        Args:
            fig: Matplotlib figure object
            output_path: Path where the figure will be saved
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            transparent: Whether to use transparent background
            **kwargs: Additional kwargs to pass to fig.savefig()
            
        Returns:
            Path to saved file
        """
        # Ensure output path has correct extension
        output_path = Path(output_path)
        output_path = output_path.with_suffix(f".{format}")
        
        # Create full path if only filename was provided
        if not output_path.is_absolute():
            output_path = self.output_dir / output_path
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save figure
        fig.savefig(
            output_path,
            format=format,
            dpi=dpi,
            transparent=transparent,
            bbox_inches='tight',
            **kwargs
        )
        
        return output_path
    
    def export_state_space(
        self,
        state_space: StateSpace,
        output_path: Union[str, Path],
        title: str = "Markdown State Space",
        format: str = "png",
        dpi: int = 300
    ) -> Path:
        """
        Export a state space visualization to a file.
        
        Args:
            state_space: StateSpace object to visualize
            output_path: Path where the visualization will be saved
            title: Title for the visualization
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            
        Returns:
            Path to saved file
        """
        # Ensure output path has correct extension
        output_path = Path(output_path)
        output_path = output_path.with_suffix(f".{format}")
        
        # Create full path if only filename was provided
        if not output_path.is_absolute():
            output_path = self.output_dir / output_path
        
        # Generate visualization
        state_space.visualize(str(output_path), title)
        
        return output_path
    
    def export_document_metrics(
        self,
        metrics_dict: Dict[str, Dict[str, Dict[str, float]]],
        output_path: Union[str, Path],
        format: str = "png",
        dpi: int = 300,
        figsize: Tuple[int, int] = (12, 8)
    ) -> Path:
        """
        Export document metrics visualization to a file.
        
        Args:
            metrics_dict: Dictionary mapping document names to their metrics
            output_path: Path where the visualization will be saved
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            figsize: Figure size (width, height)
            
        Returns:
            Path to saved file
        """
        # Create metrics visualization
        fig = plot_document_metrics(metrics_dict, figsize=figsize)
        
        # Export figure
        return self.export_figure(
            fig=fig,
            output_path=output_path,
            format=format,
            dpi=dpi
        )
    
    def export_transitions(
        self,
        chain: MarkChain,
        output_path: Union[str, Path],
        top_n: int = 10,
        format: str = "png",
        dpi: int = 300,
        figsize: Tuple[int, int] = (12, 10)
    ) -> Path:
        """
        Export state transition visualization to a file.
        
        Args:
            chain: Trained MarkChain object
            output_path: Path where the visualization will be saved
            top_n: Number of most frequent states to include
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            figsize: Figure size (width, height)
            
        Returns:
            Path to saved file
        """
        # Create transitions visualization
        fig = plot_transitions(chain, top_n=top_n, figsize=figsize)
        
        # Export figure
        return self.export_figure(
            fig=fig,
            output_path=output_path,
            format=format,
            dpi=dpi
        )
    
    def export_document_structure(
        self,
        document: Union[Document, str, Path],
        output_path: Union[str, Path],
        format: str = "png",
        dpi: int = 300,
        figsize: Tuple[int, int] = (10, 12)
    ) -> Path:
        """
        Export document structure visualization to a file.
        
        Args:
            document: MarkdownDocument, path to a markdown file, or content string
            output_path: Path where the visualization will be saved
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            figsize: Figure size (width, height)
            
        Returns:
            Path to saved file
        """
        # Create document structure visualization
        fig = plot_document_structure(document, figsize=figsize)
        
        # Export figure
        return self.export_figure(
            fig=fig,
            output_path=output_path,
            format=format,
            dpi=dpi
        )
    
    def export_readability_comparison(
        self,
        documents: Dict[str, Union[Document, str, Path]],
        output_path: Union[str, Path],
        format: str = "png",
        dpi: int = 300,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Path:
        """
        Export readability comparison visualization to a file.
        
        Args:
            documents: Dictionary mapping document names to MarkdownDocument, paths, or content strings
            output_path: Path where the visualization will be saved
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            figsize: Figure size (width, height)
            
        Returns:
            Path to saved file
        """
        # Create readability comparison visualization
        fig = plot_readability_comparison(documents, figsize=figsize)
        
        # Export figure
        return self.export_figure(
            fig=fig,
            output_path=output_path,
            format=format,
            dpi=dpi
        )
    
    def export_to_html(
        self,
        fig: plt.Figure,
        output_path: Union[str, Path],
        title: str = "Visualization Export",
        include_interactive: bool = True
    ) -> Path:
        """
        Export a matplotlib figure to a standalone HTML file.
        
        Args:
            fig: Matplotlib figure object
            output_path: Path where the HTML file will be saved
            title: Title for the HTML page
            include_interactive: Whether to include interactive elements
            
        Returns:
            Path to saved HTML file
        """
        # Ensure output path has html extension
        output_path = Path(output_path)
        output_path = output_path.with_suffix(".html")
        
        # Create full path if only filename was provided
        if not output_path.is_absolute():
            output_path = self.output_dir / output_path
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine if we should use interactive features
        if include_interactive:
            try:
                import mpld3
                html_content = mpld3.fig_to_html(fig)
            except (ImportError, Exception):
                # Fall back to static image if mpld3 not available
                include_interactive = False
        
        if not include_interactive:
            # Create a static image embedded in HTML
            img_data = io.BytesIO()
            fig.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
            img_data.seek(0)
            
            encoded = base64.b64encode(img_data.read()).decode('utf-8')
            html_content = f'<img src="data:image/png;base64,{encoded}" alt="Visualization" />'
        
        # Create HTML document
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ margin-bottom: 20px; }}
        .footer {{ margin-top: 20px; color: #666; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="visualization">
            {html_content}
        </div>
        <div class="footer">
            <p>Generated by Markdown Decision Process on {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write HTML to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def embed_in_markdown(
        self,
        fig: plt.Figure,
        output_markdown_path: Union[str, Path],
        fig_path: Optional[Union[str, Path]] = None,
        format: str = "png",
        dpi: int = 300,
        embed_base64: bool = False,
        link_text: str = "Click to view visualization",
        inline: bool = True
    ) -> Path:
        """
        Embed a visualization in a markdown document.
        
        Args:
            fig: Matplotlib figure object
            output_markdown_path: Path where the markdown file will be saved
            fig_path: Path where the figure will be saved (if None, derived from markdown path)
            format: Output format - png, pdf, svg, etc.
            dpi: Resolution for raster formats
            embed_base64: Whether to embed the image as base64 (increases file size but makes it self-contained)
            link_text: Text to use for the link (if not inline)
            inline: Whether to embed the image inline or as a link
            
        Returns:
            Path to saved markdown file
        """
        # Ensure output path has md extension
        output_markdown_path = Path(output_markdown_path)
        output_markdown_path = output_markdown_path.with_suffix(".md")
        
        # Create full path if only filename was provided
        if not output_markdown_path.is_absolute():
            output_markdown_path = self.output_dir / output_markdown_path
        
        # Ensure parent directory exists
        output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine figure path
        if fig_path is None:
            fig_path = output_markdown_path.with_suffix(f".{format}")
        else:
            fig_path = Path(fig_path)
            fig_path = fig_path.with_suffix(f".{format}")
            
            if not fig_path.is_absolute():
                fig_path = output_markdown_path.parent / fig_path
        
        # Save figure
        if not embed_base64:
            self.export_figure(fig, fig_path, format=format, dpi=dpi)
            
            # Get relative path from markdown to figure
            fig_rel_path = os.path.relpath(fig_path, output_markdown_path.parent)
            
            # Create markdown content
            if inline:
                markdown_content = f"![Visualization]({fig_rel_path})"
            else:
                markdown_content = f"[{link_text}]({fig_rel_path})"
        else:
            # Embed as base64
            img_data = io.BytesIO()
            fig.savefig(img_data, format=format, dpi=dpi, bbox_inches='tight')
            img_data.seek(0)
            
            encoded = base64.b64encode(img_data.read()).decode('utf-8')
            markdown_content = f"![Visualization](data:image/{format};base64,{encoded})"
        
        # Write markdown content
        with open(output_markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_markdown_path
    
    def export_document_with_visualizations(
        self,
        document: Union[Document, str, Path],
        output_path: Union[str, Path],
        visualizations: List[Tuple[str, plt.Figure, Dict[str, Any]]],
        to_format: str = "pdf",
        embed_base64: bool = False
    ) -> Path:
        """
        Export a document with embedded visualizations to various formats using Pandoc.
        
        Args:
            document: MarkdownDocument, path to a markdown file, or content string
            output_path: Path where the output file will be saved
            visualizations: List of tuples (marker, figure, kwargs) where:
                - marker is the text in the document to replace with the visualization
                - figure is the matplotlib figure to embed
                - kwargs are additional arguments for export_figure
            to_format: Output format (pdf, docx, html, etc.)
            embed_base64: Whether to embed images as base64 (only relevant for HTML output)
            
        Returns:
            Path to the exported file
            
        Raises:
            PandocNotFoundError: If Pandoc is not installed and required for conversion
        """
        if not self.pandoc:
            try:
                self.pandoc = PandocConverter()
            except PandocNotFoundError:
                raise PandocNotFoundError(
                    "Pandoc is required for document export but not found. "
                    "Please install Pandoc from https://pandoc.org/installing.html"
                )
        
        # Ensure we have a MarkdownDocument
        if not isinstance(document, Document):
            if isinstance(document, (str, Path)) and str(document).endswith('.md'):
                # If it's a path to a markdown file
                document = Document(file_path=document)
            else:
                # Assume it's content
                document = Document(content=str(document))
        
        # Get content
        content = document.get_content()
        
        # Create a temp directory for processing
        temp_dir = self.output_dir / f"temp_export_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Process visualizations
        for marker, fig, kwargs in visualizations:
            # Generate unique filename for this visualization
            fig_filename = f"viz_{hash(marker) % 10000:04d}.png"
            fig_path = temp_dir / fig_filename
            
            # Save the figure
            self.export_figure(fig, fig_path, **kwargs)
            
            # Replace marker in content with image reference
            img_markdown = f"![{marker}]({fig_path})"
            content = content.replace(marker, img_markdown)
        
        # Write processed markdown to temp file
        temp_md = temp_dir / "processed.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Ensure output path has correct extension
        output_path = Path(output_path)
        if not output_path.suffix or output_path.suffix.lower() != f".{to_format}":
            output_path = output_path.with_suffix(f".{to_format}")
        
        if not output_path.is_absolute():
            output_path = self.output_dir / output_path
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Special handling for HTML with base64 embedding
        extra_args = []
        if to_format.lower() == "html" and embed_base64:
            extra_args.append("--embed-resources")
            extra_args.append("--standalone")
        
        # Convert using Pandoc
        self.pandoc.convert(
            input_path=temp_md,
            output_path=output_path,
            from_format="markdown",
            to_format=to_format,
            extra_args=extra_args
        )
        
        # Clean up temp directory (optional)
        # NOTE: Uncomment to clean up temp files
        # import shutil
        # shutil.rmtree(temp_dir)
        
        return output_path
    
    def export_analysis_report(
        self,
        document: Union[Document, str, Path],
        output_path: Union[str, Path],
        format: str = "pdf",
        include_visualizations: bool = True,
        include_metrics: bool = True,
        include_structure: bool = True
    ) -> Path:
        """
        Generate and export a comprehensive analysis report for a markdown document.
        
        Args:
            document: MarkdownDocument, path to a markdown file, or content string
            output_path: Path where the report will be saved
            format: Output format (pdf, html, docx, etc.)
            include_visualizations: Whether to include visualizations
            include_metrics: Whether to include metrics
            include_structure: Whether to include structure analysis
            
        Returns:
            Path to the exported report
        """
        from .markdown_agent import MarkdownAgent
        from .quality import DocumentQuality
        
        # Ensure we have a MarkdownDocument
        if not isinstance(document, Document):
            if isinstance(document, (str, Path)) and (isinstance(document, Path) or os.path.exists(document)):
                # If it's a path to a file
                document_path = str(document)
                document = Document(file_path=document)
            else:
                # Assume it's content
                document_path = "document.md"
                document = Document(content=str(document))
        else:
            document_path = "document.md"
        
        # Get document filename for report title
        doc_name = Path(document_path).stem
        
        # Create agent and quality analyzer
        agent = MarkdownAgent()
        quality = DocumentQuality()
        
        # Analyze document
        agent_analysis = agent.analyze(document)
        quality_metrics = quality.analyze_document(document)
        
        # Create temp directory for processing
        temp_dir = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate visualizations
        visualizations = []
        
        if include_structure:
            structure_fig = plot_document_structure(document)
            structure_path = temp_dir / "structure.png"
            self.export_figure(structure_fig, structure_path)
            visualizations.append((structure_path, "Document Structure"))
        
        if include_metrics:
            # Create metrics visualization
            metrics_dict = {doc_name: quality_metrics}
            metrics_fig = plot_document_metrics(metrics_dict)
            metrics_path = temp_dir / "metrics.png"
            self.export_figure(metrics_fig, metrics_path)
            visualizations.append((metrics_path, "Document Metrics"))
        
        # Generate state space visualization if possible
        if include_visualizations and hasattr(agent, 'state_space') and agent.state_space:
            state_space_path = temp_dir / "state_space.png"
            agent.state_space.visualize(str(state_space_path))
            visualizations.append((state_space_path, "State Space Visualization"))
        
        # Generate markdown report
        report_md = temp_dir / "report.md"
        
        with open(report_md, 'w', encoding='utf-8') as f:
            # Write report header
            f.write(f"# Analysis Report: {doc_name}\n\n")
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            # Document summary
            f.write("## Document Summary\n\n")
            f.write(f"- **Filename:** {doc_name}\n")
            content = document.get_content()
            word_count = len(content.split())
            f.write(f"- **Word Count:** {word_count}\n")
            f.write(f"- **Element Count:** {len(document.get_structure())}\n\n")
            
            # Quality metrics
            f.write("## Quality Metrics\n\n")
            
            if 'readability' in quality_metrics:
                f.write("### Readability\n\n")
                for metric, value in quality_metrics['readability'].items():
                    f.write(f"- **{metric.replace('_', ' ').title()}:** {value:.2f}\n")
                f.write("\n")
            
            if 'information_density' in quality_metrics:
                f.write("### Information Density\n\n")
                for metric, value in quality_metrics['information_density'].items():
                    f.write(f"- **{metric.replace('_', ' ').title()}:** {value:.2f}\n")
                f.write("\n")
            
            if 'structural_balance' in quality_metrics:
                f.write("### Structural Balance\n\n")
                for metric, value in quality_metrics['structural_balance'].items():
                    f.write(f"- **{metric.replace('_', ' ').title()}:** {value:.2f}\n")
                f.write("\n")
            
            # Agent analysis
            f.write("## State Analysis\n\n")
            f.write(f"- **Unique States:** {agent_analysis.get('unique_states', 'N/A')}\n")
            f.write(f"- **State Transitions:** {agent_analysis.get('state_transitions', 'N/A')}\n\n")
            
            if 'value_analysis' in agent_analysis:
                f.write("### Value Analysis\n\n")
                value = agent_analysis['value_analysis']
                f.write(f"- **Total Value:** {value.get('total_value', 0):.2f}\n")
                f.write(f"- **Average Value:** {value.get('average_value', 0):.2f}\n\n")
            
            # Visualizations
            f.write("## Visualizations\n\n")
            
            for viz_path, viz_title in visualizations:
                rel_path = viz_path.relative_to(temp_dir)
                f.write(f"### {viz_title}\n\n")
                f.write(f"![{viz_title}]({rel_path})\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            # Generate recommendations based on metrics
            recommendations = []
            
            readability = quality_metrics.get('readability', {})
            if 'flesch_reading_ease' in readability and readability['flesch_reading_ease'] < 50:
                recommendations.append("Consider simplifying language to improve readability.")
            
            structure = quality_metrics.get('structural_balance', {})
            if 'heading_distribution' in structure and structure['heading_distribution'] < 0.5:
                recommendations.append("Add more subheadings to better organize content.")
            
            if not recommendations:
                recommendations.append("Document analysis complete. No specific recommendations.")
            
            for rec in recommendations:
                f.write(f"- {rec}\n")
        
        # Ensure output path has correct extension
        output_path = Path(output_path)
        if not output_path.suffix or output_path.suffix.lower() != f".{format}":
            output_path = output_path.with_suffix(f".{format}")
        
        if not output_path.is_absolute():
            output_path = self.output_dir / output_path
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert using Pandoc
        try:
            if not self.pandoc:
                self.pandoc = PandocConverter()
                
            extra_args = ["--standalone"]
            
            # Add special handling for different formats
            if format.lower() == "pdf":
                extra_args.extend([
                    "--pdf-engine=xelatex",
                    "--variable=geometry:margin=1in"
                ])
            elif format.lower() == "html":
                extra_args.extend([
                    "--css=https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css",
                    "--self-contained"
                ])
            
            self.pandoc.convert(
                input_path=report_md,
                output_path=output_path,
                from_format="markdown",
                to_format=format,
                extra_args=extra_args
            )
            
            return output_path
            
        except PandocNotFoundError:
            # If Pandoc is not available, just copy the markdown and images
            import shutil
            
            output_md = output_path.with_suffix(".md")
            shutil.copy(report_md, output_md)
            
            # Copy all visualization files
            for viz_path, _ in visualizations:
                shutil.copy(viz_path, output_path.parent / viz_path.name)
            
            print(
                "Pandoc not found. Exported report as Markdown with separate image files. "
                "Install Pandoc for PDF/HTML/DOCX conversion."
            )
            
            return output_md 