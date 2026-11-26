# Methodology and Architecture

## Representation and formal vocabulary

A document can be represented as a sequence of parsed elements and as a graph of structural relationships. The implementation exposes these representations through `Document` and `StateSpace`. Classification of a heading, list, or paragraph is a syntactic operation; interpreting an element as an instruction or definition is a separate semantic hypothesis.

Markov-chain generation estimates transition behavior from supplied documents. An action/reward formulation can also express a search over document transformations. A weighted objective can be written as $R = \sum_i w_i R_i$, but an increase in an implemented reward is not by itself an improvement in human comprehension, factual preservation, or writing quality. Those interpretations require separate measurements and controls.

MDP and POMDP notation provides design vocabulary for states, actions, observations and beliefs. Guarantees associated with a mathematical model apply only when its assumptions and the implemented solver have been established. This paper does not establish global optimality, semantic identifiability, calibrated probabilities, or a validated active-inference model for document meaning.

## Source-backed processing path

1. Parse supplied Markdown through `src/mdp/document.py` or `src/mdp/state_space.py`.
2. Inspect the resulting elements, state sequence, graph and features.
3. Train and sample `MarkChain` using explicit input documents and parameters.
4. Configure a `PolicyOptimizer` objective and record the transformations actually applied.
5. Treat `BeliefUpdater` outputs as implementation-defined heuristic beliefs until a labeled, held-out calibration study establishes another interpretation.
6. Retain input/output bytes and a run record so an observed transformation can be inspected and reproduced.

The implementation is a prototype. The formal framing does not replace parser-conformance tests, preservation checks, error handling, or evaluation on identified external data.
