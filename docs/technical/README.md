# Technical Documentation

This directory contains detailed technical documentation for implemented features of the Markdown Decision Process framework. As features are completed from the [project roadmap](../ROADMAP.md), corresponding documentation is added here to provide comprehensive information about the implementation, API, and usage.

## Core Engine Components

- [MarkChain](markchain.md) - Implementation of Markov models for markdown state transitions
- [Policy Optimization](policy_optimization.md) - Techniques for optimizing document transformations
- [State Space Analysis](state_space.md) - Graph-based analysis of markdown structure
- [Belief Update Mechanisms](belief_updates.md) - Semantic understanding and uncertainty quantification
- [Agent Architecture](agent_architecture.md) - Decision-making framework and learning mechanisms

## Integration Technologies

- [Language Model Integration](language_models.md) - Integration with LLMs and embedding models
- [Document Processing](document_processing.md) - Parser implementations and conversions
- [Content Enrichment](content_enrichment.md) - Media and data integration capabilities

## Transformations

- [Document Structure](transformations/structure.md) - Organizational and navigation transformations
- [Content Intelligence](transformations/intelligence.md) - Summarization and expansion capabilities
- [Style Transformations](transformations/style.md) - Tone, readability, and formatting adjustments

## Implementation Process

When a feature moves from the roadmap to implementation:

1. The feature is removed from the [ROADMAP.md](../ROADMAP.md) file
2. Corresponding implementation code is added to the appropriate module in `src/mdp/`
3. Tests are added to the `tests/` directory to validate the implementation
4. Technical documentation is added to this directory to describe the implementation details
5. Usage examples are added to the `examples/` directory

This process ensures that all implemented features are properly documented, tested, and exemplified for users. 