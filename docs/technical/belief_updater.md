# Belief updates

`BeliefUpdater` initializes scores for a configurable list of semantic classes. `update_from_observation()` combines the current scores with class-keyed observations. `analyze_document(state_space)` derives heuristic signals from a parsed document’s structure and returns class scores. `get_most_likely_semantics()` returns the highest-scoring class and its score.

The scores depend on the class list, handcrafted feature rules, and configured update parameters. Calibration against labeled observations remains a prospective evaluation. See the [user guide](../guides/user_guide.md) and [manuscript verification](../manuscript-build.md).
