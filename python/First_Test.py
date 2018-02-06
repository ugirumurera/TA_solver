# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np
from copy import deepcopy

# from Cost_Functions.BPR_Function import BPR_Function_class
# from Traffic_Models.Static_Model import Static_Model_Class
from Solvers.Solver_Class import Solver_class
# from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
# from Data_Types.Link_Costs_Class import Link_Costs_class
# from py4j.java_gateway import JavaGateway,GatewayParameters
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from copy import copy
import matplotlib.pyplot as plt
import os
import inspect
import csv

plt.rcParams.update({'font.size': 18})

connection = Java_Connection()

if connection.pid is not None:

    # Contains local path to input configfile, for the three_links.xml network
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
    coefficients = {}
    T = 3600  # Time horizon of interest
    sim_dt = 0.0  # Duration of one time_step for the traffic model

    sampling_dt = 1800     # Duration of time_step for the solver, in this case it is equal to sim_dt

    model_manager = Link_Model_Manager_class(configfile, connection.gateway, "static", sim_dt, "bpr", coefficients)

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

        scenario_solver = Solver_class(model_manager)
        assignment, assignment_vector = scenario_solver.Solver_function(T, sampling_dt, "FW")

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
            writer.writerow(['model type:',model_manager.traffic_model.model_type])
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

            path_costs = model_manager.evaluate(assignment, T, initial_state=None)


            #Distance to Nash
            print "\n"
            error_percentage = scenario_solver.distance_to_Nash(assignment, path_costs, sampling_dt)


            print "SUCCESS!!"

    # kill jvm
    connection.close()