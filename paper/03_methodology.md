# Methodology and Architecture

This section presents the theoretical foundations and architectural design of the Markdown Decision Process framework.

## Theoretical Foundations

This section presents the rigorous mathematical foundations underpinning the Markdown Decision Process framework, establishing document processing as a decision-theoretic problem. Drawing from David Marr's influential framework for understanding information processing systems, we analyze the framework at three complementary levels: computational theory, algorithmic implementation, and hardware/physical instantiation.

### Marr's Three Levels Applied to Document Processing

Following Marr's seminal work on vision systems, we can understand document processing at three distinct levels:

**Computational Level**: What is the goal of document processing? At this level, documents are viewed as stochastic processes where the objective is to maximize expected document quality under uncertainty. The framework models the document generation and optimization problem as finding policies that maximize cumulative reward while handling partial observability of semantic intent.

**Algorithmic Level**: How can we achieve this goal? This level concerns the specific algorithms and representations used. The framework employs Markov chains for generative modeling, graph algorithms for structural analysis, and reinforcement learning for optimization. The belief updating mechanism implements Bayesian inference to maintain probabilistic beliefs about semantic classes given syntactic observations.

**Implementation Level**: How is the framework physically realized? The current implementation uses Python with scientific computing libraries (NumPy, NetworkX, scikit-learn) running on standard computing hardware. The modular architecture allows for future hardware acceleration and distributed computing deployments.

### Document State Space

We formalize a Markdown document as a sequence of states $d = (s_1, s_2, \dots, s_n)$ where each state $s_i \in S$ represents a distinct Markdown element with rich metadata. The state space $S$ encompasses the syntactic elements that comprise Markdown documents:

**Core State Types**:
- **Heading states**: $H_k$ for $k = 1, \dots, 6$ (corresponding to heading levels)
- **Paragraph states**: $P$ (regular text content)
- **List states**: $L_u, L_o$ (unordered and ordered lists)
- **Code states**: $C$ (code blocks and inline code)
- **Link states**: $K$ (inline and reference links)
- **Table states**: $T$ (markdown tables)
- **Blockquote states**: $Q$ (quoted text)
- **Horizontal rule states**: $R$ (section dividers)

**Extended State Representation**: Each state $s \in S$ is characterized by:
- **Syntactic type**: $type(s) \in \{H_1, \dots, H_6, P, L_u, L_o, C, K, T, Q, R\}$
- **Content**: $content(s)$ - the actual text or markup content
- **Metadata**: $meta(s)$ - structural properties (e.g., heading level, list depth, code language)
- **Features**: $feat(s)$ - computed properties (e.g., length, complexity, readability scores)

This rich state representation enables sophisticated analysis beyond simple syntactic categorization. Importantly, this approach bridges the critical gap between syntax (the structural form of text) and semantics (the meaning conveyed). While traditional approaches focus primarily on syntactic parsing, our framework explicitly models the uncertainty in semantic interpretation, recognizing that the same syntactic structure can convey different meanings depending on context, domain, and author intent.

### Transition Model

The transition model captures the probabilistic structure of document evolution. For a given state $s \in S$ and action $a \in A$, the transition probability $P(s'|s, a)$ defines the likelihood of moving to state $s'$.

**Generation Transitions**: For document generation without explicit actions (uncontrolled transitions), we learn empirical transition probabilities from training corpora using smoothed maximum likelihood estimation:

$$P(s'|s) = \frac{\mathrm{count}(s, s') + \alpha}{\mathrm{count}(s) + \alpha \cdot |S|}$$

