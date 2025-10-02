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
        self.doi = "10.5281/zenodo.17244387"

        # Initialize state tracking
        self._validated = False
        self._sections = []
        self._errors = []

    def _sanitize_unicode_for_latex(self, text: str) -> str:
        """Replace problematic Unicode characters for LaTeX compatibility."""
        # Replace characters that commonly cause LaTeX compilation issues
        problematic_chars = {
            # Zero-width characters
            '\u200B': '',  # ZERO WIDTH SPACE
            '\u200C': '',  # ZERO WIDTH NON-JOINER
            '\u200D': '',  # ZERO WIDTH JOINER
            '\uFEFF': '',  # ZERO WIDTH NO-BREAK SPACE (BOM)
            '\u00A0': ' ',  # NO-BREAK SPACE -> regular space

            # Mathematical symbols that need LaTeX equivalents
            'α': r'$\alpha$',  # Greek alpha
            'β': r'$\beta$',   # Greek beta
            'γ': r'$\gamma$',  # Greek gamma
            'δ': r'$\delta$',  # Greek delta
            'ε': r'$\epsilon$', # Greek epsilon
            'θ': r'$\theta$',  # Greek theta
            'λ': r'$\lambda$', # Greek lambda
            'μ': r'$\mu$',     # Greek mu
            'π': r'$\pi$',     # Greek pi
            'σ': r'$\sigma$',  # Greek sigma
            'τ': r'$\tau$',    # Greek tau
            'φ': r'$\phi$',    # Greek phi
            'χ': r'$\chi$',    # Greek chi
            'ψ': r'$\psi$',    # Greek psi
            'ω': r'$\omega$',  # Greek omega

            # Mathematical operators and symbols
            '≤': r'$\leq$',    # Less than or equal
            '≥': r'$\geq$',    # Greater than or equal
            '≠': r'$\neq$',    # Not equal
            '≈': r'$\approx$', # Approximately equal
            '≡': r'$\equiv$',  # Identical to
            '∝': r'$\propto$', # Proportional to
            '∞': r'$\infty$',  # Infinity
            '∑': r'$\sum$',    # Summation
            '∏': r'$\prod$',   # Product
            '∫': r'$\int$',    # Integral
            '∂': r'$\partial$', # Partial derivative
            '∇': r'$\nabla$',  # Nabla
            '√': r'$\sqrt$',   # Square root
            '∆': r'$\Delta$',  # Delta (increment)
            '∪': r'$\cup$',    # Union
            '∩': r'$\cap$',    # Intersection
            '⊂': r'$\subset$', # Subset
            '⊃': r'$\supset$', # Superset
            '⊆': r'$\subseteq$', # Subset or equal
            '⊇': r'$\supseteq$', # Superset or equal
            '∈': r'$\in$',     # Element of
            '∉': r'$\notin$',  # Not element of
            '∅': r'$\emptyset$', # Empty set
            '∧': r'$\wedge$',  # Logical and
            '∨': r'$\vee$',   # Logical or
            '¬': r'$\neg$',    # Logical not
            '∀': r'$\forall$', # Universal quantifier
            '∃': r'$\exists$', # Existential quantifier
            '∴': r'$\therefore$', # Therefore
            '∵': r'$\because$',  # Because
            '∶': r':',         # Ratio
            '∷': r'::',        # Proportion
            '∼': r'$\sim$',    # Similar to
            '∽': r'$\backsim$', # Reverse similar
            '∾': r'$\thicksim$', # Thick similar
            '≃': r'$\simeq$',  # Asymptotically equal
            '≅': r'$\cong$',   # Approximately equal
            '≪': r'$\ll$',     # Much less than
            '≫': r'$\gg$',     # Much greater than
            '≶': r'$\lessgtr$', # Less-greater
            '≷': r'$\gtrless$', # Greater-less
            '≺': r'$\prec$',   # Precedes
            '≻': r'$\succ$',   # Succeeds

            # Arrows
            '←': r'$\leftarrow$',   # Left arrow
            '→': r'$\rightarrow$',   # Right arrow
            '↔': r'$\leftrightarrow$', # Left-right arrow
            '⇒': r'$\Rightarrow$',   # Right double arrow
            '⇐': r'$\Leftarrow$',   # Left double arrow
            '⇔': r'$\Leftrightarrow$', # Left-right double arrow
            '⇐': r'$\Leftarrow$',   # Left double arrow
            '⇔': r'$\Leftrightarrow$', # Left-right double arrow

            # Punctuation and typography
            '"': r"''",         # Smart quotes
            ''': r"`",          # Backtick
            ''': r"'",          # Apostrophe
            '‐': r'-',          # Hyphen
            '–': r'--',         # En dash
            '—': r'---',        # Em dash
            '…': r'\ldots',     # Ellipsis
        }

        # Apply replacements
        for unicode_char, replacement in problematic_chars.items():
            text = text.replace(unicode_char, replacement)

        return text

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        missing_deps = []

        # Check Pandoc
        try:
            subprocess.run(['pandoc', '--version'],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_deps.append("pandoc")

        # Check LaTeX (for PDF generation)
        try:
            subprocess.run(['pdflatex', '--version'],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_deps.append("pdflatex")

        if missing_deps:
            print(f"⚠ Missing dependencies: {', '.join(missing_deps)}")
            print("  Install missing tools to enable all output formats:")
            for dep in missing_deps:
                if dep == "pandoc":
                    print("    - Pandoc: https://pandoc.org/installing.html")
                elif dep == "pdflatex":
                    print("    - LaTeX: Install texlive or similar distribution")
            return False

        return True

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
            "07_results": "Results",
            "08_discussion": "Discussion",
            "09_conclusion": "Conclusion",
            "10_future_work": "Future Work",
            "12_references": "References",
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
        
        # Convert citation markers to inline format
        content = self._convert_citations_to_inline(content)

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
    
    def _convert_citations_to_inline(self, content: str) -> str:
        """Convert citation markers [@key] to inline (Author, Year) format."""
        import re
        
        # Simple mapping of common citation keys to author-year format
        # This is a simplified approach - in production you'd parse the .bib file
        citation_map = {
            'pandoc': '(MacFarlane, 2006)',
            'markdownlint': '(Markdownlint Contributors, 2023)',
            'doc2vec': '(Le & Mikolov, 2014)',
            'bert': '(Devlin et al., 2018)',
            'roberta': '(Liu et al., 2019)',
            'layout_analysis': '(Mao et al., 2005)',
            'visual_document_understanding': '(Mao et al., 2005)',
            'readability_metrics': '(Collins-Thompson & Callan, 2014)',
            'flesch_kincaid': '(Kincaid et al., 1975)',
            'document_coherence': '(Lapata & Barzilay, 2015)',
            'semantic_document_structure': '(Brin & Page, 1998)',
            'neural_document_generation': '(Li et al., 2019)',
            'multi_modal_documents': '(Yang et al., 2020)',
            'ngram_models': '(Brown et al., 1992)',
            'language_modeling': '(Jurafsky & Martin, 2023)',
            'markov_text_gen': '(Shannon, 1951)',
            'creative_text_generation': '(Radford et al., 2019)',
            'document_structure_markov': '(Taskar et al., 2005)',
            'mdp_theory': '(Puterman, 1994)',
            'sutton_barto': '(Sutton & Barto, 2018)',
            'pomdp_theory': '(Kaelbling et al., 1998)',
            'pomdp_survey': '(Kurniawati & Yadav, 2021)',
            'predictive_processing': '(Rao & Ballard, 1999)',
        }
        
        # Replace citation markers with inline format
        def replace_citation(match):
            keys = match.group(1).split(';')
            citations = []
            for key in keys:
                key = key.strip().lstrip('@')
                if key in citation_map:
                    citations.append(citation_map[key].strip('()'))
                else:
                    citations.append(key)  # Fallback to key if not in map
            return '(' + '; '.join(citations) + ')'
        
        # Pattern: [@key] or [@key1; @key2]
        content = re.sub(r'\[@([^\]]+)\]', replace_citation, content)
        
        return content

    def _create_front_matter(self) -> str:
        """Create the paper front matter."""
        front_matter = f"""---
title: "{self.title}"
author:
{chr(10).join(f'  - "{author}"' for author in self.authors)}
affiliation: "{self.affiliation}"
email: "{self.email}"
repository: "{self.repository}"
doi: "{self.doi}"
date: "{datetime.now().strftime('%B %Y')}"
abstract: |
  The Markdown Decision Process (MDP) framework revolutionizes document processing by modeling Markdown documents as stochastic decision processes analogous to Markov Decision Processes (MDPs) and Partially Observable Markov Decision Processes (POMDPs). This comprehensive framework bridges decision theory with practical document engineering, providing theoretically-grounded tools for intelligent document analysis, generation, and optimization that explicitly handle semantic uncertainty and enable interpretable, uncertainty-aware document processing.
keywords: [Markov Decision Processes, Document AI, Content Optimization, Active Inference, Probabilistic Modeling, Automated Documentation, Natural Language Generation]
---

# {self.title}

**Authors:** {', '.join(self.authors)}  \n**Affiliation:** {self.affiliation}  \n**Email:** {self.email}  \n**Repository:** {self.repository}  \n**DOI:** {self.doi}

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
        """Create PDF version of the paper using Pandoc with robust LaTeX generation."""
        if markdown_file is None:
            markdown_file = self.create_latex_compatible_markdown()

        # Check if pandoc is available
        try:
            subprocess.run(['pandoc', '--version'],
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ Pandoc not found. PDF generation requires Pandoc.")
            print("  Install Pandoc from: https://pandoc.org/")
            return None

        pdf_file = self.output_dir / "mdp_paper.pdf"
        latex_template = self.paper_dir / "academic_template.tex"

        # Primary PDF generation with custom template
        # Note: Citations in format [@key] are converted to (Author, Year) format in text
        # and the References section is manually formatted in the markdown
        cmd = [
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
            '--variable', 'fontsize=11pt',
            '--variable', 'papersize:letter',
            '--variable', 'documentclass:article',
            '--variable', 'mainfont:Linux Libertine O',
            '--variable', 'sansfont:Linux Biolinum O',
            '--variable', 'monofont:DejaVu Sans Mono',
            '--listings',
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
            print(f"✓ PDF paper created successfully: {pdf_file}")
            return str(pdf_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠ PDF generation failed: {e.stderr}")
            print("  Please check your LaTeX installation and ensure all required packages are available.")
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

        # Validate outputs
        if not self.validate_outputs():
            print("⚠ Some output files may be invalid or missing")

        # Summary
        print("\n" + "=" * 50)
        print("✅ Paper assembly complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📄 Formats created: {', '.join(formats_created)}")
        print(f"📖 Markdown file: {self.output_dir / 'mdp_paper.md'}")
        print(f"📑 LaTeX-compatible file: {self.output_dir / 'mdp_paper_latex.md'}")
        print(f"📄 PDF file: {self.output_dir / 'mdp_paper.pdf'}")
        print(f"🌐 HTML file: {self.output_dir / 'mdp_paper.html'}")
        print(f"📝 Word file: {self.output_dir / 'mdp_paper.docx'}")

        return True

    def validate_sections(self) -> bool:
        """Validate that all required sections exist and are readable."""
        required_sections = [
            "00_abstract.md",
            "01_introduction.md",
            "02_background.md",
            "03_methodology.md",
            "04_core_components.md",
            "05_implementation.md",
            "06_evaluation.md",
            "07_results.md",
            "08_discussion.md",
            "09_conclusion.md",
            "10_future_work.md",
            "12_references.md",
            "11_code.md"
        ]

        missing_sections = []
        empty_sections = []
        unreadable_sections = []

        for section in required_sections:
            section_path = self.paper_dir / section
            if not section_path.exists():
                missing_sections.append(section)
            else:
                try:
                    with open(section_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if not content:
                        empty_sections.append(section)
                    else:
                        # Basic content validation - check for section structure
                        lines = content.split('\n')
                        has_header = any(line.startswith('# ') for line in lines)
                        if not has_header:
                            print(f"⚠ Warning: {section} may not have proper section header")
                except Exception as e:
                    unreadable_sections.append(f"{section} ({e})")

        # Report issues
        issues = []
        if missing_sections:
            issues.append(f"Missing: {', '.join(missing_sections)}")
        if empty_sections:
            issues.append(f"Empty: {', '.join(empty_sections)}")
        if unreadable_sections:
            issues.append(f"Unreadable: {', '.join(unreadable_sections)}")

        if issues:
            print("⚠ Section validation issues:")
            for issue in issues:
                print(f"  {issue}")
            return False

        print("✓ All required sections validated successfully")
        self._validated = True
        return True

    def validate_outputs(self) -> bool:
        """Validate that all output files were created successfully."""
        expected_files = [
            "mdp_paper.md",
            "mdp_paper_latex.md",
            "mdp_paper.pdf",
            "mdp_paper.html",
            "mdp_paper.docx"
        ]

        missing_files = []
        invalid_files = []

        for filename in expected_files:
            file_path = self.output_dir / filename
            if not file_path.exists():
                missing_files.append(filename)
            else:
                try:
                    # Basic validation - check file size is reasonable
                    size = file_path.stat().st_size
                    if size < 1000:  # Less than 1KB is likely invalid
                        invalid_files.append(f"{filename} ({size} bytes)")
                except Exception as e:
                    invalid_files.append(f"{filename} (error: {e})")

        if missing_files or invalid_files:
            if missing_files:
                print(f"⚠ Missing output files: {', '.join(missing_files)}")
            if invalid_files:
                print(f"⚠ Potentially invalid files: {', '.join(invalid_files)}")
            return False

        print("✓ All output files validated successfully")
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
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies without assembling"
    )

    args = parser.parse_args()

    assembler = PaperAssembler(args.paper_dir, args.output_dir)

    # Check dependencies first
    if not assembler._check_dependencies():
        print("❌ Missing dependencies. Install required tools and try again.")
        return 1

    # Validate sections
    if not assembler.validate_sections():
        print("❌ Validation failed. Cannot proceed with assembly.")
        return 1

    if args.validate_only:
        print("✅ All sections validated successfully!")
        return 0

    if args.check_deps:
        print("✅ All dependencies are available!")
        return 0

    # Assemble based on format
    success = False
    try:
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
    except Exception as e:
        print(f"❌ Assembly failed with error: {e}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
