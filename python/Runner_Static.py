# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model
# It then calculates the static user equilibrium

import numpy as np
import pickle
from copy import deepcopy
import sys

from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from copy import copy
import matplotlib.pyplot as plt
from Solvers.Solver_Class import Solver_class
import os
import inspect
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver

plt.rcParams.update({'font.size': 18})

# Function to save the output data
def save_ouput_to_picle(outputfile, assignment, path_costs, run_time, error):
    # Write results to picke file
    # The DTA assignment and corresponding path_cost from file
    with open(outputfile, "wb") as f:
        pickle.dump(assignment, f)
        pickle.dump(path_costs, f)
        pickle.dump(run_time, f)
        pickle.dump(error, f)

# Flag that indicates whether we are doing decomposition or not
decompositio_flag = False

connection = Java_Connection(decompositio_flag)

if connection.pid is not None:

    # Contains local path to input configfile, for the three_links.xml network
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    scenario_name = 'MetroManila_unfiltered'   #Scenario name
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', scenario_name+'.xml')
    coefficients = {}
    T = 3600  # Time horizon of interest
    sim_dt = 0.0  # Duration of one time_step for the traffic model

    sampling_dt = 600     # Duration of time_step for the solver, in this case it is equal to sim_dt

    model_manager = Link_Model_Manager_class(configfile, "static", connection.gateway, sim_dt, "bpr", coefficients)

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


    # If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
    if model_manager.is_valid():
        num_steps = T/sampling_dt

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
                this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                outputfile = os.path.join(this_folder, os.path.pardir, 'output', scenario_name+'.picle')

                path_costs = model_manager.evaluate(assignment, T, initial_state=None)

                # Distance to Nash
                print "\n"
                error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt, OD_Matrix)
                print "%.02f" % error_percentage, "% vehicles from equilibrium"

                #print "\nDemand Assignment:"
                #assignment.print_all()


                if decompositio_flag:
                    from mpi4py import MPI

                    # MPI Directives
                    comm = MPI.COMM_WORLD
                    rank = comm.Get_rank()

                    if rank == 0:
                        print "I am rank ", rank, " going to save output"
                        save_ouput_to_picle(outputfile, assignment, path_costs, solver_algorithm, error_percentage)
                        # kill jvm
                        connection.close()

                else:
                    save_ouput_to_picle(outputfile,assignment,path_costs,solver_algorithm, error_percentage)
                    # kill jvm
                    connection.close()

                '''
                with open(outputfile, "rb") as f:
                    ass = pickle.load(f)
                    costs = pickle.load(f)
                    run_time = pickle.load(f)
                    error = pickle.load(f)
                '''


                # print "\nPath costs in seconds:"
                #path_costs.print_all_in_seconds()