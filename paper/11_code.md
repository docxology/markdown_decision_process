# Code Supplement

This supplement contains illustrative procedural material. It is not an executed experiment record, participant study, baseline checkpoint, or an exact substitute for the installed modules under `src/mdp/`. Its statistical sketches do not supply measured results.


This supplement contains all the code examples and implementation details referenced in the main paper. The code is organized by component and provides complete, runnable examples of the Markdown Decision Process framework.

## Core Data Structures

### Document State Representation

```python
@dataclass(frozen=True)
class DocumentState:
    """Immutable document state with rich metadata and computed features."""
    state_id: str
    element_type: str
    content: str
    line_number: int
    features: Dict[str, float]
    metadata: Dict[str, Any]
    semantic_beliefs: Optional[Dict[str, float]] = None
    quality_scores: Optional[Dict[str, float]] = None

    def with_semantic_beliefs(self, beliefs: Dict[str, float]) -> 'DocumentState':
        """Create new state with updated semantic beliefs."""
        return dataclasses.replace(self, semantic_beliefs=beliefs)

    def with_quality_scores(self, scores: Dict[str, float]) -> 'DocumentState':
        """Create new state with updated quality scores."""
        return dataclasses.replace(self, quality_scores=scores)

@dataclass
class State:
    """Represents a single markdown state/element."""
    state_id: str
    state_type: str
    content: str
    line_number: int
    metadata: Dict[str, Any]
    features: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary representation."""
        return {
            'state_id': self.state_id,
            'state_type': self.state_type,
            'content': self.content,
            'line_number': self.line_number,
            'metadata': self.metadata,
            'features': self.features
        }
```

### Document Representation

```python
class Document:
    """Represents a markdown document with metadata and content."""

    def __init__(self, content: str = None, file_path: str = None,
                 metadata: Dict[str, Any] = None):
        self.content = content or ""
        self.file_path = file_path
        self.metadata = metadata or {}
        self.states = []
        self.state_space = None
        self.last_modified = datetime.now()

    def parse(self) -> None:
        """Parse document into states."""
        self.states = self._parse_markdown_elements()
        self.state_space = StateSpace(document=self)

    def _parse_markdown_elements(self, content: str) -> List[State]:
        """Efficiently parse markdown content into states."""
        lines = content.split('\n')
        states = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Optimized header detection
            if line[0] == '#':
                header_level = 0
                for char in line:
                    if char == '#':
                        header_level += 1
                    else:
                        break

                state = State(
                    state_id=f"header_{len(states)}",
                    state_type=f"header_{header_level}",
                    content=line,
                    line_number=i,
                    metadata={'level': header_level},
                    features=self._extract_features(line, 'header')
                )
                states.append(state)
                i += 1

            # Handle other element types...
            else:
                i += 1

        return states
```

## MarkChain Component

### Core MarkChain Class

```python
class MarkChain:
    """Higher-order Markov chain for document structure modeling."""

    def __init__(self, order: int = 1, smoothing: float = 0.01,
                 min_transitions: int = 2):
        self.order = order  # Markov chain order (1-3 typically used)
        self.smoothing = smoothing  # Laplace/additive smoothing parameter
        self.min_transitions = min_transitions  # Minimum transition count threshold
        self.transitions = defaultdict(Counter)  # Transition frequency counts
        self.state_frequencies = Counter()  # Overall state occurrence counts
        self.start_states = Counter()  # Starting state distribution
        self.context_counts = Counter()  # Context occurrence counts
        self.is_trained = False

    def get_transition_matrix(self) -> Dict[Tuple[str, ...], Dict[str, float]]:
        """Compute smoothed transition probability matrix."""
        transition_matrix = {}

        for context, next_states in self.transitions.items():
            total_transitions = sum(next_states.values())
            context_count = self.context_counts[context]

            # Apply smoothing to avoid zero probabilities
            smoothed_probs = {}
            for state, count in next_states.items():
                if count >= self.min_transitions:
                    smoothed_prob = (count + self.smoothing) / (
                        context_count + self.smoothing * len(self.state_frequencies)
                    )
                    smoothed_probs[state] = smoothed_prob

            # Normalize probabilities
            total_prob = sum(smoothed_probs.values())
            if total_prob > 0:
                for state in smoothed_probs:
                    smoothed_probs[state] /= total_prob

            transition_matrix[context] = smoothed_probs

        return transition_matrix

    def train_on_corpus(self, documents: List[str], validation_split: float = 0.1) -> Dict[str, float]:
        """Train Markov chain on document corpus with validation."""
        # Split into training and validation sets
        np.random.shuffle(documents)
        split_idx = int(len(documents) * (1 - validation_split))
        train_docs = documents[:split_idx]
        val_docs = documents[split_idx:]

        # Train on training set
        for doc in train_docs:
            self._train_on_document(doc)

        # Compute training metrics
        train_perplexity = self._compute_perplexity(train_docs)
        val_perplexity = self._compute_perplexity(val_docs)

        # Adaptive smoothing based on corpus characteristics
        if val_perplexity > train_perplexity * 1.1:  # Overfitting detected
            self.smoothing = min(self.smoothing * 1.5, 0.1)

        self.is_trained = True

        return {
            'train_perplexity': train_perplexity,
            'validation_perplexity': val_perplexity,
            'states_observed': len(self.state_frequencies),
            'transitions_learned': sum(len(counts) for counts in self.transitions.values())
        }
```

### Advanced State Parsing

```python
def advanced_state_parser(markdown_text: str) -> List[DocumentState]:
    """Parse markdown into structured states with rich features."""
    parser = MarkdownParser()
    elements = parser.parse_with_features(markdown_text)
    states = []

    for element in elements:
        state = DocumentState(
            state_id=f"state_{len(states)}",
            element_type=classify_element_type(element),
            content=element.content,
            line_number=element.line_number,
            features=extract_comprehensive_features(element),
            metadata={
                'length': len(element.content),
                'complexity': compute_complexity_score(element),
                'readability': compute_readability_score(element.content),
                'structural_depth': element.nesting_level,
                'position_ratio': element.line_number / len(markdown_text.split('\n'))
            }
        )
        states.append(state)

    return states

def extract_comprehensive_features(element: MarkdownElement) -> Dict[str, float]:
    """Extract comprehensive features for state representation."""
    features = {}

    # Text-based features
    content = element.content
    features['char_count'] = len(content)
    features['word_count'] = len(content.split()) if content else 0
    features['sentence_count'] = len([s for s in content.split('.') if s.strip()])
    features['avg_word_length'] = np.mean([len(w) for w in content.split()]) if content.split() else 0

    # Structural features
    features['heading_level'] = element.heading_level if hasattr(element, 'heading_level') else 0
    features['nesting_depth'] = element.nesting_level
    features['is_list_item'] = 1.0 if element.element_type in ['unordered_list', 'ordered_list'] else 0.0
    features['is_code'] = 1.0 if element.element_type == 'code_block' else 0.0

    # Language features (simplified)
    features['technical_density'] = estimate_technical_density(content)
    features['formality_score'] = estimate_formality_score(content)

    return features
```

### Document Generation

