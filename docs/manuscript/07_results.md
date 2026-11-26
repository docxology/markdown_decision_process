# Implementation Evidence and Results Boundary

The current contribution is an inspectable software prototype. This revision does not report corpus-level performance measurements. No supported conclusion can currently be drawn about cross-domain generalization, comparative generation quality, convergence across external datasets, calibrated semantic confidence, lower resource use than neural baselines, or human preference.

Software tests can establish defined behavior for their inputs. Examples can illustrate parsing, sampling or transformations. They do not establish the missing experiment/study records described in [the evaluation protocol](https://github.com/docxology/markdown_decision_process/blob/main/docs/manuscript/06_evaluation.md). This distinction also applies to numbers embedded in screenshots, procedural code, or old generated documents.

The prior numerical tables and affirmative interpretations have been removed from active Sections 06 and 07. Their historical preservation is for traceability, not endorsement. A future results section must identify its own source revision and data, reproduce its tables from retained observations, and state the limits of its measurements.

## Structure of a checked-in Markdown fixture

The repository’s heading fixture follows a single sequence of six nonempty lines. The parser identifies their types and records five directed edges between consecutive lines. This small example checks the graph representation used by the implementation. Edges here indicate observed order in one file. They carry no estimate of generalization or document quality.

![Six classified Markdown lines linked in input order.](../../output/figures/heading_fixture.png){#fig:heading-fixture}
