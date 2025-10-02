# Academic Paper - AI Agent Writing Guide

## Overview

This directory contains a modular academic paper describing the Markdown Decision Process framework. The paper is designed for submission to conferences or journals in machine learning, natural language processing, or software engineering.

## Paper Structure

```
paper/
├── 00_abstract.md          # Paper abstract and keywords
├── 01_introduction.md      # Problem statement and contributions
├── 02_background.md        # Related work and theoretical foundations
├── 03_methodology.md       # System architecture and approach
├── 04_core_components.md   # Detailed component descriptions
├── 05_implementation.md    # Implementation details and algorithms
├── 06_evaluation.md        # Experimental design and setup
├── 07_results.md # Experimental results and findings
├── 08_discussion.md        # Interpretation and implications
├── 09_conclusion.md        # Summary and impact
├── 10_future_work.md       # Research directions and extensions
├── 11_references.md        # Bibliography and citations
├── assemble_paper.py       # Paper assembly script
├── outputs/                # Generated paper files
│   ├── mdp_paper.md        # Complete markdown
│   ├── mdp_paper.pdf       # PDF version
│   ├── mdp_paper.html      # HTML version
│   └── mdp_paper.docx      # Word document
└── README.md               # Paper documentation
```

## Modular Paper Design

### Why Modular?

1. **Parallel Development**: Multiple sections can be edited simultaneously
2. **Version Control**: Granular tracking of changes per section
3. **Flexible Assembly**: Generate different versions (conference vs. journal)
4. **Easy Review**: Reviewers can focus on specific sections
5. **Reusability**: Sections can be adapted for other papers

### Section Responsibilities

**00_abstract.md** - Paper Summary
- 150-250 words
- Key contributions (3-5 bullet points)
- Main results with numbers
- Keywords (5-8 terms)

**01_introduction.md** - Motivation and Overview
- Problem statement
- Limitations of existing approaches
- Proposed solution overview
- Key contributions (detailed)
- Paper organization

**02_background.md** - Context and Related Work
- Theoretical foundations (MDPs, POMDPs, Active Inference)
- Document processing approaches
- Related frameworks and tools
- Positioning of our work

**03_methodology.md** - Technical Approach
- Formal problem definition
- Architecture overview
- Mathematical formulation
- Design principles

**04_core_components.md** - System Components
- MarkChain: Generative models
- StateSpace: Structural analysis
- PolicyOptimizer: RL-based optimization
- BeliefUpdater: Semantic inference
- Integration and interplay

**05_implementation.md** - Implementation Details
- Software architecture
- Key algorithms
- Data structures
- Performance optimizations
- Plugin system

**06_evaluation.md** - Experimental Setup
- Datasets and preparation
- Evaluation metrics
- Baseline comparisons
- Statistical testing methodology

**07_results.md** - Experimental Results and Findings
- Quantitative results with statistics
- Qualitative analysis
- Ablation studies
- Limitations and threats to validity

**08_discussion.md** - Discussion and Interpretation
- Contribution summary
- Theoretical significance
- Practical implications
- Final synthesis

**09_conclusion.md** - Summary and Impact
- Contribution summary
- Theoretical significance
- Practical implications
- Final synthesis

**10_future_work.md** - Future Directions
- Theoretical extensions
- Algorithmic improvements
- Application domains
- Research opportunities

**11_references.md** - Bibliography and Citations

## Writing Guidelines

### Academic Writing Style

1. **Precise and Formal**: Use technical terminology accurately
2. **Evidence-Based**: Support claims with data or citations
3. **Balanced**: Acknowledge limitations honestly
4. **Clear**: Explain complex concepts accessibly
5. **Consistent**: Maintain terminology throughout

### MDP Theme Integration

The paper maintains the MDP conceptual framework while being accessible:

**Good Examples**:
```markdown
- "We model documents as Markov Decision Processes where..."
- "State transitions capture the probabilistic structure of..."
- "The belief updater handles semantic uncertainty through..."
```

**Avoid**:
```markdown
- "We use a cool trick to..." (too informal)
- "The system works by magic..." (imprecise)
- Overusing the theme where it obscures meaning
```

### Mathematical Notation

Use consistent notation throughout:

