# Quick start

Install the repository with Python 3.11 or later. The checked-in `.python-version` selects the version used by CI.

```bash
git clone https://github.com/docxology/markdown_decision_process.git
cd markdown_decision_process
uv sync --locked
```

Parse a document, inspect its graph, and transform its heading. Run from the checkout with `uv run --no-sync python`. The output goes to a separate file.

```python
from pathlib import Path

from mdp import Document, StateSpace
from mdp.transformations import HeadingLevelTransformation

doc = Document(content="# Inventory\n\nCount the books.\n")
graph = StateSpace(doc).graph
assert (graph.number_of_nodes(), graph.number_of_edges()) == (2, 1)

output = Path("output/inventory.md")
output.parent.mkdir(exist_ok=True)
HeadingLevelTransformation(increment=1).apply(doc, output)
assert output.read_text(encoding="utf-8").startswith("## Inventory\n")
```

Use `uv sync --locked --extra dev` to install test dependencies and follow the [verification commands](../manuscript-build.md) to prepare the readability data and run the suite. See the [user guide](user_guide.md) for training and configuration and [manuscript verification](../manuscript-build.md) for the rendered graph on a checked-in fixture.
