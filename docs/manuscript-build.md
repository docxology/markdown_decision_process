# Manuscript and verification

The [canonical manuscript source](https://github.com/docxology/markdown_decision_process/tree/main/docs/manuscript) includes the ordered sections, bibliography, configuration, preamble, and evidence review. The evaluation protocol is prospective. The historical DOI [10.5281/zenodo.17244387](https://doi.org/10.5281/zenodo.17244387) identifies the earlier deposit.

From the project root, install on Python 3.11 or later with the checked-in lockfile and generate the structural figure. The input is the existing heading fixture under `tests/fixtures/`. The command checks its graph before writing `output/figures/heading_fixture.png` and its figure registry.

```bash
uv sync --locked --extra dev
uv run --no-sync python docs/manuscript/fixture_figure.py

# Stage the same checksum-reviewed readability data used by CI.
uv run --no-sync python .github/scripts/prepare_test_data.py output/test-data
NLTK_DATA="$PWD/output/test-data" uv run --no-sync pytest --benchmark-disable
```

Use a separate checkout of [docxology/template](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2) at the pinned revision, with Pandoc, its cross-reference filter, and a LaTeX toolchain installed as described in the [Template setup guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md). Set `mdp_root` to the absolute project checkout path before running the following from the Template checkout.

```bash
uv sync --locked --no-dev
mkdir -p projects/working
ln -s "$mdp_root" projects/working/markdown_decision_process
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/markdown_decision_process
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/markdown_decision_process
```

Read the combined PDF in `output/pdf/`, the HTML at `output/web/index.html`, and the validation report in `output/reports/` in the project checkout. The Markdown export remains available through the local assembler, which checks the evidence review before composing the draft. The assembler copies the figure into its export directory when it has been generated.

```bash
uv run --no-sync python docs/manuscript/assemble_paper.py --validate-only
uv run --no-sync python docs/manuscript/assemble_paper.py --format markdown --output-dir output/paper-assembly
```
