"""Execute the public API guide examples against the real implementation."""

import re
from pathlib import Path


def test_markchain_api_python_examples_execute(tmp_path, monkeypatch):
    page = Path(__file__).parents[1] / "docs/api/markchain.md"
    examples = re.findall(r"^```python\n(.*?)^```", page.read_text(), re.M | re.S)
    assert examples, "The API guide must provide an executable Python example"
    monkeypatch.chdir(tmp_path)
    for number, example in enumerate(examples, start=1):
        exec(compile(example, f"{page.name}:example-{number}", "exec"), {})
