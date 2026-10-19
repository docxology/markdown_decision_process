# Documentation build and publication

The Documentation workflow uses Python 3.12 to build Sphinx HTML and uploads
the `github-pages` artifact. Builds run for relevant pushes, pull requests and
manual dispatches. A successful build establishes document generation, not the
validity of research claims or every illustrative guide example.

## Optional GitHub Pages deployment

Site deployment is opt-in. The build does not create a new public website or
change repository hosting settings. To enable publication:

1. Configure the repository's Pages publishing source as **GitHub Actions**.
2. Set the repository Actions variable `DOCS_PAGES_ENABLED` to `true`.
3. Run the Documentation workflow from `main` or push a relevant change.

The deployment job requires both that variable and `main`, and runs only for
pushes or manual dispatches. Its `github-pages` environment and Pages/OIDC
permissions remain separate from the read-only build job. Missing hosting
configuration is an error when deployment is explicitly enabled.

If the variable is absent or false, builds and artifact uploads still run;
the deployment job is skipped deliberately. Download the artifact from the
workflow run for inspection. The artifact action's retention period applies.

## Local build

Use Python 3.12 in an isolated environment and a disposable checkout, because
the builder stages the README and contributor guides into the docs source tree.

```sh
python -m pip install -e ".[dev]"
python -m pip install sphinx sphinx-rtd-theme myst-parser sphinx-markdown-tables
python docs/build_docs.py --clean
```

Open `docs/_build/html/index.html` to inspect the result. In-place technical
guides are preserved when their source and destination are the same file.
