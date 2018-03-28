# This script initializes a static traffic model, a cost function, and a solver to solve a
# Static Traffic Assignment Problem using the Frank-Wolfe algorithm

import numpy as np

from python.Cost_Functions.BPR_Function import BPR_Function_class
from python.Solvers.Solver_Class import Solver_class
from python.Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from python.Data_Types.Link_Costs_Class import Link_Costs_class
from python.Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from python.Java_Connection import Java_Connection
import os
import inspect

'''
# ==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
import os
import signal
import subprocess
import time
import sys
import inspect

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

jar_file_name = os.path.join(this_folder,'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar')
port_number = '25335'
print("Staring up the java gateway to access the Beats object")
try:
    process = subprocess.Popen(['java', '-jar', jar_file_name, port_number],
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(0.5)
except subprocess.CalledProcessError:
    print("caught exception")
    sys.exit()


# End of Windows specific code
# ======================================================================================
'''
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
connection = Java_Connection()

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.join(this_folder,os.path.pardir,'configfiles','seven_links.xml')

coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[5,0,0,0,5], 3L:[2,0,0,0,2], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[5,0,0,0,5]}

model_manager = Link_Model_Manager_class(configfile, "static", connection, None, "bpr", coefficients)

'''
port_number = int(port_number)
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port_number))
beats_api = gateway.entry_point.get_BeATS_API()
beats_api.load(configfile)

# This initializes an instance of static model from configfile
scenario  = Static_Model_Class(beats_api, 1, 1)
'''

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    print("\nSuccessfully initialized a static model")

    od = scenario.beats_api.get_od_info()

    total_demand = np.sum(o.get_total_demand_vps().get_value(0)*3600 for o in od)

    subnetwork_list = list(scenario.beats_api.get_subnetworks())

    time_period = 1  # Only have one time period for static model
    paths_list = list(scenario.beats_api.get_path_ids())
    link_list = list(scenario.beats_api.get_link_ids())
    commodity_list = list(scenario.beats_api.get_commodity_ids())

    # rout_list is a dictionary of [path_id]:[link_1, ...]
    route_list = {}

    for path_id in paths_list:
        route_list[path_id] = scenario.beats_api.get_subnetwork_with_id(path_id).get_link_ids()

    # Creating the demand assignment for initialization
    demand_assignments = Demand_Assignment_class(route_list,commodity_list,time_period, dt = time_period)
    demands = {}
    demand_value = np.zeros((time_period))
    demand_value1 = np.zeros((time_period))
    demand_value[0] = 2
    demand_value1[0] = 2
    demands[(1L,1L)] = demand_value
    demands[(2L,1L)] = demand_value1
    demand_assignments.set_all_demands(demands)
    print("\nDemand Assignment on path is as follows (Demand_Assignment class):")
    demand_assignments.print_all()



    # Test the Run_Model function
    print ("\nDemand Distributed from paths onto links as flows (State_Trajectory class)")
    link_states = scenario.Run_Model(demand_assignments)
    link_states.print_all()

    # Testing the Link Cost class
    print("\nCalculating the cost per link (Link Cost class)")
    print("We initialize the BPR function with the following coefficients: ")
    print(coefficients)
    num_links = scenario.beats_api.get_num_links()
    # In order to use the BPR function, we first need to get the flows the state trajectory object as a list

    flows = list()
    for state in link_states.get_all_states().values():
        flows.append(state[0].get_flow())

    # Initialize the BPR cost function
    BPR_cost_function = BPR_Function_class(coefficients)
    link_costs = Link_Costs_class(link_list, commodity_list, time_period)

    # Setting the link costs using the results returned by evaluating the BPR function given flows
    print("\nThe costs per link are as follows (Link_Costs class):")
    #l_costs = BPR_cost_function.evaluate_Cost_Function_FW(flows)
    #l_cost_dict = {}
    #l_cost_dict[(0L, 1L)] = [l_costs[0]]
    #l_cost_dict[(1L, 1L)] = [l_costs[1]]
    #l_cost_dict[(2L, 1L)] = [l_costs[2]]

    #link_costs.set_all_costs(l_cost_dict)
    #link_costs.print_all()


    print("\nRunning Frank-Wolfe on the three links network")
    scenario_solver = Solver_class(scenario, BPR_cost_function)
    print(scenario_solver.Solver_function())

    print("\nInstallation Successful!!")

# ======================================================
# Want to stop the java server
print("\nStopping the java server")
os.kill(process.pid,  signal.CTRL_C_EVENT)
# =====================================================


