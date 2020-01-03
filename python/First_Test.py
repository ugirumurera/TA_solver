# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np
from copy import deepcopy

from Solvers.Solver_Class import Solver_class
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from copy import copy
import matplotlib.pyplot as plt
import os
import inspect
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
import csv

plt.rcParams.update({'font.size': 18})

# Flag that indicates whether we are doing decomposition or not
decompositio_flag = False

connection = Java_Connection()

if connection.pid is not None:

    # Contains local path to input configfile, for the three_links.xml network
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')

    coefficients = {}
    T = 1800  # Time horizon of interest
    sim_dt = 0.0  # Duration of one time_step for the traffic model

    sampling_dt = 300     # Duration of time_step for the solver, in this case it is equal to sim_dt

    model_manager = Link_Model_Manager_class(configfile, "static", connection.gateway, sim_dt, "bpr", coefficients)

    #Estimating bpr coefficients with beats
    num_links = model_manager.otm_api.scenario().get_num_links()
    avg_travel_time = np.zeros(num_links)

    num_coeff = 5

    for i in range(num_links):
        link_info = model_manager.otm_api.scenario().get_link_with_id(long(i))
        fft= (link_info.getFull_length() /1000
              / link_info.get_ffspeed_kph())
        coefficients[long(i)] = np.zeros(num_coeff)
        coefficients[i][0] = copy(fft)
        coefficients[i][4] = copy(fft*0.15)


# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
    if model_manager.is_valid():
        num_steps = T / sampling_dt

        # Get the OD Matrix form Model Manager
        # OD Matrix can also be initialized from another source, as long as it fits the OD_Matrix class format
        OD_Matrix = model_manager.get_OD_Matrix(num_steps, sampling_dt)

        if OD_Matrix is not None:
            # Algorithm to use
            solver_algorithm = Path_Based_Frank_Wolfe_Solver

            scenario_solver = Solver_class(model_manager, solver_algorithm)
            assignment, solver_run_time = scenario_solver.Solver_function(T, sampling_dt, OD_Matrix, decompositio_flag)

            if assignment is None:
                print "Solver did not run"
            else:
                # Save assignment into a pickle file
                # this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                # outputfile = os.path.join(this_folder, os.path.pardir, 'output', scenario_name+'.picle')

                path_costs = model_manager.evaluate(assignment, T, initial_state=None)

                # Distance to Nash
                print "\n"
                error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt, OD_Matrix)
                print "%.02f" % error_percentage, "% vehicles from equilibrium"

            print "\nSUCCESS!!"

    # kill jvm
    # connection.close()