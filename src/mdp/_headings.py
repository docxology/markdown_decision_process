"""Keep fenced examples out of the document's heading state space."""

import re
from typing import Iterator, Match, Tuple

_HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def iter_atx_headings(content: str) -> Iterator[Tuple[int, Match[str]]]:
    """Yield existing ATX-heading matches and zero-based lines outside fences.

    Recognize backtick or tilde fences with up to three leading spaces. A
    closing fence must use the same marker, be at least as long as its opener,
    and have only trailing whitespace. Backtick info strings cannot contain a
    backtick. An unclosed fence consumes the remaining lines. Other Markdown
    constructs and the existing heading syntax are deliberately unchanged.
    """
    fence_marker = ""
    fence_length = 0
    for index, line in enumerate(content.split("\n")):
        fence = _FENCE.match(line)
        if fence_marker:
            if (
                fence
                and fence.group(1)[0] == fence_marker
                and len(fence.group(1)) >= fence_length
                and not fence.group(2).strip(" \t\r")
            ):
                fence_marker = ""
            continue
        if fence and (fence.group(1)[0] != "`" or "`" not in fence.group(2)):
            fence_marker = fence.group(1)[0]
            fence_length = len(fence.group(1))
            continue
        heading = _HEADING.match(line)
        if heading:
            yield index, heading
