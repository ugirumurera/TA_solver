# This script initializes a static traffic model, a cost function, and a solver to solve a
# Static Traffic Assignment Problem using the Frank-Wolfe algorithm

import numpy as np

from python.Cost_Functions.BPR_Function import BPR_Function_class
from python.Traffic_Models.Static_Model import Static_Model_Class
from python.Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from python.Data_Types.Link_Costs_Class import Link_Costs_class
from python.Traffic_States.Static_Traffic_State import Static_Traffic_State_class

def get_path_list(paths):
    path_ids_list = list()
    for path in paths:
        path_ids_list.append(path.getId())

    return path_ids_list

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
    process = subprocess.Popen(['java', '-jar', jar_file_name, port_number],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # stdout_data, stderr_data = process.communicate()
    time.sleep(0.5)
except subprocess.CalledProcessError:
    print("caught exception")
    sys.exit()


# End of Linux specific code
# ======================================================================================

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.join(this_folder,os.path.pardir,'configfiles','three_links.xml')

coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[2,0,0,0,2]}

# This initializes an instance of static model from configfile
scenario  = Static_Model_Class(configfile)

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    print("\nSuccessfully initialized a static model")

    time_period = 1  # Only have one time period for static model
    paths_list = scenario.beats_api.get_path_ids()
    commodity_list = scenario.beats_api.get_commodity_ids()

    # rout_list is a dictionary of [path_id]:[link_1, ...]
    route_list = {}
    route_list[1L] = [0L, 1L]
    route_list[2L] = [0L, 2L]

# Test used to validate the Demand_Assignment_Class
# Creating the demand assignment for initialization
demand_assignments = Demand_Assignment_class(route_list, commodity_list, time_period)
demands = {}
demand_value = np.zeros((time_period))
demand_value1 = np.zeros((time_period))
demand_value[0] = 20
demand_value1[0] = 20
demands[(1L, 1L)] = demand_value
demands[(2L, 1L)] = demand_value1
demand_assignments.set_all_demands(demands)
demand_assignments.print_all()

demand_assignments.set_demand_at_path_comm_time(2L, 1L, 0, 65)
demand_assignments.add_demand_at_path_comm_time(3L, [0L, 1L, 2L], 1L, 0, 35)

print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_on_path(1L, {1L: demand_value1})
print("\n")
demand_assignments.print_all()

demand_assignments.add_all_demands_on_path(4L, [0L, 1L, 2L], {1L: demand_value1})
print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_on_path_comm(4L, 1L, demand_value)
print("\n")
demand_assignments.print_all()

demand_assignments.add_all_demands_on_path_comm(14L, [0L, 1L, 2L], 1L, demand_value1)
print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_on_path_time_step(4L, 0, {1L: 57})
print("\n")
demand_assignments.print_all()

demand_assignments.add_all_demands_on_path_time_step(45L, [0L, 1L, 2L], 0, {1L: 90})
print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_for_commodity(1L, {43L: demand_value})
print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_on_comm_time_step(1L, 1, {45L: 273})
print("\n")
demand_assignments.print_all()

demand_assignments.set_all_demands_for_time_step(1, {(45L, 1L): 467})
print("\n")
demand_assignments.print_all()

# Test the Run_Model function
print ("\nDemand Distributed from paths onto links as flows (State_Trajectory class)")
link_states = scenario.Run_Model(demand_assignments)
link_states.print_all()

# Testing the State_Trajectory class - Testing the gets functions
link_states.get_state_on_link_comm_time(0L, 1, 0).print_state()

result = link_states.get_all_states_on_link(2)

result = link_states.get_all_states_on_link_comm(0, 1)

result = link_states.get_all_states_on_link_time_step(2, 0)

result = link_states.get_all_states_for_commodity(1)

result = link_states.get_all_states_on_comm_time_step(1, 0)

result = link_states.get_all_states_for_time_step(0)

# Testing the State_Trajectory class - Testing the sets functions

link_states.set_all_states(link_states.get_all_states())

state = Static_Traffic_State_class()
state.set_flow(576)
state_list = list()
state_list.append(state)
comm_list = {1L: state_list}

link_states.set_all_states_on_link(1, comm_list)

link_states.set_all_states_on_link_comm(1, 1, state_list)

comm_list1 = {1L: state}
link_states.set_all_states_on_link_time_step(1, 0, comm_list1)

link_states.set_all_states_for_commodity(1, comm_list)

link_states.set_all_states_on_comm_time_step(1, 0, comm_list1)

comm_list1 = {(2L, 2L): state}
link_states.set_all_demands_for_time_step(0, comm_list1)

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
l_costs = BPR_cost_function.evaluate_Cost_Function(flows)
l_cost_dict = {}
l_cost_dict[(0L, 1L)] = [l_costs[0]]
l_cost_dict[(1L, 1L)] = [l_costs[1]]
l_cost_dict[(2L, 1L)] = [l_costs[2]]

link_costs.set_all_costs(l_cost_dict)
link_costs.print_all()

# Test for Link_Costs_Class
result = link_costs.get_cost_at_link_comm_time(0, 1, 0)
result = link_costs.get_all_costs_on_link(2)
result = link_costs.get_all_costs_on_link_comm(1, 1)
result = link_costs.get_all_costs_on_link_time_step(1, 0)
result = link_costs.get_all_costs_for_commodity(1)
result = link_costs.get_all_costs_on_comm_time_step(1, 0)
result = link_costs.get_all_costs_for_time_step(0)

link_costs.set_all_costs(link_costs.get_all_costs())
comm_cost = {1L: [20]}
link_costs.set_all_costs_on_link(1, comm_cost)
print"\n"
link_costs.print_all()

link_costs.set_all_costs_on_link_comm(1, 1, [-48])
print"\n"
link_costs.print_all()

link_costs.set_all_costs_on_link_time_step(2, 0, {1L: 1085})
print"\n"
link_costs.print_all()

link_costs.set_all_costs_for_commodity(1, comm_cost)
print"\n"
link_costs.print_all()

link_costs.set_all_costs_on_comm_time_step(1, 0, {1L: [4657, 12], 2L: 3649})
print"\n"
link_costs.print_all()

link_costs.set_all_costs_for_time_step(0, {(1L, 1L): 374, (2L, 1L): 4659})
print"\n"
link_costs.print_all()
