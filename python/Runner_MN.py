import os
import inspect
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from Solvers.Solver_Class import Solver_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import time
from copy import copy
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 17})

conn = Java_Connection()

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links_mn.xml')
coefficients = {}
T = 3600  # Time horizon of interest
sim_dt = 2.0  # Duration of one time_step for the traffic model

sampling_dt = 300     # Duration of time_step for the solver, in this case it is equal to sim_dt

model_manager = Link_Model_Manager_class(configfile, conn.gateway, "mn", sim_dt, "bpr", coefficients)

#Estimating bpr coefficients with beats
num_links = model_manager.beats_api.get_num_links()
avg_travel_time = np.zeros(num_links)
num_coeff = 5

for i in range(num_links):
    fft= (model_manager.beats_api.get_link_with_id(long(i)).getFull_length() \
                         / model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps())/3600
    coefficients[long(i)] = np.zeros(num_coeff)
    coefficients[i][0] = copy(fft)
    coefficients[i][4] = copy(fft*0.15)

#print coefficients

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if model_manager.is_valid():
    num_steps = T/sampling_dt

    scenario_solver = Solver_class(model_manager)
    assignment, flow_sol = scenario_solver.Solver_function(T, sampling_dt, "FW")

    print "\n"
    assignment.print_all()

    path_costs = model_manager.evaluate(assignment, T, initial_state=None)

    print "\n"
    path_costs.print_all_in_seconds()

    # Distance to Nash
    print "\n"
    error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt)
    print "%.02f" % error_percentage, "% vehicles from equilibrium"

    plt.figure(1)
    assignment.plot_demand()

    plt.figure(2)
    path_costs.plot_costs_in_seconds()

# kill jvm
conn.close()