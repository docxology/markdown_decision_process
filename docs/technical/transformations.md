# Document Transformations

The transformations module in MDP provides a systematic approach to modifying Markdown documents for optimization and standardization. This technical documentation covers the design, implementation, and advanced usage of the transformation system.

## Core Architecture

The transformations system follows a well-defined architecture based on:

1. **Strategy Pattern**: Each transformation is implemented as a separate strategy class
2. **Command Pattern**: Transformations are executable objects that encapsulate all the logic needed
3. **Composite Pattern**: Transformations can be combined into pipelines for complex optimizations

## Base Transformation Class

All transformations inherit from the abstract `Transformation` base class:

```python
class Transformation:
    """Base class for document transformations."""
    
    def apply(self, document, output_path=None):
        """
        Apply the transformation to a document.
        
        Args:
            document: MarkdownDocument instance
            output_path: Optional path to save the transformed document
            
        Returns:
            The transformed document
        """
        # This is an abstract method that must be implemented by subclasses
        raise NotImplementedError("Subclasses must implement apply()")
    
    def is_applicable(self, document):
        """
        Check if the transformation is applicable to the document.
        
        Args:
            document: MarkdownDocument instance
            
        Returns:
            bool: True if the transformation can be applied
        """
        # Default implementation always returns True
        return True
```

## Transformation Types

### Heading Level Transformation

Adjusts heading levels to maintain proper hierarchy:

```python
class HeadingLevelTransformation(Transformation):
    """
    Normalize or adjust heading levels in a document.
    """
    
    def __init__(self, min_level=1, increment=0):
        """
        Initialize the transformation.
        
        Args:
            min_level: Minimum heading level (1-6)
            increment: Value to add to all heading levels (can be negative)
        """
        self.min_level = min_level
        self.increment = increment
        
    def apply(self, document, output_path=None):
        """Apply heading level adjustments."""
        headings = document.get_headings()
        content = document.get_content()
        
        # Sort headings by position in reverse order (to avoid offset issues)
        headings.sort(key=lambda h: h.get('position', 0), reverse=True)
        
        for heading in headings:
            level = heading.get('level', 1)
            new_level = max(self.min_level, level + self.increment)
            
            # Replace heading markdown with new level
            old_heading = '#' * level + ' ' + heading.get('text', '')
            new_heading = '#' * new_level + ' ' + heading.get('text', '')
            
            content = content.replace(old_heading, new_heading)
            
        # Update document
        document.set_content(content)
        
        # Save if output path is provided
        if output_path:
            document.save(output_path)
            
        return document
```

### List Format Transformation

Converts between ordered and unordered lists and normalizes bullet styles:

```python
class ListFormatTransformation(Transformation):
    """
    Transform list formatting (bullets, numbering, etc.).
    """
    
    def __init__(self, target_type="unordered", bullet_style="-"):
        """
        Initialize the transformation.
        
        Args:
            target_type: Target list type ("ordered" or "unordered")
            bullet_style: Bullet style for unordered lists ("-", "*", "+")
        """
        self.target_type = target_type
        self.bullet_style = bullet_style
        
    def apply(self, document, output_path=None):
        """Apply list formatting transformation."""
        # Implementation details...
```

### Code Block Format Transformation

Standardizes code block language specifications:

```python
class CodeBlockFormatTransformation(Transformation):
    """
    Transform code block formatting (language specifiers, etc.).
    """
    
    def __init__(self, target_language=None, new_language=None):
        """
        Initialize the transformation.
        
        Args:
            target_language: Language specifier to target (or None for all)
            new_language: New language specifier to use
        """
        self.target_language = target_language
        self.new_language = new_language
        
    def apply(self, document, output_path=None):
        """Apply code block transformation."""
        # Implementation details...
```

## Transformation Pipeline

The `TransformationPipeline` class combines multiple transformations into a single, unified process:

```python
class TransformationPipeline(Transformation):
    """
    A pipeline of transformations to be applied in sequence.
    """
    
    def __init__(self, transformations=None):
        """
        Initialize the pipeline.
        
        Args:
            transformations: List of Transformation instances
        """
        self.transformations = transformations or []
        
    def add_transformation(self, transformation):
        """Add a transformation to the pipeline."""
        self.transformations.append(transformation)
        
    def apply(self, document, output_path=None):
        """
        Apply all transformations in sequence.
        
        Args:
            document: MarkdownDocument instance
            output_path: Optional path to save the transformed document
            
        Returns:
            The transformed document
        """
        # Create a copy of the document to avoid modifying the original
        doc_copy = copy.deepcopy(document)
        
        # Apply each transformation in sequence
        for transformation in self.transformations:
            if transformation.is_applicable(doc_copy):
                doc_copy = transformation.apply(doc_copy)
                
        # Save the final result if output path is provided
        if output_path:
            doc_copy.save(output_path)
            
        return doc_copy
```

