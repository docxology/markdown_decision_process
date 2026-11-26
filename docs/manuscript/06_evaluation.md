# Evaluation Protocol and Evidence

## Current evidence status

This section specifies a prospective protocol. It does not report completed corpus experiments, a participant study, model comparisons, significance tests, or measured effect sizes. The previous tables lacked the records needed to verify them and have been withdrawn from this active manuscript revision. Their historical source remains available in Git and the dated publication; no replacement values have been inferred.

## Corpus and split manifest

Identify each lawfully usable document by a stable ID, origin, license or access basis, and content hash. Specify inclusion criteria, preprocessing, deduplication, and training/validation/test membership before reporting outcomes. Record failures and excluded documents. Do not describe a corpus as collected merely because a loader or procedural sketch exists.

## Baseline identity

For every neural baseline, record the exact model and tokenizer identifiers, immutable checkpoint/revision, artifact hashes when available, fine-tuning configuration, splits, random seeds, generation parameters and executable command. The earlier GPT-2 variant conflict is not resolved by selecting a model name without these records. An unexecuted baseline belongs in a plan, not a results table.

## Per-document observations

Retain the input, generated or transformed document, objective definition, parameters and raw metric values for every run. State the unit of analysis and distinguish random-seed repetitions from independent documents. For transformations, evaluate content preservation and introduced errors alongside the optimized objective. Readability proxies and entropy values must not be presented as validated comprehension or probability calibration.

## Participant research

A participant study requires a protocol, recruitment and consent/ethics basis, scoring instrument, authorized de-identified observations, exclusion rules and aggregation code. Private personal and consent records remain in approved private storage. This revision reports no participant number or study result.

## Statistical analysis

Predefine the comparison, independent sampling unit and estimand. Retain paired observations where applicable, missingness, sample sizes, effect-size definitions, uncertainty intervals, multiplicity decisions and executable analysis outputs. A function that can calculate a test is not a receipt showing that a test was performed on identified data.

## Reporting gate

Only results with input manifests, commands, raw observations, environment/source bindings and a reviewable analysis may enter a measured-results table. Publish negative and failed outcomes within the stated protocol. A future execution is a new source epoch and cannot retroactively establish the provenance of historical values.
