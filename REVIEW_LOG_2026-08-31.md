# REVIEW LOG — Agent-Ergonomics Deep Pass, 2026-08-31

Fleet lane: markdown_decision_process (agent-erg-fleet-20260831).
Method: cold-start audit per SHARED_FRAME.md, then scoped fixes. All claims
below were verified against the repo on disk this session unless marked
otherwise.

## Phase 1 — Cold-start audit (2026-08-31)

Read ONLY README.md and AGENTS.md first, then attempted three orientation tasks.

### Task (a) determine current project status — FAIL (before pass)

- README.md line 293 claims "**Test Results:** ✅ 238/243 tests passing (98%
  coverage)" with no date and no verification command.
- README badges claim "tests passing" / "coverage 80%" and link to `#`
  (decorative, self-referential).
- AGENTS.md "Version History" claims v0.1.0 (2023) / v0.2.0 / v0.3.0 (2024);
  pyproject.toml says 0.3.0 and no changelog exists in-tree, so the dates are
  unverifiable.
- run_all_tests.py KNOWN_FAILING_TESTS mixed path conventions and included
  entries not matching disk (`test_search_config.py` nonexistent;
  `tests/test_policy_optimizer.py` double-prefixed).

### Task (b) find what to do next — FAIL (before pass)

- No TODO/backlog file anywhere in the tree.
- docs/ROADMAP.md is a large undated feature tech-tree, not an actionable
  backlog. TODO.md created this pass; entry docs now point at it.

### Task (c) find how to run the primary verification — PARTIAL (before pass)

- README said `python -m pytest tests/test_core.py` — that file does not exist.
- Real documented runner is `python3 run_all_tests.py` (tests/README.md);
  root README now points there.
- No lockfile/venv in checkout; environment setup needed before pytest.

### Doc sweep (Python link checker over tracked top-level + docs md)

- README.md -> paper/outputs/mdp_paper.pdf MISSING (real output is
  paper/outputs/MarkdownDecisionProcess_DAF_10-02-2025.pdf) — FIXED.
- docs/README.md -> api/belief_updater.md MISSING (on disk: .rst) — FIXED.
- docs/index.md: 8 broken links (api/transformations.md,
  api/visualization.md, api/animations.md, api/pandoc.md,
  guides/custom_rewards.md, guides/performance.md, guides/integration.md,
  CONTRIBUTING.md wrong path) — FIXED.
- docs/AGENTS.md -> guides/new_guide.md is a worked "touch" example, not a
  live link; left as-is (false positive).

## Phase 3 — Implemented (2026-08-31)

- README.md: fixed paper link; replaced unverifiable 238/243-98% claim with
  dated verification-command form; fixed nonexistent test_core.py pointer to
  run_all_tests.py; added Agent orientation block + TODO.md link near top.
- AGENTS.md: Version History marked unverified (no changelog in tree);
  version truth pointed at pyproject.toml; TODO.md declared single backlog.
- docs/README.md, docs/index.md: broken links fixed.
- run_all_tests.py: removed nonexistent test_search_config.py entry;
  corrected tests/test_policy_optimizer.py -> test_policy_optimizer.py
  (documented-command correctness, in scope per SHARED_FRAME).
- TODO.md: created with Minor/Medium/Major sections; all Phase-1 findings
  entered.

## Phase 4 — Verify & close

- Link checker re-run over every touched doc: all resolve.
- Path-scoped commits; pushed to main. No pre-push gate declared in repo
  (no CI workflows present; verified).