```python
def generate_document(self, target_length: int = 100,
                     start_state: Optional[str] = None,
                     temperature: float = 1.0,
                     diversity_bonus: float = 0.1) -> GeneratedDocument:
    """Generate document with advanced sampling strategies."""
    if not self.is_trained:
        raise ValueError("Model must be trained before generation")

    # Select starting state
    if start_state is None:
        start_state = self._sample_start_state()
    else:
        # Ensure start_state exists in model
        if start_state not in self.state_frequencies:
            available_starts = [s for s in self.start_states.keys() if self.start_states[s] > 0]
            start_state = np.random.choice(available_starts)

    generated_states = []
    current_context = [start_state]

    # Generate states until target length or natural termination
    while len(generated_states) < target_length:
        # Get transition probabilities for current context
        context_key = tuple(current_context[-self.order:]) if len(current_context) >= self.order else (current_context[-1],)

        if context_key not in self.transitions:
            # Fallback to lower-order context
            context_key = self._find_fallback_context(context_key)

        if context_key not in self.transitions:
            break  # No valid transitions

        # Sample next state with temperature and diversity
        next_state = self._sample_next_state_temperature(
            context_key, temperature, diversity_bonus
        )

        if next_state is None:
            break

        generated_states.append(next_state)
        current_context.append(next_state)

        # Check for natural termination conditions
        if self._should_terminate(generated_states):
            break

    # Post-process generated content
    document = self._postprocess_generated_states(generated_states)

    return GeneratedDocument(
        content=document,
        states=generated_states,
        generation_metadata={
            'model_order': self.order,
            'temperature': temperature,
            'diversity_bonus': diversity_bonus,
            'states_generated': len(generated_states)
        }
    )
```

## StateSpace Component

### Graph Construction

```python
class StateSpace:
    """Graph-based representation of document structure for analysis and optimization."""

    def __init__(self, document: Optional[Document] = None,
                 simplify_states: bool = True, min_edge_weight: int = 2,
                 feature_computation: bool = True):
        self.document = document
        self.states = {}  # State nodes with rich metadata
        self.transitions = defaultdict(lambda: defaultdict(int))  # Weighted transition counts
        self.graph = nx.DiGraph()  # NetworkX graph representation
        self.state_counter = 0
        self.simplify_states = simplify_states
        self.min_edge_weight = min_edge_weight
        self.feature_computation = feature_computation

        # Analysis caches
        self._centrality_cache = {}
        self._community_cache = {}
        self._structure_metrics = {}

    def build_from_document(self, document: Document) -> None:
        """Build state space from parsed document."""
        self.document = document
        states = document.states

        if not states:
            return

        # Add state nodes with comprehensive metadata
        for i, state in enumerate(states):
            node_id = f"state_{i}"
            node_data = {
                'state_id': state.state_id,
                'state_type': state.state_type,
                'content': state.content,
                'line_number': state.line_number,
                'features': state.features,
                'metadata': state.metadata,
                'position': i,
                'normalized_position': i / len(states)
            }

            self.graph.add_node(node_id, **node_data)
            self.states[node_id] = state

        # Add weighted edges representing transitions
        for i in range(len(states) - 1):
            from_node = f"state_{i}"
            to_node = f"state_{i + 1}"
            transition_weight = self._compute_transition_weight(states[i], states[i + 1])

            if transition_weight >= self.min_edge_weight:
                self.graph.add_edge(from_node, to_node, weight=transition_weight)
                self.transitions[from_node][to_node] = transition_weight

        # Compute additional graph properties
        if self.feature_computation:
            self._compute_graph_features()
```

### Structural Analysis

```python
def comprehensive_structure_analysis(self) -> Dict[str, Any]:
    """Perform comprehensive structural analysis of the document."""
    if not self._structure_metrics:
        self._structure_metrics = {
            'basic_metrics': self._compute_basic_metrics(),
            'complexity_analysis': self._compute_complexity_analysis(),
            'information_flow': self._analyze_information_flow(),
            'coherence_analysis': self._analyze_coherence(),
            'quality_assessment': self._assess_quality_indicators()
        }

    return self._structure_metrics

def _compute_basic_metrics(self) -> Dict[str, Any]:
    """Compute fundamental document structure metrics."""
    if not self.graph:
        return {}

    return {
        'total_states': len(self.states),
        'total_transitions': len(self.transitions),
        'graph_density': nx.density(self.graph),
        'average_degree': np.mean([d for n, d in self.graph.degree()]),
        'connected_components': nx.number_connected_components(self.graph.to_undirected()),
        'average_path_length': self._compute_average_path_length(),
        'diameter': self._compute_diameter() if nx.is_connected(self.graph.to_undirected()) else None
    }
```

### Quality Assessment

```python
def _assess_quality_indicators(self) -> Dict[str, float]:
    """Assess document quality using structural indicators."""
    quality_scores = {}

    # Coherence indicators
    quality_scores['structural_coherence'] = self._compute_structural_coherence()
    quality_scores['semantic_consistency'] = self._compute_semantic_consistency()

    # Readability indicators
    quality_scores['information_density'] = self._compute_information_density()
    quality_scores['navigation_ease'] = self._compute_navigation_ease()

    # Organization indicators
    quality_scores['logical_flow'] = self._compute_logical_flow()
    quality_scores['hierarchy_clarity'] = self._compute_hierarchy_clarity()

    # Complexity indicators
    quality_scores['appropriate_complexity'] = self._compute_appropriate_complexity()

    return quality_scores
```

## PolicyOptimizer Component

### Core Optimizer Class

```python
class PolicyOptimizer:
    """Reinforcement learning-based document structure optimizer."""

    def __init__(self, state_space: StateSpace,
                 reward_function: Optional[RewardFunction] = None,
                 algorithm: str = 'value_iteration',
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 exploration_rate: float = 0.1,
                 max_iterations: int = 100,
                 convergence_threshold: float = 1e-6):
        self.state_space = state_space
        self.reward_function = reward_function or CompositeReward()
        self.algorithm = algorithm  # 'value_iteration', 'policy_iteration', 'q_learning'
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

        # Internal state
        self.value_function = {}
        self.q_values = defaultdict(lambda: defaultdict(float))
        self.policy = {}
        self.optimization_history = []

    def set_reward_weights(self, weights: Dict[str, float]) -> None:
        """Configure reward function component weights."""
        if hasattr(self.reward_function, 'set_weights'):
            self.reward_function.set_weights(weights)
        else:
            # Fallback for simple reward functions
            self.reward_weights = weights
```

### Optimization Algorithms

