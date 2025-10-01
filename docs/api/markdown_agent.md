# MarkdownAgent API Reference

The `MarkdownAgent` class provides an autonomous interface for comprehensive Markdown document processing, combining all MDP components into a unified agent.

## Class Overview

```python
class MarkdownAgent:
    """Autonomous agent for comprehensive Markdown document processing."""

    def __init__(self, exploration_rate: float = 0.2, **kwargs)
    def train(self, corpus_path: str, iterations: int = 100) -> Dict
    def analyze(self, markdown_input) -> Dict
    def optimize(self, markdown_path: str) -> str
    def generate(self, prompt: str = None, length: int = 100) -> str
    def interact(self, content: str, objective: str) -> Dict
```

## Constructor

### `__init__(exploration_rate=0.2, **kwargs)`

Initialize a MarkdownAgent with specified parameters.

**Parameters:**
- `exploration_rate` (float): Balance between exploration and exploitation
- `learning_rate` (float): Learning rate for reinforcement learning
- `discount_factor` (float): Discount factor for future rewards
- `reward_weights` (Dict[str, float]): Weights for different reward components
- `model_path` (str, optional): Path to pre-trained models

**Example:**
```python
from mdp import MarkdownAgent

agent = MarkdownAgent(
    exploration_rate=0.3,
    learning_rate=0.15,
    reward_weights={'readability': 1.0, 'structure': 0.8}
)
```

## Methods

### `train(corpus_path: str, iterations=100) -> Dict`

Train the agent on a corpus of markdown documents.

**Parameters:**
- `corpus_path` (str): Path to directory containing markdown files
- `iterations` (int): Number of training iterations

**Returns:** Dictionary with training statistics

**Example:**
```python
agent = MarkdownAgent()
stats = agent.train("docs/", iterations=50)
print(f"Training completed: {stats}")
```

### `analyze(markdown_input) -> Dict`

Analyze a markdown document and return comprehensive insights.

**Parameters:**
- `markdown_input` (Document | str | Path): Document to analyze

**Returns:** Dictionary with analysis results including structure, metrics, and semantic analysis

**Example:**
```python
result = agent.analyze("document.md")
print(f"Document coherence: {result['semantic_analysis']['coherence']}")
```

### `optimize(markdown_path: str) -> str`

Optimize an existing markdown document.

**Parameters:**
- `markdown_path` (str): Path to markdown file to optimize

**Returns:** Optimized markdown content

**Example:**
```python
optimized = agent.optimize("input.md")
with open("output.md", "w") as f:
    f.write(optimized)
```

### `generate(prompt=None, length=100) -> str`

Generate new markdown content.

**Parameters:**
- `prompt` (str, optional): Initial prompt text
- `length` (int): Maximum length of generated content

**Returns:** Generated markdown content

**Example:**
```python
content = agent.generate("# New Document", length=300)
print(content)
```

### `interact(content: str, objective: str) -> Dict`

Interactive document processing with specified objective.

**Parameters:**
- `content` (str): Markdown content to process
- `objective` (str): Processing objective ("optimize", "extend", "summarize", etc.)

**Returns:** Dictionary with processing results and metadata

**Example:**
```python
result = agent.interact(content, objective="optimize")
print(f"Actions taken: {result['actions_taken']}")
print(f"Modified content length: {len(result['modified_content'])}")
```

## Objectives

The `interact` method supports various objectives:

### "optimize"
Optimize document structure and content based on learned policies.

```python
result = agent.interact(content, objective="optimize")
# Returns: optimized content with reward metrics
```

### "extend"
Extend document with additional relevant content.

```python
result = agent.interact(content, objective="extend")
# Returns: extended content with generation metadata
```

### "summarize"
Create a summary or condensed version.

```python
result = agent.interact(content, objective="summarize")
# Returns: summarized content
```

### "analyze"
Perform comprehensive document analysis.

```python
result = agent.interact(content, objective="analyze")
# Returns: detailed analysis with metrics
```

## Usage Examples

### Basic Agent Usage

```python
from mdp import MarkdownAgent

# Initialize agent
agent = MarkdownAgent()

# Train on corpus
agent.train("documentation/")

# Analyze document
analysis = agent.analyze("README.md")
print(f"Document type: {analysis['semantic_analysis']['overall_semantic_class']}")

# Optimize document
optimized = agent.optimize("README.md")
```

### Interactive Processing

```python
from mdp import MarkdownAgent

agent = MarkdownAgent()

# Interactive optimization
content = "# My Document\n\nThis needs improvement."
result = agent.interact(content, objective="optimize")

print(f"Objective: {result['objective']}")
print(f"Actions taken: {len(result['actions_taken'])}")
print(f"Final reward: {result.get('final_reward', 'N/A')}")
```

### Document Generation

```python
from mdp import MarkdownAgent

agent = MarkdownAgent()

# Generate new content
prompt = "# API Reference\n\nThis section documents"
generated = agent.generate(prompt, length=500)

print(f"Generated {len(generated)} characters")
```

### Batch Processing

```python
from mdp import MarkdownAgent
from pathlib import Path

agent = MarkdownAgent()

# Process multiple documents
input_dir = Path("input_docs")
output_dir = Path("optimized_docs")
output_dir.mkdir(exist_ok=True)

for md_file in input_dir.glob("*.md"):
    print(f"Processing {md_file.name}...")

    # Analyze
    analysis = agent.analyze(md_file)

    # Optimize if needed
    if analysis['quality_metrics']['overall_score'] < 0.7:
        optimized = agent.optimize(str(md_file))
        output_path = output_dir / md_file.name
        with open(output_path, "w") as f:
            f.write(optimized)
        print(f"  Optimized and saved to {output_path}")
    else:
        print("  Document quality is good, no optimization needed")
```

