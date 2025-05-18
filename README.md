# Markdown Decision Process (MDP)

## Overview
Markdown Decision Process (MDP) is a framework that reimagines Markdown documents as stochastic processes analogous to Markov Decision Processes. This package provides tools to analyze, generate, and optimize Markdown content through the lens of decision theory and probabilistic modeling.

## Architecture

```mermaid
graph TD
    subgraph Core
        MD[MarkdownDocument] --> |parses| SS[StateSpace]
        MC[MarkChain] --> |generates| MD
        SS --> |informs| PO[PolicyOptimizer]
        BU[BeliefUpdater] --> |updates beliefs about| SS
        MA[MarkdownAgent] --> |uses| PO
        MA --> |observes| SS
        MA --> |updates| BU
    end
    
    subgraph Visualization
        VIS[Visualization] --> |renders| SS
        VEXP[VisualizationExporter] --> |exports| VIS
    end
    
    subgraph Extensions
        PI[PluginInterface] --- PM[PluginManager]
        PM --> |extends| Core
        EXT[External Plugins] --> |implements| PI
    end
    
    subgraph Export
        PAN[PandocConverter] --> |converts| MD
        VEXP --> |uses| PAN
    end
    
    User --> |interacts with| MA
    User --> |creates| MD
    User --> |views| VIS
```

## Core Concepts

### States and Transitions
In MDP, Markdown elements (headings, paragraphs, lists, code blocks) represent *states* in a stochastic process. Transitions between these states follow probabilistic patterns that can be learned from existing documents or defined by optimization criteria.

```mermaid
stateDiagram-v2
    [*] --> Heading1
    Heading1 --> Paragraph
    Paragraph --> Paragraph: 0.4
    Paragraph --> BulletList: 0.3
    Paragraph --> CodeBlock: 0.2
    Paragraph --> Heading2: 0.1
    BulletList --> Paragraph: 0.7
    BulletList --> BulletList: 0.3
    CodeBlock --> Paragraph: 0.9
    CodeBlock --> CodeBlock: 0.1
    Heading2 --> Paragraph: 0.8
    Heading2 --> BulletList: 0.2
    Paragraph --> [*]
```

### Partial Observability
Just as in POMDPs (Partially Observable Markov Decision Processes), the raw Markdown syntax only partially reveals the semantic meaning or rendered appearance of the content. MDP provides tools to reason about this uncertainty and make optimal decisions despite incomplete information.

### Rewards and Policies
MDP defines "reward functions" for Markdown structures based on readability, information density, and aesthetic appeal (reinforcement learning perspective). Additionally there is the option to use the probability likelihoods directly, framing the situation in terms of Active Inference and the Free Energy Principle. In either case, the package implements methods for inferring the optimal "policies" for generating and transforming Markdown files.

```mermaid
flowchart TD
    subgraph Document
        MD[Markdown Document]
    end
    
    subgraph Analysis
        Q[Quality Metrics]
        SS[State Structure]
    end
    
    subgraph Reward
        RF1[Readability]
        RF2[Information Density]
        RF3[Aesthetic Appeal]
        RF4[Custom Rewards]
    end
    
    subgraph Policy
        P1[Generation Strategy]
        P2[Transformation Strategy]
        P3[Optimization Strategy]
    end
    
    MD --> SS
    MD --> Q
    SS --> RF1
    SS --> RF2
    Q --> RF3
    RF1 --> P1
    RF2 --> P1
    RF3 --> P1
    RF4 --> P1
    RF1 --> P2
    RF2 --> P2
    RF3 --> P2
    RF4 --> P2
    P1 --> MD
    P2 --> MD
    P3 --> P1
    P3 --> P2
```

## Project Structure

```mermaid
graph TD
    subgraph src/mdp
        INIT[__init__.py] --- DOC[document.py]
        INIT --- MC[markchain.py]
        INIT --- PO[policy_optimizer.py]
        INIT --- SS[state_space.py]
        INIT --- BU[belief_updater.py]
        INIT --- MA[markdown_agent.py]
        INIT --- VIS[visualization.py]
        INIT --- EXP[export.py]
        INIT --- PAN[pandoc.py]
        INIT --- QUAL[quality.py]
        INIT --- TRANS[transformations.py]
        INIT --- PI[plugin_interface.py]
        INIT --- PM[plugin_manager.py]
        INIT --- PLUG[plugins.py]
    end
    
    subgraph examples
        EXPLUGS[plugins/] --- FPLUGIN[formatting_plugin.py]
        SAMPLEDOCS[sample_docs/]
        VIZ_OUT[visualization_output/]
        EXPLUGS --- PLUGREAD[plugins/README.md]
    end
    
    subgraph docs
        API[api/]
        TECH[technical/]
    end
    
    subgraph tests
        FIXTURES[fixtures/]
        REPORTS[reports/]
    end
```

