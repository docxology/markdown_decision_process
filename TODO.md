# TODO — markdown_decision_process

Single canonical backlog for this repo. Status surfaces (README badges,
AGENTS.md version history) must link here or to the verifying command, never
duplicate numbers. Append new entries; supersede rather than delete.

Created 2026-08-31 by the agent-ergonomics deep pass
(see REVIEW_LOG_2026-08-31.md for method).

## Minor

- [x] (verified 2026-10-25) README badges: only Python/License/DOI badges
  remain — no `#` placeholder links. (README.md)
- [x] (verified 2026-10-25) AGENTS.md "Version History" hedges its dates as
  unverified and points at `version` in pyproject.toml. (AGENTS.md)
- [x] (verified 2026-10-25) `tests/test_markchain.py.backup2` is not tracked;
  `tests/reports/` junit output is not tracked either (.gitignore covers
  `reports/`). (tests/)
- [ ] Per-module API pages still show outdated call shapes:
  `StateSpace.get_state_metadata`, `BeliefUpdater.get_confidence`,
  `MarkChain.sample(start_state, length)` / `save`/`load`,
  `DocumentQuality` result keys (`readability_score`). README.md examples were
  corrected 2026-10-25; the deep pages were not touched.
  (docs/api/*.md, docs/guides/user_guide.md)
  - Partial resolution (2026-11-05): `docs/api/markchain.md` now uses the actual
    `sample`/`generate` argument order and JSON `save_model`/`load_model` methods.
    Its Python examples execute in the test suite. The other API pages listed
    above remain pending.
  - Partial resolution (2026-11-07) The StateSpace reference and user guide
    now use `get_features` and the current nested quality metrics. Other API
    pages remain open.
- [x] (source correction 2026-11-05) Retain leading/skipped-level headings in
  `Document.get_structure`; exclude fenced code from heading parsing and heading
  level transformations while preserving fenced bytes and public return shapes.
  (src/mdp/_headings.py, tests/test_heading_boundaries.py)

## Medium

- [x] Use the dated hosted Tests workflow for status and document direct pytest.
  The compatibility runner now executes the checked-in suite without rewriting
  tests or filtering historical failures. (README.md, tests/README.md)
- [ ] docs/index.md and docs/README.md link to per-module API pages that do
  not exist for several modules (transformations, animations, pandoc) —
  either generate them via docs/build_docs.py or trim the index.
  (docs/index.md, docs/README.md)

## Major

- [x] The earlier tracked JUnit report concern is superseded. Current
  `tests/reports/` is ignored and contains no tracked entries. (.gitignore)
- [x] (source checked 2026-11-05) The earlier no-lockfile entry is
  superseded: `uv.lock` is committed. Use a frozen environment and retain its
  actual runtime receipt; a lockfile alone does not prove an experiment ran.
  (uv.lock, pyproject.toml)

- [ ] Resolve the manuscript evaluation evidence gaps in
  [paper/EVALUATION_EVIDENCE.md](paper/EVALUATION_EVIDENCE.md): baseline
  checkpoint identity, traceable experiment outputs, participant-study evidence
  and reproducible per-comparison statistics. Numerical claims remain unverified.

- [x] (source correction 2026-11-05) Remove surviving unsupported background
  comparisons and qualify future-work expectations. Require/include the evidence
  review in assembled text and cover the full body with regressions. This does
  not resolve the historical evidence gaps listed above.

## Workflowz review — 2026-11-10

- [ ] **WFZ-01 — P1: Make `StateSpace.get_state_ids(content=...)` honor its content argument or reject it.** Observable outcome: passing different nonempty Markdown content either returns IDs parsed from that content with documented state-isolation semantics, or raises a clear `NotImplementedError`/`ValueError`; it must never silently return the existing state's IDs as though they represented the argument. Evidence: `src/mdp/state_space.py:187-193` explicitly ignores parsed content and returns `list(self.states.keys())`. Acceptance probe from repo root: `python - <<'PY'\nfrom mdp.state_space import StateSpace\ns = StateSpace()\nbefore = s.get_state_ids()\ntry:\n    after = s.get_state_ids(content='# Replacement\\n\\nNew paragraph')\nexcept (NotImplementedError, ValueError):\n    pass\nelse:\n    assert after != before, (before, after)\n    assert set(after).isdisjoint(before), (before, after)\nPY` (If the implementation intentionally reuses IDs, replace the disjointness assertion with a documented contract-specific check that the returned sequence reflects the replacement document.) Dependencies/constraints: inspect the full method signature/docstring and callers before choosing parsing versus explicit rejection; preserve the no-argument behavior and public return type.

- [ ] **WFZ-02 — P1: Stop returning constant readability scores as real measurements when `textstat` is absent.** Observable outcome: core `DocumentQuality` analysis without the optional `textstat` extra either computes the advertised metrics from document text or reports those metrics unavailable with an explicit status/warning; two documents with different readability cannot receive indistinguishable hard-coded fallback values presented as measurements. Evidence: `src/mdp/quality.py:15-25` installs constant fallback functions, while `src/mdp/quality.py:184-189` separately branches on `TEXTSTAT_AVAILABLE`; `pyproject.toml:25-32` omits `textstat` from runtime dependencies and `pyproject.toml:36-51` places it in dev extras. Acceptance probe from repo root, using an environment/import harness where `textstat` is genuinely unavailable: `python - <<'PY'\nfrom mdp import Document\nfrom mdp.quality import DocumentQuality\nq = DocumentQuality()\nshort = q.analyze_document(Document(content='Cats sit. Dogs run.'))\nlong = q.analyze_document(Document(content='The extraordinarily complicated contextualization of interdisciplinary conceptualizations necessitates comprehensive reconsideration. ' * 8))\nassert short is not long\n# Assert the new explicit unavailable status, or differing measured readability values, according to the implemented contract.\nPY` Dependencies/constraints: first inspect the complete quality result schema and visualization consumers; do not silently change established score scales or make `textstat` mandatory without recording that packaging decision. The probe's final assertion must name the actual public result key/status after that inspection.

- [ ] **WFZ-03 — P1: Make word-cloud generation fail explicitly when its optional dependency is unavailable.** Observable outcome: requesting a word cloud without `wordcloud` raises a documented dependency error (or returns a documented unavailable result) instead of constructing an object whose `generate()` silently returns `None`; normal word-cloud behavior remains unchanged when the dependency is installed. Evidence: `src/mdp/visualization.py:27-39` defines `_UnavailableWordCloud` with a no-op initializer and `generate()` returning `None`; `pyproject.toml:36-51` includes `wordcloud` only in dev extras. Acceptance probe from repo root in an environment/import harness with `wordcloud` unavailable: `python - <<'PY'\nimport mdp.visualization as v\nassert not v.WORDCLOUD_AVAILABLE\ncloud = v.WordCloud(width=100, height=100)\ntry:\n    result = cloud.generate('visible words')\nexcept ImportError as e:\n    assert 'wordcloud' in str(e).lower()\nelse:\n    assert result is not None\nPY` Dependencies/constraints: inspect all `WordCloud` call sites and the public visualization API before selecting exception versus explicit result; retain the installed-dependency path and avoid changing unrelated plotting behavior.

- [ ] **WFZ-04 — P2: Align Black's target configuration with the declared Python support floor.** Observable outcome: formatting configuration no longer claims Python 3.8 as its target while package metadata requires Python 3.11+, and Black can format the declared source layout without a target-version/support mismatch. Evidence: `pyproject.toml:33` declares `requires-python = \">=3.11\"`, but `pyproject.toml:71-73` sets `target-version = [\"py38\"]`; `.python-version:1` selects 3.15, so this is a configuration-consistency task, not a request to change the runtime pin. Acceptance probe from repo root: `python -m black --check --diff src tests` using the dev environment, after adding a small temporary fixture containing a Python-3.11-only syntax form and confirming Black parses it under the configured targets; remove the fixture afterward. Dependencies/constraints: inspect Black's supported target identifiers in the locked dev environment and preserve the existing 88-column style; do not upgrade Black or change the Python runtime pin merely for this cleanup.
