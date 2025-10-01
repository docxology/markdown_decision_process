# PolicyOptimizer API Reference

The `PolicyOptimizer` class implements reinforcement learning algorithms for optimizing Markdown documents based on user-defined reward functions.

## Class Overview

```python
class PolicyOptimizer:
    """Reinforcement learning-based document optimizer."""

    def __init__(self, state_space=None, reward_function=None, **kwargs)
    def set_reward_function(self, reward_fn: Callable) -> None
    def optimize(self, document, output_path=None) -> Dict
    def value_iteration(self, max_iterations: int = 100) -> Dict
    def policy_improvement(self) -> Dict
    def q_learning(self, episodes: int = 100) -> Dict
    def evaluate_policy(self) -> Dict
```

## Constructor

### `__init__(state_space=None, reward_function=None, **kwargs)`

Initialize a PolicyOptimizer with state space and reward function.

**Parameters:**
- `state_space` (StateSpace, optional): Document state space to optimize
- `reward_function` (Callable, optional): Function to evaluate state quality
- `learning_rate` (float): Learning rate for Q-learning (default: 0.1)
- `discount_factor` (float): Discount factor for future rewards (default: 0.9)
- `exploration_factor` (float): Exploration vs exploitation balance (default: 0.2)
- `max_iterations` (int): Maximum optimization iterations (default: 100)

**Example:**
```python
from mdp import StateSpace, PolicyOptimizer

state_space = StateSpace(document)
optimizer = PolicyOptimizer(
    state_space=state_space,
    learning_rate=0.15,
    discount_factor=0.95
)
```

## Methods

### `set_reward_function(reward_fn: Callable) -> None`

Set the reward function for policy optimization.

**Parameters:**
- `reward_fn` (Callable): Function that takes a state element and returns a reward value

**Example:**
```python
def readability_reward(element):
    if element['type'] == 'paragraph':
        word_count = len(element['content'].split())
        if 50 <= word_count <= 150:
            return 1.0
        return -0.5
    return 0.0

optimizer.set_reward_function(readability_reward)
```

### `optimize(document, output_path=None) -> Dict`

Optimize a document using the configured reward function.

**Parameters:**
- `document` (Document | str | Path): Document to optimize
- `output_path` (str | Path, optional): Path to save optimized document

**Returns:** Dictionary with optimization results:
- `optimized_content`: Optimized markdown content
- `final_reward`: Final reward value achieved
- `iterations`: Number of optimization iterations
- `reward_history`: List of reward values over iterations

**Example:**
```python
result = optimizer.optimize(document, output_path="optimized.md")
print(f"Final reward: {result['final_reward']}")
print(f"Content length: {len(result['optimized_content'])}")
```

### `value_iteration(max_iterations=100) -> Dict`

Perform value iteration to find optimal policy.

**Parameters:**
- `max_iterations` (int): Maximum iterations

**Returns:** Dictionary with value function and policy

**Example:**
```python
values = optimizer.value_iteration(max_iterations=50)
print(f"Converged after {values['iterations']} iterations")
```

### `policy_improvement() -> Dict`

Improve the current policy using policy iteration.

**Returns:** Dictionary with improved policy

**Example:**
```python
improved_policy = optimizer.policy_improvement()
```

### `q_learning(episodes=100) -> Dict`

Train using Q-learning algorithm.

**Parameters:**
- `episodes` (int): Number of training episodes

**Returns:** Dictionary with learned Q-values

**Example:**
```python
q_values = optimizer.q_learning(episodes=200)
```

### `evaluate_policy() -> Dict`

Evaluate the current policy on all states.

**Returns:** Dictionary with state values and policy information

**Example:**
```python
evaluation = optimizer.evaluate_policy()
print(f"Average state value: {evaluation['average_value']}")
```

## Reward Functions

### Built-in Reward Functions

