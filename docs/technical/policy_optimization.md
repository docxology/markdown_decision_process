# Policy Optimization for Markdown Documents

The `PolicyOptimizer` class in MDP implements a strategy-based approach to optimize markdown documents for quality, clarity, and effectiveness. Drawing from the reinforcement learning concept of policy optimization, it attempts to find an optimal sequence of transformations that maximizes document quality.

## Conceptual Framework

In the Markdown Decision Process framework, we approach document optimization as a policy optimization problem:

- **States**: Different versions of a document after transformations
- **Actions**: Document transformations that can be applied
- **Reward Function**: Quality metrics that determine document goodness
- **Policy**: Strategy for selecting transformations to apply

The optimization process seeks to find a policy that maximizes the expected reward (document quality).

## Implementation Details

### Reward Functions

Reward functions measure document quality across different dimensions:

```python
class DocumentQuality:
    """Evaluates document quality along multiple dimensions."""
    
    def __init__(self):
        self.metrics = {
            "readability": self._readability_score,
            "information_density": self._information_density_score,
            "structure_clarity": self._structure_clarity_score,
            "content_coherence": self._content_coherence_score
        }
    
    def analyze_document(self, document):
        """Calculate quality metrics for a document."""
        metrics = {}
        
        # Extract document structure
        structure = document.get_structure()
        
        # Calculate individual metrics
        for name, func in self.metrics.items():
            metrics[name] = func(structure)
            
        # Calculate overall score (weighted average)
        overall_score = sum(metrics.values()) / len(metrics)
        metrics["overall_score"] = overall_score
        
        return metrics
        
    def _readability_score(self, structure):
        """Calculate readability score based on sentence length, paragraph length, etc."""
        # Implementation details...
        
    def _information_density_score(self, structure):
        """Calculate information density based on content-to-markup ratio."""
        # Implementation details...
        
    def _structure_clarity_score(self, structure):
        """Calculate structure clarity based on heading hierarchy, list nesting, etc."""
        # Implementation details...
        
    def _content_coherence_score(self, structure):
        """Calculate content coherence based on topic consistency, flow, etc."""
        # Implementation details...
```

### Transformation Selection

The `PolicyOptimizer` selects transformations based on their expected reward improvement:

```python
class PolicyOptimizer:
    """Optimizes document quality through transformation selection."""
    
    def __init__(self, reward_weights=None, custom_rewards=None):
        """
        Initialize the policy optimizer.
        
        Args:
            reward_weights: Dictionary mapping reward names to weights
            custom_rewards: Dictionary mapping custom reward names to functions
        """
        self.document_quality = DocumentQuality()
        
        # Default reward weights
        self.reward_weights = reward_weights or {
            "readability": 0.4,
            "information_density": 0.3,
            "structure_clarity": 0.2,
            "content_coherence": 0.1
        }
        
        # Add custom reward functions
        if custom_rewards:
            for name, func in custom_rewards.items():
                self.document_quality.metrics[name] = func
                if name not in self.reward_weights:
                    self.reward_weights[name] = 0.5  # Default weight for custom rewards
```

### Optimization Process

The core optimization process evaluates potential transformations and selects the best ones:

```python
def transform(self, document, iterations=3):
    """
    Transform a document to maximize reward.
    
    Args:
        document: MarkdownDocument instance
        iterations: Number of optimization iterations
        
    Returns:
        Optimized document
    """
    # Create a copy to avoid modifying the original
    current_doc = copy.deepcopy(document)
    
    # Get initial quality metrics
    current_metrics = self.document_quality.analyze_document(current_doc)
    current_score = self._calculate_weighted_score(current_metrics)
    
    # Optimization iterations
    for i in range(iterations):
        best_transformation = None
        best_score = current_score
        
        # Evaluate potential transformations
        for transformation in self._get_candidate_transformations(current_doc):
            # Apply transformation to a copy
            test_doc = copy.deepcopy(current_doc)
            transformation.apply(test_doc)
            
            # Calculate new score
            test_metrics = self.document_quality.analyze_document(test_doc)
            test_score = self._calculate_weighted_score(test_metrics)
            
            # Update best transformation if improvement found
            if test_score > best_score:
                best_score = test_score
                best_transformation = transformation
                
        # Apply best transformation if found
        if best_transformation:
            best_transformation.apply(current_doc)
            current_score = best_score
        else:
            # No improvement found, stop iteration
            break
            
    return current_doc

def _calculate_weighted_score(self, metrics):
    """Calculate weighted score from metrics."""
    score = 0.0
    total_weight = 0.0
    
    for metric, value in metrics.items():
        if metric in self.reward_weights:
            weight = self.reward_weights[metric]
            score += value * weight
            total_weight += weight
            
    return score / total_weight if total_weight > 0 else 0.0
```

## Advanced Features

### Transformation Generation

The optimizer can generate candidate transformations based on document analysis:

