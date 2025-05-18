# Belief Updating for Markdown Semantics

The `BeliefUpdater` class in MDP implements a probabilistic approach to interpreting the semantic meaning of markdown content. Drawing inspiration from Partially Observable Markov Decision Processes (POMDPs), it uses Bayesian reasoning to maintain a belief state about document semantics.

## Theoretical Foundation

In a POMDP framework, the true state of the system is not directly observable. Similarly, the semantic meaning of markdown content is not directly encoded in the syntax. The `BeliefUpdater` addresses this uncertainty through:

1. **Belief States**: Probability distributions over possible semantic meanings
2. **Observations**: Markdown syntax and structure patterns
3. **Bayesian Updates**: Adjusting beliefs based on new observations
4. **Uncertainty Modeling**: Accounting for noise and ambiguity in interpretation

## Implementation Details

### Belief Representation

Beliefs are stored as probability distributions over semantic classes:

```python
self.beliefs = {
    "instruction": 0.2,
    "explanation": 0.5,
    "warning": 0.1,
    "note": 0.1,
    "reference": 0.1
}
```

Each semantic class represents a different possible interpretation of the document's purpose or meaning.

### Initialization

The `BeliefUpdater` can be initialized with custom semantic classes and prior beliefs:

```python
def __init__(self, semantic_classes=None, noise_factor=0.2, prior_beliefs=None):
    self.semantic_classes = semantic_classes or [
        "instruction", "explanation", "example", "reference", 
        "summary", "definition", "warning", "note"
    ]
    
    # Initialize uniform belief distribution
    self.beliefs = {cls: 1.0 / len(self.semantic_classes) for cls in self.semantic_classes}
    
    # Override with prior beliefs if provided
    if prior_beliefs:
        for key, value in prior_beliefs.items():
            self.beliefs[key] = value
            
    # Initialize confidence level
    self.confidence = 0.5
    
    # Set noise factor for belief updates
    self.noise_factor = min(max(noise_factor, 0.0), 1.0)
```

### Bayesian Updating

The core of the belief updating process uses Bayes' rule to update beliefs based on observations:

```python
def update_from_observation(self, observation):
    """
    Update beliefs based on an observation dictionary.
    
    Args:
        observation: Dictionary mapping belief keys to observed values
    """
    # Store the observation
    self.observations.append(observation)
    
    for key, value in observation.items():
        current = self.get_belief(key)
        # Simple Bayesian update
        updated = (current + value) / 2  # Simplified update
        self.update_belief(key, updated)
```

More sophisticated implementations use full Bayesian updates:

```python
def _observation_step(self, prior_belief, observation):
    """Full Bayesian update based on observed features."""
    posterior = {}
    normalizer = 0
    
    for state in self.semantic_classes:
        # P(observation|state) * P(state)
        likelihood = self._calculate_likelihood(state, observation)
        posterior[state] = likelihood * prior_belief.get(state, 0)
        normalizer += posterior[state]
    
    # Normalize
    if normalizer > 0:
        for state in posterior:
            posterior[state] /= normalizer
            
    return posterior
```

### Document Analysis

The `analyze_document` method extracts observations from markdown documents:

```python
def analyze_document(self, state_space):
    """
    Analyze a document to generate beliefs about its semantic characteristics.
    
    Args:
        state_space: StateSpace instance with document structure
        
    Returns:
        Dictionary of beliefs about the document
    """
    # Extract features
    features = self._extract_document_features(state_space)
    
    # Generate beliefs from features
    beliefs = {}
    
    # Count state types
    state_types = Counter()
    for state in state_space.states.values():
        state_type = state.get('type', 'unknown')
        state_types[state_type] += 1
        
    total_states = sum(state_types.values())
    
    # Map structural features to beliefs
    if total_states > 0:
        heading_ratio = state_types.get('heading', 0) / total_states
        beliefs['structure'] = min(heading_ratio * 5, 1.0)
        
        para_ratio = state_types.get('paragraph', 0) / total_states
        beliefs['readability'] = min(para_ratio * 2, 1.0)
        
        # ... other mappings ...
        
    # Apply noise to beliefs
    if self.noise_factor > 0:
        for key in beliefs:
            noise = np.random.normal(0, self.noise_factor * 0.1)
            beliefs[key] = min(max(beliefs[key] + noise, 0.0), 1.0)
            
    return beliefs
```

