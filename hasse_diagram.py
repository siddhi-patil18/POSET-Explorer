import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from parser import format_value


def remove_self_loops(relation):
    return {
        (a, b) for a, b in relation
        if a != b
    }


def find_cover_relations(elements, relation):
    pairs = remove_self_loops(relation)
    covers = []

    for a, b in pairs:
        intermediate = any(
            x != a and x != b
            and (a, x) in relation
            and (x, b) in relation
            for x in elements
        )

        if not intermediate:
            covers.append((a, b))

    return covers


def build_hasse_graph(elements, covers):
    graph = nx.DiGraph()
    graph.add_nodes_from(elements)
    graph.add_edges_from(covers)

    rank = {}

    for node in nx.topological_sort(graph):
        previous = [
            rank[x] for x in graph.predecessors(node)
        ]
        rank[node] = max(previous, default=-1) + 1

    nx.set_node_attributes(graph, rank, "rank")

    return graph


def calculate_hasse_positions(graph):
    ranks = nx.get_node_attributes(graph, "rank")
    positions = {}

    for rank in set(ranks.values()):
        nodes = [
            n for n in graph.nodes
            if ranks[n] == rank
        ]

        nodes.sort(key=format_value)
        center = (len(nodes) - 1) / 2

        for i, node in enumerate(nodes):
            positions[node] = (i - center, rank*0.6)

    return positions


def draw_hasse_diagram(graph):
    positions = calculate_hasse_positions(graph)

    figure, axis = plt.subplots(figsize=(4, 3))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_color="#E8F1FA",
        edgecolors="#24527A",
        node_size=800,
        ax=axis,
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        arrows=False,
        edge_color="#24527A",
        ax=axis,
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        labels={
            n: format_value(n)
            for n in graph.nodes
        },
        font_size=10,
        ax=axis,
    )

    axis.set_title("Hasse Diagram")
    axis.set_axis_off()
    figure.tight_layout()

    return figure