# This class stores costs per path, by summing up the cost per link of a particular path

import numpy as np
from copy import copy, deepcopy
from collections import OrderedDict
import matplotlib.pyplot as plt

class Path_Costs_class():
    # To initialize the Assignment Array, the constructor has to receive a path_list dictionary,, a list of all commodities and
    # number of time steps in the period considered
    # The path_list dictionary is of the form [path_id]:[link_id_1, link_id_2,...] and saves the set of links that makes
    # each path with a particular path_id
    def __init__(self, num_time_steps, dt):
        self.__path_list = {}
        self.__commodity_list = list()
        self.__num_time_steps = num_time_steps
        self.__dt = dt
        self.__path_costs = {}


    def get_all_path_cots(self):
        return self.__path_costs

    def set_path_list(self, path_list):
        self.__path_list = path_list

    def set_comm_list(self, comm_list):
        self.__commodity_list = comm_list

    # Receives a Link_Costs_Class and demand_assignment objects and returns a path_costs object containing the travel
    # cost per path, where the path_costs is a [(path_id, commodity_id)] = [cost_1, cost_2,...] dictionary
    def get_path_costs(self, link_costs, demand_assignment):
        self.__path_list = demand_assignment.get_path_list()
        self.__commodity_list = demand_assignment.get_commodity_list()
        l_costs = link_costs.get_all_costs()

        for key in demand_assignment.get_all_demands().keys():
            # Get the route (list of link_ids) associated with the current path_id in key[0]
            route = demand_assignment.get_path_list()[key[0]]
            for i in range(self.__num_time_steps):
                for link_id in route:
                    if key not in self.__path_costs.keys():
                        self.__path_costs[key] = np.zeros(self.__num_time_steps)

                    self.__path_costs[key][i] = self.__path_costs[key][i] + l_costs[(link_id,key[1])][i]

        return self

    #This is the function for smart summation applicable to dynamic models
    def dynamic_path_costs(self, link_costs, demand_assignment):
        self.__path_list = demand_assignment.get_path_list()
        self.__commodity_list = demand_assignment.get_commodity_list()
        l_costs = link_costs.get_all_costs()

        for key in demand_assignment.get_all_demands().keys():
            # Get the route (list of link_ids) associated with the current path_id in key[0]
            route = demand_assignment.get_path_list()[key[0]]
            for i in range(self.__num_time_steps):
                time_step = i
                for link_id in route:
                    if key not in self.__path_costs.keys():
                        self.__path_costs[key] = np.zeros(self.__num_time_steps)

                    travel_time = l_costs[(link_id,key[1])][time_step]
                    self.__path_costs[key][i] = self.__path_costs[key][i] + travel_time

                    if travel_time < self.__num_time_steps-1:
                        time_step += travel_time
                    else:
                        break
        return self

    # Returns costs of a particular link, commodity, and time_step
    def get_cost_at_path_comm_time(self, path_id, comm_id, time_step):
        if path_id not in self.__path_list.keys() or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        if time_step < 0 or time_step > (self.__num_time_steps-1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps-1
            return

        return self.__path_costs[(path_id, comm_id)][time_step]

    def set_costs_path_commodity(self, path_id, comm_id, cost_list):
        x = []
        for cost in cost_list:
            x.append(cost)
        self.__path_costs[(path_id, comm_id)] = copy(x)

    # This vector returns the path cost as a vector
    def vector_path_costs(self):
        #a = self.__path_costs.values()
        a = OrderedDict(sorted(self.__path_costs.items()))
        return [item for sublist in a.values() for item in sublist]
        #return np.concatenate(self.__path_costs.values())

    def print_all(self):
        ordered_costs = OrderedDict(sorted(self.__path_costs.items()))
        for key in ordered_costs.keys():
            for k in range(self.__num_time_steps):
                print "path ", key[0], " commodity ", key[1], " time step ", k, " cost ", self.__path_costs[key][k]

    #Prints out the travel costs in seconds
    def print_all_in_seconds(self):
        ordered_costs = OrderedDict(sorted(self.__path_costs.items()))
        for key in ordered_costs.keys():
            for k in range(self.__num_time_steps):
                print "path ", key[0], " commodity ", key[1], " time step ", k, " cost ", self.__path_costs[key][k]*3600

    def plot_costs(self):
        sub_index = len(self.__path_costs.keys())*100+10+1

        plt.title('Path Costs')

        # Sort assignment keys to ensure ordering in plots
        sorted_demand = OrderedDict(sorted(self.__path_costs.items()))
        Horizon = (self.__num_time_steps +1)*self.__dt
        y_axis = np.arange(0., Horizon, self.__dt)
        plt.title("Path Travel Cost")

        for key in sorted_demand.keys():
            plt.subplot(sub_index)
            x_axis = [self.__path_costs[key][0]]+ list(self.__path_costs[key])
            plt.step(y_axis, x_axis,linewidth= 5)
            plt.ylabel("path "+ str(key[0]) + " cost (s)")
            plt.xlabel("Time (s)")
            sub_index += 1

        plt.show()

    def set_cost_with_vector(self, cost_vector):
        a, b = 0, self.__num_time_steps -1
        # Sort the assignment to ensure same vector every time this function is called
        sorted_demand = OrderedDict(sorted(self.__path_costs.items()))

        for key in sorted_demand.keys():
            if a == b:
                self.__path_costs[key][0] = deepcopy(cost_vector[a])
            else:
                row = cost_vector[a:(b+1)]
                self.__path_costs[key] = copy(row)
            a += self.__num_time_steps
            b += self.__num_time_steps

    # Sets all the demands with an assignment dictionary
    def set_all_costs(self, costs):
        if (any(len(key) != 2 for key in costs.keys()) or
                any(len(value) != self.__num_time_steps for value in costs.values())):
            print("Error: shape of input demand does not match shape Demand_Assignment object")
            return False

        if any(key[0] not in self.__path_list.keys() or key[1] not in self.__commodity_list for key in costs.keys()):
            print("path id or commodity id not in input demand info")
            return False

        self.__path_costs = deepcopy(costs)

    def plot_costs_in_seconds(self):
        sub_index = len(self.__path_costs.keys())*100+10+1

        plt.title('Path Costs')

        # Sort assignment keys to ensure ordering in plots
        sorted_demand = OrderedDict(sorted(self.__path_costs.items()))
        Horizon = (self.__num_time_steps +1)*self.__dt
        x_axis = np.arange(0., Horizon, self.__dt)
        plt.title("Path Travel Cost")

        for key in sorted_demand.keys():
            plt.subplot(sub_index)
            y_axis = [self.__path_costs[key][0]]+ list(self.__path_costs[key])
            y_axis = [i * 3600 for i in y_axis]
            plt.step(x_axis, y_axis,linewidth= 5)
            plt.ylabel("path "+ str(key[0]) + " cost (s)")
            plt.xlabel("Time (s)")
            sub_index += 1

        plt.show()