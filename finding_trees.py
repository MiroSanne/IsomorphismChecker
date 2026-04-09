from graph import *
from graph_io import *
import math

def count_tree_isomorphisms(graphs:list[Graph]):
    """
    Determining how many isomorphisms exist between two Trees.

    Input: Two Graphs (that are Trees)
    Output: int
        Representing the amount of isomorphisms.
    """
    G, H = graphs
    root_G, root_H = finding_root_tree(G), finding_root_tree(H)
    if len(root_G)!= len(root_H):
        return 0
    AHU_codes_G, AHU_codes_H = sorted([AHU(r) for r in root_G]), sorted([AHU(r) for r in root_H])
    print(AHU_codes_G, AHU_codes_H)
    if AHU_codes_G != AHU_codes_H:
        return 0
    if len(root_G)==2:
        if AHU_codes_G[0]==AHU_codes_H[1]:
            return number_of_AHUmorphisms(AHU_codes_G[0]) * 2
        else:
            return number_of_AHUmorphisms(AHU_codes_G[0])
    else:
        return number_of_AHUmorphisms(AHU_codes_G[0])


def number_of_AHUmorphisms(AHU_code:str):
    """
    Finding |Aut| for a AHU label.

    Input: AHU_code represented by str
    Output: int
        representing the |Aut|
    """
    inside = AHU_code[1:-1]
    if AHU_code == "0" or inside == "0":
        return 1
    subtrees, balance, start_index = [], 0, 0
    for i, char in enumerate(inside):
        if char == "0" and balance == 0:
            subtrees.append(inside[start_index:i+1])
            start_index = i+1
        elif char == "(":
            balance += 1
        elif char == ")":
            balance -= 1
            if balance == 0:
                subtrees.append(inside[start_index:i+1])
                start_index = i+1
    total_aut = 1
    for substr, n in counting_subtrees(subtrees).items():
        internal_aut = number_of_AHUmorphisms(substr)
        total_aut *= (internal_aut**n)*math.factorial(n)
    return total_aut

def counting_subtrees(subtrees = list[str]):
    counts = {}
    for s in subtrees:
        if s in counts:
            counts[s] += 1
        else:
            counts[s] = 1
    return counts

def AHU(u:Vertex, parent:Vertex=None):
    """
    Finding the unique AHU label from the root of a rooted Tree.

    Input: Vertex (that is the root of a rooted Tree)
    Output: list
        Contains either one or two vertices depending on the size of the graph.
    """
    result = []
    for v in u.neighbours:
        if v!=parent:
            result.append(AHU(v,u))
    if not result:
        return "0"
    return "(" + "".join(sorted(result)) + ")"


def finding_root_tree(G:Graph):
    """
    Finding the root of a tree.

    Input: Graph (that is a Tree)
    Output: list
        Contains either one or two roots depending on the size of the graph.
    """
    current_degree = {v:v.degree for v in G.vertices}
    queue = [v for v in G.vertices if current_degree[v]==1 or current_degree[v]==0]
    remaining_vertices = len(G.vertices)
    while remaining_vertices >2:
        remaining_vertices -= len(queue)
        new_leaves = []
        for q in queue:
            for n in q.neighbours:
                current_degree[n] -= 1
                if current_degree[n] == 1:
                    new_leaves.append(n)
        queue = new_leaves
    return queue 


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