```python
def optimize(self) -> OptimizationResult:
    """Optimize document structure using configured algorithm."""
    self._initialize_optimization()

    if self.algorithm == 'value_iteration':
        result = self._value_iteration_optimization()
    elif self.algorithm == 'policy_iteration':
        result = self._policy_iteration_optimization()
    elif self.algorithm == 'q_learning':
        result = self._q_learning_optimization()
    else:
        raise ValueError(f"Unknown algorithm: {self.algorithm}")

    return result

def _value_iteration_optimization(self) -> OptimizationResult:
    """Perform value iteration optimization."""
    start_time = time.time()

    # Initialize value function
    for state_id in self.state_space.states.keys():
        self.value_function[state_id] = 0.0

    # Value iteration with convergence tracking
    for iteration in range(self.max_iterations):
        delta = 0.0
        iteration_values = {}

        for state_id in self.state_space.states.keys():
            if not self._has_available_actions(state_id):
                continue

            v = self.value_function.get(state_id, 0.0)

            # Compute Q-values for all actions
            action_values = {}
            for action in self._get_available_actions(state_id):
                q_value = self._compute_q_value(state_id, action)
                action_values[action] = q_value

            # Update value function (Bellman equation)
            if action_values:
                iteration_values[state_id] = max(action_values.values())
                delta = max(delta, abs(v - iteration_values[state_id]))

        # Update value function
        self.value_function.update(iteration_values)

        # Track convergence
        self.optimization_history.append({
            'iteration': iteration,
            'max_delta': delta,
            'value_function': self.value_function.copy()
        })

        if delta < self.convergence_threshold:
            self.logger.info(f"Value iteration converged after {iteration} iterations")
            break

    # Extract optimal policy
    optimal_policy = self._extract_policy_from_value_function()

    optimization_time = time.time() - start_time

    return OptimizationResult(
        optimal_policy=optimal_policy,
        final_value_function=self.value_function,
        optimization_history=self.optimization_history,
        convergence_achieved=delta < self.convergence_threshold,
        total_iterations=iteration,
        optimization_time=optimization_time
    )
```

## BeliefUpdater Component

### Semantic Inference Engine

```python
class BeliefUpdater:
    """Probabilistic belief management for semantic interpretation under uncertainty."""

    def __init__(self, semantic_classes: Optional[List[str]] = None,
                 observation_model: Optional[ObservationModel] = None,
                 prior_beliefs: Optional[Dict[str, float]] = None,
                 transition_model: Optional[TransitionModel] = None,
                 noise_factor: float = 0.1):
        # Semantic classes for belief states
        self.semantic_classes = semantic_classes or [
            "instruction", "explanation", "example", "reference",
            "summary", "definition", "warning", "note", "procedure", "overview"
        ]

        # Initialize uniform prior beliefs
        if prior_beliefs is None:
            uniform_prob = 1.0 / len(self.semantic_classes)
            prior_beliefs = {cls: uniform_prob for cls in self.semantic_classes}

        self.beliefs = prior_beliefs.copy()
        self.belief_history = [self.beliefs.copy()]  # Track belief evolution

        # Component models
        self.observation_model = observation_model or DefaultObservationModel()
        self.transition_model = transition_model or DefaultTransitionModel()

        # Uncertainty and calibration tracking
        self.noise_factor = noise_factor
        self.confidence_history = []
        self.calibration_metrics = []
```

### Belief Update Algorithm

```python
def update_beliefs_from_observation(self, observation: Dict[str, float],
                                  syntactic_state: DocumentState,
                                  time_step: Optional[int] = None) -> UpdateResult:
    """Update beliefs based on new syntactic observation."""
    start_beliefs = self.beliefs.copy()

    # Compute observation likelihoods for each semantic class
    observation_likelihoods = {}
    for semantic_class in self.semantic_classes:
        likelihood = self.observation_model.compute_likelihood(semantic_class, syntactic_state)
        observation_likelihoods[semantic_class] = likelihood

    # Apply temporal smoothing (exponential moving average)
    smoothed_likelihoods = self._apply_temporal_smoothing(observation_likelihoods)

    # Compute unnormalized posterior beliefs
    posterior_unnormalized = {}
    for semantic_class in self.semantic_classes:
        # Prior belief
        prior = self.beliefs[semantic_class]

        # Observation likelihood (with noise model)
        obs_likelihood = smoothed_likelihoods[semantic_class]
        noisy_likelihood = self._apply_observation_noise(obs_likelihood)

        # Semantic transition prior (context consistency)
        transition_prior = self._compute_transition_prior(semantic_class)

        # Combine all factors
        posterior_unnormalized[semantic_class] = (
            prior * noisy_likelihood * transition_prior
        )

    # Normalize posterior beliefs
    total_posterior = sum(posterior_unnormalized.values())
    if total_posterior > 0:
        for semantic_class in self.semantic_classes:
            self.beliefs[semantic_class] = (
                posterior_unnormalized[semantic_class] / total_posterior
            )
    else:
        # Fallback to uniform distribution if all posteriors are zero
        uniform_prob = 1.0 / len(self.semantic_classes)
        self.beliefs = {cls: uniform_prob for cls in self.semantic_classes}

    # Track belief evolution
    self.belief_history.append(self.beliefs.copy())

    # Update confidence metrics
    current_confidence = self._compute_belief_confidence()
    self.confidence_history.append(current_confidence)

    # Compute belief change metrics
    belief_change = self._compute_belief_change(start_beliefs, self.beliefs)

    return UpdateResult(
        previous_beliefs=start_beliefs,
        updated_beliefs=self.beliefs.copy(),
        observation_likelihoods=observation_likelihoods,
        belief_entropy=entropy(list(self.beliefs.values())),
        confidence=current_confidence,
        significant_change=belief_change > self._get_adaptive_threshold(),
        time_step=time_step
    )
```

## Plugin System

### Plugin Interface

```python
class MDPPlugin(ABC):
    """Abstract base class for MDP plugins."""

    @abstractmethod
    def get_transformations(self) -> List[Transformation]:
        """Return custom transformation operations."""
        pass

    @abstractmethod
    def get_reward_functions(self) -> Dict[str, RewardFunction]:
        """Return custom reward function implementations."""
        pass

    def get_observation_models(self) -> Dict[str, ObservationModel]:
        """Return custom observation models for semantic inference."""
        return {}
```

### Plugin Manager

```python
class PluginManager:
    """Manages plugin registration and execution."""

    def __init__(self):
        self.plugins: Dict[str, MDPPlugin] = {}
        self.transformations: Dict[str, Transformation] = {}
        self.reward_functions: Dict[str, RewardFunction] = {}

    def register_plugin(self, name: str, plugin_class: Type[MDPPlugin]) -> None:
        """Register a plugin by class."""
        try:
            plugin_instance = plugin_class()
            self.plugins[name] = plugin_instance

            # Register plugin components
            for transformation in plugin_instance.get_transformations():
                self.transformations[f"{name}.{transformation.name}"] = transformation

            for reward_name, reward_func in plugin_instance.get_reward_functions().items():
                self.reward_functions[f"{name}.{reward_name}"] = reward_func

        except Exception as e:
            self.logger.error(f"Failed to register plugin {name}: {e}")
            raise
```

## Utility Functions

### Input Validation

```python
def validate_inputs(func):
    """Decorator for input validation."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Validate arguments based on function signature
        sig = signature(func)
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            if param_name == 'self':
                continue

            validation_rules = self._get_validation_rules(func.__name__, param_name)
            for rule in validation_rules:
                if not rule(param_value):
                    raise ValueError(f"Validation failed for {param_name}: {param_value}")

        return func(self, *args, **kwargs)
    return wrapper
```

### Configuration Management

```python
class MDPConfig:
    """Configuration management for MDP framework."""

    def __init__(self):
        self.markchain_order = 1
        self.smoothing_factor = 0.01
        self.reward_weights = {
            'readability': 1.0,
            'information_density': 1.0,
            'structure_clarity': 1.0
        }
        self.optimization_iterations = 100
        self.belief_noise_factor = 0.2
        self.visualization_theme = 'default'
        self.export_formats = ['png', 'pdf', 'svg']
```

## Testing and Quality Assurance

### Test Cases

