import numpy as np

def all_or_nothing(graph, od):
    '''
    We are given an igraph object 'g' with od in the format {from: ([to], [rate])}
    do all_or_nothing assignment
    '''
    L = np.zeros(len(graph.es), dtype="float64")

    for o in od.keys():

        out = graph.get_shortest_paths(o, to=od[o][0], weights="weight", output="epath")

        for i, inds in enumerate(out):
            L[inds] = L[inds] + od[o][1][i]

    return L

def all_or_nothing_beats(graph, od):
    '''
    We are given an igraph object 'g' with od in the format {from: ([to], [rate])}
    do all_or_nothing assignment
    '''
    L = np.zeros(len(graph.es), dtype="float64")

    for o in od:

        out = graph.get_shortest_paths(o.get_origin_node_id(), to=o.get_destination_node_id(), weights="weight", output="epath")

        for i, inds in enumerate(out):
            L[inds] = L[inds] + (o.get_total_demand_vps().get_value(0))*3600

    return L