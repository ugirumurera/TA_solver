#This is just a place holder for extra code that could be useful in the future
import igraph
import numpy as np
from Static_Model import Static_Model_Class
from Cost_functions import BPR_cost, BPR_potential


configfile =  'C:\\Users\\Juliette Ugirumurera\\Documents\\Post-Doc\\beats-tools\\python\\VI Solver\\SimpleTest.xml'



static_scenario = Static_Model_Class(configfile)

if(static_scenario.beats_api != None):
    #Putting the demand on the links
    link_flow = static_scenario.Run_Model()
    #Temporary coefficient to test static model
    f = np.array(link_flow.values())
    coefficients = dict([[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]])
    print(link_flow)
    link_costs = BPR_cost(f, coefficients)
    print(link_costs)
    links_potential = BPR_potential(coefficients,f)
    print(links_potential)

#Running Shortest path

vertices = static_scenario.beats_api.get_node_ids()
# 'edges' is a list of the edges (to_id, from_id) in the graph
edges_list = static_scenario.beats_api.get_link_connectivity()



g = igraph.Graph(vertex_attrs={"label":vertices}, edges=edges, directed=True)
g.es["weight"] = coefficients[:,0].tolist() # feel with free-flow travel times