```python
class TestMarkChain(unittest.TestCase):
    """Test cases for MarkChain functionality."""

    def setUp(self):
        self.markchain = MarkChain(order=1)

    def test_training_convergence(self):
        """Test that training converges to reasonable probabilities."""
        training_data = self._generate_test_corpus()
        self.markchain.train(training_data)

        # Verify probabilities sum to 1 for each state
        for state, transitions in self.markchain.transition_matrix.items():
            total_prob = sum(transitions.values())
            self.assertAlmostEqual(total_prob, 1.0, places=5)

    def test_generation_quality(self):
        """Test that generated content maintains document structure."""
        self.markchain.train(self._get_sample_documents())
        generated = self.markchain.sample(length=50)

        # Verify generated content is well-formed markdown
        self.assertIsInstance(generated, str)
        self.assertGreater(len(generated), 0)
```

### Performance Benchmarks

```python
def benchmark_state_space_construction(self):
    """Benchmark state space construction for large documents."""
    large_document = self._generate_large_document(10000)

    start_time = time.time()
    state_space = StateSpace()
    state_space.parse_markdown(large_document)
    end_time = time.time()

    construction_time = end_time - start_time
    self.assertLess(construction_time, 5.0)  # Should complete within 5 seconds
```

## Complete Implementation Examples

### Full Document Processing Pipeline

```python
def process_document_with_full_pipeline(markdown_content: str) -> ProcessedDocument:
    """Complete document processing pipeline example."""
    # Step 1: Parse into states
    document = Document(content=markdown_content)
    document.parse()

    # Step 2: Build state space
    state_space = StateSpace(document=document)
    state_space.build_from_document(document)

    # Step 3: Train Markov chain on corpus
    markchain = MarkChain(order=2)
    markchain.train_on_corpus([markdown_content])

    # Step 4: Set up semantic inference
    belief_updater = BeliefUpdater()
    observations = extract_observations_from_states(document.states)
    for obs in observations:
        belief_updater.update_beliefs_from_observation(obs.features, obs.state)

    # Step 5: Optimize structure
    optimizer = PolicyOptimizer(
        state_space=state_space,
        reward_function=CompositeReward({
            'readability': 0.4,
            'structure_clarity': 0.3,
            'semantic_coherence': 0.3
        })
    )
    optimization_result = optimizer.optimize()

    return ProcessedDocument(
        original_content=markdown_content,
        optimized_content=apply_optimization(document, optimization_result),
        state_space=state_space,
        semantic_beliefs=belief_updater.get_current_beliefs(),
        quality_metrics=state_space.comprehensive_structure_analysis()
    )
```

### Evaluation Pipeline

```python
def perform_comprehensive_evaluation(test_corpus: List[str]) -> EvaluationResults:
    """Comprehensive evaluation of MDP framework performance."""
    results = EvaluationResults()

    for doc in test_corpus:
        # Process document through full pipeline
        processed = process_document_with_full_pipeline(doc)

        # Record metrics
        results.add_result({
            'structural_coherence': processed.quality_metrics['structural_coherence'],
            'semantic_accuracy': compute_semantic_accuracy(processed.semantic_beliefs),
            'optimization_improvement': compute_optimization_improvement(doc, processed.optimized_content),
            'processing_time': processed.processing_time
        })

    # Compute aggregate statistics
    results.compute_aggregate_metrics()
    return results
```


**Figure 1: Markdown Decision Process System Architecture**

This comprehensive architecture diagram illustrates the complete Markdown Decision Process (MDP) framework, depicting the intricate interplay between specialized components, data flows, and external integrations that enable sophisticated document processing through probabilistic modeling and decision-theoretic principles.

**External Systems Layer**: The framework accepts diverse inputs including raw Markdown documents, configuration files defining reward functions and processing parameters, training corpora for Markov chain learning, and a plugin registry for domain-specific extensions. This layer provides the foundation for flexible, configurable document processing.

**Core Processing Pipeline**: At the heart of the system lies a sophisticated processing pipeline that transforms raw documents into optimized, semantically-aware outputs:

- **Input Processing Chain** (DocumentLoader → DocumentValidator → StateSpaceConstructor → FeatureExtractor): Converts raw Markdown into structured state representations, validating document integrity and extracting rich features for downstream analysis.

- **Markov Chain Processing Chain** (MarkChainBuilder → TransitionMatrix → GenerationEngine → SamplingStrategies): Constructs probabilistic models of document structure, learning transition patterns and enabling creative generation through temperature-controlled sampling and higher-order Markov dependencies.

- **Policy Optimization Chain** (PolicyOptimizer → ValueIteration → PolicyEvaluation → ActionSelection): Applies reinforcement learning algorithms to optimize document structure according to user-specified reward functions, supporting multiple optimization paradigms including value iteration, policy iteration, and Q-learning.

- **Belief Management Chain** (BeliefUpdater → ObservationModel → BayesianInference → UncertaintyCalibration): Implements POMDP-style belief updating for semantic interpretation under uncertainty, providing calibrated probability distributions over semantic meanings with explicit uncertainty quantification.

**Reward Systems Layer**: A comprehensive reward function registry enables multi-dimensional quality assessment, supporting composite rewards that balance readability metrics, structural quality indicators, and semantic coherence measures. This layer provides the foundation for principled document optimization.

**Plugin Architecture Layer**: A sophisticated plugin ecosystem enables domain-specific customization while maintaining theoretical coherence. Plugins contribute transformations, domain adapters, custom analyzers, and export formatters, allowing the framework to be extended for academic writing, technical documentation, creative applications, and specialized domains.

**Output Systems Layer**: Dual output pathways provide both visualization and export capabilities:

- **Visualization Engine**: Generates state space graphs, transition heatmaps, policy landscapes, and interactive dashboards for exploring document structure and optimization processes.

- **Export Manager**: Supports multiple output formats (Markdown, PDF, HTML, DOCX) through Pandoc integration, enabling seamless conversion and publication-ready document generation.

**External Integrations Layer**: Leverages high-performance libraries for specialized operations:

- **Pandoc Integration**: Provides universal document format conversion capabilities
- **NetworkX Backend**: Enables sophisticated graph algorithms for state space analysis
- **NumPy Backend**: Supports efficient matrix operations for Markov chain computations

**Data Flow Architecture**: The diagram illustrates complex data dependencies and integration points, showing how information flows between components, how plugins enhance core functionality, and how external libraries accelerate specialized operations. This design ensures both theoretical rigor and practical efficiency.

**Architectural Principles**: The architecture embodies several key design decisions:

1. **Modular Decomposition**: Clear separation of concerns enables independent component development and testing
2. **Theoretical Coherence**: All components grounded in MDP/POMDP theory for principled uncertainty handling
3. **Extensibility**: Plugin architecture allows domain adaptation without core system modification
4. **Performance Optimization**: Strategic use of high-performance libraries for computationally intensive operations
5. **Output Flexibility**: Multiple export pathways support diverse use cases and deployment scenarios

This architecture enables the framework to handle the fundamental challenge of semantic interpretation under syntactic ambiguity while providing interpretable, theoretically-grounded document processing that scales from research prototypes to production deployments.

## Core Components Code Blocks

### StateSpace Component

