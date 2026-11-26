"""Render the structural fixture for the manuscript from the repository root."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from mdp import Document, StateSpace


def main() -> None:
    source = Path("tests/fixtures/headings_original.md")
    states = StateSpace(Document(file_path=source))
    nodes = list(states.graph.nodes)
    assert len(nodes) == 6
    assert list(states.graph.edges) == list(zip(nodes, nodes[1:]))

    fig, axis = plt.subplots(figsize=(9, 1.8), layout="constrained")
    nx.draw_networkx(
        states.graph,
        pos={node: (index, 0) for index, node in enumerate(nodes)},
        labels={node: states.states[node]["type"] for node in nodes},
        node_color="#dbeafe",
        node_size=2000,
        font_size=8,
        edge_color="#334155",
        arrows=True,
        ax=axis,
    )
    axis.set_axis_off()
    path = Path("output/figures/heading_fixture.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)
    label = "fig:heading-fixture"
    registry = {
        label: {
            "label": label,
            "filename": path.name,
            "caption": "Six classified Markdown lines linked in input order.",
            "generated_by": "docs/manuscript/fixture_figure.py",
            "metadata": {
                "alt_text": "A left-to-right chain of six nodes: heading, heading, paragraph, heading, heading, paragraph.",
            },
        },
    }
    path.with_name("figure_registry.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{source}: {len(nodes)} states, {states.graph.number_of_edges()} edges → {path}")


if __name__ == "__main__":
    main()
