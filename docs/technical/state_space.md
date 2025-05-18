# State Space Analysis

The `StateSpace` class in MDP provides powerful tools for analyzing the structure of markdown documents as directed graphs. This technical documentation explores the implementation and theory behind this approach.

## Conceptual Framework

In the Markdown Decision Process framework, we model markdown documents as stochastic processes with:

- **States**: Different markdown elements (headers, paragraphs, lists, etc.)
- **Transitions**: The probability of one element following another
- **Observations**: The visible markdown syntax

The state space approach allows us to:

1. Visualize document structure as a directed graph
2. Calculate transition probabilities between different states
3. Identify common patterns and structures in documents
4. Extract features for machine learning and optimization

## Implementation Details

### State Representation

Each state in the markdown document is represented as a dictionary with metadata:

```python
state = {
    "type": "header",  # Type of markdown element
    "level": 2,        # Element-specific metadata
    "content": "## Section Title",  # Raw content
    "id": "h2_section_title"  # Generated ID
}
```

Common state types include:
- `header`: Section headings (h1-h6)
- `paragraph`: Text paragraphs
- `list`: Ordered or unordered lists
- `code`: Code blocks
- `table`: Data tables
- `blockquote`: Quoted content
- `blank`: Empty lines

### Graph Construction

The `StateSpace` class uses [NetworkX](https://networkx.org/) to create a directed graph representation of the document:

```python
self.graph = nx.DiGraph()

# Add nodes for states
for state_id, state_data in self.states.items():
    self.graph.add_node(state_id, **state_data)
    
# Add edges for transitions
for source, targets in self.transitions.items():
    for target, weight in targets.items():
        self.graph.add_edge(source, target, weight=weight)
```

Transition weights reflect the frequency of one state following another.

### Visualization

The visualization capabilities use matplotlib and NetworkX to create insightful representations of the document structure:

```python
def visualize(self, output_path="markdown_state_space.png", title="Markdown State Space"):
    """
    Visualize the state space as a directed graph and save to a file.
    """
    # Create a simplified graph for visualization
    G = self._create_visualization_graph()
    
    # Calculate node sizes based on frequency
    sizes = [...]
    
    # Generate color-coding for node types
    colors = [...]
    
    # Layout the graph
    pos = nx.spring_layout(G)
    
    # Draw the visualization
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos)
    
    # Add title and save
    plt.title(title)
    plt.savefig(output_path)
```

## Advanced Features

### Transition Probability Analysis

The `calculate_transition_probabilities()` method converts raw transition counts to probabilities:

```python
probabilities = {}
for source, targets in self.transitions.items():
    total_transitions = sum(targets.values())
    probabilities[source] = {
        target: count / total_transitions
        for target, count in targets.items()
    }
```

### Feature Extraction

The state space can extract features for machine learning:

```python
def get_features(self, state_id):
    """Extract features for a state."""
    features = {
        'type': self.states[state_id]['type'],
        'outdegree': self.graph.out_degree(state_id),
        'indegree': self.graph.in_degree(state_id),
        # Other features...
    }
    return features
```

### Document Comparison

Documents can be compared by measuring the similarity of their state spaces:

```python
def compare_documents(doc1_state_space, doc2_state_space):
    """Compare two document state spaces."""
    similarity = calculate_graph_similarity(
        doc1_state_space.graph,
        doc2_state_space.graph
    )
    return similarity
```

## Usage Examples

### Basic State Space Analysis

```python
from mdp import StateSpace

# Create state space analyzer
state_space = StateSpace()

# Analyze a document
state_space.analyze("document.md")

# Print statistics
state_space.print_statistics()

# Visualize the state space
state_space.visualize("document_structure.png")
```

### Advanced Analysis

```python
# Get transition probabilities
probs = state_space.calculate_transition_probabilities()

# Find most likely next state for a heading
heading_id = next(id for id, data in state_space.states.items() 
                 if data['type'] == 'heading')
transitions = state_space.get_transitions(heading_id)
most_likely_next = max(transitions.items(), key=lambda x: x[1])[0]

# Extract document features for machine learning
document_features = {
    state_id: state_space.get_features(state_id)
    for state_id in state_space.states
}
```

## Mathematical Foundation

The state space representation builds on concepts from graph theory and Markov processes:

- **Graph Density**: Ratio of edges to possible edges, indicating document interconnectedness
- **Centrality Measures**: Identifying key states in the document structure
- **Community Detection**: Finding clusters of related states
- **Markov Chain Analysis**: Modeling the document as a stochastic process

## Performance Considerations

For large documents, the state space analysis can be computationally intensive. Some optimizations include:

- **State Simplification**: Grouping similar states to reduce graph complexity
- **Filtered Visualization**: Only showing transitions above a minimum count
- **Incremental Parsing**: Processing the document in chunks for very large files 