from __future__ import division
from igraph import *
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree
import csv
import itertools
import random
from xml.dom import minidom
import StringIO
import random
import inspect
import timeit
import numpy as np
import random


def csv2string(data):
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow(data)
    return si.getvalue().strip('\r\n')


def generate_source_links(graph_size, scaling, num_sources, num_sinks, grid):

    if grid:
        graph = Graph.Lattice([graph_size, graph_size], circular=False, directed=True)

    else:
        num_nodes = graph_size
        e = 2.5    # 1/2*empirical average degree of road networks

        #graph = Graph.Lattice([graph_size, graph_size], nei=1,circular=False, mutual= False, directed = True)
        prob = e/(num_nodes-1)         #p probability to generate random graph based on Erdos-Ranyi method
        num_edges = int(e*num_nodes/2)
        graph = Graph.Erdos_Renyi(num_nodes,m=num_edges,directed=True)

        #in case the graph has disconnected components, connect them to the main component
        v_cluster = graph.components(mode=WEAK)
        cluster_sizes = map(lambda x: x.vcount(),v_cluster.subgraphs())    #get the size of connected component
        main_comp_index = cluster_sizes.index(max(cluster_sizes))           # index of largest connected component

        graph = v_cluster.subgraph(main_comp_index)     #Ignore the smaller components and just go with the largest component


        act_avg_degree = graph.ecount()*2/graph.vcount()    #The actual average degree of the created graph
        print "Average degree of created graph is: ", act_avg_degree

    # Generate od pairs
    # For Beats purposes, the origins to be of outdegree 1 and the sinks have to be of outdegree 1
    # For this reason, we choose vertices at the periphery of the grid graph, vertices with indegree < 4
    graph.vs["indegree"] = graph.indegree()
    graph.vs["outdegree"] = graph.outdegree()

    #In order to ensure connectivity, source nodes have to be from indices that have at least one outgoing link
    source_indices = graph.vs.select(_outdegree_gt=0).indices
    #For the sink nodes, we have to make sure that all nodes without outgoing link have a sink
    sink_nodes = graph.vs.select(_outdegree_le=0).indices
    #sink_indices = graph.vs.select(_outdegree_le=1).indices

    if len(sink_nodes) < num_sinks:
    #     sink_nodes = sink_indices + random.sample(sink_indices,num_sinks-len(sink_nodes))
    # else:
        more_indices = num_sinks-len(sink_nodes)
        more_sinks = random.sample(range(graph.vcount()), more_indices)
        sink_nodes = sink_nodes + more_sinks

    source_nodes = random.sample(source_indices, num_sources)

    source_links = np.zeros(num_sources, dtype=int)

    #Adding source node and outgoing link to od
    j = len(graph.vs)   # Starting index of new nodes
    k = 0

    for a in range(num_sources):
        # add a new node and edge to graph for origin
        graph.add_vertices(1)
        graph.add_edge(j, source_nodes[a])
        source_links[k] = graph.get_eid(j, source_nodes[a], directed=True, error=True)
        j += 1
        k += 1

    for a in range(num_sinks):
        graph.add_vertices(1)
        graph.add_edge(sink_nodes[a],j)
        j += 1


    print "Finished Adding All ods, now getting node coordinates with layout"

    # Get node ids and positions
    layout = graph.layout("kk")     # This fixes the coordinates of the nodes
    layout.scale(scaling)

    coordinates = layout.coords    # Coordinates of the nodes
    graph.vs["Coordinates"] = coordinates
    graph.vs["indices"] = graph.vs.indices
    graph.vs["label"] = graph.vs["indices"]
    print "Number of edges: ", graph.ecount() #printing the number of edges
    print "Number of nodes: ", graph.vcount() #printing the number of vertices
    print "Number of sources: ", num_sources
    print "Numver of sinks: ", num_sinks

    # plot(graph, layout=layout)

    return graph, source_links

# write the scenario to csv files
def write_to_csv(graph, all_paths):

    # Print vertices and their coordinates
    f = open('node_info.csv', 'wb')
    writer = csv.writer(f)
    node_info_title = ["Node id", "x coord", "y coord"]
    writer.writerow(node_info_title)
    for v in graph.vs:
        row = [v.index,v["Coordinates"][0],v["Coordinates"][1]]
        writer.writerow(row)

    # Get edge list
    f = open('edge_info.csv', 'wb')
    writer = csv.writer(f)
    edge_info_title = ["Link id", "source node", "end node"]
    writer.writerow(edge_info_title)
    for e in graph.es:
        row = [e.index,e.source, e.target]
        writer.writerow(row)

    # Write paths
    f = open('paths_info.csv', 'wb')
    writer = csv.writer(f)
    for o, path in all_paths.iteritems():
        writer.writerows(path)