```python
# Default reward function (simple heuristic)
def _default_reward_function(element):
    """Default reward based on element type."""
    rewards = {
        'header': 1.0,
        'paragraph': 0.5,
        'list': 0.8,
        'code': 0.3
    }
    return rewards.get(element.get('type'), 0.0)

# Readability reward (penalizes very long/short paragraphs)
def _readability_reward(element):
    if element['type'] == 'paragraph':
        word_count = len(element['content'].split())
        if 50 <= word_count <= 150:
            return 1.0
        elif word_count > 200:
            return -0.5
    return 0.0

# Information density reward (rewards code blocks)
def _information_density_reward(element):
    if element['type'] == 'code':
        return 2.0
    return 0.0
```

### Custom Reward Functions

```python
def custom_reward_function(element):
    """Custom reward based on specific criteria."""
    reward = 0.0

    if element['type'] == 'header':
        # Reward higher-level headers more
        level = element.get('level', 1)
        reward = 2.0 / level

    elif element['type'] == 'paragraph':
        # Reward moderate-length paragraphs
        word_count = len(element['content'].split())
        if 30 <= word_count <= 100:
            reward = 1.0
        elif word_count > 150:
            reward = -0.5  # Penalize very long paragraphs

    elif element['type'] == 'list':
        # Reward well-structured lists
        item_count = element.get('item_count', 0)
        if 3 <= item_count <= 10:
            reward = 1.5

    return reward

optimizer.set_reward_function(custom_reward_function)
```

## Usage Examples

### Basic Document Optimization

```python
from mdp import Document, StateSpace, PolicyOptimizer

# Create document and state space
doc = Document(content="# Document\n\nLong paragraph with many words...")
state_space = StateSpace(doc)

# Set up optimizer with custom reward
def reward_fn(element):
    if element['type'] == 'paragraph':
        words = len(element['content'].split())
        return 1.0 if words < 50 else -0.5
    return 0.0

optimizer = PolicyOptimizer(state_space=state_space)
optimizer.set_reward_function(reward_fn)

# Optimize document
result = optimizer.optimize(doc)
print(f"Optimized content length: {len(result['optimized_content'])}")
print(f"Final reward: {result['final_reward']}")
```

### Multi-Objective Optimization

```python
from mdp import Document, StateSpace, PolicyOptimizer

doc = Document(content="# Report\n\nContent here.")
state_space = StateSpace(doc)

optimizer = PolicyOptimizer(state_space=state_space)

# Define multiple reward functions
rewards = {
    'readability': lambda elem: 1.0 if elem['type'] == 'paragraph' and len(elem['content'].split()) < 80 else 0.0,
    'structure': lambda elem: 2.0 if elem['type'] == 'header' else 0.0,
    'completeness': lambda elem: 0.5  # Base completeness reward
}

# Optimize with combined reward
def combined_reward(element):
    return sum(reward_fn(element) for reward_fn in rewards.values())

optimizer.set_reward_function(combined_reward)
result = optimizer.optimize(doc)
```

### Reinforcement Learning Training

```python
from mdp import Document, StateSpace, PolicyOptimizer

doc = Document(content="# Training Document\n\nContent.")
state_space = StateSpace(doc)

optimizer = PolicyOptimizer(
    state_space=state_space,
    learning_rate=0.1,
    discount_factor=0.9,
    exploration_factor=0.2
)

# Train using Q-learning
q_values = optimizer.q_learning(episodes=100)
print(f"Learned {len(q_values)} Q-values")

# Use value iteration for convergence
values = optimizer.value_iteration(max_iterations=50)
print(f"Policy converged with average value: {values['average_value']}")
```

### Advanced Policy Evaluation

```python
from mdp import Document, StateSpace, PolicyOptimizer

doc = Document(content="# Complex Document\n\nWith various elements.")
state_space = StateSpace(doc)

optimizer = PolicyOptimizer(state_space=state_space)

# Evaluate current policy
evaluation = optimizer.evaluate_policy()
print(f"Policy evaluation: {evaluation}")

# Improve policy
improved_policy = optimizer.policy_improvement()
print(f"Policy improvement completed")

# Final optimization
result = optimizer.optimize(doc)
```

## Integration with Other Components

### With Transformations