where $\mathrm{count}(s, s')$ denotes observed transitions and $\alpha > 0$ is a smoothing parameter preventing zero probabilities.

**Action-Conditioned Transitions**: When actions are applied (document optimization), transitions depend on transformation operations that modify document structure.

### Reward Functions

Reward functions quantify the desirability of state transitions, enabling optimization toward user-specified quality criteria. We define a modular reward structure with composable components:

**Core Reward Components**:
- **Readability reward**: $R_{read}(s, a, s') = f_{read}(\mathrm{content}(s'), \mathrm{context}(s, s'))$
- **Information density reward**: $R_{info}(s, a, s') = f_{info}(\mathrm{content}(s'), \mathrm{length}(s'))$
- **Structure clarity reward**: $R_{struct}(s, a, s') = f_{struct}(\mathrm{hierarchy}(s'), \mathrm{consistency}(s, s'))$
- **Semantic coherence reward**: $R_{sem}(s, a, s') = f_{sem}(\mathrm{meaning}(s'), \mathrm{context}(s, s'))$

**Composite Reward**: The total reward combines components with user-specified weights:
$$R(s, a, s') = \sum_{i \in \mathcal{C}} w_i \cdot R_i(s, a, s')$$
where $\mathcal{C}$ is the set of reward components and $w_i \geq 0$ are component weights satisfying $\sum_{i \in \mathcal{C}} w_i = 1$.

### Belief States and Partial Observability

A fundamental insight of the MDP framework is that semantic interpretation involves inherent uncertainty. Drawing from POMDP theory, we model this as a partial observability problem where the true semantic class $c \in C$ (e.g., "instruction", "example", "definition", "reference") is not directly observable from syntactic structure.

**Observation Model**: The observation model $P(o|s, c)$ defines the probability of observing syntactic features $o$ given semantic class $c$ and syntactic state $s$. This captures the uncertain mapping from syntax to semantics.

**Belief State Dynamics**: The belief state $b(c)$ represents the posterior probability distribution over semantic classes given observation and action history:
$$b(c_t) = P(c_t | o_1, a_1, \dots, o_t, a_{t-1})$$

**Belief Update**: Following Bayesian inference, belief updates incorporate new observations:
$$b'(c) = \frac{P(o|c) \sum_{c'} P(c'|c) b(c)}{\sum_c P(o|c) \sum_{c'} P(c'|c) b(c)}$$
where $P(o|c)$ is the observation likelihood and $P(c'|c)$ represents semantic class transitions.

This formulation explicitly addresses the uncertainty inherent in document interpretation, enabling robust semantic analysis even when syntactic cues are ambiguous. This approach complements modern large language models (LLMs) by providing an interpretable, theoretically-grounded alternative that offers explicit uncertainty quantification and domain-specific customization capabilities that are difficult to achieve with black-box neural approaches.

## Architecture Overview

The MDP framework implements a modular architecture where specialized components collaborate to provide comprehensive document processing capabilities. The design emphasizes theoretical coherence while enabling practical extensibility.

**Figure 1: Markdown Decision Process System Architecture**

### Core Components

**MarkChain**: Implements sophisticated Markov chain models for document generation and transition probability estimation, supporting higher-order dependencies and smoothing techniques for robust probability estimation.

**StateSpace**: Provides graph-theoretic analysis of document structure, representing documents as directed graphs where states are nodes and transitions are weighted edges with rich metadata.

**PolicyOptimizer**: Applies reinforcement learning algorithms to optimize document structure according to user-specified reward functions, learning optimal transformation policies through value iteration or policy gradient methods.

**BeliefUpdater**: Maintains and updates probabilistic belief distributions over semantic interpretations given syntactic observations, explicitly modeling the uncertainty inherent in document understanding.

**PluginManager**: Provides extensibility through a plugin architecture that allows registration of custom transformations, reward functions, and analysis tools while maintaining theoretical coherence.

**VisualizationExporter**: Generates comprehensive visual representations of document structure, state spaces, and optimization processes, supporting multiple output formats for analysis and presentation.

## Document Processing Pipeline

The framework processes documents through a structured pipeline that transforms raw Markdown into optimized, semantically-annotated documents.

### Phase 1: Syntactic Parsing and State Extraction

Documents are parsed into their constituent syntactic elements using a robust parser that handles the full Markdown specification. The parsing process extracts rich metadata and features for each element, creating a structured representation suitable for probabilistic modeling (see Code Supplement, Section "Core Data Structures").

### Phase 2: State Space Construction and Analysis

States are organized into a graph structure that captures transition relationships and structural properties. Each state becomes a node in a directed graph, with edges representing probabilistic transitions between document elements. The graph construction process incorporates multiple weighting factors including content similarity, structural coherence, and positional relationships (see Code Supplement, Section "StateSpace Component").

### Phase 3: Semantic Analysis and Belief Propagation

The belief updater processes syntactic observations to maintain probabilistic beliefs about semantic intent. This component implements Bayesian inference to update probability distributions over semantic classes given syntactic observations, explicitly modeling the uncertainty inherent in document interpretation (see Code Supplement, Section "BeliefUpdater Component").

### Phase 4: Optimization and Policy Application

The constructed models enable document optimization through learned policies. The optimization process applies reinforcement learning algorithms to maximize user-specified reward functions, learning optimal transformation policies that balance multiple quality criteria (see Code Supplement, Section "PolicyOptimizer Component").

## Mathematical Formulation

### Value Iteration for Document Optimization

We adapt value iteration algorithms from reinforcement learning for document structure optimization:

**Value Function Initialization**:
$$V_0(s) = 0 \quad \forall s \in S$$

**Value Iteration**:
$$V_{k+1}(s) = R(s) + \gamma \max_{a \in A} \sum_{s' \in S} P(s'|s,a) V_k(s')$$

**Policy Extraction**:
$$\pi^*(s) = \arg\max_{a \in A} \sum_{s' \in S} P(s'|s,a) V^*(s')$$

where $V^*(s)$ is the optimal value function and $\pi^*(s)$ is the optimal policy.

### Belief Update for Semantic Inference

Belief states evolve through Bayesian inference as new observations arrive:

**Belief Update Rule**:
$$b'(c) = \frac{P(o|c) \sum_{c' \in C} P(c'|c) b(c)}{\sum_{c \in C} P(o|c) \sum_{c' \in C} P(c'|c) b(c)}$$

where $P(o|c)$ is the observation likelihood and $P(c'|c)$ represents semantic transition probabilities.

### Free Energy Formulation (Active Inference)

The framework supports both traditional reward-based optimization and Active Inference approaches. For Active Inference variants, we minimize variational free energy:
$$\mathcal{F} = \mathbb{E}_{q(s')}[-\ln p(o,s'|a)] + \mathbb{E}_{q(s)}[\ln q(s) - \ln p(s)]$$

This formulation provides connections to predictive processing and enables neurally-plausible document optimization algorithms. Unlike reward-based approaches that maximize predefined utility functions, Active Inference directly minimizes surprise (prediction error) on the probability distributions, providing a more principled approach to handling uncertainty in document processing.

The Markdown Decision Process framework is designed to support both paradigms:
- **Reward-based optimization**: Traditional RL approaches using explicit reward functions
- **Active Inference**: Free energy minimization without explicit rewards

This flexibility allows users to choose the optimization paradigm that best fits their theoretical preferences and application requirements.

## Implementation Considerations

### Computational Complexity Management

The framework addresses several computational challenges inherent in document processing:

- **State Space Scaling**: For large documents ($n > 1000$ states), we employ state aggregation techniques and hierarchical modeling to maintain tractability with $O(n \log n)$ complexity
- **Transition Matrix Sparsity**: Sparse transition matrices are handled through efficient storage (e.g., dictionary-based representations) reducing memory from $O(n^2)$ to $O(k)$ where $k$ is the number of non-zero transitions
- **Belief Update Efficiency**: Approximate inference methods (e.g., particle filtering) enable efficient belief state updates for real-time applications with $O(m)$ complexity for $m$ particles
- **Parallel Processing**: Graph analysis and optimization operations are parallelized across multiple cores for improved throughput

### Extensibility and Modularity

The plugin architecture ensures extensibility while preserving theoretical foundations:

The plugin system provides a clean abstraction for extending the framework with domain-specific functionality while maintaining theoretical coherence. The abstract base class defines the contract for plugins, ensuring they can contribute transformations, reward functions, and observation models to the core system (see Code Supplement, Section "Plugin System").

This design enables domain-specific customizations (e.g., academic writing plugins, technical documentation plugins) while maintaining the underlying MDP/POMDP structure and theoretical guarantees.