# create scenario xml
def create_xml(graph,source_links):

    xscenario = Element('scenario')

    # commodities ---------------------
    xcommodities = Element('commodities')
    xscenario.append(xcommodities)
    xcommodity = Element('commodity')
    xcommodities.append(xcommodity)
    xcommodity.set('id','1')
    xcommodity.set('name','global')
    xcommodity.set('pathfull','false')

    # network ---------------------
    xnetwork = Element('network')
    xscenario.append(xnetwork)

    # nodes ........................
    xnodes = Element('nodes')
    xnetwork.append(xnodes)
    for v in graph.vs:
        xnode = Element('node')
        xnodes.append(xnode)
        xnode.set('id', str(v.index))
        xnode.set('x', str(v["Coordinates"][0]))
        xnode.set('y', str(v["Coordinates"][1]))

    # links .........................
    xlinks = Element('links')
    xnetwork.append(xlinks)
    link_ids = []
    for e in graph.es:
        xlink = Element('link')
        link_ids.append(e.index)
        xlinks.append(xlink)
        xlink.set('id', str(e.index))
        xlink.set('length', str(100))   # length in meters --- FIX THIS
        xlink.set('full_lanes', str(1)) # number of lanes --- FIX THIS
        xlink.set('start_node_id', str(e.source))
        xlink.set('end_node_id', str(e.target))
        xlink.set('roadparam', "0" )

    # road params .......................
    xroadparams = Element('roadparams')
    xnetwork.append(xroadparams)
    xroadparam = Element('roadparam')
    xroadparams.append(xroadparam)
    xroadparam.set('id', "0")
    xroadparam.set('name', "Standard link")
    xroadparam.set('capacity', "2000" )     # veh/hr/lane
    xroadparam.set('speed', "60" )          # km/hr
    xroadparam.set('jam_density', "100" )   # veh/km/lane

    # # road connections .......................

    # add only the road connections needed for the paths
    # create a map from node id to road connections in that node
    road_connection_map = {}
    # road connections to xml
    xroadconnections = Element('roadconnections')
    xnetwork.append(xroadconnections)
    c = -1
    for node in graph.vs.indices:
        in_links = graph.incident(node, mode=IN)
        out_links = graph.incident(node, mode=OUT)

        # if len(out_links) < 1:
        #     print "We stop here"

        for in_l in in_links:
            for out_l in out_links:
                c += 1
                xrc = Element('roadconnection')
                xroadconnections.append(xrc)
                xrc.set('id',str(c))
                xrc.set('in_link',str(in_l))
                xrc.set('out_link',str(out_l))
                xrc.set('in_link_lanes',"1#1")
                xrc.set('out_link_lanes',"1#1")

    # # MN model --------------------
    # xmodel = Element('model')
    # xscenario.append(xmodel)
    # xmn = Element('mn')
    # xmodel.append(xmn)
    # xmn.set('max_cell_length', '100')  # m
    # xmn.text = csv2string(link_ids)

    # demands ---------------------
    xdemands = Element('demands')
    xscenario.append(xdemands)
    for source in source_links:
        xdemand = Element('demand')
        xdemands.append(xdemand)
        xdemand.set('link_id',str(source))
        xdemand.set('commodity_id',"1")
        xdemand.set('start_time',"0")
        xdemand.set('dt',"600")
        xdemand.text = "100"

    # demands ---------------------
    xsplits = Element('splits')
    xscenario.append(xsplits)
    node_list = graph.vs.select(outdegree_gt=1).indices

    #for each node that has an outgoing degree > 1 add split ratio for all incoming links
    for node in node_list:
        in_links = graph.incident(node, mode=IN)
        out_links = graph.incident(node, mode=OUT)
        split_ratio = 1/len(out_links)

        # if len(out_links) < 1:
        #     print "We stop here"

        for in_l in in_links:
            xsplit_node = Element('split_node')
            xsplits.append(xsplit_node)
            xsplit_node.set('node_id', str(node))
            xsplit_node.set('commodity_id', '1')
            xsplit_node.set('link_in', str(in_l))

            for out_l in out_links:
                xsplit = Element('split')
                xsplit_node.append(xsplit)
                xsplit.set('link_out', str(out_l))
                xsplit.text = str(split_ratio)
    return xscenario

def main():

    grid = True

    if not grid:
        # user definitions
        num_nodes = 5  # Number of nodes for graph
        graph_size = num_nodes

    else:
        # user definitions
        graph_size = 2  # grid size, leads to a grid of graph_size*graph_size nodes
        num_nodes = graph_size * graph_size

    scaling = 100  # number used to scale the resulting grid graph
    num_sources = int(num_nodes / 4)  # Number of od, have to be less that 1/2 number of nodes
    num_sinks = max(1, int(num_sources / 5))

    graph, source_links = generate_source_links(graph_size, scaling, num_sources, num_sinks, grid)

    print "Now writing to xml file"

    xscenario = create_xml(graph,source_links)

    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    name = str(num_nodes) + '_nodes.xml'
    print "Saving to xml: ", name

    if grid:
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles/Grid_Graphs', name)
    else:
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles/Split_Ratio', name)

    with open(configfile, 'w') as f:
        f.write(minidom.parseString(etree.tostring(xscenario)).toprettyxml(indent="\t"))

if __name__ == "__main__": main()