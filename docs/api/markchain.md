# MarkChain API Reference

`MarkChain` learns counts of transitions between Markdown state strings and samples
new sequences from those counts. A state is a parsed text element, not a token or
character. This page describes the implementation in `src/mdp/markchain.py`.

## Public methods

| Method | Return value | Behavior |
| --- | --- | --- |
| `MarkChain(order=1, smoothing=0.01)` | `MarkChain` | Create an empty model. |
| `train(markdown_text: str)` | `None` | Accumulate states, starting-state counts and adjacent transition counts from one string. |
| `sample(length=10, start_state=None)` | `str` | Sample a sequence of state strings, joined with two newlines. |
| `generate(length=10, prompt=None, temperature=1.0)` | `str` | Delegate to `sample(length=length, start_state=prompt)`. |
| `get_transition_probabilities(state: str)` | `dict[str, float]` | Normalize observed outgoing counts; return an empty dictionary for an unknown state. |
| `save_model(filepath: str)` | `None` | Write model data as JSON. |
| `load_model(filepath: str)` | `None` | Replace model data on this instance from JSON. |

`length` is the first positional argument to both `sample` and `generate`. Prefer
keyword arguments when selecting a starting state. There are no `save` or `load`
methods; loading is an instance operation, not a constructor or class method.

## Training and generation

The default parser skips blank lines and retains nonblank lines as state strings.
It groups a triple-backtick code block into one state, while ordinary paragraph
lines and individual list items remain separate states. It does not return typed
objects such as `header` or `paragraph` tokens, and this API does not accept a
custom parser callback.

Repeated `train` calls accumulate counts. For a positive `length`, sampling starts
at the supplied state or chooses among learned starting states by count. If a
state has no outgoing transition, sampling chooses from the learned state set.
An empty model returns an empty string. Sampling uses Python's `random` module;
it does not validate or repair the resulting Markdown structure.

This example uses a sequence whose observed outgoing transitions are unique,
so the asserted three-state result does not depend on a random seed:

```python
from mdp import MarkChain

chain = MarkChain()
chain.train("# Guide\n\nFirst paragraph.\n\n## Details")
expected = "# Guide\n\nFirst paragraph.\n\n## Details"
assert chain.sample(length=3, start_state="# Guide") == expected
assert chain.generate(length=3, prompt="# Guide") == expected
assert chain.get_transition_probabilities("# Guide") == {"First paragraph.": 1.0}
assert chain.get_transition_probabilities("Unknown") == {}
```

## Saving and loading JSON

`save_model` writes `order`, `smoothing`, transition counts, states and starting
counts. `load_model` restores those fields on an existing instance. It does not
set the `is_trained` flag; sampling checks whether states exist. Treat model files
as application input and supply a destination whose parent directory exists.
Neither method accepts a Python pickle.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from mdp import MarkChain

original = MarkChain()
original.train("# Guide\n\nFirst paragraph.\n\n## Details")
with TemporaryDirectory() as directory:
    path = Path(directory) / "model.json"
    original.save_model(str(path))
    restored = MarkChain()
    assert restored.load_model(str(path)) is None
    assert restored.states == original.states
    assert restored.transitions == original.transitions
    assert restored.start_states == original.start_states
    assert restored.sample(length=3, start_state="# Guide") == (
        "# Guide\n\nFirst paragraph.\n\n## Details"
    )
```

## Current parameter limits

`order` and `smoothing` are stored and serialized, but training currently counts
adjacent state pairs regardless of `order` and does not apply smoothing to those
counts. `temperature` is accepted by `generate` but is not used when it delegates
to `sample`. These parameters therefore do not currently provide higher-order
conditioning, Laplace smoothing or temperature-controlled generation.

A `prompt` is an exact starting-state string, not a free-text completion context.
Graph-guided policies, automatic document optimization, automatic formatting
repair and statistical quality guarantees are not part of this class's current
generation contract.
