# State space analysis

`StateSpace(Document(...))` records each recognized nonblank line as a node with its type, input text, and line number. Edges connect consecutive states. A fenced block is classified as code while it is open. The graph stores observed order and supports structural operations such as successor lookup and PageRank.

`calculate_transition_probabilities()` divides each outgoing edge’s observed weight by the sum of outgoing weights from that state. States with no outgoing edges have no observed successor. Use `visualize(path)` for an image or `graph` for access to the NetworkX graph.

See the [StateSpace API](../api/state_space.md) and the [manuscript fixture](../manuscript-build.md) for a checked-in example.
