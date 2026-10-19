# Code Supplement

The implementation described in this source revision is maintained in
[`src/mdp/`](../src/mdp/), with executable regression checks in
[`tests/`](../tests/). Use a fixed Git commit and record the environment when
evaluating it. The prior supplement's hypothetical modules, deployment recipes
and numerical example outcomes have been removed from the active paper; they
remain available in Git history and historical generated publications.

## Minimal implemented transformation

With the package installed, the following example reads an existing Markdown
file and writes a heading transformation to a separate output path:

```python
from pathlib import Path
from mdp.document import Document
from mdp.transformations import HeadingLevelTransformation, TransformationPipeline

source = Document(file_path=Path("input.md"))
pipeline = TransformationPipeline([HeadingLevelTransformation(increment=1)])
pipeline.apply(source, Path("transformed.md"))
```

This example demonstrates a structural operation. It does not measure semantic
preservation, document quality, model performance or production scalability.
The deep-path regression in `tests/test_document_paths.py` exercises this
interface using real file input and verifies the transformed content.

## Evaluation implementation remains prospective

The study proposed in Section 06 needs its own identified corpus, baseline
configuration, participant protocol where applicable, per-run observations and
analysis runner. The unit suite validates implementation behavior; it does not
provide observations for the withdrawn empirical tables. No synthetic score,
effect size or significance value is presented as an observed result here.
