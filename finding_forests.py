from graph import *
from graph_io import *
from finding_trees import *


def building_subgraph(G:Graph, BFS: dict[Vertex, int]):
    """
    Builds a subgraph from a BFS and Graph.

    Input: 
        G: Graph where we want to build a subgraph from
        BFS: Result of BFS for the subgraph
    Output:
        subgraph_G: A Graph that is a subgraph of G.
    """
    subgraph_G = Graph(directed=G.directed, simple=G.simple)
    vertex_map = {v: Vertex(subgraph_G, label=v.label) for v in BFS.keys()}
    for v in vertex_map.values():
        subgraph_G.add_vertex(v)
    processed_edges = set()
    for v in BFS.keys():
        for e in v.incidence:
            if e not in processed_edges:
                other_v = e.other_end(v)
                if other_v in vertex_map:
                    subgraph_G.add_edge(Edge(vertex_map[v], vertex_map[other_v]))
                    processed_edges.add(e)
    return subgraph_G

def is_graph_a_forest(G:Graph):
    """
    Checking if a Graph can be labeled as a Forest.

    Input: Graph.
    Output: bool
        True if Graph is a forest.
    """
    possible_trees = find_components_of_a_graph(G)
    # Forest <=> |E| = |V| - k
    return len(G.edges) == len(G.vertices) - len(possible_trees)

def find_components_of_a_graph(G:Graph):
    """
    Finds the disconnected components of a Graph.

    Input: Graph.
    Output: list
        Containing all the BFS results that form a component.
    """
    visited_vertices, possible_trees= set(), []
    for v in G.vertices:
        if v not in visited_vertices:
            labels = breadth_first_search(G,v)[0]
            found_vertices = labels.keys()
            visited_vertices.update(found_vertices)
            possible_trees.append(labels)
    return possible_trees


def count_forest_isomorphisms(graphs:list[Graph]):
    """
    Determining how many isomorphisms exist between TWO Forests.

    Input: Two Graphs (that are Forests)
    Output: int
        Representing the amount of isomorphisms.
    """
    G, H = graphs
    components_G, components_H = find_components_of_a_graph(G), find_components_of_a_graph(H)
    # Are the amount of components (k) of both graphs equal?
    if len(components_G) != len(components_H):
        return 0
    # Are the k components all the same length?
    if sorted([len(C) for C in components_G]) != sorted([len(C) for C in components_H]):
        return 0
    # Do the number of roots for all k components match?
    trees_G, trees_H = [building_subgraph(G, C) for C in components_G], [building_subgraph(H, C) for C in components_H]
    roots_G, roots_H = [finding_root_tree(T) for T in trees_G], [finding_root_tree(T) for T in trees_H]
    if sorted(len(r) for r in roots_G) != sorted(len(r) for r in roots_H):
        return 0
    # Are the AHU_codes of all Trees equal?
    AHU_code_Forest_G, AHU_code_Forest_H = [sorted([AHU(r) for r in R]) for R in roots_G], [sorted([AHU(r) for r in R]) for R in roots_H]
    if sorted(AHU_code_Forest_G) != sorted(AHU_code_Forest_H):
        return 0
    else:
        total_aut = 1
        map_aut = {min(ahu):count_tree_isomorphisms([t,t]) for t, ahu in zip(trees_G, AHU_code_Forest_G)}
        print(map_aut)
        for substr, n in counting_subtrees([min(ahu) for ahu in AHU_code_Forest_G]).items():
            base_aut = map_aut[substr]
            total_aut *= (base_aut ** n) * math.factorial(n)
    return total_aut


def counting_trees(trees = list[list[str]]):
    counts = {}
    for t in trees:
        key = tuple(sorted(t))
        if key in counts:
            counts[key] += 1
        else:
            counts[key] = 1
    return counts
