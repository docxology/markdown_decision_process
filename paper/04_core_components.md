# Core Components

The following map identifies current source entry points. It is an implementation inventory, not a measured comparison or an assertion that every proposed research feature is implemented.

| Component | Source | Inspectable interfaces | Interpretation boundary |
| --- | --- | --- | --- |
| Documents | `src/mdp/document.py` | `Document`, content updates and structural accessors | Parsed structure does not establish semantic correctness. |
| Structural graph | `src/mdp/state_space.py` | `StateSpace`, parsing, state sequence and graph features | Graph properties depend on the chosen representation. |
| Generation | `src/mdp/markchain.py` | `MarkChain.train`, `sample`, `generate` and transition probabilities | Sampling does not establish factual or human-rated quality. |
| Optimization | `src/mdp/policy_optimizer.py` | Value iteration, policy improvement, Q-learning and transformation interfaces | Objective values are properties of the configured objective. |
| Beliefs | `src/mdp/belief_updater.py` | Observation updates, entropy and document analysis | Heuristic confidence is not a measured calibration result. |
| Extensions | `src/mdp/plugin_interface.py`, `plugin_manager.py` | Plugin contracts and registration | An extension point does not establish domain validation. |

Use the installed package and its source tests to establish the exact signature and behavior for a revision. The code supplement is illustrative and is not a substitute for those source modules.