```python
def _get_candidate_transformations(self, document):
    """
    Generate candidate transformations for a document.
    
    Args:
        document: MarkdownDocument instance
        
    Returns:
        List of Transformation instances
    """
    candidates = []
    
    # Analyze document structure
    headings = document.get_headings()
    lists = document.get_lists()
    code_blocks = document.get_code_blocks()
    
    # Generate heading transformations
    if headings:
        # Check for inconsistent heading levels
        levels = [h.get('level', 1) for h in headings]
        if max(levels) - min(levels) > 3:
            # Add heading normalization
            candidates.append(HeadingLevelTransformation(min_level=1))
    
    # Generate list transformations
    if lists:
        # Check for mixed list styles
        list_types = set(lst.get('list_type', 'unordered') for lst in lists)
        if len(list_types) > 1:
            # Add list standardization
            candidates.append(ListFormatTransformation(target_type="unordered"))
    
    # Generate code block transformations
    if code_blocks:
        # Check for missing language specifiers
        missing_lang = any(not block.get('language') for block in code_blocks)
        if missing_lang:
            # Add code block language specification
            candidates.append(CodeBlockFormatTransformation(new_language="text"))
    
    # Add general transformations
    candidates.extend([
        TextStyleTransformation(bold_style="**", italic_style="*"),
        LinkFormatTransformation(style="reference"),
        TableFormatTransformation(alignment="default")
    ])
    
    return candidates
```

### Custom Transformation Pipelines

Users can define custom transformation pipelines for specific optimization goals:

```python
def transform_with_pipeline(self, document, pipeline):
    """
    Transform a document using a specific transformation pipeline.
    
    Args:
        document: MarkdownDocument instance
        pipeline: TransformationPipeline instance
        
    Returns:
        Transformed document
    """
    # Create a copy to avoid modifying the original
    doc_copy = copy.deepcopy(document)
    
    # Apply the pipeline
    pipeline.apply(doc_copy)
    
    # Calculate and store final metrics
    final_metrics = self.document_quality.analyze_document(doc_copy)
    doc_copy.metadata['quality_metrics'] = final_metrics
    
    return doc_copy
```

## Use Cases

### Document Standardization

The policy optimizer can be used to standardize document formatting:

```python
from mdp import PolicyOptimizer, MarkdownDocument

# Load documents from a directory
documents = []
for path in glob.glob("docs/*.md"):
    documents.append(MarkdownDocument(file_path=path))

# Create an optimizer focused on structure
optimizer = PolicyOptimizer(
    reward_weights={"structure_clarity": 0.8, "readability": 0.2}
)

# Standardize all documents
for doc in documents:
    optimized_doc = optimizer.transform(doc)
    optimized_doc.save(doc.file_path.replace(".md", "_optimized.md"))
```

### Content Quality Improvement

The optimizer can also focus on improving content quality:

```python
# Define a custom reward function for technical content
def technical_accuracy_reward(structure):
    """Reward documents with proper code formatting and terminology."""
    code_blocks = [e for e in structure if e['type'] == 'code']
    terminology_score = 0.0
    
    # Check for proper code formatting
    code_score = sum(1.0 for block in code_blocks if block.get('language')) / max(len(code_blocks), 1)
    
    # Check for proper terminology (simplified example)
    for paragraph in [e for e in structure if e['type'] == 'paragraph']:
        text = paragraph.get('text', '')
        if any(term in text for term in ['algorithm', 'function', 'class', 'method']):
            terminology_score += 0.2
    
    return min(1.0, (code_score + min(terminology_score, 0.8)) / 2)

# Create an optimizer for technical documentation
tech_optimizer = PolicyOptimizer(
    custom_rewards={"technical_accuracy": technical_accuracy_reward},
    reward_weights={
        "technical_accuracy": 0.6,
        "readability": 0.3,
        "structure_clarity": 0.1
    }
)

# Optimize a technical document
doc = MarkdownDocument(file_path="api_documentation.md")
optimized_doc = tech_optimizer.transform(doc)
optimized_doc.save("api_documentation_optimized.md")
```

## Performance Considerations

The optimization process can be computationally intensive, especially for large documents with many transformation candidates. Some strategies to improve performance include:

1. **Limited Transformation Subset**: Only evaluate the most promising transformations
2. **Targeted Optimization**: Focus on specific document sections rather than the entire document
3. **Parallel Evaluation**: Evaluate transformation candidates in parallel
4. **Early Stopping**: Stop iteration when improvements fall below a threshold
5. **Caching**: Cache quality metrics for document subsections

## Future Directions

1. **Learning from Examples**: Use machine learning to train transformation selection based on example documents
2. **User Feedback Integration**: Incorporate user feedback into the reward function
3. **Context-Aware Optimization**: Consider document purpose and audience in optimization
4. **Multi-Objective Optimization**: Support explicit trade-offs between competing quality goals
5. **Incremental Optimization**: Optimize documents incrementally as they evolve over time 