- **States**: $s \in S$ or $s_t$ for time-indexed states
- **Actions**: $a \in A$
- **Transitions**: $P(s'|s,a)$ or $T(s,a,s')$
- **Rewards**: $R(s,a,s')$ or $r_t$
- **Beliefs**: $b(s)$ or $b_t(s)$
- **Policies**: $\pi(a|s)$ or $\pi^*(s)$
- **Value Functions**: $V(s)$ or $V^\pi(s)$

### Citations

```markdown
# Inline citations
- Single: [@sutton2018]
- Multiple: [@sutton2018; @kaelbling1998]
- Parenthetical: "MDPs provide a framework (Sutton & Barto, 2018)"

# Reference formatting
**[1]** Sutton, R. S., & Barto, A. G. (2018). *Reinforcement learning: An introduction*. MIT press.
```

## Editing Workflow

### 1. Edit Individual Sections

```bash
# Work on specific section
code paper/03_methodology.md

# Check markdown validity
markdownlint paper/03_methodology.md

# Preview changes
python paper/assemble_paper.py --format markdown
open paper/outputs/mdp_paper.md
```

### 2. Assemble Complete Paper

```bash
# Generate all formats
python paper/assemble_paper.py --format all

# Generate specific format
python paper/assemble_paper.py --format pdf
python paper/assemble_paper.py --format html

# Validate sections first
python paper/assemble_paper.py --validate-only
```

### 3. Review and Iterate

```bash
# Check word count per section
python paper/count_words.py

# Check citation coverage
python paper/check_citations.py

# Verify equations render correctly
python paper/check_equations.py
```

## Quality Checklist

### Content Quality

- [ ] All claims are supported by evidence or citations
- [ ] Mathematical notation is consistent
- [ ] Figures and tables have descriptive captions
- [ ] Code examples are correct and runnable
- [ ] Results include statistical significance
- [ ] Limitations are honestly acknowledged
- [ ] Contributions are clearly stated

### Writing Quality

- [ ] Clear topic sentences for each paragraph
- [ ] Smooth transitions between sections
- [ ] No grammatical errors (run through Grammarly)
- [ ] Technical terms defined on first use
- [ ] Acronyms expanded on first use
- [ ] Consistent voice and tense

### Format Quality

- [ ] All sections present and complete
- [ ] References properly formatted
- [ ] Equations numbered and referenced
- [ ] Figures numbered and referenced
- [ ] Code blocks have syntax highlighting
- [ ] Links work correctly

## Assembly Script Usage

### Basic Usage

```bash
# Validate sections
python assemble_paper.py --validate-only

# Create markdown
python assemble_paper.py --format markdown

# Create PDF (requires LaTeX)
python assemble_paper.py --format pdf

# Create all formats
python assemble_paper.py --format all
```

### Advanced Options

```python
# In assemble_paper.py

class PaperAssembler:
    def __init__(self, paper_dir=None, output_dir=None):
        self.paper_dir = Path(paper_dir or Path(__file__).parent)
        self.output_dir = Path(output_dir or self.paper_dir / "outputs")
        
        # Customize metadata
        self.title = "Your Title"
        self.authors = ["Author 1", "Author 2"]
        self.affiliation = "Your Institution"
    
    def create_conference_version(self):
        """Create conference-ready version (page limit)."""
        # Filter sections, adjust formatting
        pass
    
    def create_journal_version(self):
        """Create extended journal version."""
        # Include all sections, detailed appendices
        pass
```

### Custom Templates

```python
# For custom PDF styling
def create_pdf_paper(self, template='academic'):
    """Create PDF with custom template."""
    templates = {
        'academic': 'templates/academic.tex',
        'conference': 'templates/conference.tex',
        'journal': 'templates/journal.tex'
    }
    
    cmd = [
        'pandoc',
        self.markdown_file,
        '--template', templates[template],
        '-o', self.output_dir / 'paper.pdf'
    ]
    
    subprocess.run(cmd)
```

## Submission Preparation

### Conference Submission

1. **Check Requirements**:
   - Page limit (usually 8-10 pages)
   - Format (PDF, specific template)
   - Anonymity (remove author info)
   - Supplementary material limits

2. **Prepare Files**:
   ```bash
   # Generate anonymized version
   python assemble_paper.py --format pdf --anonymous
   
   # Create supplementary material
   python create_supplementary.py
   ```

3. **Final Checks**:
   - [ ] PDF renders correctly
   - [ ] All figures visible
   - [ ] References complete
   - [ ] Page limit respected
   - [ ] Anonymization complete

### Journal Submission

1. **Extended Version**:
   ```bash
   # Create full version with appendices
   python assemble_paper.py --format pdf --journal
   ```

2. **Additional Materials**:
   - Cover letter
   - Highlights (3-5 bullet points)
   - Graphical abstract
   - Author biographies

3. **Formatting**:
   - Follow journal template
   - Include author information
   - Add acknowledgments
   - Declare conflicts of interest

## Collaboration Workflow

### Multi-Author Editing

```bash
# Create feature branch for section
git checkout -b edit/methodology

# Edit section
code paper/03_methodology.md

# Commit changes
git add paper/03_methodology.md
git commit -m "docs: Improve methodology section - add algorithm details"

# Push and create PR
git push origin edit/methodology
```

### Review Process

```markdown
# PR Template for Paper Sections

## Section Edited
- [ ] 03_methodology.md

## Changes Made
- Added detailed algorithm descriptions
- Included complexity analysis
- Updated mathematical notation for consistency

## Review Checklist
- [ ] Technical accuracy verified
- [ ] Citations added/updated
- [ ] Figures/equations numbered correctly
- [ ] Consistent with other sections
- [ ] No grammatical errors

## Related Issues
Closes #42 (Add algorithm complexity analysis)
```

## Version Management

### Paper Versions

```python
# In paper/versions.py

VERSIONS = {
    'v1.0': {
        'date': '2024-01-15',
        'venue': 'NeurIPS 2024 submission',
        'status': 'submitted',
        'changes': 'Initial submission'
    },
    'v1.1': {
        'date': '2024-03-20',
        'venue': 'NeurIPS 2024 revision',
        'status': 'revised',
        'changes': 'Addressed reviewer comments'
    },
    'v2.0': {
        'date': '2024-06-10',
        'venue': 'JMLR extended version',
        'status': 'in_preparation',
        'changes': 'Extended journal version with appendices'
    }
}
```

### Changelog

```markdown
# paper/CHANGELOG.md

## [1.1] - 2024-03-20 (NeurIPS Revision)

### Reviewer 1 Responses
- Added ablation study for belief updater (Section 7.3)
- Clarified computational complexity (Section 5.4)
- Expanded related work comparison (Section 2.3)

### Reviewer 2 Responses
- Added statistical significance tests (Section 6.4)
- Improved figure quality (Figures 3-5)
- Addressed scalability concerns (Section 8.2)

### Reviewer 3 Responses
- Clarified novelty vs. existing work (Section 1.3)
- Added real-world case study (Section 7.5)
```

## LaTeX/PDF Troubleshooting

### Common Issues

**Issue**: PDF generation fails
```bash
# Check if pandoc is installed
pandoc --version

# Check if LaTeX is installed
pdflatex --version

# Try basic generation first
pandoc paper/outputs/mdp_paper.md -o test.pdf
```

**Issue**: Equations don't render
```bash
# Ensure MathJax or LaTeX packages installed
# Use explicit math delimiters
$$
\text{Equation here}
$$
```

**Issue**: Code blocks not formatted
```python
# In assembly script, add:
'--listings',  # Enable code highlighting
'--highlight-style', 'tango'
```

## Citation Management

### BibTeX Integration

```python
# Generate BibTeX from references
def generate_bibtex():
    """Convert references.md to BibTeX format."""
    refs = parse_references('12_references.md')
    
    bibtex_entries = []
    for ref in refs:
        entry = f"""@{ref.type}{{{ref.key},
  author = {{{ref.authors}}},
  title = {{{ref.title}}},
  year = {{{ref.year}}},
  ...
}}"""
        bibtex_entries.append(entry)
    
    return '\n\n'.join(bibtex_entries)
```

### Citation Verification

```python
def verify_citations():
    """Check all citations are in references."""
    # Extract citations from all sections
    citations = extract_citations('paper/')
    
    # Load references
    references = load_references('12_references.md')
    
    # Find missing
    missing = set(citations) - set(references.keys())
    
    if missing:
        print(f"Missing references: {missing}")
    else:
        print("All citations verified ✓")
```

## Best Practices

### For AI Agents

1. **Maintain Consistency**: Use established terminology and notation
2. **Preserve Structure**: Don't reorganize without discussion
3. **Support Claims**: Add citations for new claims
4. **Test Changes**: Run assembly script after edits
5. **Document Decisions**: Explain significant changes in commits

### For Reviewers

1. **Check Technical Accuracy**: Verify algorithms and math
2. **Ensure Clarity**: Complex concepts explained well?
3. **Verify Results**: Numbers consistent across sections?
4. **Test Assembly**: Does the paper build correctly?
5. **Style Consistency**: Writing style uniform?

---

*This paper itself is a document in our MDP framework - each edit is an action, each version is a state, and we optimize toward the reward of publication and impact!* 🎓
