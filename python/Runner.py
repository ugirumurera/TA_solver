# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np

from Cost_Functions.BPR_Function import BPR_Function_class
from Traffic_Models.Static_Model import Static_Model_Class
from Solvers.Solver_Class import Solver_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Link_Costs_Class import Link_Costs_class
from py4j.java_gateway import JavaGateway,GatewayParameters
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class


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

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.join(this_folder,os.path.pardir,'configfiles','three_links.xml')

coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[1,0,0,0,1]}

port_number = int(port_number)
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port_number))
beats_api = gateway.entry_point.get_BeATS_API()
beats_api.load(configfile)

# This initializes an instance of static model from configfile
scenario  = Static_Model_Class(beats_api)

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    # Initialize the BPR cost function
    BPR_cost_function = BPR_Function_class(coefficients)

    # Initializing the Link_Model_Manager
    link_model_manager = Link_Model_Manager_class(scenario, BPR_cost_function)

    # This is to initialize the demand
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
    demand_value[0] = 1
    demand_value1[0] = 1
    demands[(1L,1L)] = demand_value
    demands[(2L,1L)] = demand_value1
    demand_assignments.set_all_demands(demands)

    # Calling the evaluate function from the Link_Model class to determine the costs per path
    path_costs = link_model_manager.evaluate(demand_assignments, None, time_period, time_period,)
    path_costs.print_all()