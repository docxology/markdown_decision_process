"""
Pytest configuration for the Markdown Decision Process test suite.

This file provides fixtures and configuration shared across test files.
"""

import pytest
import tempfile
from pathlib import Path

# Define consistent sample Markdown content for tests
SAMPLE_MARKDOWN = """# Test Document

This is a paragraph with some **important** information.

Another paragraph with additional content.

## Section 1

- List item 1
- List item 2

### Subsection

Some more text here.

```python
def test():
    return "Hello World"
```

## Section 2

This is another paragraph with the word paragraph repeated.
"""

COMPLEX_MARKDOWN = """# Complex Document Analysis

## Introduction

This document contains a variety of markdown elements for testing document analysis metrics.

## Methods

The analysis is performed using several approaches:

1. First approach with detailed explanation
2. Second approach using alternative methodology
   - With sub-methodology A
   - With sub-methodology B
3. Third approach combining previous methods

### Data Collection

Data was collected from multiple sources:

* Primary sources (interviews)
* Secondary sources (literature)
* Tertiary sources (metadata analysis)

## Results

The results indicated several key findings:

| Metric | Value | Significance |
|--------|-------|--------------|
| Metric A | 85.2 | High |
| Metric B | 42.7 | Medium |
| Metric C | 93.1 | Very High |

### Statistical Analysis

```r
# Example R code
results <- analyze(data)
significance <- test_significance(results)
```

## Discussion

The findings suggest a strong correlation between variables X and Y, contrary to previous studies by Smith et al. (2018).

### Limitations

Several limitations must be acknowledged:

1. Sample size constraints
2. Geographical limitations
3. Temporal factors

## Conclusion

In conclusion, this analysis demonstrates the effectiveness of the proposed method and suggests directions for future research.

## References

1. Smith, J. (2018). Previous analysis methods. Journal of Analysis, 23(4), 45-67.
2. Johnson, A. (2020). Modern approaches to data collection. Research Methods Today, 15(2), 123-145.
"""

@pytest.fixture
def sample_markdown():
    """Fixture to provide consistent sample Markdown content."""
    return SAMPLE_MARKDOWN

@pytest.fixture
def complex_markdown():
    """Fixture to provide consistent complex Markdown content."""
    return COMPLEX_MARKDOWN

@pytest.fixture
def sample_document_file():
    """Create a temporary markdown file and return its path."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
        tmp.write(SAMPLE_MARKDOWN)
        tmp_path = Path(tmp.name)
    
    yield tmp_path
    
    # Cleanup
    if tmp_path.exists():
        tmp_path.unlink()

@pytest.fixture
def complex_document_file():
    """Create a temporary complex markdown file and return its path."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
        tmp.write(COMPLEX_MARKDOWN)
        tmp_path = Path(tmp.name)
    
    yield tmp_path
    
    # Cleanup
    if tmp_path.exists():
        tmp_path.unlink() 