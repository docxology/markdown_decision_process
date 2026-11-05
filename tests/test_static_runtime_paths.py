"""Exercise public runtime paths previously missed by the static CI gate."""

import matplotlib.pyplot as plt
import pytest

from mdp.animations import MarkChainGenerationAnimator
from mdp.document import Document
from mdp.markchain import MarkChain
from mdp.policy_optimizer import PolicyOptimizer
from mdp.quality import DocumentQuality


def test_public_policy_parser_uses_independent_state_space():
    optimizer = PolicyOptimizer()
    elements = optimizer.parse_document("# Title\n\nA paragraph.\n\n## Details")
    assert [element["type"] for element in elements] == [
        "header", "paragraph", "header"
    ]
    assert [(element["level"], element["text"]) for element in elements
            if element["type"] == "header"] == [(1, "Title"), (2, "Details")]
    assert optimizer.state_space is None


def test_generation_animation_without_start_counts_writes_real_gif(tmp_path):
    chain = MarkChain()
    chain.train("# Only state")
    chain.start_states.clear()
    destination = tmp_path / "generation.gif"
    try:
        result = MarkChainGenerationAnimator(chain).animate_generation(
            str(destination), steps=2, fps=1
        )
        assert result == str(destination)
        assert destination.read_bytes()[:6] in (b"GIF87a", b"GIF89a")
        assert destination.stat().st_size > 100
    finally:
        plt.close("all")


def test_quality_all_metrics_requires_input_then_matches_analysis():
    quality = DocumentQuality()
    with pytest.raises(ValueError, match="document"):
        quality.get_all_metrics()
    document = Document(content="# Title\n\nSimple words make a short sentence.")
    nested = quality.analyze_document(document)
    flattened = quality.get_all_metrics()
    assert flattened["overall_score"] == nested["overall_score"]
    for category in ("readability", "information_density", "structural_balance"):
        for name, value in nested[category].items():
            assert flattened[name] == value
    assert quality.get_all_metrics(Document(content=""))["overall_readability"] == 0


def test_failed_quality_replacement_clears_previous_selection(tmp_path):
    quality = DocumentQuality()
    quality.analyze_document(Document(content="# Selected\n\nA short sentence."))
    # Opening a directory raises EISDIR on POSIX and EACCES on Windows.
    with pytest.raises((IsADirectoryError, PermissionError)):
        quality.analyze_document(tmp_path)
    with pytest.raises(ValueError, match="document"):
        quality.get_all_metrics()


def test_agent_value_and_experience_arrays_round_trip_without_mocking(tmp_path):
    from mdp.markdown_agent import MarkdownAgent

    original = MarkdownAgent()
    original.value_function = {"paragraph_0": 0.625}
    original.experiences = [{"state": "paragraph_0", "reward": 0.5}]
    original.save_models(str(tmp_path))
    restored = MarkdownAgent()
    restored.load_models(str(tmp_path))
    assert restored.value_function == original.value_function
    assert restored.experiences == original.experiences


def test_restored_q_table_keeps_unseen_values_numeric_and_can_continue_learning(tmp_path):
    from mdp.state_space import StateSpace

    space = StateSpace(Document(content="# Title\n\nA paragraph."))
    optimizer = PolicyOptimizer(space)
    destination = tmp_path / "policy.pkl"
    optimizer.save(str(destination))
    restored = PolicyOptimizer(space)
    restored.load(str(destination))
    states = list(space.states)
    assert restored.q_table[(states[0], states[1])] == 0.0
    learned = restored.q_learning(episodes=1)
    assert learned
    assert all(isinstance(value, (int, float)) for value in learned.values())
