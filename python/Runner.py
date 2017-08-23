# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np
from copy import deepcopy

# from Cost_Functions.BPR_Function import BPR_Function_class
# from Traffic_Models.Static_Model import Static_Model_Class
from Solvers.Solver_Class import Solver_class
# from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
# from Data_Types.Link_Costs_Class import Link_Costs_class
# from py4j.java_gateway import JavaGateway,GatewayParameters
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection

# ==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
import os
import inspect

connection = Java_Connection()

# Contains local path to input configfile, for the three_links.xml network
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[5,0,0,0,5], 3L:[2,0,0,0,2], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[5,0,0,0,5]}
model_manager = Link_Model_Manager_class(configfile, connection, "static", None, "bpr", coefficients)

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if model_manager.is_valid():

    num_steps = 1

    scenario_solver = Solver_class(model_manager)
    assignment, flow_sol = scenario_solver.Solver_function(num_steps)

    # Cost resulting from the path_based Frank-Wolfe
    link_states = model_manager.traffic_model.Run_Model(assignment)
    cost_path_based = model_manager.cost_function.evaluate_BPR_Potential(link_states)

    # Cost resulting from link-based Frank-Wolfe
    cost_link_based = model_manager.cost_function.evaluate_BPR_Potential_FW(flow_sol)

    print "\n"
    link_states.print_all()
    print "\n", flow_sol
    print "path-based cost: ", cost_path_based
    print "link-based cost: ", cost_link_based


# kill jvm
connection.close()