# Markdown Decision Process documentation

Markdown Decision Process is a Python prototype for parsing Markdown, analyzing document graphs, sampling Markov transitions, and applying configurable transformations and reward functions. Belief updates provide heuristic semantic labels. The corrected research draft preserves the implementation’s evidence and proposes a separate empirical evaluation.

- [Quick start](guides/quickstart.md), [user guide](guides/user_guide.md), [API reference](API_COMPLETE.md), and [technical notes](technical/README.md)
- [Manuscript, fixture, and render commands](manuscript-build.md)
- [Contributing](CONTRIBUTING.md), [development](DEVELOPMENT_PROCESS.md), and [publishing](PUBLISHING.md)

```{toctree}
:hidden:
:maxdepth: 2
:caption: Using the library

guides/quickstart
guides/user_guide
API_COMPLETE
technical/README
manuscript-build
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: Contributing

CONTRIBUTING
DEVELOPMENT_PROCESS
ROADMAP
TODO
PUBLISHING
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Module guides

api/document
api/markchain
api/state_space
api/policy_optimizer
api/markdown_agent
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: API from the source

reference/mdp
```
