# This script runs the static traffic assignment for a specified timestep in the demand profile
# It takes an integer n as input, that indicates the value to be considered in the demand profile
# for static traffic assignment. This allows to run multiple run of static traffic assignment

import argparse
import numpy as np
import pickle
from copy import deepcopy
import sys
import timeit

from python.Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from python.Java_Connection import Java_Connection
from copy import copy
import matplotlib.pyplot as plt
from python.Solvers.Solver_Class import Solver_class
import os
import inspect
import csv
from python.Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from python.Solvers.Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver, Frank_Wolfe_Solver_with_Pickle_Objects
import math
import sys


# Function to save the output data
def save_ouput_to_picle(outputfile, assignment, path_costs, run_time, error):
    # Write results to picke file
    # The DTA assignment and corresponding path_cost from file
    with open(outputfile, "wb") as f:
        pickle.dump(assignment, f)
        pickle.dump(path_costs, f)
        pickle.dump(run_time, f)
        pickle.dump(error, f)

def main():
    pass
    parser = argparse.ArgumentParser(description='Timestep in Demand profile')
    parser.add_argument("timestep", type=int, help="Time step in the Demand profile")

    # We assume that timestep is between 0 and num_steps
    args = parser.parse_args()

    T = 3600  # Time horizon of interest

    sampling_dt = 600  # Duration of time_step for the solver, in this case it is equal to sim_dt

    num_steps = T / sampling_dt

    if args.timestep < 0 or args.timestep >= num_steps:
        print "Time step specified outside of allowed range"
        sys.exit()

    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


    # Indicates whether we are going to use parallelism or not
    decompositio_flag = False

    scenario_name = 'seven_links'  # Scenario name

    # File where to save the pickled objects
    inputfile = os.path.join(this_folder, os.path.pardir, 'output',
                              scenario_name + '.pickle')

    # Read back the objects to make sure they got save correctly
    start_time1 = timeit.default_timer()
    with open(inputfile, "rb") as f:
        num_links = pickle.load(f)
        cost_function = pickle.load(f)
        OD_Matrix = pickle.load(f)
        graph_object = pickle.load(f)

    elapsed1 = timeit.default_timer() - start_time1
    print ("\nReading from Pickle object took  %s seconds" % elapsed1)

    #Now running Frank-Wolfe
    solver_algorithm = Frank_Wolfe_Solver_with_Pickle_Objects

    start_time1 = timeit.default_timer()

    #this is to be done if decompostion_flag is true
    od_subset = None
    od_temp = OD_Matrix.get_all_ods().values()
    od = np.asarray(sorted(od_temp, key=lambda h: (h.get_origin(), h.get_destination())))
    display = 1
    if decompositio_flag:
        from mpi4py import MPI

        # MPI Directives
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        if rank > 0: display = 0

        n = len(od)

        if n < size and rank >= size:
            print "Number of ods is smaller than number of process. This process will not run solver"
            sys.exit()

        local_n_c = math.ceil(float(n) / size)  # local step but ceiled
        local_n = n / size
        remainder = n % size

        if (rank < remainder):
            local_a = math.ceil(rank * local_n_c)
            local_b = math.ceil(min(local_a + local_n_c, n))
            local_n = local_n_c
        else:
            local_a = math.ceil((remainder) * local_n_c + (rank - remainder) * local_n)
            local_b = math.ceil(min(local_a + local_n, n))

        # The set of ods to use for the particular subproblem
        print "Solving for od's ", local_a, " through ", local_b - 1
        od_subset = od[int(local_a):int(local_b)]
        od = od_subset


    if display > 0: print "Running Static UE for timestep:", args.timestep

    flow = solver_algorithm(graph_object,od,cost_function,num_links, args.timestep, decompositio_flag, display)

    elapsed1 = timeit.default_timer() - start_time1
    if display == 1: print ("\nSolver took  %s seconds" % elapsed1)

    #Save resulting flow and graph object
    # File where to save the pickled objects
    if display == 1:
        outputfile = os.path.join(this_folder, os.path.pardir, 'output',
                              scenario_name + 'output_flow_time_' + str(args.timestep) + '.pickle')

        # We are going to pickle the model manager, te OD_Matrix and the BPR coefficients
        with open(outputfile, "wb") as f:
            pickle.dump(flow,f)

    # connection = Java_Connection(decompositio_flag)
    #
    # if connection.pid is not None:
    #
    #     # Contains local path to input configfile, for the three_links.xml network
    #     this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    #     scenario_name = 'scenario_varying_100_nodes'  # Scenario name
    #     configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', scenario_name + '.xml')
    #     coefficients = {}
    #
    #     model_manager = Link_Model_Manager_class(configfile, "static", connection.gateway, sim_dt, "bpr", coefficients)
    #
    #     # Estimating bpr coefficients with beats
    #     num_links = model_manager.beats_api.get_num_links()
    #     #avg_travel_time = np.zeros(num_links)
    #
    #     num_coeff = 5
    #
    #     for i in range(num_links):
    #         fft = (model_manager.beats_api.get_link_with_id(long(i)).getFull_length() \
    #                / model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps()) / 3600
    #         coefficients[long(i)] = np.zeros(num_coeff)
    #         coefficients[i][0] = copy(fft)
    #         coefficients[i][4] = copy(fft * 0.15)
    #
    #     # If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
    #     if model_manager.is_valid():
    #
    #         # Get the OD Matrix form Model Manager
    #         # OD Matrix can also be initialized from another source, as long as it fits the OD_Matrix class format
    #         OD_Matrix = model_manager.get_OD_Matrix_timestep(num_steps, sampling_dt, args.timestep)
    #
    #         if OD_Matrix is not None:
    #             # Algorithm to use
    #             #solver_algorithm = Path_Based_Frank_Wolfe_Solver
    #             solver_algorithm = Frank_Wolfe_Solver
    #
    #             #scenario_solver = Solver_class(model_manager, solver_algorithm)
    #             #In this case, the time horizon equals to the sampling dt
    #             #assignment, solver_run_time = scenario_solver.Solver_function(sampling_dt, sampling_dt, OD_Matrix,
    #             #                                                             decompositio_flag)
    #
    #             ods = OD_Matrix.get_all_ods().values()
    #
    #             start_time1 = timeit.default_timer()
    #
    #             flow = solver_algorithm(model_manager, ods, args.timestep)
    #
    #             elapsed1 = timeit.default_timer() - start_time1
    #             print ("\nSolver took  %s seconds" % elapsed1)

    #         connection.close()

    '''
    if assignment is None:
        print "Solver did not run"
    else:
        # Save assignment into a csv file
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        outputfile = os.path.join(this_folder, os.path.pardir, 'output', scenario_name + '_' +str(args.timestep)+ '.picle')

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
            save_ouput_to_picle(outputfile, assignment, path_costs, solver_algorithm, error_percentage)
            # kill jvm
            connection.close()
        '''

if __name__ == '__main__':
    main()