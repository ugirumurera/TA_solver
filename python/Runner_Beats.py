import os
import inspect
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection
from Solvers.Solver_Class import Solver_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import time
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 17})

conn = Java_Connection()

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
model_manager = BeATS_Model_Manager_class(configfile, conn.gateway)

T = 3600  # Time horizon of interest
sampling_dt = 600  # Duration of one time_step for the solver

if(model_manager.is_valid()):
    num_steps = T/sampling_dt

    scenario_solver = Solver_class(model_manager)
    assignment, flow_sol = scenario_solver.Solver_function(T, sampling_dt, "EPM")

    print "\n"
    assignment.print_all()

    path_costs = model_manager.evaluate(assignment, T, initial_state=None)

    print "\n"
    path_costs.print_all()

    #Distance to Nash
    print "\n"
    dist_to_Nash = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt)
    print "Distance to Nash is: ", dist_to_Nash

    plt.figure(1)
    assignment.plot_demand()

    plt.figure(2)
    path_costs.plot_costs()

# kill jvm
conn.close()