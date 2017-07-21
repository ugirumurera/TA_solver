# This is an object that stores a dictionary of Traffic State objects.
# The dictionary stores [link_id,commodity_id] as keys and each key is associated with (1 X number of time steps)
# dimensional array of traffic state objects per (link, commodity) pair.
# a traffic state can include flow, number of vehicles (density), and queue


from Traffic_States.Abstract_Traffic_State import Abstract_Traffic_State_class

class State_Trajectory_class():
    # The constructor receives a list of link ids (link_list), a list of commodities (commodity_list), the number
    # of time steps, and dt, the duration of one time_step
    def __init__(self, link_list, commodity_list, num_time_steps,dt):
        self.__links_list = link_list
        self.__commodity_list = commodity_list
        self.__num_time_steps = num_time_steps
        self.__dt = dt
        self.__state_trajectory = {}

    def get_num_links(self):
        return len(self.__links_list)

    def get_commodities(self):
        return len(self.__commodity_list)

    def get_num_time_step(self):
        return self.__num_time_steps

    # Return all the states
    def get_all_states(self):
        return self.__state_trajectory

    # Returns the state of a particular link, commodity, and time_step
    def get_state_on_link_comm_time(self, link_id, comm_id, time_step):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in State_Trajectory object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps-1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps-1)
            return
        return self.__state_trajectory[(link_id, comm_id)][time_step]

    # Returns all states of a particular link with link_id as a [commodity_id]: [cost_1, cost_2,...]
    # dictionary
    def get_all_states_on_link(self, link_id):
        if link_id not in self.__links_list :
            print("Link id not in State_Trajectory object")
            return
        comm_dict = {}
        for key in self.__state_trajectory.keys():
            if key[0] == link_id:
                comm_dict[key[1]] = self.__state_trajectory[key]
        return comm_dict

    #Returns all states of a particular link and commodity as an array of size: number of time steps
    def get_all_states_on_link_comm(self, link_id, comm_id):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in State_Trajectory object")
            return

        return self.__state_trajectory[(link_id,comm_id)]


    #Returns all states of a particular link and time_step as [commodity_id]: [cost_1] dictionary
    def get_all_states_on_link_time_step(self, link_id, time_step):
        if link_id not in self.__links_list :
            print("Commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return
        comm_time_dict = {}
        for key in self.__state_trajectory.keys():
            if key[0] == link_id:
                comm_time_dict[key[1]] = self.__state_trajectory[key][time_step]
        return comm_time_dict


    # Returns all states of commodity with commodity_id as a [link_id]: [cost_1, cost_2, ...] dictionary
    def get_all_states_for_commodity(self, comm_id):
        if comm_id not in self.__commodity_list:
            print("Commodity id not in list_costs object")
            return

        link_dict = {}
        for key in self.__state_trajectory.keys():
            if key[1] == comm_id:
                link_dict[key[0]] = self.__state_trajectory[key]
        return link_dict


    # Returns all states of commodity with comm_id and time_step as [link_id]: [cost_1] dictionary
    def get_all_states_on_comm_time_step(self, comm_id, time_step):
        if comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        link_time_dict = {}
        for key in self.__state_trajectory.keys():
            if key[1] == comm_id:
                link_time_dict[key[0]] = self.__state_trajectory[key][time_step]
        return link_time_dict

    # Returns all states of a particular time_step as a [(link_id,comm_id)]:[cost_time_step] dictionary
    def get_all_states_for_time_step(self, time_step):
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return

        time_dict = {}
        for key in self.__state_trajectory.keys():
            time_dict[key] = self.__state_trajectory[key][time_step]
        return time_dict

    # Sets all states with an state_trajectory dictionary
    def set_all_states(self, states):
        if (any(len(key) != 2 for key in states.keys()) or
                any(len(value) != self.__num_time_steps for value in states.values())):
            print("Error: shape of input state does not match shape of State_Trajectory object")
            return

        if any(key[0] not in self.__links_list or key[1] not in self.__commodity_list
               for key in states.keys()):
            print("Link id or commodity id not in State_Trajectory object")

        if any(not isinstance(state[i], Abstract_Traffic_State_class) for state in states.values()
               for i in range(self.__num_time_steps)):
            print "Error: states to be assigned not a traffic_state object"
            return

        if any(value[i].is_negative() for value in states.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value in state object")
            return

        self._state_trajectory = states

    # set state for a particular link, commodity, and time_step or adds the entry if did not exist in the dictionary
    def set_state_on_link_comm_time(self, link_id, comm_id, time_step, state):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        if not isinstance(state, Abstract_Traffic_State_class):
            print("Error: cost to be assigned not a Traffic State object")
            return

        if state.is_negative():
            print("Error: Negative value in state object")
            return
        if((link_id,comm_id) in self.__state_trajectory.keys()):
            self.__state_trajectory[(link_id, comm_id)][time_step] = state
        else:
            self.__state_trajectory[(link_id,comm_id)] = [Abstract_Traffic_State_class for k in range(self.__num_time_steps)]
            self.__state_trajectory[(link_id, comm_id)][time_step] = state


    # Sets all states for a link with link_id with a [comm_id_1]:[state_t0, state_t1,...] dictionary
    def set_all_states_on_link(self, link_id, states):
        if (any( not isinstance(key, ( int, long ))  for key in states.keys()) or
                any(len(value) != self.__num_time_steps for value in states.values())):
            print("Error: shape of input states does not match shape of state_trajectory object")
            return

        if link_id not in self.__links_list or any(comm_id not in self.__commodity_list for comm_id in states.keys()):
            print("Link id or commodity id not in list_costs object")
            return

        if any(not isinstance(state[i], Abstract_Traffic_State_class) for state in states.values()
               for i in range(self.__num_time_steps)):
            print("Error: state to be assigned not a Traffic state object")
            return

        if any(value[i].is_negative() for value in states.values() for i in range(self.__num_time_steps)):
            print("Error: Negative value in state object")
            return

        for comm_id in states.keys():
            self.__state_trajectory[(link_id, comm_id)] = states[comm_id]


    #Set all states to a particular link and commodity with an array of size: number of time steps
    def set_all_states_on_link_comm(self, link_id, comm_id, states):
        if link_id not in self.__links_list or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        if (len(states) != self.__num_time_steps):
            print("Error: size of state variable does not match state_trajectory array size")
            return

        if any(not isinstance(state, Abstract_Traffic_State_class) for state in states):
            print("Error: state to be assigned not a Traffic state object")
            return

        if (any(state.is_negative() for state in states for i in range(self.__num_time_steps))):
            print("Error: Negative value in Traffic State")
            return

        self.__state_trajectory[(link_id, comm_id)] = states


    #Set all states for a particular link and time_step with a [commodity_id]:[state_at_time_step] dictionary
    def set_all_states_on_link_time_step(self, link_id, time_step, states):
        if (any(not isinstance(key, (int, long))  for key in states.keys()) or
                any(not isinstance(value, Abstract_Traffic_State_class) for value in states.values())):
            print("Error: size of demand array does not match state_trajectory array size")
            return

        if link_id not in self.__links_list or any(comm_id not in self.__commodity_list for comm_id in states.keys()):
            print("Link id or commodity id not in list_costs object")
            return
        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print("Error: time period has to be between 0 and ", self.__num_time_steps - 1)
            return

        if any(state.is_negative() for state in states.values()):
            print("Error: Negative value in traffic state")
            return

        for comm_id in states.keys():
            if ((link_id, comm_id) in self.__state_trajectory.keys()):
                self.__state_trajectory[(link_id, comm_id)][time_step] = states[comm_id]
            else:
                self.__state_trajectory[(link_id, comm_id)] = [Abstract_Traffic_State_class
                                                               for k in range(self.__num_time_steps)]
                self.__state_trajectory[(link_id, comm_id)][time_step] = states[comm_id]


    # Set all states for commodity with commodity_id a [link_id_1]:[state_t0, cost_t1,...] dictionary
    def set_all_states_for_commodity(self, comm_id, states):
        if (any(not isinstance(key, ( int, long ))  for key in states.keys()) or
                any(len(value) != self.__num_time_steps for value in states.values())):
            print("Error: shape of input does not match shape of state_trajectory object")
            return

        if comm_id not in self.__commodity_list or any(link_id not in self.__links_list for link_id in states.keys()):
            print("Link id or commodity id not in list_costs object")
            return

        if any(not isinstance(state[i], Abstract_Traffic_State_class) for state in states.values()
               for i in range(self.__num_time_steps)):
            print("Error: state to be assigned not a Traffic state object")
            return

        if (any(state[i].is_negative() for state in states.values() for i in range(self.__num_time_steps))):
            print("Error: Negative value in Traffic State")
            return

        for link_id in states.keys():
            if ((link_id, comm_id) in self.__state_trajectory.keys()):
                self.__state_trajectory[(link_id, comm_id)] = states[link_id]
            else:
                self.__state_trajectory[(link_id, comm_id)] = states[link_id]


    # Set all states for a particular commodity and time_step with a [link_id_1]:[cost_at_time_step] dictionary
    def set_all_states_on_comm_time_step(self, comm_id, time_step, states):
        if (any(not isinstance(key, (int, long))  for key in states.keys()) or
                any(not isinstance(value, Abstract_Traffic_State_class) for value in states.values())):
            print("Error: shape of input states does not match shape of state_trajectory object")
            return

        if any(link_id not in self.__links_list for link_id in states.keys()) or comm_id not in self.__commodity_list:
            print("Link id or commodity id not in list_costs object")
            return

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return

        if any(value.is_negative() for value in states.values()):
            print("Error: Negative value for state object")
            return

        for link_id in states.keys():
            if ((link_id, comm_id) in self.__state_trajectory.keys()):
                self.__state_trajectory[(link_id, comm_id)][time_step] = states[link_id]
            else:
                self.__state_trajectory[(link_id, comm_id)] = [Abstract_Traffic_State_class for k in range(self.__num_time_steps-1)]
                self.__state_trajectory[(link_id, comm_id)][time_step] = states[link_id]


    # Returns all demands assigned for a particular time_step as with a [(link_id,commodity_id)]:[cost_time_step]
    # dictionary
    def set_all_demands_for_time_step(self, time_step, states):
        if (any(len(key) != 2 for key in states.keys()) or
                any(not isinstance(value, Abstract_Traffic_State_class) for value in states.values())):
            print("Error: shape of input demand does not match shape state_trajectory object")
            return

        if any(key[0] not in self.__links_list or key[1] not in self.__commodity_list
               for key in states.keys()):
            print("Link id or commodity id not in original network")
            return

        if time_step < 0 or time_step > (self.__num_time_steps - 1):
            print "Error: time period has to be between 0 and ", self.__num_time_steps - 1
            return

        if any(value.is_negative() for value in states.values()):
            print("Error: Negative value for demand")
            return

        for key in states.keys():
            if key in self.__state_trajectory.keys():
                self.__state_trajectory[key][time_step] = states[key]
            else:
                self.__state_trajectory[key] = [Abstract_Traffic_State_class for k in range(self.__num_time_steps)]
                self.__state_trajectory[key][time_step] = states[key]


    def print_all(self):
        for key in self.__state_trajectory.keys():
            for k in range(self.__num_time_steps):
                print "link ", key[0], " commodity ", key[1], " time step ", k, " state ",
                self.__state_trajectory[key][k].print_state()

