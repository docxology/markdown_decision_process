# Markdown Decision Process Paper

This directory contains the modular sections of an academic paper describing the Markdown Decision Process framework.

## Evaluation evidence status

The corrected active source withdraws unsupported numerical tables, participant-study results and model/statistical comparisons. Section 06 is a prospective evaluation protocol; Section 07 reports the implementation/evidence boundary. Historical GPT-2 identity remains unresolved. See [Evaluation evidence review](EVALUATION_EVIDENCE.md). Previously generated files in `outputs/` are historical artifacts and do not contain this correction; assemble the modular sources into a new review-output directory without replacing those originals. The evidence review is required and included in the assembled Markdown and LaTeX-compatible Markdown.

## Overview

The paper is organized into modular sections that can be assembled into a complete academic paper. Each section focuses on a specific aspect of the framework:

- **00_abstract.md**: Paper abstract and keywords
- **01_introduction.md**: Problem statement and contributions
- **02_background.md**: Related work and theoretical foundations
- **03_methodology.md**: Theoretical foundations and architecture
- **04_core_components.md**: Detailed component descriptions
- **05_implementation.md**: Implementation details and technical considerations
- **06_evaluation.md**: Prospective evaluation protocol and evidence requirements
- **07_results.md**: Implementation evidence and limits on results
- **08_discussion.md**: Interpretation and implications
- **09_conclusion.md**: Summary and final remarks
- **10_future_work.md**: Future research directions
- **11_code.md**: Implemented source pointers and a minimal structural example
- **12_references.md**: Bibliography and citations

## Repository Information

**Repository:** https://github.com/docxology/markdown_decision_process
**Author:** Daniel Ari Friedman
**Email:** daniel@activeinference.institute

## Assembly and Compilation

### Using the Assembly Script

Run from the repository root. Choose a new output directory for each review;
previous files in `paper/outputs/` remain historical artifacts.

```bash
# Validate sections and the evidence-review appendix; no TeX dependency
python paper/assemble_paper.py --validate-only --output-dir /path/to/new-review-output

# Assemble the corrected draft without requiring a PDF toolchain
python paper/assemble_paper.py --format markdown --output-dir /path/to/new-review-output

# Other formats require the appropriate local tools
python paper/assemble_paper.py --format html --output-dir /path/to/new-review-output
python paper/assemble_paper.py --format pdf --output-dir /path/to/new-review-output
```

Use the assembler rather than a filename glob: numbered globs can omit the
code supplement, references and unnumbered evidence review. The assembler
preserves the correction's draft status and labels the existing DOI as a
historical publication. Successful assembly checks file structure; it does not
verify research data or establish a new publication version.

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
7. **Evaluation**: Prospective experimental design and evidence requirements
8. **Results**: Implementation evidence and results boundary
9. **Discussion**: Interpretation and implications
10. **Conclusion**: Summary and impact
11. **Future Work**: Research directions and extensions
12. **References**: Bibliography and citations

## Contributing

When contributing to the paper:

1. Edit the relevant section file(s)
2. Run the assembly script to verify the complete paper
3. Check the requested formats in the new review-output directory and report unavailable tools explicitly
4. Update this README if you add new sections or change the structure

## Version Control

Each section is tracked separately in version control, allowing for:

- Independent review of specific sections
- Granular change tracking
- Collaborative editing of different parts
- Easy rollback of specific sections if needed

## Citation

The corrected source is a review draft, not a new deposited edition. Cite the
specific Git commit when discussing this correction. The [historical 2025
publication](https://doi.org/10.5281/zenodo.17244387) retains its original DOI;
its deposited files do not include the corrected source revision.

## Support

For questions about the paper or framework:

- **Issues**: https://github.com/docxology/markdown_decision_process/issues
- **Discussions**: https://github.com/docxology/markdown_decision_process/discussions
- **Email**: daniel@activeinference.institute

---

*This paper describes a software prototype and prospective research. Future empirical claims require the source-bound evidence and review listed in EVALUATION_EVIDENCE.md.*