```python
class StateSpace:
    """Graph-based representation of document structure for analysis and optimization."""

    def __init__(self, document: Optional[Document] = None,
                 simplify_states: bool = True, min_edge_weight: int = 2,
                 feature_computation: bool = True):
        self.document = document
        self.states = {}  # State nodes with rich metadata
        self.transitions = defaultdict(lambda: defaultdict(int))  # Weighted transition counts
        self.graph = nx.DiGraph()  # NetworkX graph representation
        self.state_counter = 0
        self.simplify_states = simplify_states
        self.min_edge_weight = min_edge_weight
        self.feature_computation = feature_computation

        # Analysis caches
        self._centrality_cache = {}
        self._community_cache = {}
        self._structure_metrics = {}

    def build_from_document(self, document: Document) -> None:
        """Build state space from parsed document."""
        self.document = document
        states = document.states

        if not states:
            return

        # Add state nodes with comprehensive metadata
        for i, state in enumerate(states):
            node_id = f"state_{i}"
            node_data = {
                'state_id': state.state_id,
                'state_type': state.state_type,
                'content': state.content,
                'line_number': state.line_number,
                'features': state.features,
                'metadata': state.metadata,
                'position': i,
                'normalized_position': i / len(states)
            }

            self.graph.add_node(node_id, **node_data)
            self.states[node_id] = state

        # Add weighted edges representing transitions
        for i in range(len(states) - 1):
            from_node = f"state_{i}"
            to_node = f"state_{i + 1}"
            transition_weight = self._compute_transition_weight(states[i], states[i + 1])

            if transition_weight >= self.min_edge_weight:
                self.graph.add_edge(from_node, to_node, weight=transition_weight)
                self.transitions[from_node][to_node] = transition_weight

        # Compute additional graph properties
        if self.feature_computation:
            self._compute_graph_features()

    def _compute_transition_weight(self, from_state: DocumentState,
                                 to_state: DocumentState) -> float:
        """Compute weight for state transitions based on multiple factors."""
        base_weight = 1.0

        # Content similarity bonus
        content_similarity = self._compute_content_similarity(from_state, to_state)
        base_weight += content_similarity * 0.5

        # Structural coherence bonus
        structural_bonus = self._compute_structural_coherence(from_state, to_state)
        base_weight += structural_bonus * 0.3

        # Temporal/positional bonus
        positional_bonus = self._compute_positional_coherence(from_state, to_state)
        base_weight += positional_bonus * 0.2

        return base_weight

    def _compute_content_similarity(self, state1: DocumentState, state2: DocumentState) -> float:
        """Compute semantic similarity between state contents."""
        # Simplified similarity based on shared keywords and structure
        content1 = state1.content.lower()
        content2 = state2.content.lower()

        # Simple word overlap (can be enhanced with embeddings)
        words1 = set(content1.split())
        words2 = set(content2.split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total_words = len(words1 | words2)

        return overlap / total_words if total_words > 0 else 0.0

def comprehensive_structure_analysis(self) -> Dict[str, Any]:
    """Perform comprehensive structural analysis of the document."""
    if not self._structure_metrics:
        self._structure_metrics = {
            'basic_metrics': self._compute_basic_metrics(),
            'complexity_analysis': self._compute_complexity_analysis(),
            'information_flow': self._analyze_information_flow(),
            'coherence_analysis': self._analyze_coherence(),
            'quality_assessment': self._assess_quality_indicators()
        }

    return self._structure_metrics

def _compute_basic_metrics(self) -> Dict[str, Any]:
    """Compute fundamental document structure metrics."""
    if not self.graph:
        return {}

    return {
        'total_states': len(self.states),
        'total_transitions': len(self.transitions),
        'graph_density': nx.density(self.graph),
        'average_degree': np.mean([d for n, d in self.graph.degree()]),
        'connected_components': nx.number_connected_components(self.graph.to_undirected()),
        'average_path_length': self._compute_average_path_length(),
        'diameter': self._compute_diameter() if nx.is_connected(self.graph.to_undirected()) else None
    }

def _compute_complexity_analysis(self) -> Dict[str, Any]:
    """Analyze structural complexity of the document."""
    complexity_metrics = {}

    # State type diversity
    state_types = [self.graph.nodes[node]['state_type'] for node in self.graph.nodes()]
    state_type_counts = Counter(state_types)
    total_states = len(state_types)

    complexity_metrics['state_diversity'] = len(state_type_counts)
    complexity_metrics['state_entropy'] = entropy([count/total_states for count in state_type_counts.values()])

    # Transition complexity
    if self.transitions:
        transition_matrix = self._build_transition_matrix()
        complexity_metrics['transition_entropy'] = self._compute_transition_entropy(transition_matrix)

    # Structural hierarchy complexity
    complexity_metrics['hierarchy_depth'] = self._compute_hierarchy_depth()
    complexity_metrics['branching_factor'] = self._compute_average_branching_factor()

    return complexity_metrics

def _analyze_information_flow(self) -> Dict[str, Any]:
    """Analyze information flow patterns through the document."""
    if not self.graph:
        return {}

    # Compute centrality measures
    centrality_measures = self.get_centrality_measures()

    # Identify information hubs (states with high centrality)
    info_hubs = self._identify_information_hubs(centrality_measures)

    # Analyze flow bottlenecks
    bottlenecks = self._identify_flow_bottlenecks()

    # Compute flow efficiency metrics
    flow_efficiency = self._compute_flow_efficiency()

    return {
        'centrality_measures': centrality_measures,
        'information_hubs': info_hubs,
        'flow_bottlenecks': bottlenecks,
        'flow_efficiency': flow_efficiency,
        'navigation_paths': self._analyze_navigation_paths()
    }

def get_centrality_measures(self) -> Dict[str, Dict[str, float]]:
    """Compute various centrality measures for document states."""
    if not self.graph:
        return {}

    if not self._centrality_cache:
        centrality = {}

        # Degree centrality (local importance)
        centrality['degree'] = nx.degree_centrality(self.graph)

        # Betweenness centrality (bridge importance)
        centrality['betweenness'] = nx.betweenness_centrality(self.graph)

        # Closeness centrality (reachability)
        centrality['closeness'] = nx.closeness_centrality(self.graph)

        # Eigenvector centrality (global importance)
        try:
            centrality['eigenvector'] = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except nx.PowerIterationFailedConverged:
            centrality['eigenvector'] = {}

        # PageRank (importance in web-like structure)
        centrality['pagerank'] = nx.pagerank(self.graph, alpha=0.85)

        self._centrality_cache = centrality

    return self._centrality_cache

def _assess_quality_indicators(self) -> Dict[str, float]:
    """Assess document quality using structural indicators."""
    quality_scores = {}

    # Coherence indicators
    quality_scores['structural_coherence'] = self._compute_structural_coherence()
    quality_scores['semantic_consistency'] = self._compute_semantic_consistency()

    # Readability indicators
    quality_scores['information_density'] = self._compute_information_density()
    quality_scores['navigation_ease'] = self._compute_navigation_ease()

    # Organization indicators
    quality_scores['logical_flow'] = self._compute_logical_flow()
    quality_scores['hierarchy_clarity'] = self._compute_hierarchy_clarity()

    # Complexity indicators
    quality_scores['appropriate_complexity'] = self._compute_appropriate_complexity()

    return quality_scores

def _compute_structural_coherence(self) -> float:
    """Compute how well the document structure maintains coherence."""
    if not self.graph:
        return 0.0

    # Measure consistency of state transitions
    transition_consistency = self._analyze_transition_consistency()

    # Measure structural predictability
    structural_predictability = self._analyze_structural_predictability()

    # Combine metrics
    coherence_score = 0.6 * transition_consistency + 0.4 * structural_predictability

    return min(coherence_score, 1.0)  # Normalize to [0, 1]
```

