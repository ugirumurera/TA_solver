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

def csv2string(data):
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow(data)
    return si.getvalue().strip('\r\n')

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
            for e in link_id:
                if e.source == p[i] and e.target == p[i+1]:
                    trans_path.append(e.index)

        new_paths.append(trans_path)
    return new_paths

def generate_graph_and_paths(graph_size, scaling, num_nodes, num_ods, max_length, paths_per_od):

    graph = Graph.Lattice([graph_size, graph_size], circular=False, directed = True)

    # Generate od pairs

    graph.vs["indegree"] = graph.indegree()

    permutations = np.asarray(list(itertools.permutations(range(graph.vcount()), 2)))
    od_indices = random.sample(range(1, len(permutations)), num_ods)
    odpairs = permutations[od_indices]

    origins = np.zeros(num_ods)         # Array for origins
    destinations = np.zeros(num_ods)    # Array for destinations
    
    #pairs = list(itertools.combinations(od_indices, 2)
    # For Beats purposes, the origins to be of outdegree 1 and the sinks have to be of outdegree 1
    # For this reason, we need to add source node and outgoing link to od
    j = len(graph.vs)   # Starting index of new nodes
    i = 0

    origin_dic = {}          # Keeps track of which od nodes has been seen already and the source added added
    dest_dic = {}           # Keep track of which destination node has been seen and the sink node added

    for o in odpairs:
        # add a new node and edge to graph for origin if we have not seen this node as origin yet
        if o[0] not in origin_dic.keys():
            graph.add_vertices(1)
            graph.add_edge(j, o[0])
            origins[i] = j
            origin_dic[o[0]] = j
            j += 1
        else:
            origins[i] = origin_dic[o[0]]

        # add a new node and edge to the graph for destination if this node has not been seen as destinaiton yet
        if o[1] not in dest_dic.keys():
            graph.add_vertices(1)
            graph.add_edge(o[1], j)
            destinations[i] = j
            dest_dic[o[1]] = j
            j += 1
        else:
            destinations[i] = dest_dic[o[1]]

        i += 1
        print "od is ", o

    print "Finished Adding All ods, now getting node coordinates with layout"

    #Creating the actual ods
    ods = zip(origins,destinations)

    # Get node ids and positions
    layout = graph.layout("kk")     # This fixes the coordinates of the nodes
    layout.scale(scaling)

    coordinates = layout.coords    # Coordinates of the nodes
    graph.vs["Coordinates"] = coordinates
    graph.vs["indices"] = graph.vs.indices
    #graph.vs["label"] = graph.vs["indices"]
    print(graph.ecount()) #printing the number of edges
    #plot(graph, layout=layout)

    print "Moving to getting paths for all ods"
    # Generate the paths between the od pairs
    all_paths = {}
    for o in ods:
        #Find all paths between origin and destination that have at most max_length edges
        #start_time1 = timeit.default_timer()
        # Each iteration the weight of the shortest path is multiplied by power to allow to
        # find a new shortest path
        # Add edge weights to graph, we start will all edges with weight 1
        graph.es["weight"] = np.ones(graph.ecount())
        factor = 10
        paths = []
        for i in range(paths_per_od):
            path = graph.get_shortest_paths(int(o[0]), int(o[1]), weights="weight", mode=OUT, output="epath")
            paths.append(path[0])

            #change weight of edges in path in order to find new shortest path
            size_of_path = len(path[0])
            new_weights = np.multiply(factor**(i+1),np.ones(size_of_path))
            graph.es[path[0]]["weight"] = new_weights
        #elapsed1 = timeit.default_timer() - start_time1

        #If we could not get paths_per_od paths between the od, double the max_length value
        #if len(paths) < paths_per_od:
            #paths = find_all_paths_len(graph,o[0],o[1],maxlen=max_length*2)

        #Sort paths by length so that the shortest are first
        #paths.sort(key=len)
        print "Finding paths for od ", o[0], " and dest ", o[1]
        #new_paths = translate_paths(graph, paths[0:paths_per_od])

        all_paths[o] = paths

    return graph, all_paths

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

