# Contributing to Markdown Decision Process

We welcome contributions to the Markdown Decision Process (MDP) project! This document provides guidelines for contributing code, documentation, and ideas.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Feature Requests](#feature-requests)
- [Bug Reports](#bug-reports)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please ensure all interactions are professional and constructive.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/markdown_decision_process.git`
3. Create a branch for your work: `git checkout -b feature/your-feature-name`

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Coding Standards

We follow standard Python best practices:

- Code should be formatted with Black
- Imports should be sorted with isort
- Type hints should be used for all function definitions
- Functions and classes should have docstrings (Google style)
- Variable names should be descriptive
- Tests should be written for new features

## Pull Request Process

1. Update documentation for any changes to interfaces
2. Add or update tests as appropriate
3. Ensure all CI checks pass
4. Request a review from a maintainer
5. Incorporate feedback from reviews
6. Once approved, a maintainer will merge your PR

## Feature Requests

Feature requests are welcome. Please submit them as issues with the "enhancement" label and include:

- A clear description of the feature
- The motivation for the feature
- Example use cases
- If possible, a rough sketch of the API design

## Bug Reports

When reporting bugs, please include:

- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, etc.)
- Possible solutions (if you have any ideas)

## Adding New Components

If you're adding a new major component to the MDP framework, consider these guidelines:

1. **Maintain the theme**: The component should maintain the playful connection between Markdown and Markov processes
2. **Follow existing patterns**: Look at the existing modules for design patterns
3. **Partial observability**: Consider how your component handles uncertainty
4. **Policy and rewards**: If applicable, define what "good" markdown looks like in your context
5. **Documentation**: Include a conceptual explanation in addition to API docs

## API Stability

As MDP is currently in alpha, APIs may change. When proposing changes that break backward compatibility:

1. Document the changes clearly
2. Provide migration paths where possible
3. Add deprecation warnings for one minor version before removing functionality

Thank you for contributing to Markdown Decision Process! 