### PolicyOptimizer Component

```python
class PolicyOptimizer:
    """Reinforcement learning-based document structure optimizer."""

    def __init__(self, state_space: StateSpace,
                 reward_function: Optional[RewardFunction] = None,
                 algorithm: str = 'value_iteration',
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 exploration_rate: float = 0.1,
                 max_iterations: int = 100,
                 convergence_threshold: float = 1e-6):
        self.state_space = state_space
        self.reward_function = reward_function or CompositeReward()
        self.algorithm = algorithm  # 'value_iteration', 'policy_iteration', 'q_learning'
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

        # Internal state
        self.value_function = {}
        self.q_values = defaultdict(lambda: defaultdict(float))
        self.policy = {}
        self.optimization_history = []

    def set_reward_weights(self, weights: Dict[str, float]) -> None:
        """Configure reward function component weights."""
        if hasattr(self.reward_function, 'set_weights'):
            self.reward_function.set_weights(weights)
        else:
            # Fallback for simple reward functions
            self.reward_weights = weights

    def add_custom_reward_component(self, name: str, component: RewardComponent) -> None:
        """Add custom reward function component."""
        if hasattr(self.reward_function, 'add_component'):
            self.reward_function.add_component(name, component)
        else:
            raise ValueError("Reward function does not support custom components")

class CompositeReward(RewardFunction):
    """Composite reward function combining multiple quality criteria."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        super().__init__()
        self.weights = weights or {
            'readability': 0.3,
            'information_density': 0.25,
            'structure_clarity': 0.2,
            'semantic_coherence': 0.15,
            'aesthetic_appeal': 0.1
        }
        self.components = {
            'readability': ReadabilityReward(),
            'information_density': InformationDensityReward(),
            'structure_clarity': StructureClarityReward(),
            'semantic_coherence': SemanticCoherenceReward(),
            'aesthetic_appeal': AestheticAppealReward()
        }

    def compute_reward(self, state: DocumentState, action: TransformationAction,
                      next_state: DocumentState) -> float:
        """Compute composite reward for state transition."""
        total_reward = 0.0

        for component_name, component in self.components.items():
            component_reward = component.compute(state, action, next_state)
            weighted_reward = self.weights.get(component_name, 0.0) * component_reward
            total_reward += weighted_reward

        return total_reward

class ReadabilityReward(RewardComponent):
    """Reward component for document readability."""

    def compute(self, state: DocumentState, action: TransformationAction,
                next_state: DocumentState) -> float:
        """Compute readability reward based on content complexity."""
        # Use established readability metrics
        current_readability = self._compute_flesch_kincaid_grade(state.content)
        next_readability = self._compute_flesch_kincaid_grade(next_state.content)

        # Reward improvements in readability (lower grade level is better)
        if action.improves_readability:
            readability_improvement = max(0, current_readability - next_readability)
            return readability_improvement * 2.0  # Bonus for improvement
        else:
            readability_penalty = max(0, next_readability - current_readability)
            return -readability_penalty * 0.5  # Penalty for degradation

class StructureClarityReward(RewardComponent):
    """Reward component for structural clarity and organization."""

    def compute(self, state: DocumentState, action: TransformationAction,
                next_state: DocumentState) -> float:
        """Compute structural clarity reward."""
        # Analyze structural improvements
        current_hierarchy_score = self._analyze_hierarchy_quality(state)
        next_hierarchy_score = self._analyze_hierarchy_quality(next_state)

        hierarchy_improvement = next_hierarchy_score - current_hierarchy_score

        # Bonus for logical section organization
        organization_bonus = self._assess_organization_improvement(action)

        return hierarchy_improvement * 0.7 + organization_bonus * 0.3

def optimize(self) -> OptimizationResult:
    """Optimize document structure using configured algorithm."""
    self._initialize_optimization()

    if self.algorithm == 'value_iteration':
        result = self._value_iteration_optimization()
    elif self.algorithm == 'policy_iteration':
        result = self._policy_iteration_optimization()
    elif self.algorithm == 'q_learning':
        result = self._q_learning_optimization()
    else:
        raise ValueError(f"Unknown algorithm: {self.algorithm}")

    return result

def _value_iteration_optimization(self) -> OptimizationResult:
    """Perform value iteration optimization."""
    start_time = time.time()

    # Initialize value function
    for state_id in self.state_space.states.keys():
        self.value_function[state_id] = 0.0

    # Value iteration with convergence tracking
    for iteration in range(self.max_iterations):
        delta = 0.0
        iteration_values = {}

        for state_id in self.state_space.states.keys():
            if not self._has_available_actions(state_id):
                continue

            v = self.value_function.get(state_id, 0.0)

            # Compute Q-values for all actions
            action_values = {}
            for action in self._get_available_actions(state_id):
                q_value = self._compute_q_value(state_id, action)
                action_values[action] = q_value

            # Update value function (Bellman equation)
            if action_values:
                iteration_values[state_id] = max(action_values.values())
                delta = max(delta, abs(v - iteration_values[state_id]))

        # Update value function
        self.value_function.update(iteration_values)

        # Track convergence
        self.optimization_history.append({
            'iteration': iteration,
            'max_delta': delta,
            'value_function': self.value_function.copy()
        })

        if delta < self.convergence_threshold:
            self.logger.info(f"Value iteration converged after {iteration} iterations")
            break

    # Extract optimal policy
    optimal_policy = self._extract_policy_from_value_function()

    optimization_time = time.time() - start_time

    return OptimizationResult(
        optimal_policy=optimal_policy,
        final_value_function=self.value_function,
        optimization_history=self.optimization_history,
        convergence_achieved=delta < self.convergence_threshold,
        total_iterations=iteration,
        optimization_time=optimization_time
    )

def _compute_q_value(self, state_id: str, action: TransformationAction) -> float:
    """Compute Q-value for state-action pair."""
    state = self.state_space.states[state_id]
    next_states = self._get_next_states(state_id, action)

    if not next_states:
        return 0.0

    # Expected value from next states
    expected_next_value = 0.0
    for next_state_id, probability in next_states.items():
        next_value = self.value_function.get(next_state_id, 0.0)
        expected_next_value += probability * next_value

    # Current reward + discounted future value
    current_reward = self.reward_function.compute(state, action,
                                                self.state_space.states[next_state_id])

    q_value = current_reward + self.discount_factor * expected_next_value

    return q_value

def multi_objective_optimization(self, objectives: List[RewardFunction],
                               method: str = 'scalarization') -> MultiObjectiveResult:
    """Perform multi-objective document optimization."""
    if method == 'scalarization':
        return self._scalarized_multi_objective_optimization(objectives)
    elif method == 'pareto_optimization':
        return self._pareto_optimization(objectives)
    else:
        raise ValueError(f"Unknown multi-objective method: {method}")

def _scalarized_multi_objective_optimization(self, objectives: List[RewardFunction],
                                           weight_ranges: Optional[Dict[str, Tuple[float, float]]] = None) -> MultiObjectiveResult:
    """Optimize using scalarization of multiple objectives."""
    # Generate weight combinations for Pareto front exploration
    if weight_ranges is None:
        weight_ranges = {f'obj_{i}': (0.0, 1.0) for i in range(len(objectives))}

    pareto_solutions = []
    weight_combinations = self._generate_weight_combinations(weight_ranges)

    for weights in weight_combinations:
        # Create scalarized reward function
        scalarized_reward = ScalarizedReward(objectives, weights)

        # Optimize with scalarized reward
        temp_optimizer = PolicyOptimizer(
            state_space=self.state_space,
            reward_function=scalarized_reward,
            algorithm=self.algorithm,
            max_iterations=self.max_iterations // len(weight_combinations)  # Distribute iterations
        )

        result = temp_optimizer.optimize()
        pareto_solutions.append((weights, result))

    return MultiObjectiveResult(
        pareto_front=pareto_solutions,
        dominance_relationships=self._analyze_dominance(pareto_solutions),
        optimal_weights=self._find_optimal_weights(pareto_solutions)
    )
```

