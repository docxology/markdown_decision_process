# Markdown Decision Process User Guide

This comprehensive guide will help you get started with the Markdown Decision Process (MDP) framework and make the most of its capabilities.

## 🚀 Quick Start

### Installation

```bash
# Install with uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or with pip
pip install -e .
```

### Basic Usage

```python
from mdp import Document, MarkdownAgent

# Create a document
doc = Document(content="# My Document\n\nThis is content.")

# Create an agent
agent = MarkdownAgent()

# Analyze and optimize
result = agent.interact(doc.content, objective="optimize")
print(f"Optimized: {result['modified_content']}")
```

## 📚 Core Concepts

### States and Transitions

In MDP, every Markdown element becomes a **state**:
- `# Header` → Header state
- `Paragraph text` → Paragraph state
- `- List item` → List state
- ````python`code` → Code state

**Transitions** define how states connect, creating a **Markov Decision Process** where each state has probabilistic connections to others.

### Reward Functions

Reward functions define what makes a document "good":

```python
def readability_reward(element):
    """Reward readable paragraph lengths"""
    if element['type'] == 'paragraph':
        word_count = len(element['content'].split())
        if 50 <= word_count <= 150:
            return 1.0  # Good length
        return -0.5   # Too long or too short
    return 0.0
```

### Belief States

Belief states track semantic understanding:

```python
from mdp import BeliefUpdater

updater = BeliefUpdater()
updater.update_from_observation({
    "instruction": 0.7,
    "example": 0.2,
    "reference": 0.1
})
```

## 🎯 Common Use Cases

### Document Optimization

```python
from mdp import MarkdownAgent

agent = MarkdownAgent()
result = agent.interact(content, objective="optimize")

# Access results
optimized_content = result['modified_content']
actions_taken = result['actions_taken']
final_reward = result.get('final_reward')
```

**Available objectives:**
- `"optimize"` - Improve document structure and quality
- `"extend"` - Add relevant content
- `"summarize"` - Create condensed version
- `"analyze"` - Detailed document analysis

### Content Generation

```python
from mdp import MarkChain

# Train on corpus
chain = MarkChain()
chain.train(corpus_content)

# Generate new content
new_content = chain.generate("# New Section", length=300)
```

### Document Analysis

```python
from mdp import Document, StateSpace

doc = Document(content=content)
state_space = StateSpace(doc)

print(f"Document has {len(state_space.graph.nodes)} states")
print(f"State space density: {len(state_space.graph.edges) / len(state_space.graph.nodes)}")
```

## 🔧 Configuration

### Agent Configuration

```python
from mdp import MarkdownAgent

agent = MarkdownAgent(
    exploration_rate=0.2,      # Balance exploration/exploitation
    learning_rate=0.1,         # Learning rate for RL
    discount_factor=0.9,       # Future reward discount
    reward_weights={           # Custom reward component weights
        'readability': 1.0,
        'structure': 0.8,
        'completeness': 0.6
    }
)
```

### Reward Function Design

```python
def custom_reward_function(element):
    """Design reward functions for your domain"""
    reward = 0.0

    if element['type'] == 'header':
        # Reward appropriate header hierarchy
        level = element.get('level', 1)
        reward = 2.0 / level

    elif element['type'] == 'paragraph':
        # Reward good paragraph length
        word_count = len(element['content'].split())
        if 30 <= word_count <= 100:
            reward = 1.0
        elif word_count > 150:
            reward = -0.5  # Penalize long paragraphs

    elif element['type'] == 'code':
        # Reward code with good practices
        if element.get('language'):
            reward = 2.0  # Language specified
        else:
            reward = 1.0  # Basic code block

    return reward
```

## 📊 Analysis and Metrics

### Document Quality Metrics

```python
from mdp import Document, StateSpace
from mdp.quality import DocumentQuality

doc = Document(content=content)
quality = DocumentQuality()
metrics = quality.analyze_document(doc)

print(f"Overall quality: {metrics['overall_score']}")
print(f"Readability: {metrics['readability_score']}")
print(f"Structure: {metrics['structure_score']}")
```

### State Space Analysis

```python
from mdp import Document, StateSpace

doc = Document(content=content)
state_space = StateSpace(doc)

# Get state statistics
print(f"Total states: {len(state_space.graph.nodes)}")
print(f"Total transitions: {len(state_space.graph.edges)}")
print(f"Average connectivity: {len(state_space.graph.edges) / len(state_space.graph.nodes)}")

# Analyze specific states
for node_id in state_space.graph.nodes:
    metadata = state_space.get_state_metadata(node_id)
    successors = state_space.get_successor_states(node_id)
    print(f"{node_id}: {metadata['type']} -> {len(successors)} successors")
```

## 🎨 Visualizations

### Document Structure

```python
from mdp import plot_document_structure

fig = plot_document_structure(document)
fig.savefig("document_structure.png")
```

### State Transitions

```python
from mdp import plot_transitions

fig = plot_transitions(markchain)
fig.savefig("transitions.png")
```

### State Space Network

```python
state_space.visualize("state_space.png")
```

## 🔄 Advanced Workflows

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
    with open(md_file, 'r') as f:
        content = f.read()

    result = agent.interact(content, objective="optimize")

    output_path = output_dir / md_file.name
    with open(output_path, 'w') as f:
        f.write(result['modified_content'])
