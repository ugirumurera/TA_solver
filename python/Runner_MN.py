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
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver

plt.rcParams.update({'font.size': 17})

# Flag that indicates whether we are doing decomposition or not
decompositio_flag = False

conn = Java_Connection()

if conn.pid is not None:

    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
    coefficients = {}
    T = 3600  # Time horizon of interest
    sim_dt = 2.0  # Duration of one time_step for the traffic model

    sampling_dt = 1200     # Duration of time_step for the solver, in this case it is equal to sim_dt

    model_manager = Link_Model_Manager_class(configfile, "mn", conn.gateway, sim_dt, "bpr", coefficients)

    #Estimating bpr coefficients with beats
    num_links = model_manager.otm_api.get_num_links()
    avg_travel_time = np.zeros(num_links)
    num_coeff = 5

    for i in range(num_links):
        fft= (model_manager.otm_api.get_link_with_id(long(i)).getFull_length() \
              / model_manager.otm_api.get_link_with_id(long(i)).get_ffspeed_mps()) / 3600
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

                #Save assignment into a csv file
                this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                outputfile = os.path.join(this_folder, os.path.pardir, 'output', 'seven_links_mn.csv')

                # We first save in the paramenters of the scenario
                csv_file = open(outputfile, 'wb')
                writer = csv.writer(csv_file)
                # Saving the model type
                writer.writerow(['model type:','BeATS'])
                od = model_manager.otm_api.get_od_info()
                demand_api = [item * 3600 for item in od[0].get_total_demand_vps().getValues()]
                od_dt = od[0].get_total_demand_vps().getDt()
                if od_dt is None:
                    od_dt = sampling_dt

                # Saving the demand per od and time horizon value
                writer.writerow(['demand dt (s)', 'od demand (vh)','T (s)'])
                writer.writerow([od_dt,demand_api,T])

                writer.writerow(['(path ID, commodity ID)', 'array of demand (vh) per dt on path'])
                # Now we save the assignment values to csv file
                for key, value in assignment.get_all_demands().items():
                    writer.writerow([key, value])

                csv_file.close()

                #print "\nDemand Assignment:"
                #assignment.print_all()

                path_costs = model_manager.evaluate(assignment, T, initial_state=None)

                #print "\nPath cost in seconds:"
                #path_costs.print_all_in_seconds()

                #Distance to Nash
                print "\n"
                error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt, OD_Matrix)
                print "%.02f" % error_percentage ,"% vehicles from equilibrium"

    # kill jvm
    conn.close()