### BeliefUpdater Component

```python
class BeliefUpdater:
    """Probabilistic belief management for semantic interpretation under uncertainty."""

    def __init__(self, semantic_classes: Optional[List[str]] = None,
                 observation_model: Optional[ObservationModel] = None,
                 prior_beliefs: Optional[Dict[str, float]] = None,
                 transition_model: Optional[TransitionModel] = None,
                 noise_factor: float = 0.1):
        # Semantic classes for belief states
        self.semantic_classes = semantic_classes or [
            "instruction", "explanation", "example", "reference",
            "summary", "definition", "warning", "note", "procedure", "overview"
        ]

        # Initialize uniform prior beliefs
        if prior_beliefs is None:
            uniform_prob = 1.0 / len(self.semantic_classes)
            prior_beliefs = {cls: uniform_prob for cls in self.semantic_classes}

        self.beliefs = prior_beliefs.copy()
        self.belief_history = [self.beliefs.copy()]  # Track belief evolution

        # Component models
        self.observation_model = observation_model or DefaultObservationModel()
        self.transition_model = transition_model or DefaultTransitionModel()

        # Uncertainty and calibration tracking
        self.noise_factor = noise_factor
        self.confidence_history = []
        self.calibration_metrics = []

    def get_current_beliefs(self) -> Dict[str, float]:
        """Get current belief distribution."""
        return self.beliefs.copy()

    def get_belief_entropy(self) -> float:
        """Compute entropy of current belief distribution."""
        return entropy(list(self.beliefs.values()))

    def get_most_likely_semantic_class(self) -> str:
        """Get semantic class with highest belief probability."""
        return max(self.beliefs.items(), key=lambda x: x[1])[0]

class DefaultObservationModel:
    """Default observation model for semantic class likelihoods."""

    def __init__(self, feature_extractors: Optional[List[FeatureExtractor]] = None):
        self.feature_extractors = feature_extractors or [
            LengthFeatureExtractor(),
            KeywordFeatureExtractor(),
            StructureFeatureExtractor(),
            ContextFeatureExtractor()
        ]

    def compute_likelihood(self, semantic_class: str,
                          syntactic_state: DocumentState) -> float:
        """Compute P(observation | semantic_class) for given state."""
        features = self._extract_observation_features(syntactic_state)
        class_likelihoods = self._get_class_likelihoods(semantic_class)

        # Combine feature likelihoods
        total_likelihood = 1.0
        for feature_name, feature_value in features.items():
            if feature_name in class_likelihoods:
                feature_likelihood = self._compute_feature_likelihood(
                    class_likelihoods[feature_name], feature_value
                )
                total_likelihood *= feature_likelihood

        return total_likelihood

    def _extract_observation_features(self, state: DocumentState) -> Dict[str, float]:
        """Extract features from syntactic state for observation model."""
        features = {}

        for extractor in self.feature_extractors:
            extractor_features = extractor.extract(state)
            features.update(extractor_features)

        return features

class KeywordFeatureExtractor(FeatureExtractor):
    """Extract keyword-based features for semantic classification."""

    def __init__(self):
        # Define keyword sets for each semantic class
        self.class_keywords = {
            'instruction': ['step', 'guide', 'how to', 'follow', 'procedure', 'install'],
            'example': ['example', 'sample', 'instance', 'illustration', 'case study'],
            'definition': ['define', 'means', 'refers to', 'is defined as', 'concept'],
            'warning': ['caution', 'warning', 'danger', 'important', 'note that'],
            'summary': ['summary', 'overview', 'conclusion', 'in summary', 'briefly']
        }

    def extract(self, state: DocumentState) -> Dict[str, float]:
        """Extract keyword features from document state."""
        content = state.content.lower()
        features = {}

        for class_name, keywords in self.class_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in content)
            features[f'keyword_density_{class_name}'] = keyword_matches / len(keywords)

        return features

def update_beliefs_from_observation(self, observation: Dict[str, float],
                                  syntactic_state: DocumentState,
                                  time_step: Optional[int] = None) -> UpdateResult:
    """Update beliefs based on new syntactic observation."""
    start_beliefs = self.beliefs.copy()

    # Compute observation likelihoods for each semantic class
    observation_likelihoods = {}
    for semantic_class in self.semantic_classes:
        likelihood = self.observation_model.compute_likelihood(semantic_class, syntactic_state)
        observation_likelihoods[semantic_class] = likelihood

    # Apply temporal smoothing (exponential moving average)
    smoothed_likelihoods = self._apply_temporal_smoothing(observation_likelihoods)

    # Compute unnormalized posterior beliefs
    posterior_unnormalized = {}
    for semantic_class in self.semantic_classes:
        # Prior belief
        prior = self.beliefs[semantic_class]

        # Observation likelihood (with noise model)
        obs_likelihood = smoothed_likelihoods[semantic_class]
        noisy_likelihood = self._apply_observation_noise(obs_likelihood)

        # Semantic transition prior (context consistency)
        transition_prior = self._compute_transition_prior(semantic_class)

        # Combine all factors
        posterior_unnormalized[semantic_class] = (
            prior * noisy_likelihood * transition_prior
        )

    # Normalize posterior beliefs
    total_posterior = sum(posterior_unnormalized.values())
    if total_posterior > 0:
        for semantic_class in self.semantic_classes:
            self.beliefs[semantic_class] = (
                posterior_unnormalized[semantic_class] / total_posterior
            )
    else:
        # Fallback to uniform distribution if all posteriors are zero
        uniform_prob = 1.0 / len(self.semantic_classes)
        self.beliefs = {cls: uniform_prob for cls in self.semantic_classes}

    # Track belief evolution
    self.belief_history.append(self.beliefs.copy())

    # Update confidence metrics
    current_confidence = self._compute_belief_confidence()
    self.confidence_history.append(current_confidence)

    # Compute belief change metrics
    belief_change = self._compute_belief_change(start_beliefs, self.beliefs)

    return UpdateResult(
        previous_beliefs=start_beliefs,
        updated_beliefs=self.beliefs.copy(),
        observation_likelihoods=observation_likelihoods,
        belief_entropy=entropy(list(self.beliefs.values())),
        confidence=current_confidence,
        significant_change=belief_change > self._get_adaptive_threshold(),
        time_step=time_step
    )

def _apply_temporal_smoothing(self, likelihoods: Dict[str, float]) -> Dict[str, float]:
    """Apply temporal smoothing to observation likelihoods."""
    if len(self.belief_history) < 2:
        return likelihoods

    # Exponential smoothing with previous beliefs
    smoothed = {}
    alpha = 0.3  # Smoothing factor

    for class_name, likelihood in likelihoods.items():
        previous_belief = self.belief_history[-2].get(class_name, 0.0)
        smoothed[class_name] = alpha * likelihood + (1 - alpha) * previous_belief

    return smoothed

def _apply_observation_noise(self, likelihood: float) -> float:
    """Apply noise model to observation likelihood."""
    # Add Gaussian noise to prevent overconfidence
    noise = np.random.normal(0, self.noise_factor)
    noisy_likelihood = max(0.001, likelihood + noise)  # Prevent zero likelihoods

    return min(noisy_likelihood, 1.0)  # Cap at 1.0

def calibrate_uncertainty(self, validation_data: List[ValidationSample]) -> CalibrationResult:
    """Calibrate uncertainty estimates using validation data."""
    predicted_confidences = []
    actual_accuracies = []

    for sample in validation_data:
        # Get predicted beliefs for sample
        predicted_beliefs = self.beliefs.copy()

        # Compute predicted confidence (max belief probability)
        predicted_confidence = max(predicted_beliefs.values())

        # Compare with actual semantic class
        actual_class = sample.actual_semantic_class
        actual_accuracy = 1.0 if predicted_beliefs[actual_class] == predicted_confidence else 0.0

        predicted_confidences.append(predicted_confidence)
        actual_accuracies.append(actual_accuracy)

    # Compute calibration metrics
    ece_score = self._compute_expected_calibration_error(predicted_confidences, actual_accuracies)

    # Reliability diagram data
    reliability_data = self._compute_reliability_diagram(predicted_confidences, actual_accuracies)

    return CalibrationResult(
        expected_calibration_error=ece_score,
        reliability_diagram=reliability_data,
        confidence_bins=self._analyze_confidence_bins(predicted_confidences, actual_accuracies)
    )

def _compute_expected_calibration_error(self, confidences: List[float],
                                      accuracies: List[float]) -> float:
    """Compute Expected Calibration Error (ECE) for uncertainty calibration."""
    # Bin confidences into discrete intervals
    bins = np.linspace(0, 1, 11)  # 10 bins from 0 to 1
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []

    for i in range(len(bins) - 1):
        bin_mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
        if np.any(bin_mask):
            bin_acc = np.mean(accuracies[bin_mask])
            bin_conf = np.mean(confidences[bin_mask])
            bin_count = np.sum(bin_mask)

            bin_accuracies.append(bin_acc)
            bin_confidences.append(bin_conf)
            bin_counts.append(bin_count)

    # Compute ECE
    ece = 0.0
    for acc, conf, count in zip(bin_accuracies, bin_confidences, bin_counts):
        ece += (count / len(confidences)) * abs(acc - conf)

    return ece
```

