# This script initializes a static traffic model, a cost function, and a solver to solve a
# Static Traffic Assignment Problem using the Frank-Wolfe algorithm

import numpy as np

from python.Solvers.Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from python.Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
#from Solvers.Decomposition_Solver import Decomposition_Solver
from python.Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from python.Java_Connection import Java_Connection
from python.Data_Types.Demand_Assignment_Class import Demand_Assignment_class

#==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
from subprocess import call
import os
import sys
import signal
import time
import inspect

# make Java connection
connection = Java_Connection()

# create a static/bpr model manager
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
bpr_coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [5, 0, 0, 0, 5], 3L: [2, 0, 0, 0, 2],
                    4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [5, 0, 0, 0, 5]}
model_manager = Link_Model_Manager_class(configfile, connection, "static", None, "bpr", bpr_coefficients)

# create a demand assignment
api = model_manager.beats_api

time_period = 1  # Only have one time period for static model
paths_list = list(api.get_path_ids())
commodity_list = list(api.get_commodity_ids())
route_list = {}

for path_id in paths_list:
    route_list[path_id] = api.get_subnetwork_with_id(path_id).get_link_ids()

# Creating the demand assignment for initialization
demand_assignments = Demand_Assignment_class(route_list, commodity_list, time_period, dt=time_period)
demands = {}
demand_value = np.zeros(time_period)
demand_value1 = np.zeros(time_period)
demand_value[0] = 2
demand_value1[0] = 2
demands[(1L, 1L)] = demand_value
demands[(2L, 1L)] = demand_value1
demands[(3L, 1L)] = demand_value
demand_assignments.set_all_demands(demands)

num_steps = 1
frank_sol = Frank_Wolfe_Solver(model_manager)
assignment_seq = Path_Based_Frank_Wolfe_Solver(model_manager, num_steps)
# Cost resulting from the path_based Frank-Wolfe
link_states = model_manager.traffic_model.Run_Model(assignment_seq)
cost_path_based = model_manager.cost_function.evaluate_BPR_Potential(link_states)

# Cost resulting from link-based Frank-Wolfe
cost_link_based = model_manager.cost_function.evaluate_BPR_Potential_FW(frank_sol)

print "Path-based Frank_Wolfe ", cost_path_based
print "Link_based Frank_Wolfe ", cost_link_based

