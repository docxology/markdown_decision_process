# Document transformations

Transformations apply structural or formatting changes to a `Document`. The built-in edits handle heading levels, list markers, links, code fence labels, table alignment, and text emphasis. Give each transformation the parameters that describe the change and specify a distinct output path.

A `TransformationPipeline` applies its list of transformations in order. Each subsequent operation sees the previous operation’s output. Run the example in the [quick start](../guides/quickstart.md) and compare the transformed Markdown with its source.
