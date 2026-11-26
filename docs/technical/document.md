# Documents

`Document` loads a UTF-8 file or accepts a Markdown string. Its structure, heading, list, and code-block accessors expose the recognized elements. The document and state-space parsers share fence tracking and preserve line locations at their respective parsing scales.

`update_content(text)` reparses the supplied text. `save(path)` writes the current content to the specified path. See the [Document API](../api/document.md) and the [quick start](../guides/quickstart.md) for examples.
