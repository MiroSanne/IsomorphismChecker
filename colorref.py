from graph import *
from graph_io import *
from finding_trees import *
from finding_forests import *
from collections import Counter


def fast_colorref(graphs: list[Graph], colouring: dict[tuple[int, Vertex], int] = None, counter: int = 0):
    """
    Apply the fast color refinement algorithm to a list of graphs.
    Uses partition refinement with a queue of splitters for O((n+m) log n) complexity.

    Input:
        graphs: list of Graphs
        colouring: initial colouring represented by a dictionary {(graph_index, Vertex): int}
        counter: integer representing the next unused colour
    Output:
        same_class: bool
            True if all graphs are in the same equivalence class
        discrete: bool
            True if the colouring is discrete
        most_frequent_colour: int
            The colour that occurs most frequently
        all_vertices: dict[(int, Vertex), int]
            The final stable colouring
        colour_counter: int
            Updated colour for new colours
    """

    # If no initial colouring was given we give it a (uniform) colouring
    if colouring is None or colouring == {}:
        colouring = {}
        for gi, graph in enumerate(graphs):
            for v in graph.vertices:
                colouring[(gi, v)] = 0
        counter = 1

    # Setup
    all_vertices: dict[tuple[int, Vertex], int] = colouring.copy()
    colour_classes: dict[int, set] = {}
    final_colours: list[list[int]] = []

    # Build colour_classes as the inverse of all_vertices
    for key, colour in all_vertices.items():
        if colour not in colour_classes:
            colour_classes[colour] = set()
        colour_classes[colour].add(key)

    colour_counter = counter
    queue: set[int] = set(colour_classes.keys())

    # Colour refinement
    while queue:
        C_id = queue.pop()
        C = colour_classes[C_id]

        # Count how many neighbours each vertex has inside C
        # Only touches vertices adjacent to C → O(edges incident to C)
        neighbour_count: dict[tuple, int] = {}
        for (gi, v) in C:
            for u in v.neighbours:
                key = (gi, u)
                neighbour_count[key] = neighbour_count.get(key, 0) + 1

        # Only colour classes that have at least one vertex touching C can be split
        affected_classes = set()
        for key in neighbour_count:
            affected_classes.add(all_vertices[key])

        for D_id in affected_classes:
            D = colour_classes[D_id]

            # Build non-zero groups by iterating only neighbour_count (not all of D)
            # Vertices absent from neighbour_count have an implicit count of 0
            non_zero_groups: dict[int, set] = {}
            for key, count in neighbour_count.items():
                if all_vertices[key] == D_id:
                    if count not in non_zero_groups:
                        non_zero_groups[count] = set()
                    non_zero_groups[count].add(key)

            # Check if an implicit zero group exists (vertices in D with no neighbours in C)
            non_zero_total = sum(len(g) for g in non_zero_groups.values())
            zero_size = len(D) - non_zero_total

            # Total distinct groups; if only 1, D doesn't split
            total_groups = len(non_zero_groups) + (1 if zero_size > 0 else 0)
            if total_groups <= 1:
                continue

            # Determine the largest group without building the zero set unnecessarily
            best_nz_key = max(non_zero_groups, key=lambda c: len(non_zero_groups[c]))

            if zero_size >= len(non_zero_groups[best_nz_key]):
                # Zero group is largest — keeps D_id, no need to enumerate it
                largest_count = 0
                groups = dict(non_zero_groups)
                # groups[0] intentionally omitted — zero group stays in D naturally
            else:
                # A non-zero group is largest — only now build the zero set
                largest_count = best_nz_key
                all_non_zero = set().union(*non_zero_groups.values())
                groups = dict(non_zero_groups)
                if zero_size > 0:
                    groups[0] = D - all_non_zero

            for count, vertices in groups.items():
                if count == largest_count:
                    continue

                new_id = colour_counter
                colour_counter += 1

                # Update both all_vertices and colour_classes
                for key in vertices:
                    all_vertices[key] = new_id
                    D.discard(key)
                colour_classes[new_id] = vertices

                # Queue rule: D_id always retains the largest group so new_id is always
                # the smaller half — enqueue new_id regardless of whether D_id was queued
                queue.add(new_id)

    # Get colours separately per graph and sorted
    # Explicit (gi, v) lookup avoids dict-order fragility when called with a pre-built colouring
    # Also safe for UnsafeGraph whose .vertices returns an unordered set
    for gi, graph in enumerate(graphs):
        graph_colours = sorted([all_vertices[(gi, v)] for v in graph.vertices])
        final_colours.append(graph_colours)

    # Get list of which graphs are in the same equivalence colour class
    graph_colours_map: dict[tuple, list] = {}
    for index, graph_colours in enumerate(final_colours):
        if tuple(graph_colours) not in graph_colours_map:
            graph_colours_map[tuple(graph_colours)] = []
        graph_colours_map[tuple(graph_colours)].append(index)
    similiar_graphs = list(graph_colours_map.values())

    # Fill in the answer
    same_class = len(similiar_graphs) == 1
    most_frequent_colour = max(Counter(final_colours[0]).items(), key=lambda pair: pair[1])[0]
    discrete = len(final_colours[0]) == len(set(final_colours[0]))
    return same_class, discrete, most_frequent_colour, all_vertices, colour_counter


