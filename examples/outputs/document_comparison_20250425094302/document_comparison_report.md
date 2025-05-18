# Markdown Document Comparison Report

## Overview

This report compares 4 Markdown documents based on their structure (state space) and semantic content (beliefs).

## Documents Analyzed

| Document | States | Transitions | Dominant Semantic Class |
|----------|--------|-------------|-------------------------|
| research_paper | 0 | 10 | explanation (0.48) |
| document_with_markers | 0 | 5 | explanation (0.40) |
| technical_doc | 0 | 14 | explanation (0.45) |
| blog_post | 0 | 5 | explanation (0.48) |

## Semantic Beliefs Comparison

The following table shows the semantic belief values for each document:

| Document | Technical | Conceptual | Instructional | Informational | Persuasive |
|----------|-----------|------------|---------------|---------------|------------|
| research_paper | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| document_with_markers | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| technical_doc | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| blog_post | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

## Document Similarity

The following pairs of documents have the highest semantic similarity:

- **research_paper** and **blog_post**: 0.98
- **research_paper** and **document_with_markers**: 0.98
- **document_with_markers** and **blog_post**: 0.96
- **technical_doc** and **blog_post**: 0.94
- **research_paper** and **technical_doc**: 0.93

## Visualizations

The following visualizations are available in the output directory:

- **research_paper**:
  - State Space: [document_comparison_20250425094302/research_paper_state_space.png](document_comparison_20250425094302/research_paper_state_space.png)
  - Belief Heatmap: [document_comparison_20250425094302/research_paper_beliefs.png](document_comparison_20250425094302/research_paper_beliefs.png)
- **document_with_markers**:
  - State Space: [document_comparison_20250425094302/document_with_markers_state_space.png](document_comparison_20250425094302/document_with_markers_state_space.png)
  - Belief Heatmap: [document_comparison_20250425094302/document_with_markers_beliefs.png](document_comparison_20250425094302/document_with_markers_beliefs.png)
- **technical_doc**:
  - State Space: [document_comparison_20250425094302/technical_doc_state_space.png](document_comparison_20250425094302/technical_doc_state_space.png)
  - Belief Heatmap: [document_comparison_20250425094302/technical_doc_beliefs.png](document_comparison_20250425094302/technical_doc_beliefs.png)
- **blog_post**:
  - State Space: [document_comparison_20250425094302/blog_post_state_space.png](document_comparison_20250425094302/blog_post_state_space.png)
  - Belief Heatmap: [document_comparison_20250425094302/blog_post_beliefs.png](document_comparison_20250425094302/blog_post_beliefs.png)
- **Document Similarity Matrix**: [document_comparison_20250425094302/document_similarity_matrix.png](document_comparison_20250425094302/document_similarity_matrix.png)

## Analysis Methodology

This comparison uses two primary methods of analysis:

1. **State Space Analysis**: Represents the document structure as states and transitions between markdown elements.
2. **Belief Analysis**: Uses a belief updater to estimate the semantic content of each document based on predefined semantic classes.

*Report generated on 2025-04-25 09:43:08*
