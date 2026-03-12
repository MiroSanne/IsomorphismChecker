from graph import *
from graph_io import *
from collections import Counter

def basic_colorref(path):
   
    with open(path) as f:
        graphs = load_graph(f, Graph, True)
    answers = []
    
    #Setup
    sig_table = {}
    initalize_neighbours = tuple([0] * len(graphs[0].vertices[0].neighbours))
    sig_table[(0,initalize_neighbours)] = 0
    colour_amount_collection: list[int] = []
    final_iterations: list[int] = []
    is_done:list[bool] = []
    all_vertices:dict[Vertex, int] = {}
    final_colours: list[list[int]] = []
    

    for graph in graphs:
        vertices_colours = {vertex: 0 for vertex in graph.vertices}
        all_vertices.update(vertices_colours)
        colour_amount_collection.append(0)
        final_iterations.append(0)
        is_done.append(False)

    i=0
    colour_counter = 1
    old_colour_amount = 1

    #Colour refinement
    while True:
        i += 1
        #Update vertex colours
        new_all_vertices, sig_table, colour_counter = single_iteration(all_vertices, sig_table, colour_counter)
        all_vertices = new_all_vertices
        
        #Get and store itteration
        last_stop = 0
        for index, graph in enumerate(graphs):
            length = len(graph.vertices)
            graph_colours = list(all_vertices.values())[last_stop:last_stop+length]
            unique_colours = len(set(graph_colours))
            if is_done[index] == False:
                if unique_colours == colour_amount_collection[index]:
                    is_done[index] = True
                    final_iterations[index] = i-1                  
                else:
                    colour_amount_collection[index] = unique_colours 
            last_stop += length
        
        if sum(colour_amount_collection) == old_colour_amount or all(colour_amount == 1 for colour_amount in colour_amount_collection):
            break
        
        old_colour_amount = sum(colour_amount_collection)

    #Get colours seperatly per graph and sorted
    last_stop = 0
    for graph in graphs:
        length = len(graph.vertices)
        graph_colours = sorted(list(all_vertices.values())[last_stop:last_stop+length])
        final_colours.append(graph_colours)
        last_stop += length

    # Get list of which graphs are in the same equivalance colour class
    graph_colours_map:dict[tuple, list] = {}
    for index, graph_colours in enumerate(final_colours):
        if tuple(graph_colours) not in graph_colours_map:
            graph_colours_map[tuple(graph_colours)] = []
        graph_colours_map[tuple(graph_colours)].append(index)
    similiar_graphs = list(graph_colours_map.values())

    #Fill in the answer
    for graphs_indexes in similiar_graphs:
        index = graphs_indexes[0]
        graph_colours = final_colours[index]
        sorted_frequency = sorted(Counter(graph_colours).values())
        iteration = final_iterations[index]
        discreet = all(frequency == 1 for frequency in sorted_frequency)
        answers.append((graphs_indexes, sorted_frequency, iteration, discreet))  
    return answers


def single_iteration(vertices_colours:dict[Vertex, int], sig_table:dict, colour_counter:int):
    new_vertices_colours = vertices_colours.copy()
    for  vertex in vertices_colours.keys():
                colour = vertices_colours[vertex]
                neighbours = tuple(sorted(vertices_colours[neighbour] for neighbour in vertex.neighbours))
                if (colour,neighbours) in sig_table:
                    new_vertices_colours[vertex] = sig_table[(colour,neighbours)]
                else:
                    sig_table[(colour,neighbours)] = colour_counter
                    new_vertices_colours[vertex] = colour_counter
                    colour_counter += 1
    return new_vertices_colours, sig_table, colour_counter



def count_isomorphism(D,I):

    #Compute the coarsest stable colouring β of G = {G, H} that refines α(D, I)

    if(unbalanced):
        return 0
    if(discreet):
        return 1
    # Choose a colour class C with | C | ≥ 4.
    #Choose x ∈ C ∩ V(G).
    # num = 0
    # for all y ∈ C ∩ V (H):
    #     num := num + CountIsomorphism(D + x, I + y)
    return num