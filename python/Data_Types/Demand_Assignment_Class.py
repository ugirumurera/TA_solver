# This is a class that stores the demand assignment on path per time period
# the dictionary stores [path_id,commodity_id] as keys and each key is associated with (1 X number of time steps)
# dimensional array of demands per (path,commodity) pair.

import numpy as np
from copy import deepcopy, copy
from collections import OrderedDict
import matplotlib.pyplot as plt

class Demand_Assignment_class():

    #To initialize the Assignment Array, the constructor has to receive a path_list dictionary, list of commodity ,
    # commdity_list, ids number of time steps in the period considered and dt the duration of one time step for the demand profile
    def __init__(self, path_list, commodity_list, num_time_steps, dt):
        # path_list saves a dictionary of the form [path_id]:[link_id, ...] of lists of link_ids that forms each path
        self.__path_list = path_list
        self.__commodity_list = commodity_list
        self.__num_time_steps = num_time_steps
        self.__dt = dt
        self.__assignment = OrderedDict()

    def get_num_paths(self):
        return len(self.__path_list.keys())

    def get_num_commodities(self):
        return len(self.__commodity_list)

    def get_num_time_step(self):
        return self.__num_time_steps

    def get_all_demands(self):
        return self.__assignment

    def get_commodity_list(self):
        return self.__commodity_list

    def get_path_list(self):
        return self.__path_list

    def get_dt(self):
        return self.__dt

    # Adds new routes to the Demand_Assignment object using a [path_id]:[link_id_1, link_id_2, ...]
    def add_path(self, route_list):
        self.__assignment.update(route_list)

    # Returns demand assigned to a particular path, commodity, and time, where time is in seconds
    def get_demand_at_path_comm_time(self, path_id, comm_id, time):

        time_step = self.get_time_step(time)

        if path_id not in self.__path_list or comm_id not in self.__commodity_list:
            print("path id or commodity id not in Demand_Assignment object")
            return False
        if time_step < 0 or time_step > (self.__num_time_steps-1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps-1)
            return False
        return self.__assignment[(path_id, comm_id)][time_step]

    # Returns all demands assigned to a particular path with path_id as a [comm_id]: [demand_1, demand_2,...]
    # dictionary, where each commodity is associated with (1 X num_time_steps) dimensional array
    def get_all_demands_on_path(self, path_id):
        if path_id not in self.__path_list :
            print("path id not in Demand_Assignment object")
            return False
        path_dict = {}
        for key in self.__assignment.keys():
            if key[0] == path_id:
                path_dict[key[1]] = self.__assignment[key]
        return path_dict

    #Returns all demands assigned to a particular path and commodity as an array of size: number of time steps
    def get_all_demands_on_path_comm(self, path_id, comm_id):
        if path_id not in self.__path_list or comm_id not in self.__commodity_list:
            print("path id or commodity id not in Demand_Assignment object")
            return False
        return self.__assignment[(path_id,comm_id)]

    #Returns all demands assigned to a particular path and time_step as [commodity_id]: [demand] dictionary
    def get_all_demands_on_path_time_step(self, path_id, time):

        time_step = self.get_time_step(time)

        if path_id not in self.__path_list :
            print("Commodity id not in Demand_Assignment object")
            return False
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        path_time_dict = {}
        for key in self.__assignment.keys():
            if key[0] == path_id:
                path_time_dict[key[1]] = self.__assignment[key][time_step]
        return path_time_dict


    # Returns all demands assigned for commodity with commodity_id as a (number of paths x number of time steps)
    # dimensional array
    def get_all_demands_for_commodity(self, comm_id):
        if comm_id not in self.__commodity_list:
            print("Commodity id not in Demand_Assignment object")
            return False

        comm_dict = {}
        for key in self.__assignment.keys():
            if key[1] == comm_id:
                comm_dict[key[0]] = self.__assignment[key]
        return comm_dict

    #Was here
    # Returns all demands assigned for a particular commodity and time_step as [path_id]: [demand] dictionary
    def get_all_demands_on_comm_time_step(self, comm_id, time):

        time_step = self.get_time_step(time)

        if comm_id not in self.__commodity_list:
            print("Commodity id not in Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        comm_time_dict = {}
        for key in self.__assignment.keys():
            if key[1] == comm_id:
                comm_time_dict[key[0]] = self.__assignment[key][time_step]
        return comm_time_dict

    # Returns all demands assigned for a particular time_step as a [(path_id,comm_id)]:[demand] dictionary
    def get_all_demands_for_time_step(self, time):

        time_step = self.get_time_step(time)

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        time_dict = {}
        for key in self.__assignment.keys():
            time_dict[key] = self.__assignment[key][time_step]
        return time_dict

    # Sets all the demands with an assignment dictionary
    def set_all_demands(self, demands):
        if (any(len(key) != 2 for key in demands.keys()) or
                any(len(value) != self.__num_time_steps for value in demands.values())):
            print("Error: shape of input demand does not match shape Demand_Assignment object")
            return False

        if any(value[i] < 0 for value in demands.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for demand")
            return False

        if any(key[0] not in self.__path_list.keys() or key[1] not in self.__commodity_list for key in demands.keys()):
            print("path id or commodity id not in input demand info")
            return False

        self.__assignment = deepcopy(demands)

    # Adds demands with an assignment and path dictionaries
    def add_demands(self, demands, route_list):
        if (any(len(key) != 2 for key in demands.keys()) or
                any(len(value) != self.__num_time_steps for value in demands.values())):
            print("Error: shape of input demand does not match shape demand assignment object")
            return False

        if any(value[i] < 0 for value in demands.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for demand")
            return False

        if any(key[0] not in route_list or key[1] not in self.__commodity_list for key in demands.keys()):
            print("path id or commodity id not in input demand info")
            return False

        self.__assignment.update(demands)
        self.__path_list.update(route_list)

    # set demand for a particular path, commodity, and time_step or adds the entry if did not exist in the dictionary
    def set_demand_at_path_comm_time(self, path_id, comm_id, time, demand):

        time_step = self.get_time_step(time)

        if(demand < 0):
            print("Error: Negative value for demand")
            return False
        if(path_id, comm_id) not in self.__assignment.keys():
            print("Error: (path_id, comm_id) key not in Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return False

        self.__assignment[path_id, comm_id][time_step] = copy(demand)

    # Adds a demand for a particular path, commodity, and time_step or adds the entry if did not exist in the dictionary
    # route is a list of links that makes up the path with path_id
    def add_demand_at_path_comm_time(self, path_id, route, comm_id, time, demand):

        time_step = self.get_time_step(time)

        if (demand < 0):
            print("Error: Negative value for demand")
            return False

        if comm_id not in self.__commodity_list:
            print("Error: commodity id not in Demand Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        if ((path_id, comm_id) in self.__assignment.keys()):
            self.__assignment[(path_id, comm_id)][time_step] = demand
        else:
            self.__assignment[(path_id, comm_id)] = np.zeros((self.__num_time_steps))
            self.__assignment[(path_id, comm_id)][time_step] = demand
            route_list = {path_id:route}
            self.__path_list.update(route_list)

    # Sets all demands assigned for a particular path with path_id with a [comm_id_1]:[demand_t1, demand_t2,...] dictionary
    def set_all_demands_on_path(self, path_id, demands):
        if (any(not isinstance(key, ( int, long ))  for key in demands.keys()) or
                any(len(value) != self.__num_time_steps for value in demands.values())):
            print("Error: shape of input demand does not match shape of Demand_Assignment")
            return False

        if any(value[i] < 0 for value in demands.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for demand")
            return False

        if path_id not in self.__path_list or any(comm_id not in self.__commodity_list for comm_id in demands.keys()):
            print("Error: path id or commodity id not in Demand_Assignment object")
            return False

        for comm_id in demands.keys():
            self.__assignment[(path_id, comm_id)] =demands[comm_id]

    # Adds all demands for new path with path_id with a [comm_id_1]:[demand_t1, demand_t2,...] dictionary
    def add_all_demands_on_path(self, path_id, route, demands):
        if (any(not isinstance(key, (int, long)) for key in demands.keys()) or
                any(len(value) != self.__num_time_steps for value in demands.values())):
            print("Error: shape of input demand does not match shape of Demand_Assignment")
            return False

        if any(comm_id not in self.__commodity_list for comm_id in demands.keys()):
            print("Error: commodity id not in Demand_Assignment object")
            return False

        if any(value[i] < 0 for value in demands.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for demand")
            return False

        for comm_id in demands.keys():
            self.__assignment[path_id, comm_id] = demands[comm_id]
            route_list = {path_id: route}
            self.__path_list.update(route_list)

    #Set all demands assigned to a particular path and commodity with an array of size: number of time steps
    def set_all_demands_on_path_comm(self, path_id, comm_id, demands):
        if (len(demands) != self.__num_time_steps):
            print("Error: shape of input demand array does not match Demand_Assignment object")
            return False

        if (path_id not in self.__path_list.keys() or comm_id not in self.__commodity_list):
            print("Error: path id or commodity id not in Demand Assignment object")
            return False

        if (any(demand < 0 for demand in demands)):
            print("Error: Negative value for demand")
            return False

        self.__assignment[(path_id, comm_id)] = deepcopy(demands)

    # Adds demands assigned to a new path, and existing commodity with an array of size: number of time steps
    def add_all_demands_on_path_comm(self, path_id, route, comm_id, demands):
        if len(demands) != self.__num_time_steps:
            print("Error: shape of input demand does not match shape of Demand_Assignment object")
            return False

        if  comm_id not in self.__commodity_list:
            print("Error: commodity id not in Demand Assignment object")
            return False

        if any(demand < 0 for demand in demands):
            print("Error: Negative value for demand")
            return False

        self.__assignment[(path_id, comm_id)] = demands
        route_list = {path_id: route}
        self.__path_list.update(route_list)

    #Set all demands assigned for a particular path and time_step with a [comm_id_1]:[demand_at_time_step] dictionary
    def set_all_demands_on_path_time_step(self, path_id, time, demands):

        time_step = self.get_time_step(time)

        if (any(not isinstance(key, (int, long))  for key in demands.keys()) or
                any( not isinstance(value, (int, long)) for value in demands.values())):
            print("Error: shape of input demand does not match shape of Demand_Assignment object")
            return False

        if any(key not in self.__commodity_list for key in demands.keys() or path_id not in self.__path_list.keys()):
            print("Error: path id or commodity id not in Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return False

        if any(demand < 0 for demand in demands.values()):
            print("Error: Negative value for demand")
            return False

        for comm_id in demands.keys():
            if ((path_id, comm_id) in self.__assignment.keys()):
                self.__assignment[(path_id, comm_id)][time_step] = demands[comm_id]
            else:
                self.__assignment[(path_id, comm_id)] = np.zeros((self.__num_time_steps))
                self.__assignment[(path_id, comm_id)][time_step] =demands[comm_id]

    # Set all demands assigned for a particular path and time_step with a [comm_id_1]:[demand_at_time_step] dictionary
    def add_all_demands_on_path_time_step(self, path_id, route, time, demands):

        time_step = self.get_time_step(time)

        if (any(not isinstance(key, (int, long)) for key in demands.keys()) or
                any(not isinstance(value, (int, long)) for value in demands.values())):
            print("Error: shape of input demand does not match shape of Demand_Assignment object")
            return False

        if any(key not in self.__commodity_list for key in demands.keys()):
            print("Error: commodity id not in Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        if any(demand < 0 for demand in demands.values()):
            print("Error: Negative value for demand")
            return False

        for comm_id in demands.keys():
            if ((path_id, comm_id) in self.__assignment.keys()):
                self.__assignment[(path_id, comm_id)][time_step] = demands[comm_id]
            else:
                self.__assignment[(path_id, comm_id)] = np.zeros((self.__num_time_steps))
                self.__assignment[(path_id, comm_id)][time_step] = demands[comm_id]
            route_list = {path_id: route}
            self.__path_list.update(route_list)

    # Set all demands assigned for commodity with a dictionary of the form
    # a [path_id]:[demand_t1, demand_t2,...]
    def set_all_demands_for_commodity(self, comm_id, demands):
        if (any( not isinstance(key, ( int, long ))  for key in demands.keys()) or
                any(len(value) != self.__num_time_steps for value in demands.values())):
            print("Error: shape of input demand array does not shape of Demand_Assignment object")
            return False

        if comm_id not in self.__commodity_list or \
                any(path_id not in self.__path_list.keys() for path_id in demands.keys()):
            print("Error: path id or commodity id not in Demand_Assignment object")
            return False

        if any(value[i] < 0 for value in demands.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for demand")
            return False

        for path_id in demands.keys():
            self.__assignment[(path_id, comm_id)] =demands[path_id]

    # Set all demands assigned for a particular path and time_step with a [path_id_1]:[demand_at_time_step] dictionary
    def set_all_demands_on_comm_time_step(self, comm_id, time, demands):

        time_step = self.get_time_step(time)

        if (any(not isinstance(key, (int, long))  for key in demands.keys()) or
                any(not isinstance(value, (int, long)) for value in demands.values())):
            print("Error: shape of input demand does not match shape of Demand_Assignment object")
            return False

        if comm_id not in self.__commodity_list or \
                any(path_id not in self.__path_list.keys() for path_id in demands.keys()):
            print("Error: path id or commodity id not in Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return False

        if any(demand < 0 for demand in demands.values()):
            print("Error: Negative value for demand")
            return False

        for path_id in demands.keys():
            if ((path_id, comm_id) in self.__assignment.keys()):
                self.__assignment[(path_id, comm_id)][time_step] = demands[path_id]
            else:
                self.__assignment[(path_id, comm_id)] = np.zeros((self.__num_time_steps))
                self.__assignment[(path_id, comm_id)][time_step] =demands[path_id]


    # Returns all demands assigned for a particular time_step as with a [(path_id,commodity_id)]:[demand_time_step]
    # dictionary
    def set_all_demands_for_time_step(self, time, demands):

        time_step = self.get_time_step(time)

        if (any(len(key) != 2 for key in demands.keys()) or
                any(not isinstance(value, (int, long)) for value in demands.values())):
            print("Error: shape of input demand does not match Demand_Assignment object")
            return False

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return False

        if any(demand < 0 for demand in demands.values()):
            print("Error: Negative value for demand")
            return False

        if any(key not in self.__assignment.keys() for key in demands.keys()):
            print('Error: path id or commodity id not in Demand_Assignment object')

        for key in demands.keys():
            if key in self.__assignment.keys():
                self.__assignment[key][time_step] = demands[key]
            else:
                self.__assignment[key] = np.zeros((self.__num_time_steps))
                self.__assignment[key][time_step] = demands[key]

    # Creates an empty assignment with keys
    def set_keys(self, keys):
        # first check if the keys contain the right commodity ids and path ids
        if any(len(key) != 2 or key[0] not in self.__path_list.keys()
               or key[1] not in self.__commodity_list for key in keys):
            print "Demand assignment keys not right format or contain unknown path id or commodity id"
            return False
        else:
            for key in keys:
                self.__assignment[key] = np.zeros(self.__num_time_steps)

    # Creates a vector out of the demand_assignment values
    def vector_assignment(self):
        a = OrderedDict(sorted(self.__assignment.items()))
        return [item for sublist in a.values() for item in sublist]
        #return np.concatenate(self.__assignment.values())

    def set_demand_with_vector(self, demand_vector):
        a, b = 0, self.__num_time_steps -1
        # Sort the assignment to ensure same vector every time this function is called
        sorted_demand = OrderedDict(sorted(self.__assignment.items()))

        for key in sorted_demand.keys():
            if a == b:
                self.__assignment[0] = deepcopy(demand_vector[a])
            else:
                row = demand_vector[a:(b+1)]
                self.__assignment[key] = copy(row)
            a += self.__num_time_steps
            b += self.__num_time_steps

    def get_time_step(self,time):
        if self.__dt is not None:
            return int(time / self.__dt)  # Calculating first the corresponding time_step in the demand profile
        else:
            return 0

    def print_all(self):
        for key in self.__assignment.keys():
            for k in range(self.__num_time_steps):
                print "path ", key[0], " commodity ", key[1], " time step ", k, " demand ", self.__assignment[key][k]

    def plot_demand(self):
        sub_index = len(self.__assignment.keys())*100+10+1
        # Sort assignment keys to ensure ordering in plots
        sorted_demand = OrderedDict(sorted(self.__assignment.items()))
        Horizon = (self.__num_time_steps +1)*self.__dt
        y_axis = np.arange(0., Horizon, self.__dt)

        for key in sorted_demand.keys():
            plt.subplot(sub_index)
            x_axis = [self.__assignment[key][0]]+ list(self.__assignment[key])
            plt.step(y_axis, x_axis)
            ylabel = "path "+ str(key[0]) + " (vh)"
            plt.ylabel(ylabel)
            sub_index += 1

        plt.show()