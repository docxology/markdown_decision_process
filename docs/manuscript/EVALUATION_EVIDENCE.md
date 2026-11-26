# Evaluation evidence review

Review base: `18af4f5` (2026-10-13). Scope: tracked manuscript sections,
code supplement, examples, fixtures and test reports. No external private
records were accessed. Absence in this repository does not establish that a
study was never performed.

## Unresolved claims and acceptance criteria

- **GPT-2 identity:** Section 06 originally described Medium but its table
  named Small. Provide the model/checkpoint identifier and hash, tokenizer,
  fine-tuning configuration, corpus/split manifest, seeds, executable runner
  and raw outputs. Until then neither variant is asserted as the actual model.
- **Experiment values:** supply source datasets or lawful reproducible access,
  document identifiers and splits, metric definitions, environment and commands,
  and per-run observations for every reported table. Do not infer performance
  from unit tests or illustrative examples.
- **Participant study:** the reported 25 participants and ratings need a
  protocol, recruitment and consent/ethics basis, scoring instrument,
  appropriately de-identified response data and aggregation procedure.
  Personal data and consent records should remain in approved private storage;
  publish only authorized de-identified evidence.
- **Significance/effect sizes:** supply paired observations, independent units,
  sample sizes, test statistics, degrees of freedom where applicable,
  multiplicity treatment, confidence intervals and executable analysis outputs.
  The supplement's statistical code is a procedural sketch, not a run receipt.

## Corrected source revision (2026-10-19)

Unsupported numerical tables and study/model comparisons have been withdrawn
from the active manuscript, together with affirmative performance/calibration
interpretations in the abstract, introduction, implementation, discussion and
conclusion. Section 06 is now a prospective protocol and Section 07 states the
current results boundary. No new experiment or participant study was invented.

The original claim context is preserved at immutable source revision
`ec902bb5661b3741b2b802ab37ee4469d8369318` and in the dated published assets.
Neither historical provenance nor broad scientific validity is marked resolved.
Reintroducing a measured result requires the acceptance evidence listed above.


## Active-source consistency follow-up (2026-11-05)

Review base: `8c7b8d22f4ee0e37508cff0ef2974bf9c552142b`. The active
background still asserted calibrated probabilities, optimal policies and
favorable resource comparisons despite the corrected results boundary. Those
assertions and unsupported priority/guarantee claims are removed by this
follow-up. The future-work list is a plan with unmeasured expected impacts.
The evidence review now accompanies both assembled text formats and is a
required assembly input. These are source and reporting corrections, not newly
recovered measurements or a new deposited edition.

### Acceptance for a future evidence-bearing revision

Before adding a results table or affirmative comparison, retain a reviewable
bundle that connects each claim to its actual observations:

1. **Source and execution:** full source revision, exact command, interpreter
   and resolved dependency versions, parameters and seeds, input/output hashes,
   exit status and failures. Identify the runner and record when it ran.
2. **Corpus and model identity:** lawful data access, stable document IDs,
   content hashes, preprocessing, exclusions and split/deduplication rules;
   exact model and tokenizer revisions/checkpoint hashes, training configuration
   and generation parameters. An unavailable historical checkpoint stays
   unavailable; a newly selected GPT-2 variant is a new baseline, not a recovery.
3. **Observations and metrics:** raw per-document/per-run observations linked
   to those IDs and artifacts, metric definitions and executable aggregation.
   Report content preservation and errors alongside any configured reward.
   Test fixtures, illustrative output and benchmark timings do not substitute
   for a corpus quality or calibration study.
4. **Human evidence:** study protocol, recruitment and consent/ethics basis,
   scoring instrument, exclusion/missingness rules and aggregation procedure.
   Keep personal and consent records private; publish only authorized,
   appropriately de-identified observations and the permitted review statement.
   Do not infer a participant count or reconstruct individual responses.
5. **Statistical comparison:** identify the estimand, independent sampling unit,
   paired observations and effective sample size, treatment of repeated seeds,
   test/statistic and degrees of freedom where applicable, effect sizes,
   confidence intervals and multiplicity handling. Bind generated tables to
   executable analysis and retained outputs, including failures and limitations.

Human review must assess whether that evidence supports the particular claim;
file presence, a passing unit test or successful assembly does not certify
scientific validity. A new measurement bundle establishes its own dated source
epoch and must not be labeled a replication or repair of missing historical
observations without the original records. Until then the evaluation remains
prospective and the historical provenance gaps remain unresolved.
