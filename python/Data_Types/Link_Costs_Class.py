# This is an object that stores a dictionary of costs per links.
# the dictionary stores [link_id,commodity_id] as keys and each key is associated with (1 X number of time steps)
# dimensional array of costs per (link, commodity) pair

import numpy as np
from copy import deepcopy
class Link_Costs_class():
    #To initialize the link_costs dictionary, the constructor has to receive a list of all links, a list of all commodities and
    # number of time steps in the period considered
    def __init__(self, links_list, commodity_list, num_time_steps):
        self.__links_list = links_list
        self.__commodity_list = commodity_list
        self.__num_time_steps = num_time_steps
        self.__link_costs = {}

    # Get number of links
    def get_num_links(self):
        return len(self.__links_list)

    # Get number of commodities
    def get_num_commodities(self):
        return len(self.__commodity_list)

    # Get number of time steps
    def get_num_time_step(self):
        return self.__num_time_steps

    # Return all the cost
    def get_all_costs(self):
        return self.__link_costs

    # Returns costs of a particular link, commodity, and time_step
    def get_cost_at_link_comm_time(self, link_id, comm_id, time_step):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        if time_step < 0 or time_step > (self.__num_time_steps-1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps-1
            return

        return self.__link_costs[(link_id, comm_id)][time_step]

    # Returns all costs of a particular link with link_id as a [comm-id]: [cost_1, cost_2,...]
    # dictionary
    def get_all_costs_on_link(self, link_id):
        if link_id not in self.__links_list :
            print("Link id not in list_costs object")
            return
        comm_dict = {}
        for key in self.__link_costs.keys():
            if key[0] == link_id:
                comm_dict[key[1]] = self.__link_costs[key]
        return comm_dict

    #Returns all costs of a particular link and commodity as an array of size: number of time steps
    def get_all_costs_on_link_comm(self, link_id, comm_id):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        return self.__link_costs[(link_id,comm_id)]


    #Returns all costs of particular link and time_step as [commodity_id]: [cost_1] dictionary
    def get_all_costs_on_link_time_step(self, link_id, time_step):
        if link_id not in self.__links_list :
            print("Link id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return
        comm_time_dict = {}
        for key in self.__link_costs.keys():
            if key[0] == link_id:
                comm_time_dict[key[1]] = self.__link_costs[key][time_step]
        return comm_time_dict


    # Returns all costs fpr commodity with commodity_id as a [link_id]: [cost_1, cost_2, ...] dictionary
    def get_all_costs_for_commodity(self, comm_id):
        if comm_id not in self.__commodity_list:
            print("Commodity id not in list_costs object")
            return

        link_dict = {}
        for key in self.__link_costs.keys():
            if key[1] == comm_id:
                link_dict[key[0]] = self.__link_costs[key]
        return link_dict


    # Returns all costs for commodity with comm_id and time_step as [link_id]: [cost_1] dictionary
    def get_all_costs_on_comm_time_step(self, comm_id, time_step):
        if comm_id not in self.__commodity_list:
            print("Commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        link_time_dict = {}
        for key in self.__link_costs.keys():
            if key[1] == comm_id:
                link_time_dict[key[0]] = self.__link_costs[key][time_step]
        return link_time_dict

    # Returns all costs for a particular time_step as a [(link_id,comm_id)]:[cost_time_step] dictionary
    def get_all_costs_for_time_step(self, time_step):
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return

        time_dict = {}
        for key in self.__link_costs.keys():
            time_dict[key] = self.__link_costs[key][time_step]
        return time_dict

    # Sets all the costs with an costs dictionary
    def set_all_costs(self, costs):
        if (any(len(key) != 2 for key in costs.keys()) or
                any(len(value) != self.__num_time_steps for value in costs.values())):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if any(key[0] not in self.__links_list or key[1] not in self.__commodity_list
               for key in costs.keys()):
            print("Link id or commodity id not in original network")

        if any(value < 0 for value in costs.values()):
            print("Error: Negative value for cost")
            return
        self.__link_costs = deepcopy(costs)

    # set cost for a particular link, commodity, and time_step or adds the entry if did not exist in the dictionary
    def set_cost_at_link_comm_time(self, link_id, comm_id, time_step, cost):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        if cost < 0:
            print("Error: Negative value for cost")
            return
        if((link_id,comm_id) in self.__link_costs.keys()):
            self.__link_costs[(link_id, comm_id)][time_step] = cost
        else:
            self.__link_costs[(link_id,comm_id)] = np.zeros((self.__num_time_steps))
            self.__link_costs[(link_id, comm_id)][time_step] = cost

    # Sets all costs for a link with link_id with a [comm_id_1]:[cost_t1, cost_t2,...] dictionary
    def set_all_costs_on_link(self, link_id, costs):
        if (any(not isinstance(key, ( int, long ))  for key in costs.keys()) or
                any(len(value) != self.__num_time_steps for value in costs.values())):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if link_id not in self.__links_list or any(comm_id not in self.__commodity_list for comm_id in costs.keys()):
            print("Link id not in list_costs object")
            return

        if any(value[i] < 0 for value in costs.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for cost")
            return

        for comm_id in costs.keys():
            if ((link_id, comm_id) in self.__link_costs.keys()):
                self.__link_costs[(link_id, comm_id)] = costs[comm_id]
            else:
                self.__link_costs[(link_id, comm_id)] = costs[comm_id]


    #Set all costs to a particular link and commodity with an array of size: number of time steps
    def set_all_costs_on_link_comm(self, link_id, comm_id, costs):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        if (len(costs) != self.__num_time_steps):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if (any(cost < 0 for cost in costs for i in range(self.__num_time_steps))):
            print("Error: Negative value for cost")
            return

        self.__link_costs[(link_id, comm_id)] = costs


    #Set all costs for a particular link and time_step with a [comm_id_1]:[cost_at_time_step] dictionary
    def set_all_costs_on_link_time_step(self, link_id, time_step, costs):
        if ( any(not isinstance(key, (int, long))  for key in costs.keys()) or
                any(not isinstance(value, (int, long)) for value in costs.values())):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if link_id not in self.__links_list or any(comm_id not in self.__commodity_list for comm_id in costs.keys()):
            print("Link id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print"Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return

        if any(cost < 0 for cost in costs.values()):
            print("Error: Negative value for cost")
            return

        for comm_id in costs.keys():
            if ((link_id, comm_id) in self.__link_costs.keys()):
                self.__link_costs[(link_id, comm_id)][time_step] = costs[comm_id]
            else:
                self.__link_costs[(link_id, comm_id)] = np.zeros((self.__num_time_steps))
                self.__link_costs[(link_id, comm_id)][time_step] = costs[comm_id]


    # Set all costs for commodity with commodity_id a [link_id_1]:[cost_t1, cost_t2,...] dictionary
    def set_all_costs_for_commodity(self, comm_id, costs):
        if (any(not isinstance(key, ( int, long ))  for key in costs.keys()) or
                any(len(value) != self.__num_time_steps for value in costs.values())):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if comm_id not in self.__commodity_list or any(link_id not in self.__links_list for link_id in costs.keys()):
            print("Commodity id not in list_costs object")
            return

        if any(value[i] < 0 for value in costs.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value for cost")
            return

        for link_id in costs.keys():
            if ((link_id, comm_id) in self.__link_costs.keys()):
                self.__link_costs[(link_id, comm_id)] = costs[link_id]
            else:
                self.__link_costs[(link_id, comm_id)] =costs[link_id]


    # Set all costs for a particular commodity and time_step with a [link_id_1]:[cost_at_time_step] dictionary
    def set_all_costs_on_comm_time_step(self, comm_id, time_step, costs):
        if (any(not isinstance(key, (int, long))  for key in costs.keys()) or
                any(not isinstance(value, (int, long)) for value in costs.values())):
            print("Error: shape of input costs does not match shape of link_costs object")
            return

        if any(link_id not in self.__links_list for link_id in costs.keys()) or comm_id not in self.__commodity_list:
            print("Commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        if any(cost < 0 for cost in costs.values()):
            print("Error: Negative value for cost")
            return

        for link_id in costs.keys():
            if ((link_id, comm_id) in self.__link_costs.keys()):
                self.__link_costs[(link_id, comm_id)][time_step] = costs[link_id]
            else:
                self.__link_costs[(link_id, comm_id)] = np.zeros((self.__num_time_steps))
                self.__link_costs[(link_id, comm_id)][time_step] =costs[link_id]

    # Returns all costs for a particular time_step as with a [(link_id,commodity_id)]:[cost_time_step]
    # dictionary
    def set_all_costs_for_time_step(self, time_step, costs):
        if (any(len(key) != 2 for key in costs.keys()) or
                any(not isinstance(value, (int, long)) for value in costs.values())):
            print("Error: shape of input cost does not match shape of link_costs object")
            return

        if any(key[0] not in self.__links_list or key[1] not in self.__commodity_list
               for key in costs.keys()):
            print("Link id or commodity id not in original network")
            return

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        if any(cost < 0 for cost in costs.values()):
            print("Error: Negative value for cost")
            return

        for key in costs.keys():
            if key in self.__link_costs.keys():
                self.__link_costs[key][time_step] = costs[key]
            else:
                self.__link_costs[key] = np.zeros((self.__num_time_steps))
                self.__link_costs[key][time_step] = costs[key]


    def print_all(self):
        for key in self.__link_costs.keys():
            for k in range(self.__num_time_steps):
                print "link ", key[0], " commodity ", key[1], " time step ", k, " cost ", self.__link_costs[key][k]
