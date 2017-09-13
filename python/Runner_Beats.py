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

conn = Java_Connection()

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
sim_dt = 2
model_manager = BeATS_Model_Manager_class(configfile, conn.gateway, sim_dt)

T = 3600  # Time horizon of interest
sampling_dt = 1800  # Duration of one time_step
if(model_manager.is_valid()):
    num_steps = T/sampling_dt

    scenario_solver = Solver_class(model_manager)
    assignment, flow_sol = scenario_solver.Solver_function(num_steps, sampling_dt)

    assignment.print_all()

    path_costs = model_manager.evaluate(assignment, sampling_dt, T)

    print "\n"
    path_costs.print_all()

    plt.figure(1)
    assignment.plot_demand()

    plt.figure(2)
    path_costs.plot_costs()

# kill jvm
conn.close()