#This script combines the traffic model, cost function, and solver into one program to solve a
#particular Traffic Assignment Problem

# When running on windows machine, first launch the java code Entry_Point_BeATS.java that is under 'beats-tools/java/py4jbeats/src/main/java'
# And comment out the portion marked for linux system

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
print("Staring up the java server")
process = subprocess.Popen(['java', '-jar', jar_file_name, port_number])

time.sleep(0.5)

#End of Windows specific code
#======================================================================================

# Contains local path to input configfile
configfile =  'C:/Users/Juliette Ugirumurera/Documents/Post-Doc/Code/ta_solver/configfiles/three_links.xml'
coefficients = {0L:[2,0,0,0,2],1L:[2,0,0,0,2],2L:[2,0,0,0,2]}
#coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[5,0,0,0,5], 3L:[2,0,0,0,2], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[5,0,0,0,5]}

#This initializes an instance of static model from configfile
scenario  = Static_Model_Class(configfile)

#If scenario.beas_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    print("Successfully initialized a static model")

    time_period = 1  # Only have one time period for static model
    num_paths = scenario.beats_api.get_num_subnetworks()
    num_commodities = scenario.beats_api.get_num_commodities()
    demands = np.zeros((num_paths, num_commodities, time_period))
    demands.fill(200)
    demand_assignments = Demand_Assignment_class(num_paths,num_commodities,time_period)
    demand_assignments.set_all_demands(demands)

    # Test the Run_Model function
    print ("\nTest for Run_Model Function")
    link_states = scenario.Run_Model(demand_assignments)
    link_states.print_all()

    #Testing the Strate Trajectory class using the BPR function
    print("\nTest for State_Trajectory Class")
    #In order to use the BPR function, we first need to get the flows the state trajectory object as a list
    flows = link_states.get_state_values_as_list()
    #Initialize the BPR cost function
    travel_time_function = BPR_Function_class(coefficients)
    print(travel_time_function.evaluate_Cost_Function(flows))

    # Testing the Link Cost class
    print("\nTest for Link_Costs Class")
    num_links = scenario.beats_api.get_num_links()
    cost_values = np.zeros((num_links, num_commodities, time_period))
    cost_values.fill(20)
    link_costs = Link_Costs_class(num_links, num_commodities, time_period)
    link_costs.set_all_costs(cost_values)
    print(link_costs.get_all_costs())


# Want to stop the java server
time.sleep(5)
print("\nstoping java server")
os.kill(process.pid, signal.SIGTERM)
time.sleep(5)