```python
from mdp import Document, StateSpace, PolicyOptimizer, TransformationPipeline, HeadingLevelTransformation

doc = Document(content="# Doc\n\nContent.")
state_space = StateSpace(doc)

# Create transformation pipeline
pipeline = TransformationPipeline([
    HeadingLevelTransformation(increment=1)
])

optimizer = PolicyOptimizer(
    state_space=state_space,
    transformation_pipeline=pipeline
)

# Optimize with transformations
result = optimizer.optimize(doc)
```

### With BeliefUpdater for Context-Aware Optimization

```python
from mdp import Document, StateSpace, PolicyOptimizer, BeliefUpdater

doc = Document(content="# Guide\n\nInstructions.")
state_space = StateSpace(doc)

# Set up belief tracking
updater = BeliefUpdater()
semantic_context = {"instruction": 0.8, "reference": 0.2}

# Context-aware reward function
def contextual_reward(element):
    base_reward = len(element['content'].split()) * 0.1

    # Adjust based on semantic context
    if semantic_context.get("instruction", 0) > 0.5:
        if element['type'] == 'paragraph':
            return base_reward * 1.5  # Favor instructional content
    elif semantic_context.get("reference", 0) > 0.5:
        if element['type'] == 'header':
            return base_reward * 2.0  # Favor structured reference

    return base_reward

optimizer = PolicyOptimizer(state_space=state_space)
optimizer.set_reward_function(contextual_reward)

result = optimizer.optimize(doc)
```

## Performance Considerations

- **Q-Learning**: More episodes = better policy but longer training time
- **Value Iteration**: More iterations = better convergence but diminishing returns
- **State Space Size**: Larger state spaces require more computation
- **Reward Function Complexity**: Complex rewards may slow optimization

## Best Practices

1. **Start Simple**: Begin with basic reward functions and simple documents
2. **Iterative Development**: Test and refine reward functions incrementally
3. **Validation**: Always validate optimized results manually
4. **Parameter Tuning**: Experiment with learning rates and discount factors
5. **Early Stopping**: Use convergence criteria to avoid overfitting

## Common Reward Function Patterns

### Length-Based Rewards

```python
def length_reward(element):
    """Reward appropriate content lengths."""
    if element['type'] == 'paragraph':
        word_count = len(element['content'].split())
        if word_count < 20:
            return -0.5  # Too short
        elif 20 <= word_count <= 100:
            return 1.0   # Just right
        else:
            return -0.2  # Too long

    return 0.0
```

### Structure-Based Rewards

```python
def structure_reward(element):
    """Reward good document structure."""
    rewards = {
        'header': lambda e: 2.0 / max(e.get('level', 1), 1),
        'list': lambda e: 1.0 if e.get('item_count', 0) >= 2 else -0.5,
        'code': lambda e: 1.5 if e.get('language') else 0.5,
    }

    reward_fn = rewards.get(element['type'])
    return reward_fn(element) if reward_fn else 0.0
```

### Quality-Based Rewards

```python
def quality_reward(element):
    """Reward high-quality content indicators."""
    if element['type'] == 'paragraph':
        content = element['content']

        # Reward presence of important words
        important_words = ['important', 'key', 'essential', 'critical']
        has_important = any(word in content.lower() for word in important_words)
        if has_important:
            return 1.5

        # Penalize filler words
        filler_words = ['very', 'really', 'quite', 'somewhat']
        filler_count = sum(content.lower().count(word) for word in filler_words)
        if filler_count > 2:
            return -0.5

    return 0.0
```

## Error Handling

```python
try:
    result = optimizer.optimize(document)
except Exception as e:
    print(f"Optimization failed: {e}")
    # Fallback to simpler optimization or manual review
```

## Debugging and Visualization

```python
# Examine learned policy
policy = optimizer.policy
for state, actions in policy.items():
    print(f"State {state}: {actions}")

# Check value function
values = optimizer.value_function
for state, value in values.items():
    print(f"State {state} value: {value}")

# Analyze reward history
if 'reward_history' in result:
    rewards = result['reward_history']
    print(f"Reward progression: {rewards}")
```


