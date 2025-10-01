# Markdown Decision Process Paper

This directory contains the modular sections of an academic paper describing the Markdown Decision Process framework.

## Overview

The paper is organized into modular sections that can be assembled into a complete academic paper. Each section focuses on a specific aspect of the framework:

- **00_abstract.md**: Paper abstract and keywords
- **01_introduction.md**: Problem statement and contributions
- **02_background.md**: Related work and theoretical foundations
- **03_methodology.md**: Theoretical foundations and architecture
- **04_core_components.md**: Detailed component descriptions
- **05_implementation.md**: Implementation details and technical considerations
- **06_evaluation.md**: Experimental evaluation and results
- **07_results_discussion.md**: Interpretation and implications
- **08_conclusion.md**: Summary and final remarks
- **09_future_work.md**: Future research directions
- **10_references.md**: Bibliography and citations

## Repository Information

**Repository:** https://github.com/docxology/markdown_decision_process
**Author:** Daniel Ari Friedman
**Email:** daniel@activeinference.institute

## Assembly and Compilation

### Using the Assembly Script

The easiest way to create the complete paper is using the provided assembly script:

```bash
# Validate all sections are present
python assemble_paper.py --validate-only

# Create paper in all formats
python assemble_paper.py --format all

# Create specific formats
python assemble_paper.py --format pdf
python assemble_paper.py --format html
python assemble_paper.py --format markdown
```

### Manual Assembly

If you prefer to assemble the paper manually:

1. Concatenate the section files in numerical order
2. Add appropriate front matter (title, authors, abstract)
3. Use Pandoc for format conversion:

```bash
# Combine sections
cat 0?_*.md > complete_paper.md

# Convert to PDF
pandoc complete_paper.md -o paper.pdf --pdf-engine=pdflatex

# Convert to HTML
pandoc complete_paper.md -o paper.html --self-contained

# Convert to Word
pandoc complete_paper.md -o paper.docx
```

## Output Formats

The assembly script can generate multiple output formats:

- **Markdown** (`.md`): Complete paper in Markdown format
- **PDF** (`.pdf`): Formatted academic paper (requires LaTeX)
- **HTML** (`.html`): Web-viewable version with styling
- **Word Document** (`.docx`): Microsoft Word compatible format
- **LaTeX** (`.tex`): LaTeX source for custom formatting

## Dependencies

For PDF generation, ensure you have:
- Pandoc: https://pandoc.org/
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)

For Word document generation:
- Pandoc (with Word support)

## Customization

### Modifying Sections

Each section can be edited independently. The assembly script will automatically include any changes when you regenerate the paper.

### Adding New Sections

To add a new section:

1. Create a file named with the pattern `XX_title.md` (e.g., `11_appendix.md`)
2. Update the assembly script if needed to include the new section
3. Run the assembly script to generate the updated paper

### Styling and Templates

For advanced formatting customization:

1. Create custom Pandoc templates in this directory
2. Modify the assembly script to use your templates
3. Add custom CSS for HTML output

## Paper Structure

The paper follows a standard academic structure:

1. **Abstract**: Overview of the framework and contributions
2. **Introduction**: Problem motivation and solution approach
3. **Background**: Related work and theoretical foundations
4. **Methodology**: Theoretical foundations and system architecture
5. **Core Components**: Detailed description of main components
6. **Implementation**: Technical implementation details
7. **Evaluation**: Experimental design and results
8. **Results & Discussion**: Interpretation and implications
9. **Conclusion**: Summary and impact
10. **Future Work**: Research directions and extensions
11. **References**: Bibliography and citations

## Contributing

When contributing to the paper:

1. Edit the relevant section file(s)
2. Run the assembly script to verify the complete paper
3. Check that all formats generate correctly
4. Update this README if you add new sections or change the structure

## Version Control

Each section is tracked separately in version control, allowing for:

- Independent review of specific sections
- Granular change tracking
- Collaborative editing of different parts
- Easy rollback of specific sections if needed

## Citation

If you reference this work, please cite as:

```bibtex
@software{mdp_framework,
  title={Markdown Decision Process (MDP): A Framework for Probabilistic Document Analysis and Optimization},
  author={Friedman, Daniel Ari},
  year={2023},
  url={https://github.com/docxology/markdown_decision_process}
}
```

## Support

For questions about the paper or framework:

- **Issues**: https://github.com/docxology/markdown_decision_process/issues
- **Discussions**: https://github.com/docxology/markdown_decision_process/discussions
- **Email**: daniel@activeinference.institute

---

*This paper describes ongoing research in probabilistic modeling and document processing. The Markdown Decision Process framework represents a novel approach to understanding and optimizing digital documents through the lens of decision theory and stochastic processes.*
