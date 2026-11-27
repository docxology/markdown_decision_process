# Markdown Decision Process test suite

## Setup

From the repository root, install the locked development dependencies and
prepare the CMU pronunciation dictionary used by the readability tests.

```bash
uv sync --locked --extra dev
uv run --locked --no-sync python .github/scripts/prepare_test_data.py output/test-data
export NLTK_DATA="$PWD/output/test-data"
```

The [preparation script](../.github/scripts/prepare_test_data.py) verifies the
same archive size and SHA-256 as CI. It expects a fresh destination. For an
offline setup, pass `--archive` with the path to an acquired copy of the
reviewed ZIP. Reuse the prepared directory by setting `NLTK_DATA` in each test
shell.

## Run tests

Use the same pytest entry point as the [test workflow](../.github/workflows/tests.yml).

```bash
uv run --locked --no-sync python -m pytest --benchmark-disable tests/
uv run --locked --no-sync python -m pytest --collect-only tests/
uv run --locked --no-sync python -m pytest tests/test_document.py
uv run --locked --no-sync python -m pytest --benchmark-disable --cov=src tests/
uv run --locked --no-sync python -m pytest tests/ --benchmark-only
```

Each test module follows the `test_*.py` naming convention. Use pytest's path,
node ID, and marker selection for focused runs. Collection or import failures
are part of the result and should be fixed in the original test.

The compatibility command `python tests/run_all_tests.py` runs the same
checked-in tests and returns pytest's exit status. It supports `--module`,
`--list` for collection, `--coverage`, `--env-info`, and verbosity controls.
The former test-rewriting and failure-filtering options have been retired.