## Implementation Techniques

### Pattern Matching

Many transformations use regular expressions for pattern matching:

```python
def _transform_ordered_to_unordered(self, content):
    """Convert ordered lists to unordered lists."""
    pattern = r'^(\s*)(\d+\.\s+)(.+)$'
    replacement = r'\1' + self.bullet_style + r' \3'
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)
```

### Structure-Based Transformation

Some transformations operate on the document structure rather than the raw text:

```python
def apply(self, document, output_path=None):
    """Apply table transformation."""
    tables = document.get_tables()
    content = document.get_content()
    
    for table in tables:
        # Get table content and position
        table_content = table.get('content', '')
        table_position = table.get('position', 0)
        
        # Transform table structure
        new_table_content = self._transform_table(table)
        
        # Replace in content
        content = content.replace(table_content, new_table_content)
        
    # Update document
    document.set_content(content)
    
    # Save if output path is provided
    if output_path:
        document.save(output_path)
        
    return document
```

### Text Style Transformations

Text style transformations handle emphasis formatting:

```python
class TextStyleTransformation(Transformation):
    """
    Normalize text emphasis styles.
    """
    
    def __init__(self, bold_style="**", italic_style="*"):
        """
        Initialize the transformation.
        
        Args:
            bold_style: Target bold style ("**" or "__")
            italic_style: Target italic style ("*" or "_")
        """
        self.bold_style = bold_style
        self.italic_style = italic_style
        
    def apply(self, document, output_path=None):
        """Apply text style transformation."""
        content = document.get_content()
        
        # Transform bold style
        if self.bold_style == "**":
            content = re.sub(r'__(.+?)__', r'**\1**', content)
        else:
            content = re.sub(r'\*\*(.+?)\*\*', r'__\1__', content)
            
        # Transform italic style
        if self.italic_style == "*":
            content = re.sub(r'_([^_]+)_', r'*\1*', content)
        else:
            content = re.sub(r'\*([^\*]+)\*', r'_\1_', content)
            
        # Update document
        document.set_content(content)
        
        # Save if output path is provided
        if output_path:
            document.save(output_path)
            
        return document
```

## Advanced Usage

### Extending the System

New transformations can be created by extending the base class:

```python
class CustomTransformation(Transformation):
    """Custom transformation for specific needs."""
    
    def __init__(self, custom_param):
        self.custom_param = custom_param
        
    def apply(self, document, output_path=None):
        # Custom transformation logic
        content = document.get_content()
        
        # Apply transformation
        transformed_content = self._custom_transform(content)
        
        # Update document
        document.set_content(transformed_content)
        
        # Save if output path is provided
        if output_path:
            document.save(output_path)
            
        return document
        
    def _custom_transform(self, content):
        # Implementation of the custom transformation
        pass
```

### Integration with PolicyOptimizer

Transformations can be used as actions in the PolicyOptimizer framework:

```python
from mdp import PolicyOptimizer, TransformationPipeline
from mdp.transformations import HeadingLevelTransformation, ListFormatTransformation

# Create a pipeline of transformations
pipeline = TransformationPipeline([
    HeadingLevelTransformation(min_level=1),
    ListFormatTransformation(target_type="unordered")
])

# Create a policy optimizer with custom rewards
optimizer = PolicyOptimizer(
    reward_weights={"readability": 0.7, "information_density": 0.3}
)

# Use the pipeline as part of the optimization process
optimized_doc = optimizer.transform_with_pipeline(document, pipeline)
```

## Performance Considerations

### Efficiency

Different transformations have different computational complexities:

- **HeadingLevelTransformation**: O(h) where h is the number of headings
- **ListFormatTransformation**: O(l) where l is the number of list items
- **TextStyleTransformation**: O(n) where n is the document size due to regex operations

### Optimizations

To improve performance for large documents:

1. Use structure-based transformations where possible (faster than regex)
2. Apply transformations selectively based on document needs
3. Combine related transformations to minimize document parsing
4. Use incremental transformations for very large documents

## Use Cases

- **Style Standardization**: Ensure consistent formatting across documentation
- **Accessibility Improvements**: Transform documents for better readability
- **Format Conversion**: Prepare documents for different publishing platforms
- **SEO Optimization**: Improve structure for better search engine ranking
- **Content Adaptation**: Modify content for different audience needs 