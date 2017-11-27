from igraph import *
import csv
import numpy as np
import itertools
import random

# Size of grid
graph_size = 5  # grid size, leads to a grid of graph_size*graph_size nodes
num_nodes = graph_size*graph_size   # Number of nodes in the graph
num_ods = 10    # Number of od, have to be less that 1/2 number of nodes
scaling = 1000  # number used to scale the resulting grid graph

g = Graph.Lattice([graph_size, graph_size], circular=False)


# Get node ids and positions
layout = g.layout("kk")     # This fixes the coordinates of the nodes
layout.scale(scaling)

coordinates = layout.coords    # Coordinates of the nodes

nodes_ids = g.vs.indices    # Gets the node ids
g.vs["ID"] = nodes_ids      # Saves nodes ids as attributes of the nodes in the graph object
g.vs["Coordinates"] = coordinates
g.vs["label"] = g.vs["Coordinates"]  # We label the nodes by the ID

# Print vertices and their coordinates
f = open('node_info.csv', 'wb')
writer = csv.writer(f)
node_info_title = ["Node id", "x coord", "y coord"]
writer.writerow(node_info_title)
for v in g.vs:
    row = [v["ID"],v["Coordinates"][0],v["Coordinates"][1]]
    writer.writerow(row)

# Get edge list
g.es["ID"] = g.es.indices
g.es["node_ids"] = g.get_edgelist()
f = open('edge_info.csv', 'wb')
writer = csv.writer(f)
edge_info_title = ["Link id", "source node", "end node"]
writer.writerow(edge_info_title)
for e in g.es:
    row = [e["ID"],e["node_ids"][0], e["node_ids"][1]]
    writer.writerow(row)

# Generate od pairs
pairs = list(itertools.combinations(range(num_nodes), 2))   # Generates the pairs
random.shuffle(pairs)   # shuffles the od pairs to allow for variability
ods = pairs[0:num_ods]

# Generate the paths between the od pairs and save them to csv file
f = open('paths_info.csv', 'wb')
writer = csv.writer(f)
for o in ods:
    paths = g.get_all_shortest_paths(o[0], o[1])
    writer.writerows(paths)

# Plot the resulting graph
plot(g, layout = layout)    # Plotting the graph

