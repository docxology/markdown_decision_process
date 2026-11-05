# Development Process for MDP Features

This document outlines the methodical process for implementing features from the [Markdown Decision Process Roadmap](ROADMAP.md).

## Feature Implementation Workflow

The following workflow describes how to take a feature from the roadmap to a completed implementation:

### 1. Feature Selection

1. Select a feature or set of related features from the [roadmap](ROADMAP.md)
2. Create an issue in the project tracker with:
   - Feature description from roadmap
   - Acceptance criteria
   - Any dependencies on other features
   - Technical approach considerations

### 2. Design Phase

1. Research the state-of-the-art for this type of feature
2. Create a design document in `docs/design/` with:
   - Algorithms and approaches to be used
   - API design
   - Performance considerations
   - Integration with existing components
3. Seek feedback and refine the design

### 3. Implementation Phase

1. Create tests in `tests/` that validate the feature (test-driven development)
2. Implement the feature in the appropriate module in `src/mdp/`
3. Create examples in `examples/` that demonstrate the feature's usage
4. Ensure all tests pass with the implementation

### 4. Documentation Phase

1. Create or update technical documentation in `docs/technical/`
2. Update API references
3. Create visualizations if applicable
4. Update the main README if the feature is significant

### 5. Verification Phase

1. Run all tests to ensure no regressions
2. Review code quality and performance
3. Gather feedback on usability from examples

### 6. Roadmap Update

1. Mark the feature as implemented (✅) in the roadmap
2. Update implementation status in technical documentation
3. Remove completed features from future roadmap iterations

## Documentation Structure

For each major component, the documentation should include:

### In `docs/technical/[component].md`:

- **Implementation Status:** What features are implemented vs. in progress
- **Core Concepts:** Theoretical foundation and key abstractions
- **API Reference:** Complete API with examples
- **Performance Characteristics:** Speed, memory usage, etc.
- **Examples:** Common usage patterns
- **Implementation Details:** Algorithms and technical details
- **Testing:** How the component is tested
- **Future Work:** Upcoming improvements

### In `tests/test_[component].py`:

- Unit tests for all methods and edge cases
- Integration tests with other components
- Performance benchmarks

### In `examples/`:

- Standalone examples showing practical usage
- Combined examples showing integration with other components

## Feature Status Tracking

Features move through the following statuses:

1. **Planned:** Listed in the roadmap
2. **In Progress:** Being actively worked on
3. **Implemented:** Code complete with tests
4. **Documented:** Full documentation available
5. **Released:** Included in a versioned release

## Example: Implementing Variable-Order Markov Models

Here's an example of how the variable-order Markov models feature was implemented:

1. **Selection:**
   - Selected "Implement variable-order Markov models for better context awareness" from MarkChain Evolution section

2. **Design:**
   - Researched variable-order Markov chains, focusing on backoff models and interpolation
   - Created design document outlining the approach
   - Designed API extensions to the MarkChain class

3. **Implementation:**
   - Added tests for variable-order functionality in `tests/test_markchain.py`
   - Implemented the feature in `src/mdp/markchain.py`
   - Created an example in `examples/variable_order_comparison.py`

4. **Documentation:**
   - Updated `docs/technical/markchain.md` with details of the implementation
   - Added API reference and examples

5. **Verification:**
   - Ran comprehensive tests to ensure correctness
   - Benchmarked performance against the previous implementation

6. **Roadmap Update:**
   - Marked the feature as implemented in `docs/ROADMAP.md`
   - Updated status in technical documentation

## Conventions and Best Practices

### Code Style

- Follow the project's code style as defined in `.cursorrules`
- Use type hints for all function parameters and return values
- Add comprehensive docstrings in Google style
- Write clean, maintainable, and efficient code

### Testing

- Aim for >90% test coverage for all new features
- Include both happy path and edge case tests
- Add performance tests for critical components

### Offline validation inputs

