"""Read the project's legacy data pickles through an explicit capability gate.

Policy uncertainty does not grant a serialized object permission to run code.
Only plain optimizer data and the known DiGraph/cache-view classes are supported;
custom Python objects, reward callables and other globals require migration.
"""

import io
import pickle  # nosec B403  # restricted Unpickler below, never unrestricted load
import pickletools  # nosec B403  # opcode inspection only, no object loading
from typing import Any, BinaryIO, Mapping

from networkx.classes.coreviews import AdjacencyView, AtlasView
from networkx.classes.digraph import DiGraph
from networkx.classes.reportviews import (
    DiDegreeView,
    InDegreeView,
    InEdgeView,
    NodeView,
    OutDegreeView,
    OutEdgeView,
)

MAX_LEGACY_PICKLE_BYTES = 32 * 1024 * 1024
_GRAPH_GLOBALS: Mapping[tuple[str, str], Any] = {
    ("networkx.classes.digraph", "DiGraph"): DiGraph,
    ("networkx.classes.coreviews", "AdjacencyView"): AdjacencyView,
    ("networkx.classes.coreviews", "AtlasView"): AtlasView,
    ("networkx.classes.reportviews", "NodeView"): NodeView,
    ("networkx.classes.reportviews", "OutEdgeView"): OutEdgeView,
    ("networkx.classes.reportviews", "InEdgeView"): InEdgeView,
    ("networkx.classes.reportviews", "DiDegreeView"): DiDegreeView,
    ("networkx.classes.reportviews", "InDegreeView"): InDegreeView,
    ("networkx.classes.reportviews", "OutDegreeView"): OutDegreeView,
}


class _RestrictedUnpickler(pickle.Unpickler):
    def __init__(
        self, stream: BinaryIO, allowed: Mapping[tuple[str, str], Any]
    ) -> None:
        super().__init__(stream)
        self._allowed = allowed

    def find_class(self, module: str, name: str) -> Any:
        try:
            return self._allowed[(module, name)]
        except KeyError as error:
            raise pickle.UnpicklingError("Global lookup is not permitted") from error

    def persistent_load(self, pid: Any) -> Any:
        raise pickle.UnpicklingError("Persistent objects are not permitted")


def _load(
    stream: BinaryIO, allowed: Mapping[tuple[str, str], Any]
) -> Any:
    raw = stream.read(MAX_LEGACY_PICKLE_BYTES + 1)
    if not isinstance(raw, bytes) or len(raw) > MAX_LEGACY_PICKLE_BYTES:
        raise pickle.UnpicklingError("Legacy pickle is not bounded binary data")
    last_name, last_position = "", -1
    try:
        for opcode, _, position in pickletools.genops(raw):
            # EXT opcodes can use copyreg's process-wide extension cache without
            # consulting find_class. Refuse them before constructing any object.
            if opcode.name in {"EXT1", "EXT2", "EXT4", "PERSID", "BINPERSID"}:
                raise pickle.UnpicklingError(
                    "Extension and persistent objects are not permitted"
                )
            if position is None:
                raise pickle.UnpicklingError("Malformed legacy pickle offset")
            last_name, last_position = opcode.name, position
    except (ValueError, UnicodeError, OverflowError) as error:
        raise pickle.UnpicklingError("Malformed legacy pickle") from error
    if last_name != "STOP" or last_position + 1 != len(raw):
        raise pickle.UnpicklingError("Expected exactly one complete legacy pickle")
    return _RestrictedUnpickler(io.BytesIO(raw), allowed).load()


def load_optimizer_pickle(stream: BinaryIO) -> dict[str, Any]:
    """Load plain native-container optimizer state, with no global lookups."""
    state = _load(stream, {})
    if type(state) is not dict:
        raise pickle.UnpicklingError("Optimizer pickle must contain a plain dictionary")
    return state


def load_digraph_pickle(stream: BinaryIO) -> DiGraph:
    """Load an ordinary DiGraph, including its known cached property views."""
    graph = _load(stream, _GRAPH_GLOBALS)
    if type(graph) is not DiGraph:
        raise pickle.UnpicklingError("State-space pickle must contain a DiGraph")
    return graph
