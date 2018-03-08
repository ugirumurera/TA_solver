# This is a class to hold the OD demand information

import numpy as np
from copy import deepcopy, copy
from collections import OrderedDict
import matplotlib.pyplot as plt

class OD_class():

    #To initialize the Assignment Array, the constructor has to receive a path_list dictionary, list of commodity ,
    # commdity_list, ids number of time steps in the period considered and dt the duration of one time step for the demand profile
    def __init__(self, origin, destination,comm_id, path_list, num_time_steps, dt):
        # path_list saves a dictionary of the form [path_id]:[link_id, ...] of lists of link_ids that forms each path
        self.__origin = origin
        self.__destination = destination

        self.__path_list = path_list
        self.__comm_id = comm_id
        self.__num_time_steps = num_time_steps
        self.__dt = dt
        self.__demand = {}

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
