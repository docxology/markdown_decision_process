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

## Medium

- [ ] Establish a dated, command-verified test-status surface (e.g. refresh a
  STATUS line in this file after each full `python3 run_all_tests.py` run)
  and have README link to it instead of prose numbers. (TODO.md, README.md)
- [ ] docs/index.md and docs/README.md link to per-module API pages that do
  not exist for several modules (transformations, animations, pandoc) —
  either generate them via docs/build_docs.py or trim the index.
  (docs/index.md, docs/README.md)

## Major

- [ ] tests/reports/ holds 12 git-tracked junit XML files from 2025-06-25 —
  transient test output in version control. Stop tracking the directory
  (add to .gitignore), keep one exemplar if useful, or purge. (tests/reports/)
- [ ] No lockfile; environment reproducibility depends on loose pyproject
  extras. Add a uv/requirements lock or document the pinned dev install.
  (pyproject.toml)

- [ ] Resolve the manuscript evaluation evidence gaps in
  [paper/EVALUATION_EVIDENCE.md](paper/EVALUATION_EVIDENCE.md): baseline
  checkpoint identity, traceable experiment outputs, participant-study evidence
  and reproducible per-comparison statistics. Numerical claims remain unverified.