## Advanced Features

### Uncertainty Quantification

The `calculate_entropy` method provides a measure of uncertainty in the current belief state:

```python
def calculate_entropy(self):
    """
    Calculate the entropy of the current belief distribution.
    
    Returns:
        Entropy value
    """
    values = [v for v in self.beliefs.values() if v > 0]
    if not values:
        return 0.0
        
    # Normalize to ensure sum is 1
    total = sum(values)
    if total == 0:
        return 0.0
        
    normalized = [v / total for v in values]
    
    # Calculate entropy
    entropy = -sum(p * np.log2(p) for p in normalized if p > 0)
    return entropy
```

Higher entropy indicates greater uncertainty in the belief state.

### Belief Persistence

Beliefs can be saved to and loaded from disk:

```python
def save_beliefs(self, filepath):
    """Save the current belief state to a file."""
    with open(filepath, 'w') as f:
        json.dump({
            'beliefs': self.beliefs,
            'confidence': self.confidence,
            'observations': self.observations
        }, f)

def load_beliefs(self, filepath):
    """Load beliefs from a file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
        self.beliefs = data.get('beliefs', {})
        self.confidence = data.get('confidence', 0.0)
        self.observations = data.get('observations', [])
```

### Semantic Classification

The `get_most_likely_semantics` method returns the most probable semantic class:

```python
def get_most_likely_semantics(self):
    """
    Get the most likely semantic class based on current belief.
    
    Returns:
        Tuple of (most likely class, probability)
    """
    most_likely = max(self.beliefs.items(), key=lambda x: x[1])
    return most_likely
```

## Usage Examples

### Basic Semantic Analysis

```python
from mdp import BeliefUpdater, StateSpace

# Create a belief updater
updater = BeliefUpdater()

# Create and analyze a state space
state_space = StateSpace()
state_space.analyze("document.md")

# Update beliefs based on document analysis
beliefs = updater.analyze_document(state_space)

# Get the most likely semantic interpretation
semantic_class, probability = updater.get_most_likely_semantics()
print(f"Document type: {semantic_class} (confidence: {probability:.2f})")
```

### Domain-Specific Analysis

```python
# Create a belief updater for technical documentation
tech_updater = BeliefUpdater(
    semantic_classes=["api", "tutorial", "reference"],
    prior_beliefs={
        "structure": 0.8,
        "complexity": 0.7,
        "reference": 0.6
    }
)

# Analyze a technical document
tech_beliefs = tech_updater.analyze_document_file("api_doc.md")

# Measure uncertainty in classification
entropy = tech_updater.calculate_entropy()
print(f"Classification uncertainty: {entropy:.2f}")
```

## Performance and Limitations

### Computational Considerations

- Belief updates are generally efficient, with complexity O(n) where n is the number of semantic classes
- The observation model calculation can be more intensive, especially with complex feature extraction

### Current Limitations

1. The default observation model uses simple heuristics rather than learned patterns
2. Limited handling of context and document coherence
3. No natural language understanding for deeper semantic analysis
4. Fixed semantic classes rather than open-ended interpretation

## Future Directions

1. **Learned Observation Models**: Training the observation model from labeled data
2. **Hierarchical Belief Updating**: Modeling beliefs at multiple levels (document, section, paragraph)
3. **Temporal Belief Dynamics**: Modeling how semantics evolve through document flow
4. **Integration with NLP Models**: Using embeddings for richer semantic understanding
5. **Active Learning**: Using uncertainty to guide further information gathering 