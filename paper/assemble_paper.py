#!/usr/bin/env python3
"""
Paper Assembly Script for Markdown Decision Process

This script assembles all the modular paper sections into a complete academic paper
in both Markdown and PDF formats.

Author: Daniel Ari Friedman
Email: daniel@activeinference.institute
Repository: https://github.com/docxology/markdown_decision_process
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import argparse
import re

class PaperAssembler:
    """Assembles modular paper sections into a complete academic paper."""

    def __init__(self, paper_dir: str = None, output_dir: str = None):
        """Initialize the paper assembler.

        Args:
            paper_dir: Directory containing paper sections (default: current dir)
            output_dir: Output directory for assembled paper (default: paper/outputs)
        """
        self.paper_dir = Path(paper_dir or Path(__file__).parent)
        self.output_dir = Path(output_dir or self.paper_dir / "outputs")
        self.output_dir.mkdir(exist_ok=True)

        # Paper metadata
        self.title = "Markdown Decision Process: A Framework for Probabilistic Document Analysis and Optimization"
        self.authors = ["Daniel Ari Friedman"]
        self.affiliation = "Active Inference Institute"
        self.email = "daniel@activeinference.institute"
        self.repository = "https://github.com/docxology/markdown_decision_process"

    def _sanitize_unicode_for_latex(self, text: str) -> str:
        """Replace Unicode characters that cause LaTeX compilation errors."""
        # Common problematic Unicode characters and their LaTeX equivalents
        unicode_replacements = {
            '↔': r'$\leftrightarrow$',
            '↔︎': r'$\leftrightarrow$',
            '→': r'\rightarrow',
            '←': r'\leftarrow',
            '⇒': r'\Rightarrow',
            '⇐': r'\Leftarrow',
            '⇔': r'\Leftrightarrow',
            '≥': r'$\geq$',
            '≤': r'$\leq$',
            '≠': r'$\neq$',
            '∞': r'$\infty$',
            '∑': r'$\sum$',
            '∫': r'$\int$',
            '∂': r'$\partial$',
            '∆': r'$\Delta$',
            '∇': r'$\nabla$',
            '∏': r'$\prod$',
            '√': r'$\sqrt$',
            '≈': r'$\approx$',
            '≡': r'$\equiv$',
            '∝': r'$\propto$',
            '∪': r'$\cup$',
            '∩': r'$\cap$',
            '⊂': r'$\subset$',
            '⊃': r'$\supset$',
            '⊆': r'$\subseteq$',
            '⊇': r'$\supseteq$',
            '∈': r'$\in$',
            '∉': r'$\notin$',
            '∅': r'$\emptyset$',
            '∧': r'$\wedge$',
            '∨': r'$\vee$',
            '¬': r'$\neg$',
            '∀': r'$\forall$',
            '∃': r'$\exists$',
            '∄': r'$\nexists$',
            '∴': r'$\therefore$',
            '∵': r'$\because$',
            '∶': r':',
            '∷': r'::',
            '∼': r'$\sim$',
            '∽': r'$\backsim$',
            '∾': r'$\thicksim$',
            '≃': r'$\simeq$',
            '≅': r'$\cong$',
            '≪': r'$\ll$',
            '≫': r'$\gg$',
            '≶': r'$\lessgtr$',
            '≷': r'$\gtrless$',
            '≺': r'$\prec$',
            '≻': r'$\succ$',
            '‐': r'-',  # hyphen
            '–': r'--',  # en dash
            '—': r'---',  # em dash
            '…': r'\ldots',  # ellipsis
            '"': r"''",  # smart quotes
            ''': r"`",  # backtick
            ''': r"'",  # apostrophe
            '′': r"'",  # prime
            '″': r"''",  # double prime
            ''': r'"',  # left double quote
            ''': r'"',  # right double quote
            ''': r"'",  # left single quote
            ''': r"'",  # right single quote
        }

        # Apply replacements
        for unicode_char, latex_equiv in unicode_replacements.items():
            text = text.replace(unicode_char, latex_equiv)

        # Handle remaining problematic characters by removing them or replacing with safe alternatives
        # Remove zero-width characters and other invisible Unicode
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

        # Replace other potentially problematic Unicode characters with safe ASCII
        text = re.sub(r'[^\x00-\x7F]', lambda m: f'[{ord(m.group(0)):04X}]', text)

        return text

    def _convert_mermaid_diagrams(self, content: str) -> str:
        """Convert Mermaid diagrams to SVG for proper PDF embedding."""
        import re

        # Find all Mermaid code blocks
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)

        if not mermaid_blocks:
            return content

        # For each Mermaid block, replace with SVG placeholder
        # In a real implementation, you'd use a Mermaid renderer like puppeteer
        # For now, we'll create a simple SVG representation
        for i, mermaid_code in enumerate(mermaid_blocks):
            # Create a simple SVG representation of the graph
            svg_content = self._create_simple_svg_from_mermaid(mermaid_code, i)
            content = content.replace(
                f'```mermaid\n{mermaid_code}\n```',
                f'![Mermaid Diagram {i+1}](data:image/svg+xml;base64,{svg_content})'
            )

        return content

    def _create_simple_svg_from_mermaid(self, mermaid_code: str, index: int) -> str:
        """Create a simple SVG representation from Mermaid code."""
        # This is a simplified implementation
        # In production, use a proper Mermaid renderer

        # Extract nodes and edges from basic Mermaid syntax
        lines = mermaid_code.strip().split('\n')
        nodes = []
        edges = []

        for line in lines:
            line = line.strip()
            if line.startswith('A[') or line.startswith('B[') or line.startswith('C[') or line.startswith('D['):
                # Simple node extraction
                if 'Markdown Document' in line:
                    nodes.append(('A', 'Markdown Document'))
                elif 'StateSpace' in line:
                    nodes.append(('B', 'StateSpace Analyzer'))
                elif 'MarkChain' in line:
                    nodes.append(('C', 'MarkChain Generator'))
                elif 'PolicyOptimizer' in line:
                    nodes.append(('D', 'PolicyOptimizer'))
            elif '-->' in line:
                # Simple edge extraction
                parts = line.split('-->')
                if len(parts) == 2:
                    from_node = parts[0].strip()
                    to_node = parts[1].strip()
                    edges.append((from_node, to_node))

        # Create simple SVG
        svg_width = 600
        svg_height = 400

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .node {{ fill: #e1f5fe; stroke: #01579b; stroke-width: 2; }}
      .edge {{ stroke: #01579b; stroke-width: 2; fill: none; }}
      .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #01579b; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="100%" height="100%" fill="#f5f5f5"/>

  <!-- Title -->
  <text x="50%" y="30" text-anchor="middle" class="text" font-size="16" font-weight="bold">
    System Architecture Diagram
  </text>
'''

        # Add nodes (simplified positioning)
        node_positions = {
            'A': (100, 150),
            'B': (300, 100),
            'C': (300, 250),
            'D': (500, 150)
        }

        for node_id, (x, y) in node_positions.items():
            svg += f'''
  <!-- Node {node_id} -->
  <circle cx="{x}" cy="{y}" r="40" class="node"/>
  <text x="{x}" y="{y+5}" text-anchor="middle" class="text" font-size="10">
    {node_id}
  </text>
'''

        # Add edges
        for from_node, to_node in edges:
            if from_node in node_positions and to_node in node_positions:
                x1, y1 = node_positions[from_node]
                x2, y2 = node_positions[to_node]
                svg += f'''
  <!-- Edge {from_node} -> {to_node} -->
  <line x1="{x1+40}" y1="{y1}" x2="{x2-40}" y2="{y2}" class="edge"/>
  <polygon points="{x2-40-10},{y2-5} {x2-40},{y2} {x2-40-10},{y2+5}" fill="#01579b"/>
'''

        svg += '</svg>'

        # Base64 encode the SVG
        import base64
        svg_bytes = svg.encode('utf-8')
        encoded_svg = base64.b64encode(svg_bytes).decode('utf-8')

        return encoded_svg

    def get_paper_sections(self) -> list:
        """Get all paper sections in order."""
        sections = []

        # Define section order and files
        section_files = {
            "00_abstract": "Abstract",
            "01_introduction": "Introduction",
            "02_background": "Background and Related Work",
            "03_methodology": "Methodology and Architecture",
            "04_core_components": "Core Components",
            "05_implementation": "Implementation Details",
            "06_evaluation": "Evaluation and Experiments",
            "07_results_discussion": "Results and Discussion",
            "08_conclusion": "Conclusion",
            "09_future_work": "Future Work",
            "10_references": "References",
            "11_code": "Code Supplement"
        }

        for filename, title in section_files.items():
            section_path = self.paper_dir / f"{filename}.md"
            if section_path.exists():
                sections.append((title, section_path))

        return sections

    def create_markdown_paper(self) -> str:
        """Create the complete paper in Markdown format."""
        sections = self.get_paper_sections()

        # Create front matter
        front_matter = self._create_front_matter()

        # Combine all sections
        content_parts = [front_matter]

        for title, section_path in sections:
            # Add section header
            content_parts.append(f"\n\n# {title}\n")

            # Read and add section content
            with open(section_path, 'r', encoding='utf-8') as f:
                section_content = f.read().strip()

            # Clean up section content (remove any existing headers)
            lines = section_content.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.startswith('# '):
                    continue  # Skip existing main headers
                cleaned_lines.append(line)

            content_parts.append('\n'.join(cleaned_lines))

        # Join everything together
        full_content = '\n'.join(content_parts)

        # Write to file
        output_file = self.output_dir / "mdp_paper.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)

        print(f"✓ Markdown paper created: {output_file}")
        return str(output_file)

    def create_latex_compatible_markdown(self) -> str:
        """Create a LaTeX-compatible version of the markdown paper."""
        # First create the regular markdown
        markdown_file = self.create_markdown_paper()

        # Read the markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert Mermaid diagrams to SVG for better PDF compatibility
        content = self._convert_mermaid_diagrams(content)

        # Sanitize Unicode characters for LaTeX compatibility (but not in YAML front matter)
        lines = content.split('\n')
        sanitized_lines = []
        in_front_matter = False

        for line in lines:
            if line.strip() == '---' and not in_front_matter:
                in_front_matter = True
                sanitized_lines.append(line)
            elif line.strip() == '---' and in_front_matter:
                in_front_matter = False
                sanitized_lines.append(line)
            elif in_front_matter:
                # Don't sanitize YAML front matter
                sanitized_lines.append(line)
            else:
                # Sanitize content for LaTeX compatibility
                sanitized_lines.append(self._sanitize_unicode_for_latex(line))

        sanitized_content = '\n'.join(sanitized_lines)

        # Write the LaTeX-compatible version
        latex_md_file = self.output_dir / "mdp_paper_latex.md"
        with open(latex_md_file, 'w', encoding='utf-8') as f:
            f.write(sanitized_content)

        print(f"✓ LaTeX-compatible markdown created: {latex_md_file}")
        return str(latex_md_file)

    def _create_front_matter(self) -> str:
        """Create the paper front matter."""
        front_matter = f"""---
