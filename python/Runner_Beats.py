import os
import inspect
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import time

conn = Java_Connection()

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(this_folder, os.path.pardir, os.path.pardir, 'configfiles', 'seven_links.xml')
dt = 2
model_manager = BeATS_Model_Manager_class(configfile, conn.gateway, dt)

if(model_manager.is_valid()):
    path_list = dict()
    od = model_manager.beats_api.get_od_info()

    # Initializing the demand assignment
    commodity_list = list(model_manager.beats_api.get_commodity_ids())

    T = 3600  # Time horizon of interest
    demand_dt = 1800.0
    num_steps = int(T / demand_dt)

    assignment = Demand_Assignment_class(path_list, commodity_list,
                                     num_steps, demand_dt)

    # Populating the Demand Assignment, based on the paths associated with ODs
    for o in od:
        count = 0
        comm_id = o.get_commodity_id()

        demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)

        # Before assigning the demand, we want to make sure it can be properly distributed given the number of
        # Time step in our problem
        if demand_size > num_steps or num_steps % len(demand_api) != 0:
            print "Demand specified in xml cannot not be properly divided among time steps"

        for path in o.get_subnetworks():
            path_list[path.getId()] = path.get_link_ids()
            if count == 0:
                # Creates an array of demands from the xml demand profile to be assignmed into the demand assignment
                ass_demand = np.zeros(num_steps)
                for i in range(num_steps):
                    index = int(i / (num_steps / demand_size))
                    ass_demand[i] = demand_api[index]

                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, ass_demand)
            else:
                demand = np.zeros(num_steps)
                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
            count += 1

    assignment.print_all()
    #Evaluating the path_costs
    path_costs = model_manager.evaluate(assignment, demand_dt, T)

    path_costs.print_all()