# This script initializes a static traffic model, a cost function, and a solver to solve a
# Static Traffic Assignment Problem using the Frank-Wolfe algorithm

import numpy as np

from Cost_Functions.BPR_Function import BPR_Function_class
from Traffic_Models.Static_Model import Static_Model_Class
from Solvers.Solver import Solver_class
from Data_Types.Demand_Assignment import Demand_Assignment_class
from Data_Types.Link_Costs import Link_Costs_class

#==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
import os
import signal
import subprocess
import time

jar_file_name = 'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar'
port_number = '25335'
print("Staring up the java gateway to access the Beats object")
process = subprocess.Popen(['java', '-jar', jar_file_name, port_number])

time.sleep(0.5)

#End of Linux specific code
#======================================================================================

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.abspath('../configfiles/three_links.xml')

coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[2,0,0,0,2]}

#This initializes an instance of static model from configfile
scenario  = Static_Model_Class(configfile)

#If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    print("\nSuccessfully initialized a static model")

    time_period = 1  # Only have one time period for static model
    num_paths = scenario.beats_api.get_num_subnetworks()
    num_commodities = scenario.beats_api.get_num_commodities()
    demands = np.zeros((num_paths, num_commodities, time_period))
    demands.fill(10)
    demand_assignments = Demand_Assignment_class(num_paths,num_commodities,time_period)
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
    flows = link_states.get_state_values_as_list()
    # Initialize the BPR cost function
    BPR_cost_function = BPR_Function_class(coefficients)
    link_costs = Link_Costs_class(num_links, num_commodities, time_period)
    #Setting the link costs using the results returned by evaluating the BPR function given flows

    print("\nThe costs per link are as follows (Link_Costs class):")
    l_costs = BPR_cost_function.evaluate_Cost_Function(flows)
    link_costs.set_all_costs_on_comm_time_step(0,0, l_costs)
    link_costs.print_all()

    print("\nRunning Frank-Wolfe on the three links network")
    scenario_solver = Solver_class(scenario, BPR_cost_function)
    print(scenario_solver.Solver_function())

    print("\nInstallation Successful!!")

#======================================================
# Want to stop the java server
print("\nStopping the java server")
os.kill(process.pid,  signal.CTRL_C_EVENT)
#=====================================================

