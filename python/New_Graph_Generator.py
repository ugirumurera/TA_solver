import numpy as np
import igraph
from Graph_Generator import find_all_paths_len

def construct_igraph(graph):
    # 'vertices' contains the range of the vertices' indices in the graph
    vertices = range(int(np.min(graph[:,1:3])), int(np.max(graph[:,1:3]))+1)
    # 'edges' is a list of the edges (to_id, from_id) in the graph
    edges = graph[:,1:3].astype(int).tolist()
    g = igraph.Graph(vertex_attrs={"label":vertices}, edges=edges, directed=True)
    g.es["weight"] = graph[:,3].tolist() # feel with free-flow travel times
    return g

name = 'LA'
graphLocation = name + '_net.csv'
graph_data= np.loadtxt(graphLocation, delimiter=',', skiprows=1)
graph = construct_igraph(graph_data)

demandLocation = name + '_od.csv'
demand = np.loadtxt(demandLocation, delimiter=',', skiprows=1)

origin = int(demand[0,0])
dest = int(demand[0,1])
max_length = 50

paths = find_all_paths_len(graph,origin,dest,maxlen=max_length)

print "od ", origin, " destination ", dest