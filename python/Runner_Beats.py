from __future__ import division
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
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Solvers.Extra_Projection_Method_Solver import Extra_Projection_Method_Solver

# Flag that indicates whether we are doing decomposition or not
decompositio_flag = False

conn = Java_Connection()

if conn.pid is not None:
    sim_dt = 2.0
    T = 3600  # Time horizon of interest
    sampling_dt = 300  # Duration of one time_step for the solver

    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
<<<<<<< HEAD
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'scenario_varying_100_nodes.xml')
    model_manager = BeATS_Model_Manager_class(configfile, conn.gateway, sim_dt)

=======
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'scenario_varying_demand_4.xml')
    model_manager = BeATS_Model_Manager_class(configfile, "ctm", conn.gateway, sim_dt)
>>>>>>> gabriel/loadmodel

    if(model_manager.is_valid()):
        num_steps = int(T/sampling_dt)

        # Algorithm to solve the problem
        solver_algorithm = Extra_Projection_Method_Solver
        #solver_algorithm = Path_Based_Frank_Wolfe_Solver

        scenario_solver = Solver_class(model_manager, solver_algorithm)
        assignment, assignment_vector = scenario_solver.Solver_function(T, sampling_dt, decompositio_flag)

        if assignment is None:
            print "Solver did not run"
        else:
            #Save assignment into a csv file
            this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            outputfile = os.path.join(this_folder, os.path.pardir, 'output', 'seven_links.csv')

            # We first save in the paramenters of the scenario
            csv_file = open(outputfile, 'wb')
            writer = csv.writer(csv_file)
            # Saving the model type
            writer.writerow(['model type:','BeATS'])
            od = model_manager.beats_api.get_od_info()
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

            #print "\nPath costs in secons:"
            #path_costs.print_all()

            #Distance to Nash
            print "\n"
            error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt)
            print "%.02f" % error_percentage ,"% vehicles from equilibrium"

            '''
            plt.figure(1)
            assignment.plot_demand()

            plt.figure(2)
            path_costs.plot_costs()
            '''


    # kill jvm
    conn.close()