title: "{self.title}"
author:
{chr(10).join(f'  - "{author}"' for author in self.authors)}
affiliation: "{self.affiliation}"
email: "{self.email}"
repository: "{self.repository}"
date: "{datetime.now().strftime('%B %Y')}"
abstract: |
  Markdown Decision Process (MDP) is a novel framework that reimagines Markdown documents as stochastic processes analogous to Markov Decision Processes. This package provides tools to analyze, generate, and optimize Markdown content through the lens of decision theory and probabilistic modeling.
keywords: [Markov Decision Processes, Markdown Processing, Document Generation, Active Inference, Probabilistic Modeling, Content Optimization]
---

# {self.title}

**Authors:** {', '.join(self.authors)}  \n**Affiliation:** {self.affiliation}  \n**Email:** {self.email}  \n**Repository:** {self.repository}

"""

        return front_matter

    def _extract_abstract(self) -> str:
        """Extract abstract from the first section (00_abstract.md)."""
        abstract_file = self.paper_dir / "00_abstract.md"
        if abstract_file.exists():
            with open(abstract_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract content after the first header (assuming it's the abstract)
                lines = content.split('\n')
                abstract_lines = []
                for line in lines:
                    if line.startswith('# '):
                        continue  # Skip headers
                    abstract_lines.append(line)
                return '\n'.join(abstract_lines).strip()
        return "This paper presents the Markdown Decision Process framework for probabilistic document analysis and optimization."

    def create_pdf_paper(self, markdown_file: str = None) -> str:
        """Create PDF version of the paper using Pandoc with improved LaTeX support."""
        if markdown_file is None:
            # Use LaTeX-compatible markdown for PDF generation
            markdown_file = self.create_latex_compatible_markdown()

        # Check if pandoc is available
        try:
            subprocess.run(['pandoc', '--version'],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ Pandoc not found. PDF generation requires Pandoc.")
            print("  Install Pandoc from: https://pandoc.org/")
            return None

        # PDF generation options - comprehensive LaTeX setup
        pdf_file = self.output_dir / "mdp_paper.pdf"
        latex_template = self.paper_dir / "academic_template.tex"

        # First try with custom LaTeX template for best quality
        cmd_latex = [
            'pandoc',
            markdown_file,
            '-o', str(pdf_file),
            '--template', str(latex_template),
            '--pdf-engine=pdflatex',
            '--number-sections',
            '--table-of-contents',
            '--toc-depth=3',
            '--metadata', f'author={", ".join(self.authors)}',
            '--metadata', f'title={self.title}',
            '--metadata', f'abstract={self._extract_abstract()}',
            '--variable', 'geometry:margin=1in',
            '--variable', 'fontfamily:libertine',
            '--variable', 'fontsize:11pt',
            '--variable', 'papersize:letter',
            # Additional LaTeX packages for better support
            '--variable', 'documentclass:article',
            '--variable', 'mainfont:Linux Libertine O',
            '--variable', 'sansfont:Linux Biolinum O',
            '--variable', 'monofont:DejaVu Sans Mono',
            # Enable listings for code blocks
            '--listings',
            # Bibliography support with citeproc for proper citation processing
            '--bibliography', str(self.paper_dir / 'references.bib'),
            '--citeproc',
        ]

        try:
            result = subprocess.run(cmd_latex, capture_output=True, text=True, check=True, timeout=120)
            print(f"✓ PDF paper created with LaTeX template: {pdf_file}")
            return str(pdf_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠ LaTeX PDF generation with template failed: {e.stderr}")
            print("  Trying with built-in LaTeX template...")

            # Fallback: Use Pandoc's built-in LaTeX template
            cmd_builtin_latex = [
                'pandoc',
                markdown_file,
                '-o', str(pdf_file),
                '--pdf-engine=pdflatex',
                '--number-sections',
                '--table-of-contents',
                '--toc-depth=3',
                '--metadata', f'author={", ".join(self.authors)}',
                '--metadata', f'title={self.title}',
                '--variable', 'geometry:margin=1in',
                '--variable', 'fontfamily:libertine',
                '--variable', 'fontsize:11pt',
                '--listings',  # Enable code syntax highlighting
                '--bibliography', str(self.paper_dir / 'references.bib'),
                '--citeproc',  # Enable proper citation processing
            ]

            try:
                result = subprocess.run(cmd_builtin_latex, capture_output=True, text=True, check=True, timeout=120)
                print(f"✓ PDF paper created with built-in template: {pdf_file}")
                return str(pdf_file)
            except subprocess.CalledProcessError as e:
                print(f"⚠ Built-in LaTeX PDF generation failed: {e.stderr}")
                print("  Trying HTML-to-PDF conversion...")

                # Fallback: HTML to PDF using wkhtmltopdf if available
                try:
                    # First create HTML
                    html_file = self.output_dir / "temp_paper.html"
                    html_cmd = [
                        'pandoc',
                        markdown_file,
                        '-o', str(html_file),
                        '--standalone',
                        '--embed-resources',
                        '--table-of-contents',
                        '--number-sections',
                        '--metadata', f'author={", ".join(self.authors)}',
                        '--metadata', f'title={self.title}',
                        '--css', str(self.paper_dir / 'academic.css'),  # Custom CSS if available
                    ]
                    subprocess.run(html_cmd, capture_output=True, check=True)

                    # Check if wkhtmltopdf is available
                    try:
                        subprocess.run(['wkhtmltopdf', '--version'],
                                     capture_output=True, check=True, timeout=10)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("  wkhtmltopdf not available, trying pandoc's HTML-to-PDF...")
                        # Use pandoc's HTML-to-PDF engine as fallback
                        pdf_cmd = [
                            'pandoc',
                            str(html_file),
                            '-o', str(pdf_file),
                            '--pdf-engine=wkhtmltopdf',
                        ]
                        subprocess.run(pdf_cmd, capture_output=True, check=True, timeout=60)
                    else:
                        # Use wkhtmltopdf directly
                        pdf_cmd = [
                            'wkhtmltopdf',
                            '--page-size', 'Letter',
                            '--margin-top', '1in',
                            '--margin-bottom', '1in',
                            '--margin-left', '1in',
                            '--margin-right', '1in',
                            '--encoding', 'UTF-8',
                            str(html_file),
                            str(pdf_file)
                        ]
                        subprocess.run(pdf_cmd, capture_output=True, check=True, timeout=60)

                    # Clean up temp file
                    if html_file.exists():
                        html_file.unlink()

                    print(f"✓ PDF created via HTML conversion: {pdf_file}")
                    return str(pdf_file)

                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    print("  HTML-to-PDF also failed. Trying minimal LaTeX PDF...")

                    # Final fallback: very basic PDF with minimal LaTeX
                    basic_cmd = [
                        'pandoc',
                        markdown_file,
                        '-o', str(pdf_file),
                        '--pdf-engine=pdflatex',
                        '--variable', 'geometry:margin=1.5in',
                        '--variable', 'fontsize:10pt',
                    ]

                    try:
                        subprocess.run(basic_cmd, capture_output=True, check=True, timeout=60)
                        print(f"✓ Basic PDF created: {pdf_file}")
                        return str(pdf_file)
                    except subprocess.CalledProcessError:
                        print("✗ All PDF generation methods failed.")
                        return None

    def create_latex_paper(self, markdown_file: str = None) -> str:
        """Create LaTeX version for advanced formatting."""
        if markdown_file is None:
            markdown_file = self.create_markdown_paper()

        latex_file = self.output_dir / "mdp_paper.tex"

        cmd = [
            'pandoc',
            markdown_file,
            '-o', str(latex_file),
            '--template', str(self.paper_dir / "academic_template.tex"),  # Custom template
            '--listings',
            '--number-sections',
            '--bibliography', str(self.paper_dir / "references.bib"),
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✓ LaTeX paper created: {latex_file}")
            return str(latex_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠ LaTeX generation failed: {e.stderr}")
            return None

    def create_word_document(self, markdown_file: str = None) -> str:
        """Create Word document version."""
        if markdown_file is None:
            markdown_file = self.create_markdown_paper()

        docx_file = self.output_dir / "mdp_paper.docx"

        # Try basic Word document generation
        cmd = [
            'pandoc',
            markdown_file,
            '-o', str(docx_file),
            '--metadata', f'author={", ".join(self.authors)}',
            '--metadata', f'title={self.title}',
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✓ Word document created: {docx_file}")
            return str(docx_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠ Word document generation failed: {e.stderr}")
            return None

    def create_html_paper(self, markdown_file: str = None) -> str:
        """Create HTML version with styling."""
        if markdown_file is None:
            markdown_file = self.create_markdown_paper()

        html_file = self.output_dir / "mdp_paper.html"

        # Try with embedded resources first
        cmd = [
            'pandoc',
            markdown_file,
            '-o', str(html_file),
            '--embed-resources',
            '--standalone',
            '--table-of-contents',
            '--number-sections',
            '--metadata', f'author={", ".join(self.authors)}',
            '--metadata', f'title={self.title}',
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✓ HTML paper created: {html_file}")
            return str(html_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠ HTML generation with embedded resources failed: {e.stderr}")
            print("  Trying basic HTML generation...")

            # Fallback to basic HTML
            basic_cmd = [
                'pandoc',
                markdown_file,
                '-o', str(html_file),
                '--standalone',
                '--table-of-contents',
                '--number-sections',
            ]

            try:
                subprocess.run(basic_cmd, capture_output=True, check=True)
                print(f"✓ Basic HTML paper created: {html_file}")
                return str(html_file)
            except subprocess.CalledProcessError:
                print("✗ HTML generation failed completely.")
                return None

    def create_all_formats(self):
        """Create the paper in all supported formats."""
        print("📄 Assembling Markdown Decision Process Paper")
        print("=" * 50)

        # Create markdown version first (for HTML and Word)
        markdown_file = self.create_markdown_paper()

        if not markdown_file:
            print("✗ Failed to create base markdown file")
            return False

        # Create LaTeX-compatible version for PDF
        latex_markdown_file = self.create_latex_compatible_markdown()

        # Create other formats
        formats_created = ["Markdown"]

        if self.create_pdf_paper(latex_markdown_file):
            formats_created.append("PDF")

        if self.create_html_paper(markdown_file):
            formats_created.append("HTML")

        if self.create_word_document(markdown_file):
            formats_created.append("Word")

        # Summary
        print("\n" + "=" * 50)
        print("✅ Paper assembly complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📄 Formats created: {', '.join(formats_created)}")
        print(f"📖 Markdown file: {self.output_dir / 'mdp_paper.md'}")
        print(f"📑 LaTeX-compatible file: {self.output_dir / 'mdp_paper_latex.md'}")

        return True

    def validate_sections(self) -> bool:
        """Validate that all required sections exist."""
        required_sections = [
            "00_abstract.md",
            "01_introduction.md",
            "02_background.md",
            "03_methodology.md",
            "04_core_components.md",
            "05_implementation.md",
            "06_evaluation.md",
            "07_results_discussion.md",
            "08_conclusion.md",
            "09_future_work.md",
            "10_references.md",
            "11_code.md"
        ]

        missing_sections = []

        for section in required_sections:
            section_path = self.paper_dir / section
            if not section_path.exists():
                missing_sections.append(section)

        if missing_sections:
            print(f"⚠ Missing sections: {', '.join(missing_sections)}")
            return False

        print("✓ All required sections found")
        return True


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Assemble Markdown Decision Process paper from modular sections"
    )
    parser.add_argument(
        "--paper-dir",
        default=None,
        help="Directory containing paper sections (default: paper/)"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for assembled paper (default: paper/outputs/)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "pdf", "html", "word", "latex", "all"],
        default="all",
        help="Output format(s) to generate"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate sections without assembling"
    )

    args = parser.parse_args()

    assembler = PaperAssembler(args.paper_dir, args.output_dir)

    # Validate sections first
    if not assembler.validate_sections():
        print("❌ Validation failed. Cannot proceed with assembly.")
        return 1

    if args.validate_only:
        print("✅ All sections validated successfully!")
        return 0

    # Assemble based on format
    if args.format == "all":
        success = assembler.create_all_formats()
    elif args.format == "markdown":
        success = assembler.create_markdown_paper() is not None
    elif args.format == "pdf":
        success = assembler.create_pdf_paper() is not None
    elif args.format == "html":
        success = assembler.create_html_paper() is not None
    elif args.format == "word":
        success = assembler.create_word_document() is not None
    elif args.format == "latex":
        success = assembler.create_latex_paper() is not None

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
