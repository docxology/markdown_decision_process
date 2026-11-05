"""Real legacy round trips and rejection before any serialized code executes."""

import copyreg
import pickle
import struct
from datetime import datetime
from pathlib import Path

import networkx as nx
import pytest

from mdp.policy_optimizer import PolicyOptimizer
from mdp.state_space import StateSpace


def _space():
    space = StateSpace()
    space.parse_markdown("# Public title\n\nRetained paragraph.")
    return space


def _target(kind):
    return PolicyOptimizer(_space()) if kind == "optimizer" else _space()


def _refused_without_execution(target, path, marker):
    previous_graph = getattr(target, "graph", None)
    previous_table = dict(getattr(target, "q_table", {}))
    error = None
    try:
        target.load(str(path))
    except Exception as caught:
        error = caught
    # Check this first: the old loader executes the reducer and only then fails
    # when it tries to use the returned integer as a model dictionary/graph.
    assert not marker.exists(), "Serialized callable executed before load failed"
    assert isinstance(error, pickle.UnpicklingError)
    if previous_graph is not None:
        assert target.graph is previous_graph
    else:
        assert dict(target.q_table) == previous_table


@pytest.mark.parametrize("kind,suffix", [("optimizer", ".pkl"), ("graph", ".gpickle")])
def test_eval_reducer_is_rejected_before_creating_its_tmp_marker(tmp_path, kind, suffix):
    marker = tmp_path / "executed.txt"
    expression = f"__import__('pathlib').Path({str(marker)!r}).write_text('executed')"

    class MarkerReducer:
        def __reduce__(self):
            return eval, (expression,)

    path = tmp_path / ("malicious" + suffix)
    path.write_bytes(pickle.dumps(MarkerReducer(), protocol=4))
    _refused_without_execution(_target(kind), path, marker)


def _extension_marker_writer(marker):
    """A test-only reducer target whose only effect is its tmp_path marker."""
    return Path(marker).write_text("executed")


@pytest.mark.parametrize("kind,suffix", [("optimizer", ".pkl"), ("graph", ".gpickle")])
def test_primed_extension_cache_cannot_bypass_global_restriction(tmp_path, kind, suffix):
    marker = tmp_path / "extension-executed.txt"
    argument = str(marker).encode()
    code = 0x52A710
    copyreg.add_extension(__name__, "_extension_marker_writer", code)
    try:
        # Public registration plus a real function-only pickle produces and
        # primes the reachable extension cache without calling the function.
        # Protocol 2 deliberately avoids FRAME length bookkeeping in the next
        # payload, which appends the marker argument and REDUCE operation.
        function_pickle = pickle.dumps(_extension_marker_writer, protocol=2)
        assert pickle.EXT4 in function_pickle
        restored = pickle.loads(function_pickle)  # nosec B301  # locally generated function reference, no reducer execution
        assert restored is _extension_marker_writer
        assert not marker.exists()
        payload = (
            function_pickle[:-1]
            + pickle.BINUNICODE + struct.pack("<I", len(argument)) + argument
            + pickle.TUPLE1 + pickle.REDUCE + pickle.STOP
        )
        path = tmp_path / ("extension" + suffix)
        path.write_bytes(payload)
        _refused_without_execution(_target(kind), path, marker)
    finally:
        copyreg.remove_extension(__name__, "_extension_marker_writer", code)


@pytest.mark.parametrize("kind,suffix", [("optimizer", ".pkl"), ("graph", ".gpickle")])
def test_unreviewed_global_is_rejected(tmp_path, kind, suffix):
    path = tmp_path / ("unknown" + suffix)
    path.write_bytes(pickle.dumps(datetime(2026, 11, 5), protocol=4))
    with pytest.raises(pickle.UnpicklingError, match="not permitted"):
        _target(kind).load(str(path))


def test_plain_optimizer_state_round_trip_keeps_q_table_and_parameters(tmp_path):
    original = PolicyOptimizer(_space())
    original.q_table = {("header_0", "paragraph_1"): 1.25}
    original.policy = {"header_0": {"paragraph_1": 0.75}}
    original.value_function = {"header_0": 2.5}
    original.learning_rate = 0.125
    original.discount_factor = 0.875
    original.exploration_factor = 0.25
    original.max_iterations = 7
    original.reward_weights = {"readability": 1.0}
    original.custom_rewards = {}
    path = tmp_path / "model.pkl"
    original.save(str(path))
    loaded = PolicyOptimizer(_space())
    loaded.load(str(path))
    assert dict(loaded.q_table) == dict(original.q_table)
    assert dict(loaded.policy) == original.policy
    assert loaded.value_function == original.value_function
    assert (loaded.learning_rate, loaded.discount_factor, loaded.exploration_factor, loaded.max_iterations) == (0.125, 0.875, 0.25, 7)
    assert loaded.reward_weights == original.reward_weights
    assert loaded.custom_rewards == {}
    assert loaded.reward_function.__name__ == "_default_reward_function"


def test_digraph_round_trip_keeps_data_and_cached_views(tmp_path):
    original = _space()
    original.graph.graph["label"] = "ordinary retained graph"
    original.graph.nodes["header_0"]["tags"] = {"one", "two"}
    original.graph["header_0"]["paragraph_1"]["count"] = 3
    for name in ("nodes", "edges", "adj", "succ", "pred", "degree", "in_degree", "out_degree", "in_edges", "out_edges"):
        getattr(original.graph, name)  # populate actual NetworkX cached properties
    path = tmp_path / "graph.gpickle"
    original.save(path)
    loaded = StateSpace()
    loaded.load(path)
    assert type(loaded.graph) is nx.DiGraph
    assert dict(loaded.graph.nodes(data=True)) == dict(original.graph.nodes(data=True))
    assert list(loaded.graph.edges(data=True)) == list(original.graph.edges(data=True))
    assert loaded.graph.graph == original.graph.graph
    assert loaded.transitions["header_0"]["paragraph_1"] == 3
    assert loaded.graph.nodes["header_0"] is loaded.graph._node["header_0"]
    assert list(loaded.graph.degree) == list(original.graph.degree)


def test_concatenated_or_truncated_pickle_is_refused(tmp_path):
    path = tmp_path / "bad.pkl"
    for payload in (pickle.dumps({}) + pickle.dumps({}), pickle.dumps({})[:-1]):
        path.write_bytes(payload)
        with pytest.raises(pickle.UnpicklingError):
            PolicyOptimizer(_space()).load(str(path))