```

### Custom Transformation Pipelines

```python
from mdp import TransformationPipeline, HeadingLevelTransformation, ListFormatTransformation

# Create transformation sequence
pipeline = TransformationPipeline([
    HeadingLevelTransformation(increment=1),  # Increase heading levels
    ListFormatTransformation("ordered")      # Convert to ordered lists
])

# Apply to document
pipeline.apply(document, "transformed.md")
```

### Integration with External Tools

```python
from mdp import PandocConverter

# Convert optimized documents
converter = PandocConverter()
converter.convert("optimized.md", "output.pdf")
converter.convert("optimized.md", "output.html")
```

## 🛠️ Troubleshooting

### Common Issues

#### "Document has no structure"
```python
# Check document content
doc = Document(content=content)
structure = doc.get_structure()

if not structure:
    print("Document appears empty or malformed")
else:
    print(f"Found {len(structure)} elements")
```

#### "State space has no nodes"
```python
# Check if document was analyzed
state_space = StateSpace(document)

if not state_space.graph.nodes:
    # Try analyzing explicitly
    state_space.analyze("document.md")
```

#### "Optimization not improving document"
```python
# Check reward function
def debug_reward(element):
    reward = calculate_reward(element)
    print(f"{element['type']}: {reward}")
    return reward

optimizer.set_reward_function(debug_reward)
```

### Performance Issues

#### Slow Training
- Reduce `max_iterations` in training
- Use smaller training corpora
- Lower Markov chain order

#### High Memory Usage
- Process documents in batches
- Use incremental analysis for large documents
- Clear intermediate results when possible

#### Slow Generation
- Use lower Markov chain order
- Reduce generation length
- Cache frequently used models

## 📈 Best Practices

### 1. Start Simple
Begin with basic reward functions and simple documents, then add complexity.

### 2. Iterative Development
Test and refine reward functions incrementally:
```python
# Start with simple rewards
def basic_reward(element):
    return 1.0 if element['type'] == 'header' else 0.5

# Add complexity gradually
def advanced_reward(element):
    base_reward = basic_reward(element)

    # Add length considerations
    if element['type'] == 'paragraph':
        word_count = len(element['content'].split())
        if word_count > 100:
            base_reward -= 0.5

    return base_reward
```

### 3. Validation
Always validate results:
```python
# Before optimization
original_structure = doc.get_structure()
original_length = len(doc.content)

# After optimization
result = agent.interact(content, objective="optimize")
optimized_structure = Document(content=result['modified_content']).get_structure()
optimized_length = len(result['modified_content'])

print(f"Structure elements: {len(original_structure)} -> {len(optimized_structure)}")
print(f"Content length: {original_length} -> {optimized_length}")
```

### 4. Domain Adaptation
Customize for your specific domain:
```python
# Technical documentation
def tech_doc_reward(element):
    if element['type'] == 'code':
        return 3.0  # Highly value code examples
    elif element['type'] == 'header':
        return 1.5  # Value clear structure
    return 0.5

# Academic writing
def academic_reward(element):
    if element['type'] == 'paragraph':
        # Academic style: longer, more formal paragraphs
        word_count = len(element['content'].split())
        if 100 <= word_count <= 300:
            return 2.0
    return 0.0
```

### 5. Error Handling
Implement robust error handling:
```python
try:
    result = agent.interact(content, objective="optimize")
except Exception as e:
    print(f"Optimization failed: {e}")
    # Fallback to simpler processing or manual review
    result = {'modified_content': content, 'actions_taken': []}
```

## 🔍 Debugging

### Enable Debug Output

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# MDP operations will now show detailed information
result = agent.interact(content, objective="optimize")
```

### Inspect Internal State

```python
# Check agent components
print(f"Generator trained: {agent.generator.is_trained}")
print(f"State space nodes: {len(agent.state_space.graph.nodes)}")

# Check reward function
test_element = {'type': 'paragraph', 'content': 'Test content'}
reward = agent.optimizer.reward_function(test_element)
print(f"Test element reward: {reward}")
```

### Visualize Decision Process

```python
# Visualize state space
agent.state_space.visualize("debug_state_space.png")

# Check policy values
policy_values = agent.optimizer.evaluate_policy()
for state, value in list(policy_values.items())[:5]:
    print(f"{state}: {value}")
```

## 📚 Learning Resources

### API Documentation
- [Document API](../api/document.md)
- [StateSpace API](../api/state_space.md)
- [MarkChain API](../api/markchain.md)
- [PolicyOptimizer API](../api/policy_optimizer.md)
- [MarkdownAgent API](../api/markdown_agent.md)

### Examples
- [Basic Usage](../examples/basic_usage.py)
- [Advanced Usage](../examples/advanced_usage.py)

### Tutorials
- Getting Started Tutorial
- Custom Reward Functions
- Performance Optimization

## 🤝 Contributing

Found a bug or want to add features? See our [Contributing Guide](../../CONTRIBUTING.md).

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/markdown_decision_process/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/markdown_decision_process/discussions)
- **Documentation**: This user guide and API reference

---

Happy document processing! 🚀


