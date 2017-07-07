#This is just a place holder for extra code that could be useful in the future
import igraph
import numpy as np
from Static_Model import Static_Model_Class
from Cost_functions import BPR_cost, BPR_potential


configfile =  'C:\\Users\\Juliette Ugirumurera\\Documents\\Post-Doc\\beats-tools\\python\\VI Solver\\SimpleTest.xml'
'''
if (len(demands) != self.num_time_steps):
    print("Error: size of demand array does not match demand assignment array size")
    return
'''
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

#===========================================
'''
Below are the tests for the Demand_Assignment class
    # Initializing the demand assignment array class
    time_period = 1  # Only have one time period for static model
    num_paths = scenario.beats_api.get_num_subnetworks()
    num_commodities = scenario.beats_api.get_num_commodities()
    demands = scenario.beats_api.get_demands()
    assignments = Demand_Assignment_class(num_paths, num_commodities, time_period)

    #Testing assignment_of_demands class
    assignments.set_demand_at_path_comm_time(1,0,0,100)
    print(assignments.get_demand_at_path_comm_time(1,0,0))

    demands = np.zeros((num_commodities,time_period))
    demands[0,0] = 200
    assignments.set_all_demands_on_path(0,demands)
    print(assignments.get_all_demands_on_path(0))

    demands = np.zeros((num_paths, time_period))
    demands.fill(300)
    assignments.set_all_demands_for_commodity(0,demands)
    print(assignments.get_all_demands_for_commodity(0))

    demands = np.zeros((num_paths, num_commodities))
    demands.fill(100)
    assignments.set_all_demands_for_time_step(0, demands)
    print(assignments.get_all_demands_for_time_step(0))

    demands = np.zeros((num_paths))
    demands.fill(455)
    assignments.set_all_demands_on_comm_time_step(0,0,demands)
    print(assignments.get_all_demands_for_time_step(0))

    demands = np.zeros((time_period))
    demands.fill(378)
    assignments.set_all_demands_on_path_comm(1,0, demands)
    print(assignments.get_all_demands_on_path_comm(1,0))

    demands = np.zeros((num_commodities))
    demands.fill(283)
    assignments.set_all_demands_on_path_time_step(0,0,demands)
    print(assignments.get_all_demands_on_path_time_step(0,0))
'''

'''
#Overriding the run model function from the base class
def Run_Model_one(self, demands_assignments, initial_state = None, dt = None, T = None):
    #creates a list of link_ids
    link_id_list = self.get_list_link_ids()
    #creates a list of all commodities
    commodity_list = self.get_list_commodities()

    #Create array for flows
    link_flow = np.zeros((len(link_id_list), len(commodity_list)))

    for demand in demands:
        # check if the demand in demand is defined on paths
        if not demand.is_path:
            print('code assumes all demands are defined on paths')
            return
        # loop through links on the path
        path_info = self.beats_api.get_subnetwork_with_id(demand.getPath_id())  # this is a SubnetworkInfo object
        for link_id in path_info.getLink_ids():
            link_flow[link_id][demand.getCommodity_id()-1] = link_flow[link_id][demand.getCommodity_id()-1] + (demand.getProfile().get_value(0)*3600)

    return link_id_list, commodity_list, link_flow
'''