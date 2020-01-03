from __future__ import division
import os
import inspect
from Model_Manager.OTM_Model_Manager import OTM_Model_Manager_class
from Java_Connection import Java_Connection
from Solvers.Solver_Class import Solver_class
import argparse
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import time
import matplotlib.pyplot as plt
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Solvers.Extra_Projection_Method_Solver import Extra_Projection_Method_Solver
from Solvers.Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver

def call_solver(args):
    # Flag that indicates whether we are doing decomposition or not
    decomposition_flag = args.decomposition_flag

    conn = Java_Connection(decomposition_flag)

    if conn.pid is not None:
        sim_dt = 2.0
        T = args.T  # Time horizon of interest
        sampling_dt = args.sampling_dt  # Duration of one time_step for the solver

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', args.configfile)

        instantaneous = True      # Indicates whether we are doing ctm predictive (True) or instantaneous (False)
        model_manager = OTM_Model_Manager_class(configfile, args.model, conn.gateway, sim_dt)

        if(model_manager.is_valid()):
            num_steps = int(T/sampling_dt)

            # Get the OD Matrix form Model Manager
            # OD Matrix can also be initialized from another source, as long as it fits the OD_Matrix class format
            OD_Matrix = model_manager.get_OD_Matrix(num_steps, sampling_dt)

            if OD_Matrix is not None:
                # Algorithm to solve the problem
                if args.solver_algorithm == "FW": solver_algorithm = Path_Based_Frank_Wolfe_Solver
                elif args.solver_algorithm == "MSA": solver_algorithm = Method_of_Successive_Averages_Solver
                else: solver_algorithm = Extra_Projection_Method_Solver

                scenario_solver = Solver_class(model_manager, solver_algorithm)
                assignment, solver_run_time = scenario_solver.Solver_function(T, sampling_dt, OD_Matrix, decomposition_flag)

                if assignment is None:
                    print "Solver did not run"
                else:
                    #Save assignment into a csv file
                    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                    outputfile = os.path.join(this_folder, os.path.pardir, 'output', args.configfile[:-4]+'.csv')

                    # # We first save in the paramenters of the scenario
                    # csv_file = open(outputfile, 'wb')
                    # writer = csv.writer(csv_file)
                    # # Saving the model type
                    # writer.writerow(['model type:','BeATS'])
                    # od = model_manager.otm_api.get_od_info()
                    # demand_api = [item * 3600 for item in od[0].get_total_demand_vps().getValues()]
                    # od_dt = od[0].get_total_demand_vps().getDt()
                    # if od_dt is None:
                    #     od_dt = sampling_dt
                    #
                    # # Saving the demand per od and time horizon value
                    # writer.writerow(['demand dt (s)', 'od demand (vh)','T (s)'])
                    # writer.writerow([od_dt,demand_api,T])
                    #
                    # writer.writerow(['(path ID, commodity ID)', 'array of demand (vh) per dt on path'])
                    # # Now we save the assignment values to csv file
                    # for key, value in assignment.get_all_demands().items():
                    #     writer.writerow([key, value])
                    #
                    # csv_file.close()

                    #print "\nDemand Assignment:"
                    #assignment.print_all()

                    path_costs = model_manager.evaluate(assignment, T, initial_state=None)

                    #print "\nPath costs in secons:"
                    #path_costs.print_all()
                    if decomposition_flag:
                        from mpi4py import MPI

                        comm = MPI.COMM_WORLD
                        rank = comm.Get_rank()
                    else:
                        rank = 0

                    #Distance to Nash
                    error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt,OD_Matrix)
                    if rank == 0:
                        print "\n"
                        print "%.02f" % error_percentage ,"% vehicles from equilibrium"

                    '''
                    plt.figure(1)
                    assignment.plot_demand()
    
                    plt.figure(2)
                    path_costs.plot_costs()
                    '''

                    # COMMENT THIS OUT WHEN RUNNING IN PYCHARM
                    # kill jvm
                    # conn.close()

# The main function
def main():
    pass
    parser = argparse.ArgumentParser(description='Process config file and DTA parameters')
    parser.add_argument(type=str, dest="configfile", help="otm configuration file (mandatory)")
    parser.add_argument( '--run-in-parallel', dest="decomposition_flag", action='store_true',
                        help="Whether to run in parallel or not (default false)")
    parser.add_argument('--period',type=float, nargs='?', dest="T", default=600, help="DTA time period")
    parser.add_argument('--dt', type=float, nargs='?', dest="sampling_dt", default=60, help="DTA sampling dt")
    parser.add_argument(type=str, nargs='?', dest="model", default= "ctm", help="traffic model: ctm or static")
    parser.add_argument(type=str, nargs='?', dest="solver_algorithm",
                        default= "EPM", help="DTA algorithm: FW for FrankWofle, EPM for Extra Projection Method" 
                                                 " and MSA for Method of Successive Averages")

    args = parser.parse_args()

    # call solver with given arguments
    call_solver(args)



if __name__ == "__main__":
    main()