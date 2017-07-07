# This is a class that stores the demand assignment on path per time period
# Saves the Assignment as a 3 dimensional array assignment, where assignment[path_id][commodity_id][time] is the demand
# assigned to a path with path_id, for commodity with commodity_id, and for a particular time t in assignment period.

import numpy as np

class Demand_Assignment_class():

    #To initialize the Assignment Array, the constructor has to receive the number of paths, number of commodities and
    # number of time steps in the period considered
    def __init__(self, num_paths, num_commodities, num_time_steps):
        self.__num_paths = num_paths
        self.__num_commodities = num_commodities
        self.__num_time_steps = num_time_steps
        self.__assignment = np.zeros((num_paths, num_commodities, num_time_steps))

    def get_num_paths(self):
        return self.__num_paths

    def get_commodities(self):
        return self.__num_commodities

    def get_num_time_step(self):
        return self.__num_time_steps

    # Returns demand assigned to a particular path, commodity, and time_step
    def get_demand_at_path_comm_time(self, path_id, comm_id, time_step):
        return self.__assignment[path_id, comm_id, time_step]

    # Returns all demands assigned to a particular path with path_id as a (number of commodities x number of time steps)
    # dimensional array
    def get_all_demands_on_path(self, path_id):
        return self.__assignment[path_id,:,:]

    #Returns all demands assigned to a particular path and commodity as an array of size: number of time steps
    def get_all_demands_on_path_comm(self, path_id, comm_id):
        return self.__assignment[path_id,comm_id,:]

    #Returns all demands assigned to a particular path and time_step as an array of size: number of commodities
    def get_all_demands_on_path_time_step(self, path_id, time_step):
        return self.__assignment[path_id,:,time_step]

    # Returns all demands assigned for commodity with commodity_id as a (number of paths x number of time steps)
    # dimensional array
    def get_all_demands_for_commodity(self, comm_id):
        return self.__assignment[:, comm_id, :]

    # Returns all demands assigned for a particular commodity and time_step as an array of size: number of paths
    def get_all_demands_on_comm_time_step(self, comm_id, time_step):
        return self.__assignment[:, comm_id, time_step]

    # Returns all demands assigned for a particular time_step as a (number of paths x number of commodities)
    # dimensional array
    def get_all_demands_for_time_step(self, time_step):
        return self.__assignment[:, :, time_step]

    # Sets all the demands with a three dimensional arra
    def set_all_demands(self, demands):
        if (demands.shape[0] != self.__num_paths or demands.shape[1] != self.__num_commodities or
                    demands.shape[2] != self.__num_time_steps ):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if any(demands < 0):
            print("Error: Negative value for demand")
            return
        self.__assignment[:, :, :] = demands

    # set demand for a particular path, commodity, and time_step
    def set_demand_at_path_comm_time(self, path_id, comm_id, time_step, demand):
        if(demand < 0):
            print("Error: Negative value for demand")
            return
        self.__assignment[path_id, comm_id, time_step] = demand

    # Sets all demands assigned for a particular path with path_id with a (number of commodities x number of time steps)
    # dimensional numpy array
    def set_all_demands_on_path(self, path_id, demands):
        if (demands.shape[0] != self.__num_commodities or demands.shape[1] != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if any(demands < 0):
            print("Error: Negative value for demand")
            return
        self.__assignment[path_id,:,:] = demands

    #Set all demands assigned to a particular path and commodity with an array of size: number of time steps
    def set_all_demands_on_path_comm(self, path_id, comm_id, demands):
        if (len(demands) != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(demands < 0)):
            print("Error: Negative value for demand")
            return
        self.__assignment[path_id,comm_id,:] = demands

    #Set all demands assigned for a particular path and time_step with an array of size: number of commodities
    def set_all_demands_on_path_time_step(self, path_id, time_step, demands):
        if(len(demands) != self.__num_commodities):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(demands < 0)):
            print("Error: Negative value for demand")
            return
        self.__assignment[path_id,:,time_step] = demands

    # Set all demands assigned for commodity with commodity_id with a (number of paths x number of time steps)
    # dimensional array
    def set_all_demands_for_commodity(self, comm_id, demands):
        if (demands.shape[0] != self.__num_paths or demands.shape[1] != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(demands < 0)):
            print("Error: Negative value for demand")
            return

        self.__assignment[:, comm_id, :] = demands

    # Set all demands assigned for a particular commodity and time_step with an array of size: number of paths
    def set_all_demands_on_comm_time_step(self, comm_id, time_step, demands):
        if(len(demands) != self.__num_paths):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(demands < 0)):
            print("Error: Negative value for demand")
            return

        self.__assignment[:,comm_id,time_step] = demands

    # Returns all demands assigned for a particular time_step as a (number of paths x number of commodities)
    # dimensional array
    def set_all_demands_for_time_step(self, time_step, demands):
        if (demands.shape[0] != self.__num_paths or demands.shape[1] != self.__num_commodities):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(demands < 0)):
            print("Error: Negative value for demand")
            return

        self.__assignment[:, :, time_step] = demands
