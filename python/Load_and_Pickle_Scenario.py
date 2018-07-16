import numpy as np
import pickle
import timeit
from copy import deepcopy
import sys

from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from copy import copy
from Solvers.Frank_Wolfe_Solver_Static import construct_igraph
import os
import inspect
import argparse

# Flag that indicates whether we are doing decomposition or not
decompositio_flag = False

# Flag that indicates whether we are doing decomposition or not

connection = Java_Connection(decompositio_flag)

if connection.pid is not None:

    # Contains local path to input configfile, for the three_links.xml network
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    scenario_name = 'scenario'   #Scenario name
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', scenario_name+'.xml')

    print "Loading data for: ",scenario_name

    # File where to save the pickled objects
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    outputfile = os.path.join(this_folder, os.path.pardir, 'output', scenario_name + '.pickle')

    coefficients = {}       #BPR Coefficients

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
            # Construct igraph object
            traffic_scenario = model_manager.traffic_model
            cost_function = model_manager.cost_function
            num_of_links = traffic_scenario.beats_api.get_num_links()
            graph_object = construct_igraph(traffic_scenario, cost_function)


            # We are going to pickle the model manager, te OD_Matrix and the BPR coefficients
            with open(outputfile, "wb") as f:
                pickle.dump(num_links, f)
                pickle.dump(cost_function, f)
                pickle.dump(OD_Matrix, f)
                pickle.dump(graph_object,f)


            # Read back the objects to make sure they got save correctly
            start_time1 = timeit.default_timer()
            with open(outputfile, "rb") as f:
                n_links = pickle.load(f)
                c_function = pickle.load(f)
                OD_M = pickle.load(f)
                g_object = pickle.load(f)

            elapsed1 = timeit.default_timer() - start_time1
            print ("\nReading from Pickle object took  %s seconds" % elapsed1)

        connection.close()