## Advanced Features

### Custom Reward Weights

```python
from mdp import MarkdownAgent

# Configure agent with custom reward weights
agent = MarkdownAgent(
    reward_weights={
        'readability': 1.2,
        'structure': 0.8,
        'completeness': 0.6,
        'conciseness': 0.4
    }
)

# Training will emphasize readability and structure
agent.train("corpus/")
```

### Model Persistence

```python
from mdp import MarkdownAgent

# Train agent
agent = MarkdownAgent()
agent.train("large_corpus/", iterations=200)

# Save trained models
agent.save_models("trained_agent/")

# Load in production
production_agent = MarkdownAgent()
production_agent.load_models("trained_agent/")
```

### Integration with External Tools

```python
from mdp import MarkdownAgent, PandocConverter

agent = MarkdownAgent()

# Optimize document
optimized = agent.optimize("document.md")

# Convert to other formats
converter = PandocConverter()
converter.convert("document.md", "document.pdf")
converter.convert("document.md", "document.html")
```

## Integration with Other Components

### With StateSpace for Deep Analysis

```python
from mdp import MarkdownAgent, StateSpace

agent = MarkdownAgent()
analysis = agent.analyze("document.md")

# Get underlying state space for detailed analysis
state_space = agent.state_space
print(f"Document has {len(state_space.graph.nodes)} states")
print(f"State space density: {len(state_space.graph.edges) / len(state_space.graph.nodes)}")
```

### With PolicyOptimizer for Custom Optimization

```python
from mdp import MarkdownAgent, PolicyOptimizer

agent = MarkdownAgent()

# Access internal optimizer for custom configuration
optimizer = agent.optimizer

# Set custom reward function
def custom_reward(element):
    if element['type'] == 'code':
        return 3.0  # Highly reward code blocks
    return 1.0

optimizer.set_reward_function(custom_reward)

# Use in interaction
result = agent.interact(content, objective="optimize")
```

### With BeliefUpdater for Semantic Context

```python
from mdp import MarkdownAgent, BeliefUpdater

agent = MarkdownAgent()

# Set semantic context
semantic_context = {
    "instruction": 0.6,
    "example": 0.3,
    "reference": 0.1
}

# Context-aware processing
result = agent.interact(content, objective="optimize")
```

## Error Handling

```python
from mdp import MarkdownAgent

agent = MarkdownAgent()

try:
    result = agent.interact(content, objective="invalid_objective")
except ValueError as e:
    print(f"Invalid objective: {e}")

try:
    analysis = agent.analyze("nonexistent.md")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Performance Considerations

- **Training Time**: Larger corpora require more training iterations
- **Memory Usage**: Agent maintains multiple models (MarkChain, PolicyOptimizer, etc.)
- **Generation Speed**: Higher quality generation may be slower
- **Analysis Depth**: Deep analysis provides more insights but takes longer

## Best Practices

1. **Training**: Train on diverse, high-quality corpora
2. **Objectives**: Use appropriate objectives for your use case
3. **Validation**: Always review agent outputs before using in production
4. **Customization**: Tune reward weights for your specific domain
5. **Persistence**: Save trained models for consistent behavior

## Common Patterns

### Document Quality Improvement

```python
agent = MarkdownAgent()

# Analyze current quality
analysis = agent.analyze(document)

if analysis['quality_metrics']['overall_score'] < 0.8:
    # Optimize if quality is poor
    result = agent.interact(document, objective="optimize")
    improved_content = result['modified_content']
else:
    improved_content = document
```

### Content Extension

```python
agent = MarkdownAgent()

# Extend existing content
existing = "# Project Overview\n\nCurrent content."
result = agent.interact(existing, objective="extend")

# Append generated content
extended_content = result['modified_content']
```

### Multi-Document Processing

```python
agent = MarkdownAgent()
agent.train("knowledge_base/")

# Process multiple documents
documents = ["doc1.md", "doc2.md", "doc3.md"]

for doc_path in documents:
    analysis = agent.analyze(doc_path)

    if analysis['semantic_analysis']['overall_semantic_class'] == "instruction":
        # Optimize instructional content
        result = agent.interact(open(doc_path).read(), objective="optimize")
        # Save optimized version
```

## Debugging and Monitoring

```python
# Monitor agent decisions
result = agent.interact(content, objective="optimize")

print(f"Objective: {result['objective']}")
print(f"Actions taken: {result['actions_taken']}")
print(f"Final reward: {result.get('final_reward', 'N/A')}")

# Check agent state
print(f"Exploration rate: {agent.exploration_rate}")
print(f"Training iterations: {agent.generator.is_trained}")
```

## Configuration Options

```python
# Full configuration example
agent = MarkdownAgent(
    exploration_rate=0.2,      # Balance exploration/exploitation
    learning_rate=0.1,         # Learning rate for RL
    discount_factor=0.9,       # Future reward discount
    reward_weights={           # Custom reward component weights
        'readability': 1.0,
        'structure': 0.8,
        'completeness': 0.6
    },
    model_path=None           # Path to pre-trained models
)
```


