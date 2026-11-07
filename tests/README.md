# Markdown Decision Process test suite

Install the project and its development extras. Run the checked-in suite from
the repository root with the same pytest entry point used in CI.

```bash
python -m pytest --benchmark-disable tests/
python -m pytest --collect-only tests/
python -m pytest tests/test_document.py
python -m pytest --benchmark-disable --cov=src tests/
python -m pytest tests/ --benchmark-only
```

Each test module follows the `test_*.py` naming convention. Use pytest's path,
node ID, and marker selection for focused runs. Collection or import failures
are part of the result and should be fixed in the original test.

The compatibility command `python tests/run_all_tests.py` runs the same
checked-in tests and returns pytest's exit status. It supports `--module`,
`--list` for collection, `--coverage`, `--env-info`, and verbosity controls.
The former test-rewriting and failure-filtering options have been retired.