## Features

- **MarkChain**: Generate Markdown using Markov chains trained on existing documents
- **StateSpace**: Visualize the state space and transition probabilities of your Markdown
- **PolicyOptimizer**: Transform Markdown documents to optimize for specified reward functions
- **BeliefUpdater**: Reason about semantic meaning from syntactic structure
- **MarkdownAgent**: An autonomous agent that explores and exploits the Markdown state space
- **VisualizationExporter**: Export visualizations and documents in various formats (PNG, PDF, SVG, HTML)
- **Plugin System**: Extend functionality with custom transformations and reward functions

## Installation

```bash
pip install markdown-decision-process
```

## Quick Start

```python
from mdp import MarkChain, PolicyOptimizer

# Generate Markdown using a trained model
generator = MarkChain.from_corpus("path/to/documents/")
new_document = generator.sample(length=500)

# Optimize an existing document
optimizer = PolicyOptimizer(reward_weights={"readability": 0.7, "information_density": 0.3})
improved_document = optimizer.transform("path/to/document.md")
```

### Visualization and Export

```python
from mdp import StateSpace, VisualizationExporter
from mdp.document import MarkdownDocument

# Analyze a document and visualize its state space
state_space = StateSpace()
state_space.parse_markdown_file("path/to/document.md")

# Initialize the exporter
exporter = VisualizationExporter(output_dir="outputs")

# Export state space visualization in different formats
exporter.export_state_space(state_space, "state_space.png")
exporter.export_state_space(state_space, "state_space.pdf")
exporter.export_state_space(state_space, "state_space.svg")

# Generate a comprehensive analysis report
document = MarkdownDocument(file_path="path/to/document.md")
exporter.export_analysis_report(document, "analysis_report.pdf")

# Export a document with embedded visualizations
exporter.export_document_with_visualizations(
    document="path/to/document_with_markers.md",
    output_path="enhanced_document.pdf",
    visualizations=[
        ("<!-- VISUALIZATION: STATE_SPACE -->", state_space_fig, {"format": "png"}),
    ],
    to_format="pdf"
)
```

### Using Plugins

```python
from mdp import MarkdownDocument, PluginManager
from mdp.plugins import MDPPlugin

# Register and use a custom plugin
plugin_manager = PluginManager()
plugin_manager.register_plugin("formatting", "examples.plugins.formatting_plugin")

# Use a plugin's transformations
document = MarkdownDocument(file_path="document.md")
formatted_content = plugin_manager.apply_transformation(
    "formatting.fix_headings", 
    document.get_content()
)

# Calculate reward using a plugin's reward function
consistency_score = plugin_manager.calculate_reward(
    "formatting.consistency_score", 
    formatted_content
)
```

## Document Processing Workflow

```mermaid
sequenceDiagram
    participant User
    participant MD as MarkdownDocument
    participant MC as MarkChain
    participant SS as StateSpace
    participant PO as PolicyOptimizer
    participant VE as VisualizationExporter
    
    User->>MD: Create or load document
    MD->>SS: Parse structure
    SS->>MD: Return state representation
    
    alt Generate new content
        User->>MC: Train on corpus
        User->>MC: Generate content
        MC->>MD: Return generated markdown
    end
    
    alt Optimize document
        User->>PO: Configure reward weights
        User->>PO: Optimize document
        PO->>SS: Analyze current states
        PO->>PO: Apply transformations
        PO->>MD: Update with optimized content
    end
    
    alt Visualize and export
        User->>VE: Configure export options
        VE->>SS: Request state space data
        SS->>VE: Return visualization data
        VE->>User: Export visualizations/report
    end
```

## Documentation

For comprehensive documentation, see [docs/](docs/README.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more details. 