"""Dynamic Hasse-diagram calculations and Matplotlib rendering."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from parser import format_value


def remove_self_loops(
    relation: set[tuple[Any, Any]],
) -> set[tuple[Any, Any]]:
    """Remove reflexive pairs because Hasse diagrams do not draw loops."""

    return {
        (lower, upper)
        for lower, upper in relation
        if lower != upper
    }


def remove_transitive_edges(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> list[tuple[Any, Any]]:
    """Keep only relation pairs with no intermediate element."""

    non_loop_pairs = remove_self_loops(relation)
    cover_relations: list[tuple[Any, Any]] = []

    for lower, upper in non_loop_pairs:
        has_intermediate_element = any(
            middle not in {lower, upper}
            and (lower, middle) in relation
            and (middle, upper) in relation
            for middle in elements
        )

        if not has_intermediate_element:
            cover_relations.append((lower, upper))

    element_order = {
        element: index
        for index, element in enumerate(elements)
    }

    cover_relations.sort(
        key=lambda pair: (
            element_order[pair[0]],
            element_order[pair[1]],
        )
    )

    return cover_relations


def find_cover_relations(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> list[tuple[Any, Any]]:
    """Return the cover relations of a valid POSET."""

    return remove_transitive_edges(
        elements,
        relation,
    )


def build_hasse_graph(
    elements: list[Any],
    covers: list[tuple[Any, Any]],
) -> nx.DiGraph:
    """Build a directed graph from computed nodes and cover edges."""

    graph = nx.DiGraph()

    graph.add_nodes_from(elements)
    graph.add_edges_from(covers)

    # A valid POSET cover graph is acyclic.
    # Calculate a level for every node dynamically.
    ranks: dict[Any, int] = {}

    for node in nx.topological_sort(graph):
        predecessor_ranks = [
            ranks[predecessor]
            for predecessor in graph.predecessors(node)
        ]

        ranks[node] = max(
            predecessor_ranks,
            default=-1,
        ) + 1

    nx.set_node_attributes(
        graph,
        ranks,
        "rank",
    )

    return graph


def calculate_hasse_positions(
    graph: nx.DiGraph,
) -> dict[Any, tuple[float, float]]:
    """Calculate adaptive positions for any finite cover graph."""

    groups: defaultdict[int, list[Any]] = defaultdict(list)

    ranks = nx.get_node_attributes(
        graph,
        "rank",
    )

    for node, rank in ranks.items():
        groups[rank].append(node)

    positions: dict[Any, tuple[float, float]] = {}

    for rank, nodes in groups.items():
        ordered_nodes = sorted(
            nodes,
            key=format_value,
        )

        center = (len(ordered_nodes) - 1) / 2

        for index, node in enumerate(ordered_nodes):
            # Coordinates depend on graph size and calculated rank.
            positions[node] = (
                float(index - center),
                float(rank),
            )

    return positions


def draw_hasse_diagram(
    graph: nx.DiGraph,
):
    """Return a Matplotlib figure for the generated Hasse graph."""

    positions = calculate_hasse_positions(graph)

    node_count = max(
        len(graph.nodes),
        1,
    )

    ranks = nx.get_node_attributes(
        graph,
        "rank",
    )

    rank_count = max(
        ranks.values(),
        default=0,
    ) + 1

    figure_width = max(
        7.0,
        min(
            16.0,
            4.5 + node_count * 0.55,
        ),
    )

    figure_height = max(
        4.5,
        min(
            12.0,
            3.5 + rank_count * 1.25,
        ),
    )

    figure, axis = plt.subplots(
        figsize=(
            figure_width,
            figure_height,
        ),
    )

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_color="#E8F1FA",
        edgecolors="#24527A",
        node_size=1700,
        linewidths=1.5,
        ax=axis,
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="#24527A",
        width=1.8,
        arrows=False,
        ax=axis,
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels={
            node: format_value(node)
            for node in graph.nodes
        },
        font_color="#16324F",
        font_size=10,
        ax=axis,
    )

    axis.set_title(
        "Hasse Diagram",
        fontsize=14,
        pad=16,
    )

    axis.set_axis_off()
    figure.tight_layout()

    return figure