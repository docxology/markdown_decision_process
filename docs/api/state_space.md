# StateSpace API Reference

`StateSpace` represents nonempty Markdown lines as nodes in a directed graph.
Its edges follow the order of the lines within each document. Each node stores
its type, stripped content, and zero-based source line number. Fenced code
delimiters and the lines between them have type `code`, so a comment or list
marker inside a fence does not create a document heading or list state.

## Construct a state space

Pass a `Document` at construction or call `parse_markdown(content)` to add raw
text. Use `analyze(path)` for a Markdown file or the immediate `*.md` files in a
directory. Repeated calls accumulate nodes and transitions, with a new sequence
for each input.

```python
from mdp import Document, StateSpace

document = Document(content="# Introduction\n\nA paragraph.\n\n## Details")
space = StateSpace(document)

assert list(space.graph.nodes) == ["header_0", "paragraph_1", "header_2"]
assert space.get_state("header_2") == {
    "type": "header",
    "content": "## Details",
    "line": 4,
}
```

## Inspect states and transitions

`get_state(state_id)` returns the state record or `None`. The numeric suffix is
a counter across all state types. `get_features(state_id)` returns the type,
incoming and outgoing edge counts, and the fields available for the state
type, such as heading level or code language. `get_successor_states(state_id)`
returns the IDs connected by outgoing edges. Use
`calculate_transition_probabilities()` to normalize outgoing transition
counts per source state.

```python
from mdp import Document, StateSpace

space = StateSpace(Document(content="# Introduction\n\nA paragraph."))
assert space.get_successor_states("header_0") == ["paragraph_1"]
assert space.get_features("header_0")["level"] == 1
assert space.calculate_transition_probabilities()["header_0"]["paragraph_1"] == 1.0
```

`extract_structure()` returns an ordered list of dictionaries with `type`,
`content`, and `state`. Header entries also include `level` and `header`.
`extract_structure(content)` analyzes the supplied text in an independent
state space.

## Visualize a state space

`visualize(output_path, title)` saves a graph image if there are states.

```python
from mdp import Document, StateSpace

space = StateSpace(Document(content="# Title\n\nDocument content."))
space.visualize("state_space.png", title="Document State Space")
```

## Use with MarkChain

`MarkChain` learns text states from the Markdown input. Train on the
document's content and sample with a text state as the starting value.

```python
from mdp import Document, MarkChain

document = Document(content="# Title\n\nA paragraph.")
chain = MarkChain()
chain.train(document.get_content())
assert chain.sample(length=1, start_state="# Title") == "# Title"
```