Use a frozen `uv.lock` environment and record the actual interpreter, dependency
inventory, native tools, command and source revision. The project pin remains
Python 3.15; Python 3.11 is also supported by `requires-python`. The locked
WordCloud 1.9.6 release has no CPython 3.15 wheel for macOS arm64, so a binary-only
3.15 bootstrap cannot be reported as a full-suite pass. Record a supported
interpreter explicitly rather than silently changing the pin.

Readability tests additionally need NLTK's CMU dictionary. Prepare it before an
offline run; do not rely on a test making a network download. The reviewed
[current test resource](https://raw.githubusercontent.com/nltk/nltk_data/550b6625bcef1f2abff2ff770a5a0d272c9c6b2a/packages/corpora/cmudict.zip)
is 896,069 bytes with SHA-256
`d07cca47fd72ad32ea9d8ad1219f85301eeaf4568f8b6b73747506a71fb5afd6`.
Its immutable [index](https://raw.githubusercontent.com/nltk/nltk_data/550b6625bcef1f2abff2ff770a5a0d272c9c6b2a/index.xml)
and [license metadata](https://raw.githubusercontent.com/nltk/nltk_data/550b6625bcef1f2abff2ff770a5a0d272c9c6b2a/packages/corpora/cmudict.xml)
identify CMU as the source and permit research/commercial use with requested
acknowledgment. Verify size/hash, extract under a private
`NLTK_DATA/corpora/cmudict/` directory and retain the data binding with the run.
Do not commit this wordlist or treat it as recovered manuscript study data.

Run `python -B -m pytest --benchmark-disable tests/` in an independent staging
copy when repository writes are disallowed: existing tests create output files.
Disabling benchmark calibration executes benchmark functions once; it supplies
implementation checks, not paper performance evidence. Report every skipped or
unavailable test. The real metadata tests require an actual local Pandoc;
`extract_metadata` reads its JSON AST and does not require PyYAML.

The test workflow stages that exact dictionary with
[prepare_test_data.py](../.github/scripts/prepare_test_data.py), checks size and
SHA-256 before extraction, and keeps it under `runner.temp`. Its `--archive PATH`
option validates a retained local copy without network access. Ordinary test
runs use `--benchmark-disable`; the separate benchmark step retains calibration.
Linux/Python 3.11 also installs the official Ubuntu 24.04 Pandoc package and
requires the real metadata integration tests. Other matrix entries retain
optional native-tool behavior. Pushes to `codex/**` run the same path-filtered
workflow before an ordinary promotion of the tested commit to `main`.

Security scanning keeps all Bandit checks enabled. Narrow inline annotations
identify document-model pseudo-random sampling (B311), explicit caller-requested
local Pandoc commands passed as argument lists without a shell (B603/B404), and
pickle serialization/restricted-reader imports (B403). These annotations do not
permit unrestricted deserialization. Pandoc binary overrides, filters and extra
options remain choices made by the calling local application.

`PolicyOptimizer.load` and the `.gpickle` branch of `StateSpace.load` read at most
32 MiB and accept exactly one complete legacy pickle. The optimizer accepts plain
data; graphs accept the explicit ordinary `DiGraph` and cached-view classes.
Unknown globals and custom reward callables/object classes are rejected.
Extension-cache entries and persistent references are refused before object
construction. Existing standard save/load formats remain supported and input
files are never rewritten.
Custom Python-object persistence needs a separate reviewed data migration.
Tests exercise real round trips and malicious reducers that may only write a
marker in their disposable test directory. These are implementation/security
checks, not recovered historical experiment evidence.

### Documentation

- Keep documentation in sync with code
- Use consistent formatting and terminology
- Include examples for all major use cases
- Document performance considerations

### Commits and Pull Requests

- Use descriptive commit messages
- Reference the issue number in commits
- Keep pull requests focused on a single feature or bugfix
- Ensure all tests pass before requesting review

Following this process ensures that the MDP project develops in a methodical, well-documented manner, with features moving smoothly from roadmap to implementation. 