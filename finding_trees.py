from graph import *
from graph_io import *

def is_graph_a_tree(G:Graph):
    """
    Checking if a Graph can be labeled as a Tree.

    Input: Graph.
    Output: bool
        True if Graph is a Tree.
    """
    # Is the relation between edges and vertices correct?
    if len(G.edges) != len(G.vertices) - 1:
        return False
    # Is the graph also connected?
    elif len(breadth_first_search(G)[0]) != len(G.vertices):
        return False
    # We now have |E|=|V|-1 & Connected => G is a Tree
    else:
        return True

    
def breadth_first_search(G:Graph, start_vertex:Vertex=None):
    """
    Perform the breadth first search (BFS) algorithm.

    Input: Graph.
    Output: list as in DM lectures.
    """
    if start_vertex is None:
        start_vertex = G.vertices[0]
    label, parent, L, k = {start_vertex:1}, {}, [start_vertex], 1
    while L:
        v = L.pop(0)
        for w in v.neighbours:
            if w not in label:
                k += 1
                label[w], parent[w] = k, v
                L.append(w)
    return label, parent