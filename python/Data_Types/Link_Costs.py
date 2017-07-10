# This is an object that stores a three dimensional array of costs per link
# Each entry (i,j,k) in the array is the cost for link (i) for commodity (j) at time step (k)

import numpy as np
class Link_Costs_class():
    #To initialize the Assignment Array, the constructor has to receive the number of links, number of commodities and
    # number of time steps in the period considered
    def __init__(self, num_links, num_commodities, num_time_steps):
        self.__num_links = num_links
        self.__num_commodities = num_commodities
        self.__num_time_steps = num_time_steps
        self.__link_costs = np.zeros((num_links, num_commodities, num_time_steps))

    # Get number of links
    def get_num_links(self):
        return self.__num_links

    # Get number of commodities
    def get_commodities(self):
        return self.__num_commodities

    # Get number of time steps
    def get_num_time_step(self):
        return self.__num_time_steps

    # Return all the cost
    def get_all_costs(self):
        return self.__link_costs

    # Returns cost of on link_id, commodity, and time_step
    def get_cost_at_link_comm_time(self, link_id, comm_id, time_step):
        return self.__link_costs[link_id, comm_id, time_step]

    # Returns all costs on a link with link_id as a (number of commodities x number of time steps) dimensional array
    def get_all_costs_on_link(self, link_id):
        return self.__link_costs[link_id,:,:]

    #Returns all costs to on a link and commodity as an array of size: number of time steps
    def get_all_costs_on_link_comm(self, link_id, comm_id):
        return self.__link_costs[link_id,comm_id,:]

    #Returns all costs on a link and time_step as an array of size: number of commodities
    def get_all_costs_on_link_time_step(self, link_id, time_step):
        return self.__link_costs[link_id,:,time_step]

    # Returns all costs fora commodity with commodity_id as a (number of links x number of time steps)
    # dimensional array
    def get_all_costs_for_commodity(self, comm_id):
        return self.__link_costs[:, comm_id, :]

    # Returns all costs for a particular commodity and time_step as an array of size: number of links
    def get_all_costs_on_comm_time_step(self, comm_id, time_step):
        return self.__link_costs[:, comm_id, time_step]

    # Returns all costs for a particular time_step as a (number of links x number of commodities) dimensional array
    def get_all_costs_for_time_step(self, time_step):
        return self.__link_costs[:, :, time_step]

    # Sets all costs with a three dimensional array
    def set_all_costs(self, costs):
        if (costs.shape[0] != self.__num_links or costs.shape[1] != self.__num_commodities or
                    costs.shape[2] != self.__num_time_steps ):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if any(costs < 0):
            print("Error: Negative value for demand")
            return
        self.__link_costs[:, :, :] = costs

    # Sets costs for a particular link, commodity, and time_step
    def set_costs_at_link_comm_time(self, link_id, comm_id, time_step, costs):
        if(costs < 0):
            print("Error: Negative value for demand")
            return
        self.__link_costs[link_id, comm_id, time_step] = costs

    # Sets all costs for a particular link with link_id with a (number of commodities x number of time steps)
    # dimensional numpy array
    def set_all_costs_on_link(self, link_id, costs):
        if (costs.shape[0] != self.__num_commodities or costs.shape[1] != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if any(costs < 0):
            print("Error: Negative value for demand")
            return
        self.__link_costs[link_id,:,:] = costs

    #Sets all costs for a particular link and commodity with an array of size: number of time steps
    def set_all_costs_on_link_comm(self, link_id, comm_id, costs):
        if (len(costs) != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(costs < 0)):
            print("Error: Negative value for demand")
            return
        self.__link_costs[link_id,comm_id,:] = costs

    #Sets costs for a particular link and time_step with an array of size: number of commodities
    def set_all_costs_on_link_time_step(self, link_id, time_step, costs):
        if(len(costs) != self.__num_commodities):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(costs < 0)):
            print("Error: Negative value for demand")
            return
        self.__link_costs[link_id,:,time_step] = costs

    # Sets costs for commodity with commodity_id with a (number of links x number of time steps)
    # dimensional array
    def set_all_costs_for_commodity(self, comm_id, costs):
        if (costs.shape[0] != self.__num_links or costs.shape[1] != self.__num_time_steps):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(costs < 0)):
            print("Error: Negative value for demand")
            return

        self.__link_costs[:, comm_id, :] = costs

    # Sets costs for a particular commodity and time_step with an array of size: number of links
    def set_all_costs_on_comm_time_step(self, comm_id, time_step, costs):
        if(len(costs) != self.__num_links):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(costs < 0)):
            print("Error: Negative value for demand")
            return

        self.__link_costs[:,comm_id,time_step] = costs

    # Sets costs assigned for a particular time_step with a (number of links x number of commodities)
    # dimensional array
    def set_all_costs_for_time_step(self, time_step, costs):
        if (costs.shape[0] != self.__num_links or costs.shape[1] != self.__num_commodities):
            print("Error: size of demand array does not match demand assignment array size")
            return

        if (any(costs < 0)):
            print("Error: Negative value for demand")
            return

        self.__link_costs[:, :, time_step] = costs


    # Prints out all the traffic states
    def print_all(self):
        for i in range(self.__num_links):
            for j in range(self.__num_commodities):
                for k in range(self.__num_time_steps):
                    print "link ", i, " commodity ", j, " time step ", k, " cost",
                    print(self.__link_costs[i,j,k])