# write the scenario to an xml file
def write_to_xml(graph,all_paths):

    xscenario = Element('scenario')

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

    # road connections .......................

    # add only the road connections needed for the paths
    # create a map from node id to road connections in that node
    road_connection_map = {}
    for od, paths in all_paths.iteritems():
        for path in paths:
            for i in range(len(path)-1):
                up_link = graph.es[path[i]]
                dn_link = graph.es[path[i+1]]

                if up_link.target != dn_link.source:
                    print 'ERROR!!!!!', up_link.target, dn_link.source

                node_id = up_link.target
                if node_id in road_connection_map:

                    # ignore if it is already present
                    if 0==len([item for item in road_connection_map[node_id] if (item[0] == path[i] and item[1] == path[i+1])]):
                        road_connection_map[node_id].append((path[i], path[i+1]))
                else:
                    road_connection_map[node_id] = [(path[i], path[i+1])]

    # road connections to xml
    xroadconnections = Element('roadconnections')
    xnetwork.append(xroadconnections)
    c = -1
    for node_id, tuple_list in road_connection_map.iteritems():
        for in_out_link in tuple_list:
            c += 1
            xrc = Element('roadconnection')
            xroadconnections.append(xrc)
            xrc.set('id',str(c))
            xrc.set('in_link',str(in_out_link[0]))
            xrc.set('out_link',str(in_out_link[1]))
            xrc.set('in_link_lanes',"1#1")
            xrc.set('out_link_lanes',"1#1")

    # MN model --------------------
    xmodel = Element('model')
    xscenario.append(xmodel)
    xmn = Element('mn')
    xmodel.append(xmn)
    xmn.set('max_cell_length', '100')  # m
    xmn.text = csv2string(link_ids)

    # paths ---------------------
    xsubnetworks = Element('subnetworks')
    xscenario.append(xsubnetworks)
    c = -1
    path_ids = []
    for od, paths in all_paths.iteritems():
        for path in paths:
            c += 1
            path_ids.append(c)
            xsubnetwork = Element('subnetwork')
            xsubnetworks.append(xsubnetwork)
            xsubnetwork.set('id',str(path_ids[c]))
            xsubnetwork.text = csv2string(path)

    # demands ---------------------
    xdemands = Element('demands')
    xscenario.append(xdemands)
    for path_id in path_ids:
        xdemand = Element('demand')
        xdemands.append(xdemand)
        xdemand.set('commodity_id',"0")
        xdemand.set('subnetwork',str(path_id))
        xdemand.set('start_time',"0")
        xdemand.set('dt',"600")
        xdemand.text = "100,500,100,500,100,500"

    # commodities ---------------------
    xcommodities = Element('commodities')
    xscenario.append(xcommodities)
    xcommodity = Element('commodity')
    xcommodities.append(xcommodity)
    xcommodity.set('id','0')
    xcommodity.set('pathfull','true')
    xcommodity.set('name','car')
    xcommodity.set('subnetworks',csv2string(path_ids))

    # write to file ---------------------
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'scenario_varying_2500_nodes_5000_ods.xml')
    with open(configfile, 'w') as f:
        f.write(minidom.parseString(etree.tostring(xscenario)).toprettyxml(indent="\t"))

def main():

    # user definitions
    graph_size = 50  # grid size, leads to a grid of graph_size*graph_size nodes
    scaling = 1000 # number used to scale the resulting grid graph
    max_length =25  # Maximum number of nodes in paths returned
    paths_per_od = 5    # Number of paths saved per OD

    num_nodes = graph_size*graph_size   # Number of nodes in the graph
    num_ods = num_nodes*2   # Number of od, have to be less that 1/2 number of nodes

    graph, all_paths = generate_graph_and_paths(graph_size, scaling, num_nodes, num_ods, max_length, paths_per_od)

    print "Now writing to xml file"
    # write_to_csv(graph,all_paths)

    write_to_xml(graph,all_paths)

    # Plot the resulting graph
    # graph.vs["ID"] = graph.vs.indices
    # graph.vs["label"] = graph.vs["ID"]      # We label the nodes by the ID
    # plot(graph, layout = layout)            # Plotting the graph

if __name__ == "__main__": main()