# User guide

Use the [quick start](quickstart.md) to install the project and run a complete example.

## Graphs and sampling

`Document(content=...)` accepts Markdown text. `Document(file_path=...)` loads a local file. `StateSpace(document)` builds a directed graph whose nodes describe recognized nonblank lines, with edges between consecutive states. Call `calculate_transition_probabilities()` for normalized outgoing weights, or `visualize(output_path)` to save a graph image.

`MarkChain` learns transitions over a separate state representation based on Markdown text segments. Train it on each input string, then sample a sequence.

```python
from mdp import MarkChain

chain = MarkChain()
chain.train("# Inventory\n\nCount books.\n\nRecord the total.")
print(chain.sample(length=3))
```

Sampling uses the learned transition counts, with fallback sampling when a state has no outgoing transitions. Use `save_model(path)` and `load_model(path)` for explicitly named model files.

## Transformations and scoring

Use [transformations](../technical/transformations.md) for known edits such as changing headings, links, or lists. A `TransformationPipeline` applies transformations in order and writes to the output path you give it. Inspect the output before replacing the original.

`PolicyOptimizer(state_space, max_iterations=...)` exposes state-graph algorithms, including value iteration and Q-learning. Its separate `optimize(document, output_path=...)` routine searches over structural edits using internal scoring heuristics. It returns a dictionary with `optimized_content`, `final_reward`, `iterations`, and `reward_history`. See the [optimization notes](../technical/policy_optimization.md) for the distinction between graph rewards and edit scores.

`BeliefUpdater().analyze_document(state_space)` returns heuristic semantic-class scores. These scores use features from the current document. The [evaluation protocol](../manuscript-build.md) identifies what would be required to validate them against observations.

## Optional export and plots

The [API reference](../API_COMPLETE.md) lists the plotting and export interfaces. Pandoc format conversion requires a `pandoc` executable. PDF output also needs a PDF engine supported by Pandoc. To build the documentation site, use the [local Sphinx instructions](../PUBLISHING.md).
