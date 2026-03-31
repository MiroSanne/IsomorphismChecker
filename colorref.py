from graph import *
from graph_io import *
from collections import Counter

def basic_colorref(graphs: list[Graph], colouring: dict[tuple[int,Vertex], int], counter: int = 0):
    """
    Apply the color refinement algorithm to a list of graphs.

    Input:
        graphs: list of Graphs
        colouring: initial colouring represented by a dictionary {Vertex: int}
        counter: integer representing the next unused colour 
    Output: 
        same_class: bool 
            True if all graphs are in the same equivalence class
        discrete: bool
            True if the colouring is discrete
        most_frequent_colour: int
            The colour that occurs most frequently
        all_vertices: dict[Vertex, int]
            The final stable colouring
        colour_counter: int
            Updated colour for new colours
    """
    
    # If no initial colouring was given we give it a (uniform) colouring
    vertexdict = {}
    if colouring == {}:
        # Uniform colouring:
        for gi, graph in enumerate(graphs):
            for v in graph.vertices:
                key = (gi, v)
                vertexdict[v] = gi
                colouring[key] = 0
        counter = 1
    else:
        for gi, graph in enumerate(graphs):
            for v in graph.vertices:
                vertexdict[v] = gi

    #Setup
    sig_table = {}
    colour_amount_collection: list[int] = []
    final_iterations: list[int] = []
    is_done:list[bool] = []
    all_vertices:dict[tuple[int,Vertex], int] = {}
    final_colours: list[list[int]] = []

    last_stop = 0
    for index, graph in enumerate(graphs):
        all_vertices = colouring.copy()
        number_of_vertices = len(graph.vertices)
        graph_colours = list(all_vertices.values())[last_stop:last_stop + number_of_vertices]
        unique_colours = len(set(graph_colours))
        colour_amount_collection.append(unique_colours)
        last_stop += number_of_vertices
        final_iterations.append(0)
        is_done.append(False)

    i=0
    colour_counter = counter
    old_colour_amount = sum(colour_amount_collection)

    #Colour refinement
    while True:
        i += 1
        #Update vertex colours
        all_vertices, sig_table, colour_counter = single_iteration(all_vertices, sig_table, colour_counter, vertexdict)
        
        #Get and store iteration
        last_stop = 0
        for index, graph in enumerate(graphs):
            number_of_vertices = len(graph.vertices)
            graph_colours = list(all_vertices.values())[last_stop:last_stop+number_of_vertices]
            unique_colours = len(set(graph_colours))
            if is_done[index] == False:
                if unique_colours == colour_amount_collection[index]:
                    is_done[index] = True
                    final_iterations[index] = i-1                  
                else:
                    colour_amount_collection[index] = unique_colours 
            last_stop += number_of_vertices

        #Todo: check if all case is redundant?
        if sum(colour_amount_collection) == old_colour_amount or all(colour_amount == 1 for colour_amount in colour_amount_collection):
            break
        
        old_colour_amount = sum(colour_amount_collection)

    #Get colours seperatly per graph and sorted
    last_stop = 0
    for graph in graphs:
        number_of_vertices = len(graph.vertices)
        graph_colours = sorted(list(all_vertices.values())[last_stop:last_stop+number_of_vertices])
        final_colours.append(graph_colours)
        last_stop += number_of_vertices

    # Get list of which graphs are in the same equivalance colour class
    graph_colours_map:dict[tuple, list] = {}
    for index, graph_colours in enumerate(final_colours):
        if tuple(graph_colours) not in graph_colours_map:
            graph_colours_map[tuple(graph_colours)] = []
        graph_colours_map[tuple(graph_colours)].append(index)
    similiar_graphs = list(graph_colours_map.values())

    #Fill in the answer

    same_class = len(similiar_graphs)==1
    most_frequent_colour = max(Counter(final_colours[0]).items(), key=lambda pair: pair[1])[0]
    discrete = len(final_colours[0]) == len(set(final_colours[0]))
    return same_class, discrete, most_frequent_colour, all_vertices, colour_counter


def single_iteration(vertices_colours:dict[tuple[int,Vertex], int], sig_table:dict, colour_counter:int, vertexdict: dict[Vertex, int]):
    new_vertices_colours = vertices_colours.copy()
    for key in vertices_colours.keys():
                colour = vertices_colours[key]
                neighbours = tuple(sorted(vertices_colours[vertexdict[neighbour], neighbour] for neighbour in key[1].neighbours))
                if (colour,neighbours) in sig_table:
                    new_vertices_colours[key] = sig_table[(colour,neighbours)]
                else:
                    sig_table[(colour,neighbours)] = colour_counter
                    new_vertices_colours[key] = colour_counter
                    colour_counter += 1
    return new_vertices_colours, sig_table, colour_counter



def count_isomorphism(D:list, I:list, graphs, colouring, counter):
    same_class, discreet, most_frequent_colour, all_vertices, counter = basic_colorref(graphs, colouring, counter)

    if not same_class:
        return 0
    if discreet:
        return 1

    last_stop = 0
    graphs_colours= []
    for graph in graphs:
        number_of_vertices = len(graph.vertices)
        graph_colours = list(all_vertices.items())[last_stop:last_stop+number_of_vertices]
        graphs_colours.append(graph_colours)
        last_stop += number_of_vertices

    xs = [vertex for vertex, colour in graphs_colours[0] if colour == most_frequent_colour]
    ys = [vertex for vertex, colour in graphs_colours[1] if colour == most_frequent_colour]
    x = xs[0]
    selected_colour = counter
    counter += 1
    all_vertices[x] = selected_colour
    num = 0
    for y in ys:
        all_vertices[y] = selected_colour
        D.append(x)
        I.append(y)
        num = num + count_isomorphism(D, I, graphs, all_vertices, counter)
    return num



def solver(file):
    with open(file, 'r') as f:
        graphs = load_graph(f, Graph, True)

    if file.endswith("GIAut.grl.txt"):
        print("Sets of isomorphic graphs:")
        pairs = []
        for index, first_graph in enumerate(graphs):
            for index2, second_graph in enumerate(graphs):
                if first_graph != second_graph:
                    isomorphisms = count_isomorphism([],[],[first_graph,second_graph],{},0)
                    if isomorphisms != 0:
                        pairs.append((index,index2))
        for group in groups_from_pairs(pairs):
            print(group)

        print("Graphs with automorphisms:")
        for index, graph in enumerate(graphs):
            automorphisms = count_isomorphism([], [], [graph, graph], {}, 0)
            print(" " + index.__str__() + " : " + automorphisms.__str__())

    elif file.endswith("Aut.grl.txt"):
        print("Graphs with automorphisms:")
        for index, graph in enumerate(graphs):
            automorphisms = count_isomorphism([],[],[graph,graph],{},0)
            print(" " + index.__str__() + " : " + automorphisms.__str__())

    elif file.endswith("GI.grl.txt"):
        print("Sets of isomorphic graphs")
        pairs = []
        for index, first_graph in enumerate(graphs):
            for index2, second_graph in enumerate(graphs):
                if first_graph != second_graph:
                    isomorphisms = count_isomorphism([],[],[first_graph,second_graph],{},0)
                    if isomorphisms != 0:
                        pairs.append((index,index2))
        for group in groups_from_pairs(pairs):
            print(group)
    else:
        return None




def groups_from_pairs(pairs):
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
