from igraph import *
import csv
import numpy as np
import itertools
import random

#Function used to determine all paths between ods
def find_all_paths(graph, start, end):
    def find_all_paths_aux(adjlist, start, end, path):
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        for node in adjlist[start] - set(path):
            paths.extend(find_all_paths_aux(adjlist, node, end, path))
        return paths

    adjlist = [set(graph.neighbors(node)) for node in xrange(graph.vcount())]
    return find_all_paths_aux(adjlist, start, end, [])

# Function that determines all paths between ods that have lengh les or equal to given maxlengh
def find_all_paths_len(graph, start, end, mode = 'OUT', maxlen = None):
    def find_all_paths_aux(adjlist, start, end, path, maxlen = None):
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        if maxlen is None or len(path) <= maxlen:
            for node in adjlist[start] - set(path):
                paths.extend(find_all_paths_aux(adjlist, node, end, path, maxlen))
        return paths
    adjlist = [set(graph.neighbors(node, mode = mode)) \
        for node in xrange(graph.vcount())]
    all_paths = []
    start = start if type(start) is list else [start]
    end = end if type(end) is list else [end]
    for s in start:
        for e in end:
            all_paths.extend(find_all_paths_aux(adjlist, s, e, [], maxlen))
    return all_paths

#Change path representation from node list to link ids list
def translate_paths(g, paths):
    new_paths = []
    for p in paths:
        trans_path = []
        for i in range(len(p)-1):
            source_list = [p[i]]
            end_list = [p[i+1]]
            link_id = g.es.select(_between = (source_list,end_list))
            trans_path.append(link_id.indices[0])

        new_paths.append(trans_path)
    return new_paths

def main():
    # Size of grid
    graph_size = 5  # grid size, leads to a grid of graph_size*graph_size nodes
    num_nodes = graph_size*graph_size   # Number of nodes in the graph
    num_ods = num_nodes/2    # Number of od, have to be less that 1/2 number of nodes
    scaling = 1000  # number used to scale the resulting grid graph
    max_length = 6  # Maximum number of nodes in paths returned
    paths_per_od = 5    # Number of paths saved per OD

    g = Graph.Lattice([graph_size, graph_size], circular=False, directed = True)


    # Get node ids and positions
    layout = g.layout("kk")     # This fixes the coordinates of the nodes
    layout.scale(scaling)

    coordinates = layout.coords    # Coordinates of the nodes
    g.vs["Coordinates"] = coordinates


    # Print vertices and their coordinates
    f = open('node_info.csv', 'wb')
    writer = csv.writer(f)
    node_info_title = ["Node id", "x coord", "y coord"]
    writer.writerow(node_info_title)
    for v in g.vs:
        row = [v.index,v["Coordinates"][0],v["Coordinates"][1]]
        writer.writerow(row)

    # Get edge list
    f = open('edge_info.csv', 'wb')
    writer = csv.writer(f)
    edge_info_title = ["Link id", "source node", "end node"]
    writer.writerow(edge_info_title)
    for e in g.es:
        row = [e.index,e.source, e.target]
        writer.writerow(row)

    # Generate od pairs
    pairs = list(itertools.combinations(range(num_nodes), 2))   # Generates the pairs
    random.shuffle(pairs)   # shuffles the od pairs to allow for variability
    ods = pairs[0:num_ods]

    # Generate the paths between the od pairs and save them to csv file
    f = open('paths_info.csv', 'wb')
    writer = csv.writer(f)
    for o in ods:
        #Find all paths between origin and destination that have at most max_length edges
        paths = find_all_paths_len(g,o[0],o[1],maxlen=max_length)

        #If we could not get paths_per_od paths between the od, double the max_length value
        if len(paths) < paths_per_od:
            paths = find_all_paths_len(g,o[0],o[1],maxlen=max_length*2)

        #Sort paths by length so that the shortest are first
        paths.sort(key=len)
        new_paths = translate_paths(g, paths[0:paths_per_od])
        writer.writerows(new_paths)

    # Plot the resulting graph
    g.vs["ID"] = g.vs.indices
    g.vs["label"] = g.vs["ID"]  # We label the nodes by the ID
    plot(g, layout = layout)    # Plotting the graph

if __name__ == "__main__": main()