# This is a class to hold the OD demand information including origin, destination, path list,
# commodity id and the demand profile per od. Demand profile is an array of n demand values, where
# n is the number of time steps in the planning horizon.

import numpy as np
from copy import deepcopy, copy
from collections import OrderedDict
import matplotlib.pyplot as plt

class OD_Pair():

    #To initialize the Assignment Array, the constructor has to receive a path_list dictionary, list of commodity ,
    # commdity_list, ids number of time steps in the period considered and dt the duration of one time step for the demand profile
    def __init__(self, origin = None, destination=None,num_time_steps= None,comm_id = None, demand = None,path_list = None):
        # path_list saves a dictionary of the form [path_id]:[link_id, ...] of lists of link_ids that forms each path
        self.__origin = origin
        self.__destination = destination
        if path_list is None: self.__path_list = {}
        self.__comm_id = comm_id
        if num_time_steps is not None:
            if demand is not None and len(demand) == num_time_steps:
                self.__demand = demand
            else: self.__demand = np.zeros(num_time_steps)
        else: self.__demand = None

    def get_path_list(self):
        return self.__path_list

    def get_comm_id(self):
        return self.__comm_id

    def get_num_time_steps(self):
        return self.__num_time_steps

    def get_dt(self):
        return self.__dt

    def get_demand(self):
        return self.__demand

    def get_origin(self):
        return self.__origin

    def get_destination(self):
        return self.__destination

    def set_path_list(self, path_list):
        if any(not isinstance(key, (int, long)) for key in path_list.keys()) or \
                any(not isinstance(value, (int, long)) for value in path_list.values()):
            print " Path List format incorrect"
            return None

        self.__path_list = deepcopy(path_list)

    def set_origin(self, origin):
        self.__origin = origin

    def set_destination(self, dest):
        self.__destination = dest

    def set_commodity(self, comm):
        self.__comm_id = comm

    def set_num_steps(self, num):
        self.__num_time_steps = num

    def set_dt(self, dt):
        self.__dt = dt

    def set_demand(self, demand):
        if (demand < 0).all():
            print "one or more demand values are less than zero"
            return None
        if len(demand) < self.__num_time_steps or len(demand) > self.__num_time_steps:
            print "size of demand array incorrect"
            return None

        self.__demand = copy(demand)

    def set_demand_time_step(self, time, demand_value):
        if time < 0 or time > self.__num_time_steps-1:
            print "time specified out of range"
            return None

        if not isinstance(demand_value, (int, float)):
            print "demand value not integer or float"
            return None

        self.__demand[time] = demand_value

    def set_od_with_Beats(self, od, num_steps, dt):
        self.__origin = od.get_origin_node_id()
        self.__destination = od.get_destination_node_id()
        self.__comm_id = od.get_commodity_id()

        #Setting the path_list for the od
        for path in od.get_subnetworks():
            self.__path_list[path.getId()] = list(path.get_link_ids())

        demand_api = [item * 3600 for item in od.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)
        demand_dt = od.get_total_demand_vps().getDt()

        # Before assigning the demand, we want to make sure it can be properly distributed given the number of
        # Time step in our problem
        if (dt > demand_dt or demand_dt % dt > 0) and (demand_size > 1):
            print "Demand specified in xml cannot not be properly divided among time steps"
            return None

        self.__demand = np.zeros(num_steps)

        if demand_size == num_steps:
            self.__demand = copy(demand_api)
        else:
            for i in range(num_steps):
                index = int(i / (num_steps / demand_size))
                #demand = od.get_total_demand_vps().get_value(index) * 3600
                self.__demand[i] = demand_api[index]

    def set_od_with_Beats_timestep(self, od, num_steps, dt, timestep):
        self.__origin = od.get_origin_node_id()
        self.__destination = od.get_destination_node_id()
        self.__comm_id = od.get_commodity_id()

        #Setting the path_list for the od
        for path in od.get_subnetworks():
            self.__path_list[path.getId()] = list(path.get_link_ids())

        demand_api = [item * 3600 for item in od.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)
        demand_dt = od.get_total_demand_vps().getDt()

        # Before assigning the demand, we want to make sure it can be properly distributed given the number of
        # Time step in our problem
        if (dt > demand_dt or demand_dt % dt > 0) and (demand_size > 1):
            print "Demand specified in xml cannot not be properly divided among time steps"
            return None

        self.__demand = np.zeros(1)

        if demand_size == num_steps:
            self.__demand[0] = od.get_total_demand_vps().get_value(timestep) * 3600
        else:
            index = int((timestep) / (num_steps / demand_size))
            self.__demand[0] = od.get_total_demand_vps().get_value(index) * 3600

    def print_od_data(self):
        print "origin: ", self.__origin, " , destination: ", self.__destination, " commodity: ",\
        self.__comm_id
        print "Path_list: ", self.__path_list
        print "Demand: ", self.__demand


