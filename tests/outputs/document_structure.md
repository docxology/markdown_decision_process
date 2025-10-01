# Document Structure Analysis

This file shows the structure extracted from the test document.

## Original Markdown

```markdown
# Test Document

This is a paragraph with some **important** information.

## Section 1
- Item 1
- Item 2

### Subsection
Some more text here.

```python
def test_function():
    return "Hello World"
```

## Section 2
This is another paragraph.

```

## Extracted Structure

### Section 1

**Header**: Test Document

**Level**: 1

**Content**:

```
# Test Document
```

### Section 2

**Header**: No header

**Level**: Unknown

**Content**:

```
This is a paragraph with some **important** information.
```

### Section 3

**Header**: Section 1

**Level**: 2

**Content**:

```
## Section 1
```

### Section 4

**Header**: No header

**Level**: Unknown

**Content**:

```
- Item 1
```

### Section 5

**Header**: No header

**Level**: Unknown

**Content**:

```
- Item 2
```

### Section 6

**Header**: Subsection

**Level**: 3

**Content**:

```
### Subsection
```

### Section 7

**Header**: No header

**Level**: Unknown

**Content**:

```
Some more text here.
```

### Section 8

**Header**: No header

**Level**: Unknown

**Content**:

```
```python
```

### Section 9

**Header**: No header

**Level**: Unknown

**Content**:

```
def test_function():
```

### Section 10

**Header**: No header

**Level**: Unknown

**Content**:

```
return "Hello World"
```

### Section 11

**Header**: No header

**Level**: Unknown

**Content**:

```
```
```

### Section 12

**Header**: Section 2

**Level**: 2

**Content**:

```
## Section 2
```

### Section 13

**Header**: No header

**Level**: Unknown

**Content**:

```
This is another paragraph.
```

