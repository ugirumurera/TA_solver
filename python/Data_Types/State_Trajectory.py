# This is an object that stores a three dimensional array of Traffic State objects.
# The traffic state object stores the traffic state per link_id(i), per commodity(j) and per time step k, where
# a traffic state can include flow, number of vehicles (density, and queue

from Traffic_States.Traffic_State import Abstract_Traffic_State
class State_Trajectory_class():
    def __init__(self, num_links, num_commodities, num_time_steps):
        self.__num_links = num_links
        self.__num_commodities = num_commodities
        self.__num_time_steps = num_time_steps
        self.__state_trajectory = [[[Abstract_Traffic_State for k in range(num_time_steps)] for j in range (num_commodities)]
                                 for i in range(num_links)]

    def get_num_links(self):
        return self.__num_links

    def get_commodities(self):
        return self.__num_commodities

    def get_num_time_step(self):
        return self.__num_time_steps

    # Returns the Traffic state of link with link_id, commodity with comm_id, and at time time_step
    def get_state_link_comm_time(self, link_id, comm_id, time_step):
        return self.__state_trajectory[link_id][comm_id][time_step]

    # Sets the Traffic state of link with link_id, commodity with comm_id, and at time time_step
    def set_state_link_comm_time(self, link_id, comm_id, time_step, state_object):
        self.__state_trajectory[link_id][comm_id][time_step] = state_object

    # Prints out the Traffic state of link with link_id, commodity with comm_id, and at time time_step
    def print_link_comm_time(self, link_id, comm_id, time_step):
        self.__state_trajectory[link_id][comm_id][time_step].print_state()

    # Prints out all the traffic states
    def print_all(self):
        for i in range(self.__num_links):
            for j in range(self.__num_commodities):
                for k in range(self.__num_time_steps):
                    self.__state_trajectory[i][j][k].print_state()


    # Returns just the values of all the traffic state objects as a list,  this would be useful for ease of manipulation
    def get_state_values_as_list(self):
        link_state_values = list()
        for i in range(self.__num_links):
            for j in range(self.__num_commodities):
                for k in range(self.__num_time_steps):
                    link_state_values.append(self.__state_trajectory[i][j][k].get_state_value())

        return link_state_values