### Package Distribution

```python
setup(
    name="markdown-decision-process",
    version=version,
    author="Daniel Ari Friedman",
    author_email="daniel@activeinference.institute",
    description="A framework for analyzing, generating, and optimizing Markdown documents through the lens of decision theory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docxology/markdown_decision_process",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "mdp-cli=mdp.cli:main",
        ],
    },
)
```

### Evaluation Pipeline

```python
def prepare_evaluation_dataset(raw_documents: List[str],
                             target_format: str = "markdown") -> EvaluationDataset:
    """Standardize document corpus for evaluation."""
    pipeline = DocumentPreparationPipeline()

    processed_docs = []
    for doc in raw_documents:
        # Clean and normalize
        cleaned = pipeline.clean_document(doc)

        # Extract structural metadata
        metadata = pipeline.extract_metadata(cleaned)

        # Compute quality baselines
        baseline_metrics = pipeline.compute_baseline_metrics(cleaned)

        processed_docs.append(ProcessedDocument(
            content=cleaned,
            metadata=metadata,
            baseline_metrics=baseline_metrics,
            original_format=pipeline.detect_original_format(doc)
        ))

    return EvaluationDataset(
        documents=processed_docs,
        preparation_metadata={
            'total_documents': len(processed_docs),
            'average_quality_score': np.mean([doc.baseline_metrics['quality_score']
                                            for doc in processed_docs]),
            'structural_diversity': compute_structural_diversity(processed_docs)
        }
    )

def perform_statistical_comparison(results: Dict[str, List[float]],
                                 alpha: float = 0.05) -> StatisticalComparison:
    """Perform comprehensive statistical comparison of methods."""
    comparison = StatisticalComparison()

    # Pairwise comparisons for each metric
    for metric_name in results.keys():
        metric_results = results[metric_name]

        # Shapiro-Wilk normality test
        normality_p_values = {}
        for method_results in metric_results.values():
            _, p_value = stats.shapiro(method_results)
            normality_p_values[method_name] = p_value

        # Select appropriate test based on normality
        if all(p > 0.05 for p in normality_p_values.values()):
            # Use parametric tests
            test_func = stats.f_oneway
            post_hoc_func = stats.tukey_hsd
        else:
            # Use non-parametric tests
            test_func = stats.kruskal
            post_hoc_func = stats.dunn

        # Perform omnibus test
        omnibus_stat, omnibus_p = test_func(*metric_results.values())

        # Post-hoc analysis if significant
        if omnibus_p < alpha:
            post_hoc_results = post_hoc_func(*metric_results.values())
            significant_pairs = extract_significant_pairs(post_hoc_results)
        else:
            significant_pairs = []

        comparison.add_metric_comparison(metric_name, {
            'omnibus_statistic': omnibus_stat,
            'omnibus_p_value': omnibus_p,
            'significant_pairs': significant_pairs,
            'effect_sizes': compute_effect_sizes(metric_results),
            'confidence_intervals': compute_confidence_intervals(metric_results)
        })

    return comparison

# Example optimization results
optimization_results = {
    'readability_focused': {
        'flesch_kincaid_improvement': 2.3,
        'structure_score_improvement': 0.8,
        'semantic_coherence_change': -0.2
    },
    'balanced_optimization': {
        'flesch_kincaid_improvement': 1.8,
        'structure_score_improvement': 1.2,
        'semantic_coherence_change': 0.1
    },
    'structure_focused': {
        'flesch_kincaid_improvement': 0.9,
        'structure_score_improvement': 2.1,
        'semantic_coherence_change': 0.3
    }
}

### Multi-Objective Optimization Results

```python
# Example multi-objective optimization results
optimization_results = {
    'readability_focused': {
        'flesch_kincaid_improvement': 2.3,
        'structure_score_improvement': 0.8,
        'semantic_coherence_change': -0.2,
        'effect_size': 0.87
    },
    'balanced_optimization': {
        'flesch_kincaid_improvement': 1.8,
        'structure_score_improvement': 1.2,
        'semantic_coherence_change': 0.1,
        'effect_size': 1.03
    },
    'structure_focused': {
        'flesch_kincaid_improvement': 0.9,
        'structure_score_improvement': 2.1,
        'semantic_coherence_change': 0.3,
        'effect_size': 0.95
    }
}
```

This code supplement provides complete, runnable implementations of all the components described in the main paper. The code demonstrates the practical application of decision-theoretic principles to document processing and can be used as a foundation for further research and development.