def count_isomorphism(D: list, I: list, graphs: list[Graph], colouring: dict[tuple[int, Vertex], int], counter: int):
    """
    Count the number of isomorphisms between two graphs.

    Input:
        D: List of vertices from the first graph that have been fixed.
        I: List of vertices from the second graph that have been fixed.
        graphs: List containing the two Graphs.
        colouring: Current colouring.
        counter: Current colour counter.
    Output:
        num: int
            Total number of isomorphisms found between the two graphs.
    """
    G, H = graphs
    if len(D) != len(I) or len(G.edges) != len(H.edges):
        return 0
    G_tree, H_tree = is_graph_a_tree(G), is_graph_a_tree(H)
    if G_tree != H_tree:
        return 0
    elif G_tree:
        return count_tree_isomorphisms(graphs)
    G_Forest, H_Forest = is_graph_a_forest(G), is_graph_a_forest(H)
    if G_Forest != H_Forest:
        return 0
    elif G_Forest:
        return count_forest_isomorphisms(graphs)

    # Use fast colour refinement for O((n+m) log n) complexity
    same_class, discreet, most_frequent_colour, all_vertices, counter = fast_colorref(graphs, colouring, counter)
    if not same_class:
        return 0
    if discreet:
        return 1

    # Robust (gi, v) lookup instead of fragile dict-order slicing
    # Safe for both Graph (ordered _vlist) and UnsafeGraph (unordered _v set)
    xs = [(0, v) for v in graphs[0].vertices if all_vertices[(0, v)] == most_frequent_colour]
    ys = [(1, v) for v in graphs[1].vertices if all_vertices[(1, v)] == most_frequent_colour]

    x = xs[0]
    selected_colour = counter
    counter += 1
    all_vertices[x] = selected_colour

    num = 0
    for y in ys:
        copy_of_all_vertices = all_vertices.copy()
        copy_of_all_vertices[y] = selected_colour
        Dy = D.copy()
        Dy.append(x)
        Iy = I.copy()
        Iy.append(y)
        num = num + count_isomorphism(Dy, Iy, graphs, copy_of_all_vertices, counter)
    return num


def solver(file: str):
    """
    Solve the isomorphism or automorphism problem based on the filename suffix.

    Input:
        file: string path to a .grl.txt file.
    Output:
        None. Results are printed directly to the console.
    """
    with open(file, 'r') as f:
        graphs = load_graph(f, Graph, True)

    if file.endswith("GIAut.grl.txt"):
        print("Sets of isomorphic graphs:")
        pairs = []
        # Only check unordered pairs to avoid redundant work
        for index in range(len(graphs)):
            for index2 in range(index + 1, len(graphs)):
                isomorphisms = count_isomorphism([], [], [graphs[index], graphs[index2]], {}, 0)
                if isomorphisms != 0:
                    pairs.append((index, index2))
        for group in groups_from_pairs(pairs):
            print(group)

        print("Graphs with automorphisms:")
        for index, graph in enumerate(graphs):
            automorphisms = count_isomorphism([], [], [graph, graph], {}, 0)
            print(" " + str(index) + ": " + str(automorphisms))

    elif file.endswith("Aut.grl.txt"):
        print("Graphs with automorphisms:")
        for index, graph in enumerate(graphs):
            automorphisms = count_isomorphism([], [], [graph, graph], {}, 0)
            print(" " + str(index) + ": " + str(automorphisms))

    elif file.endswith("GI.grl.txt"):
        print("Sets of isomorphic graphs:")
        pairs = []
        # Only check unordered pairs to avoid redundant work
        for index in range(len(graphs)):
            for index2 in range(index + 1, len(graphs)):
                isomorphisms = count_isomorphism([], [], [graphs[index], graphs[index2]], {}, 0)
                if isomorphisms != 0:
                    pairs.append((index, index2))
        for group in groups_from_pairs(pairs):
            print(group)


def groups_from_pairs(pairs: list[tuple[int, int]]):
    """
    Organize pairs of isomorphic graphs into distinct equivalence groups.

    Input:
        pairs: list of tuples (index1, index2) representing found isomorphisms between graphs.
    Output:
        list[list[int]]: A list of groups, where each group contains the indices of graphs
                         that are isomorphic to each other.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in pairs:
        union(a, b)

    comps = {}
    for x in parent:
        comps.setdefault(find(x), []).append(x)
    return [sorted(c) for c in comps.values()]