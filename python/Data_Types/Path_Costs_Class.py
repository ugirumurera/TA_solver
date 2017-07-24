# This class stores costs per path, by summing up the cost per link of a particular path

import numpy as np

class Path_Costs_class():
    # To initialize the Assignment Array, the constructor has to receive a path_list dictionary,, a list of all commodities and
    # number of time steps in the period considered
    # The path_list dictionary is of the form [path_id]:[link_id_1, link_id_2,...] and saves the set of links that makes
    # each path with a particular path_id
    def __init__(self, num_time_steps, dt):
        self.__path_list = {}
        self.__commodity_list = list()
        self.__num_time_steps = num_time_steps
        self.__dta = dt
        self.__path_costs = {}

    # Receives a Link_Costs_Class and demand_assignment objects and returns a path_costs object containing the travel
    # cost per path, where the path_costs is a [(path_id, commodity_id)] = [cost_1, cost_2,...] dictionary
    def get_path_costs(self, link_costs, demand_assignment):
        for key in demand_assignment.get_all_demands().keys():
            # Get the route (list of link_ids) associated with the current path_id in key[0]
            route = demand_assignment.get_path_list()[key[0]]

            for link_id in route:
                if key not in self.__path_costs.keys():
                    self.__path_costs[key] = np.zeros(self.__num_time_steps)

                self.__path_costs[key] = self.__path_costs[key] + link_costs.get_all_costs()[(link_id,key[1])]

        return self

    def print_all(self):
        for key in self.__path_costs.keys():
            for k in range(self.__num_time_steps):
                print "path ", key[0], " commodity ", key[1], " time step ", k, " cost ", self.__path_costs[key][k]