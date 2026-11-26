# Markov-chain sampling

The parser keeps headings, nonblank paragraph lines, and list items as separate states. It groups a triple-backtick fenced block into one state. `MarkChain.train(text)` accumulates the start-state and adjacent-transition counts. Repeated calls extend those counts. Training accepts Markdown text, which callers can read from one or more local files.

`sample(length, start_state=None)` chooses the first segment from the observed start counts unless the caller names one. It draws each succeeding segment in proportion to the observed outgoing transition counts. When no such transition exists, it samples from the learned states. The output joins sampled segments with blank lines.

The current transition map is keyed by a single current state. Constructor fields such as `order` and `smoothing` do not change this sampling path. See the [MarkChain API](../api/markchain.md) and [training example](../guides/user_guide.md) for working interfaces.
