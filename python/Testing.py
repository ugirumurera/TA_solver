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
import multiprocessing as mp
from copy import copy, deepcopy
from Solvers.Projection_onto_Simplex import Projection_onto_Simplex
import csv

#from mpi4py import MPI

d = np.array([])
print d.size
d[(1,2)] = np.zeros(5)

d2 = deepcopy(d)

d2[(1,3)] = 'hello'

def array_combine(a, b, indices):
    b[indices] = a
    return b

if __name__ == '__main__':
    #comm = MPI.COMM_WORLD
    #rank = comm.Get_rank()
    #my_op = MPI.Op.Create(my_dic_combine)
    rank = 0

    x = 5*np.ones(3)

    key_start = rank*10

    indices = np.asarray(range(1,5))

    #y = np.concatenate(x,indices)

    dict_i = np.ones(3)

    dict_k = np.zeros(10)
    indices_k = [1,2,5]

    array_combine(dict_i,dict_k, indices_k)
    #comm.Allreduce(dict_i, dict_k, op = my_op)

    print dict_k


'''
data = [np.arange(8).reshape(2, 4), np.arange(10).reshape(2, 5)]


#Testing writing numpy to csv
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
outputfile = os.path.join(this_folder, os.path.pardir, 'output', 'testing.csv')

c = np.ones(5)*12
d = np.ones(3)*4

csv_file = open(outputfile, 'wb')
writer = csv.writer(csv_file)

# Saving the demand per od and time horizon value
writer.writerow(c)
writer.writerow(d)

csv_file.close()

csv_file = open(outputfile, 'a')
np.savetxt(csv_file,c)
np.savetxt(csv_file,d)

f_handle = file('my_file.csv', 'a')
np.savetxt(f_handle, c)
np.savetxt(f_handle, d)
f_handle.close()


x = [20399.998,20399.998,20399.998,20459.998,20399.998]
a = 3000

y = Projection_onto_Simplex(x,a)

x = [1,2,3]
a = np.linalg.norm(x,1)


conn = Java_Connection()

def initialize_assignment(a):
    print 'process id:', os.getpid(), " num ", a
    
    for o in od:
        count = 0
        comm_id = o.get_commodity_id()

        demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)
        demand_dt = o.get_total_demand_vps().getDt()

        # Before assigning the demand, we want to make sure it can be properly distributed given the number of
        # Time step in our problem
        if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
            print "Demand specified in xml cannot not be properly divided among time steps"

        for path in o.get_subnetworks():
            path_list[path.getId()] = path.get_link_ids()
            demand = np.zeros(num_steps)
            assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
    
if __name__ == '__main__':

    if conn.pid is not None:
        sim_dt = 2.0
        T = 3600  # Time horizon of interest
        sampling_dt = 300  # Duration of one time_step for the solver

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'scenario_varying_100_nodes.xml')
        model_manager = BeATS_Model_Manager_class(configfile, conn.gateway, sim_dt)

        print "Finished Loading. Going to Solving"

        if (model_manager.is_valid()):
            path_list = dict()
            od = list(model_manager.beats_api.get_od_info())
            num_steps = int(T / sampling_dt)

            # Initializing the demand assignment
            commodity_list = list(model_manager.beats_api.get_commodity_ids())
            assignment = Demand_Assignment_class(path_list, commodity_list,
                                                 num_steps, sampling_dt)

            print mp.cpu_count()
            x = [1,2,3,4,5,6,8,9,303]
            # Creating a pool of processors
            pool = mp.Pool(processes=4)
            # Populating the Demand Assignment, based on the paths associated with ODs
            y = [pool.apply(o.get_subnetworks(), args=(o,)) for o in od]

            print "we are done"

        # kill jvm
        conn.close()

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
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links_mn.xml')
coefficients = {}
T = 3600  # Time horizon of interest
sim_dt = 2.0  # Duration of one time_step for the traffic model

sampling_dt = 1800     # Duration of time_step for the solver, in this case it is equal to sim_dt

model_manager = Link_Model_Manager_class(configfile, conn.gateway, "mn", sim_dt, "bpr", coefficients)

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

if model_manager.is_valid():
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

    for i in range(10):
        path_costs = model_manager.evaluate(assignment,T, initial_state = None)
        print "\n"
        #path_costs.print_all_in_seconds()


# kill jvm
conn.close()

'''