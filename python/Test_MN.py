import os
import inspect
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
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

sampling_dt = 1200     # Duration of time_step for the solver, in this case it is equal to sim_dt

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

if(model_manager.is_valid()):
    path_list = dict()
    od = model_manager.beats_api.get_od_info()
    num_steps = int(T / sampling_dt)

    # Initializing the demand assignment
    commodity_list = list(model_manager.beats_api.get_commodity_ids())
    assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, sampling_dt)

    # Populating the Demand Assignment, based on the paths associated with ODs
    for o in od:
        count = 0
        comm_id = o.get_commodity_id()

        #if demand_size > num_steps or num_steps % len(demand_api) != 0:
            #print "Demand specified in xml cannot not be properly divided among time steps"
            #return

        for path in o.get_subnetworks():
            path_list[path.getId()] = path.get_link_ids()

            demand_api = [item * 3600 for item in
                          model_manager.beats_api.get_demand_with_ids("pathfull", path.getId(), comm_id).getProfile().getValues()]
            demand_api = np.asarray(demand_api)
            demand_size = len(demand_api)
            demand_dt = o.get_total_demand_vps().getDt()

            # Before assigning the demand, we want to make sure it can be properly distributed given the number of
            # Time step in our problem
            if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
                print "Demand specified in xml cannot not be properly divided among time steps"

            #Creates an array of demands from the xml demand profile to be assignmed into the demand assignment
            ass_demand = np.zeros(num_steps)
            for i in range(num_steps):
                #index = int(i / (num_steps/demand_size))
                index = int(i*sampling_dt/demand_dt)
                if index > demand_size-1:
                    index = demand_size-1
                ass_demand[i] = demand_api[index]

            assignment.set_all_demands_on_path_comm(path.getId(),comm_id, ass_demand)

    path_costs = model_manager.evaluate(assignment,T, initial_state = None)



# kill jvm
conn.close()