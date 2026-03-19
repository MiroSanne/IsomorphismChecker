from colorref import *
from colorrefOld import *
with open("colorref_largeexampleedt_6_960.grl.txt") as f:
    graphs = load_graph(f, Graph, True)

all_vertices ={}
for graph in graphs:
        vertices_colours = {vertex: 0 for vertex in graph.vertices}
        all_vertices.update(vertices_colours)
print(basic_colorref_old("colorref_largeexampleedt_6_960.grl.txt"))
print(count_isomorphism([], [], graphs, all_vertices, 0))

with open("colorref_smallexampleed_2_49.grl.txt") as f:
    graphs = load_graph(f, Graph, True)

all_vertices ={}
for graph in graphs:
        vertices_colours = {vertex: 0 for vertex in graph.vertices}
        all_vertices.update(vertices_colours)
print(basic_colorref_old("colorref_smallexampleed_2_49.grl.txt"))
print(count_isomorphism([], [], graphs, all_vertices, 0))