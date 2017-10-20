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
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[2,0,0,0,2], 3L:[1,0,0,0,1], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[1,0,0,0,1]}

T = 3600  # Time horizon of interest
sim_dt = None  # Duration of one time_step for the traffic model

sampling_dt = 150     # Duration of time_step for the solver, in this case it is equal to sim_dt

model_manager = Link_Model_Manager_class(configfile, conn.gateway, "mn", sim_dt, "bpr", coefficients)

#Estimating bpr coefficients with beats
num_links = 7
avg_travel_time = np.zeros(num_links)

for i in range(num_links):
    #fft = 1000/model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps()
    fft= (model_manager.beats_api.get_link_with_id(long(i)).getFull_length() \
                         / model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps())/3600
    #avg_travel_time[i] = model_manager.beats_api.get_link_with_id(long(i)).getFull_length()\
                      #/model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps()
    coefficients[i][0] = copy(fft)
    coefficients[i][4] = copy(fft*0.15)

#print avg_travel_time

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if model_manager.is_valid():
    num_steps = T/sampling_dt

    scenario_solver = Solver_class(model_manager)
    assignment, flow_sol = scenario_solver.Solver_function(T, sampling_dt, "FW")

    print "\n"
    assignment.print_all()

    path_costs = model_manager.evaluate(assignment, T, initial_state=None)

    print "\n"
    path_costs.print_all()

    # Distance to Nash
    print "\n"
    dist_to_Nash = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt)
    print "Distance to Nash is: ", dist_to_Nash

    plt.figure(1)
    assignment.plot_demand()

    plt.figure(2)
    path_costs.plot_costs()

# kill jvm
conn.close()